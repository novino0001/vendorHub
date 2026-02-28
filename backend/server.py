from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import jwt
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production-12345')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Create the main app without a prefix
app = FastAPI(title="Contractor Hub API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()


# ============= MODELS =============
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserRole(str):
    VENDOR = "vendor"
    FIRM = "firm"


class Category(str):
    CIVIL = "civil"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    TRANSPORT = "transport"


# Request/Response Models
class VendorSignupRequest(BaseModel):
    vendor_name: str
    email: EmailStr
    phone: str
    password: str
    gst_no: str
    revenue: float
    employee_count: int
    categories: List[Literal["civil", "mechanical", "electrical", "transport"]]
    service_locations: List[str]
    short_bio: str
    avatar_base64: Optional[str] = None

    @validator('gst_no')
    def validate_gst(cls, v):
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gst_pattern, v):
            raise ValueError('Invalid GST number format')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number')
        return v

    @validator('categories')
    def validate_categories(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one category is required')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str


class VendorResponse(BaseModel):
    id: str
    vendor_name: str
    email: str
    phone: str
    categories: List[str]
    service_locations: List[str]
    short_bio: str
    avatar_base64: Optional[str] = None
    created_at: datetime


class VendorFullProfileResponse(VendorResponse):
    gst_no: str
    revenue: float
    employee_count: int


class VendorPublicProfileResponse(BaseModel):
    id: str
    vendor_name: str
    categories: List[str]
    service_locations: List[str]
    short_bio: str
    avatar_base64: Optional[str] = None


class VendorUpdateRequest(BaseModel):
    vendor_name: Optional[str] = None
    phone: Optional[str] = None
    gst_no: Optional[str] = None
    revenue: Optional[float] = None
    employee_count: Optional[int] = None
    categories: Optional[List[str]] = None
    service_locations: Optional[List[str]] = None
    short_bio: Optional[str] = None
    avatar_base64: Optional[str] = None


class FirmResponse(BaseModel):
    id: str
    name: str
    category: str
    office_location: str
    description: str
    logo_base64: Optional[str] = None
    is_following: Optional[bool] = False


class PaginatedVendorsResponse(BaseModel):
    vendors: List[VendorPublicProfileResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class PaginatedFirmsResponse(BaseModel):
    firms: List[FirmResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ============= UTILITY FUNCTIONS =============
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


async def get_current_vendor(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != UserRole.VENDOR:
        raise HTTPException(status_code=403, detail="Not authorized as vendor")
    
    vendor = await db.vendors.find_one({"user_id": str(current_user["_id"])})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    
    return vendor


# ============= API ROUTES =============

@api_router.post("/auth/signup/vendor", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup_vendor(vendor_data: VendorSignupRequest):
    # Check if email already exists
    existing_user = await db.users.find_one({"email": vendor_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_pw = hash_password(vendor_data.password)
    user_doc = {
        "email": vendor_data.email,
        "password_hash": hashed_pw,
        "role": UserRole.VENDOR,
        "created_at": datetime.utcnow()
    }
    user_result = await db.users.insert_one(user_doc)
    user_id = str(user_result.inserted_id)
    
    # Create vendor profile
    vendor_doc = {
        "user_id": user_id,
        "vendor_name": vendor_data.vendor_name,
        "phone": vendor_data.phone,
        "gst_no": vendor_data.gst_no,
        "revenue": vendor_data.revenue,
        "employee_count": vendor_data.employee_count,
        "categories": vendor_data.categories,
        "service_locations": vendor_data.service_locations,
        "short_bio": vendor_data.short_bio,
        "avatar_base64": vendor_data.avatar_base64,
        "created_at": datetime.utcnow()
    }
    await db.vendors.insert_one(vendor_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id, "role": UserRole.VENDOR})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        role=UserRole.VENDOR
    )


@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user["_id"]),
        role=user["role"]
    )


@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    if current_user["role"] == UserRole.VENDOR:
        vendor = await db.vendors.find_one({"user_id": user_id})
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")
        
        return {
            "id": user_id,
            "email": current_user["email"],
            "role": current_user["role"],
            "vendor_name": vendor["vendor_name"],
            "phone": vendor["phone"],
            "gst_no": vendor["gst_no"],
            "revenue": vendor["revenue"],
            "employee_count": vendor["employee_count"],
            "categories": vendor["categories"],
            "service_locations": vendor["service_locations"],
            "short_bio": vendor["short_bio"],
            "avatar_base64": vendor.get("avatar_base64"),
            "created_at": vendor["created_at"]
        }
    
    return {
        "id": user_id,
        "email": current_user["email"],
        "role": current_user["role"]
    }


@api_router.get("/vendors/me", response_model=VendorFullProfileResponse)
async def get_my_vendor_profile(vendor: dict = Depends(get_current_vendor), current_user: dict = Depends(get_current_user)):
    return VendorFullProfileResponse(
        id=str(current_user["_id"]),
        vendor_name=vendor["vendor_name"],
        email=current_user["email"],
        phone=vendor["phone"],
        gst_no=vendor["gst_no"],
        revenue=vendor["revenue"],
        employee_count=vendor["employee_count"],
        categories=vendor["categories"],
        service_locations=vendor["service_locations"],
        short_bio=vendor["short_bio"],
        avatar_base64=vendor.get("avatar_base64"),
        created_at=vendor["created_at"]
    )


@api_router.put("/vendors/me", response_model=VendorFullProfileResponse)
async def update_my_vendor_profile(
    update_data: VendorUpdateRequest,
    vendor: dict = Depends(get_current_vendor),
    current_user: dict = Depends(get_current_user)
):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if update_dict:
        await db.vendors.update_one(
            {"user_id": str(current_user["_id"])},
            {"$set": update_dict}
        )
    
    # Fetch updated vendor
    updated_vendor = await db.vendors.find_one({"user_id": str(current_user["_id"])})
    
    return VendorFullProfileResponse(
        id=str(current_user["_id"]),
        vendor_name=updated_vendor["vendor_name"],
        email=current_user["email"],
        phone=updated_vendor["phone"],
        gst_no=updated_vendor["gst_no"],
        revenue=updated_vendor["revenue"],
        employee_count=updated_vendor["employee_count"],
        categories=updated_vendor["categories"],
        service_locations=updated_vendor["service_locations"],
        short_bio=updated_vendor["short_bio"],
        avatar_base64=updated_vendor.get("avatar_base64"),
        created_at=updated_vendor["created_at"]
    )


@api_router.get("/vendors", response_model=PaginatedVendorsResponse)
async def list_vendors(
    category: Optional[str] = None,
    location: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    # Build query
    query = {}
    if category:
        query["categories"] = category
    if location:
        query["service_locations"] = {"$regex": location, "$options": "i"}
    
    # Exclude current user from listing
    query["user_id"] = {"$ne": str(current_user["_id"])}
    
    # Get total count
    total = await db.vendors.count_documents(query)
    
    # Build sort
    sort_field = "created_at"
    sort_order = -1
    if sort_by == "revenue":
        sort_field = "revenue"
    elif sort_by == "employee_count":
        sort_field = "employee_count"
    
    # Fetch vendors
    skip = (page - 1) * per_page
    vendors_cursor = db.vendors.find(query).sort(sort_field, sort_order).skip(skip).limit(per_page)
    vendors = await vendors_cursor.to_list(length=per_page)
    
    # Map to response (public view - limited fields)
    vendor_list = [
        VendorPublicProfileResponse(
            id=v["user_id"],
            vendor_name=v["vendor_name"],
            categories=v["categories"],
            service_locations=v["service_locations"],
            short_bio=v["short_bio"],
            avatar_base64=v.get("avatar_base64")
        )
        for v in vendors
    ]
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedVendorsResponse(
        vendors=vendor_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@api_router.get("/vendors/{vendor_id}", response_model=VendorPublicProfileResponse)
async def get_vendor_public_profile(vendor_id: str, current_user: dict = Depends(get_current_user)):
    # Find user by ID
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid vendor ID")
    
    user = await db.users.find_one({"_id": ObjectId(vendor_id)})
    if not user or user["role"] != UserRole.VENDOR:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    vendor = await db.vendors.find_one({"user_id": vendor_id})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    
    return VendorPublicProfileResponse(
        id=vendor_id,
        vendor_name=vendor["vendor_name"],
        categories=vendor["categories"],
        service_locations=vendor["service_locations"],
        short_bio=vendor["short_bio"],
        avatar_base64=vendor.get("avatar_base64")
    )


@api_router.get("/firms", response_model=PaginatedFirmsResponse)
async def list_firms(
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    # Get total count
    total = await db.firms.count_documents({})
    
    # Fetch firms
    skip = (page - 1) * per_page
    firms_cursor = db.firms.find({}).skip(skip).limit(per_page)
    firms = await firms_cursor.to_list(length=per_page)
    
    # Check which firms the current user is following
    following_cursor = db.firm_followers.find({"vendor_id": str(current_user["_id"])})
    following = await following_cursor.to_list(length=None)
    following_firm_ids = {f["firm_id"] for f in following}
    
    # Map to response
    firm_list = [
        FirmResponse(
            id=str(f["_id"]),
            name=f["name"],
            category=f["category"],
            office_location=f["office_location"],
            description=f["description"],
            logo_base64=f.get("logo_base64"),
            is_following=str(f["_id"]) in following_firm_ids
        )
        for f in firms
    ]
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedFirmsResponse(
        firms=firm_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@api_router.get("/firms/{firm_id}")
async def get_firm(firm_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(firm_id):
        raise HTTPException(status_code=400, detail="Invalid firm ID")
    
    firm = await db.firms.find_one({"_id": ObjectId(firm_id)})
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    # Check if following
    following = await db.firm_followers.find_one({
        "firm_id": firm_id,
        "vendor_id": str(current_user["_id"])
    })
    
    return FirmResponse(
        id=str(firm["_id"]),
        name=firm["name"],
        category=firm["category"],
        office_location=firm["office_location"],
        description=firm["description"],
        logo_base64=firm.get("logo_base64"),
        is_following=following is not None
    )


@api_router.post("/firms/{firm_id}/follow")
async def follow_firm(firm_id: str, vendor: dict = Depends(get_current_vendor), current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(firm_id):
        raise HTTPException(status_code=400, detail="Invalid firm ID")
    
    # Check if firm exists
    firm = await db.firms.find_one({"_id": ObjectId(firm_id)})
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    # Check if already following
    existing = await db.firm_followers.find_one({
        "firm_id": firm_id,
        "vendor_id": str(current_user["_id"])
    })
    
    if existing:
        return {"message": "Already following this firm", "is_following": True}
    
    # Create follow relationship
    follow_doc = {
        "firm_id": firm_id,
        "vendor_id": str(current_user["_id"]),
        "created_at": datetime.utcnow()
    }
    await db.firm_followers.insert_one(follow_doc)
    
    return {"message": "Successfully followed firm", "is_following": True}


@api_router.delete("/firms/{firm_id}/unfollow")
async def unfollow_firm(firm_id: str, vendor: dict = Depends(get_current_vendor), current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(firm_id):
        raise HTTPException(status_code=400, detail="Invalid firm ID")
    
    # Delete follow relationship
    result = await db.firm_followers.delete_one({
        "firm_id": firm_id,
        "vendor_id": str(current_user["_id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not following this firm")
    
    return {"message": "Successfully unfollowed firm", "is_following": False}


@api_router.get("/vendors/me/following")
async def get_my_following(
    current_user: dict = Depends(get_current_user),
    vendor: dict = Depends(get_current_vendor)
):
    # Get all firms the vendor is following
    following_cursor = db.firm_followers.find({"vendor_id": str(current_user["_id"])})
    following = await following_cursor.to_list(length=None)
    
    firm_ids = [ObjectId(f["firm_id"]) for f in following if ObjectId.is_valid(f["firm_id"])]
    
    if not firm_ids:
        return {"firms": [], "total": 0}
    
    # Fetch firm details
    firms_cursor = db.firms.find({"_id": {"$in": firm_ids}})
    firms = await firms_cursor.to_list(length=None)
    
    firm_list = [
        FirmResponse(
            id=str(f["_id"]),
            name=f["name"],
            category=f["category"],
            office_location=f["office_location"],
            description=f["description"],
            logo_base64=f.get("logo_base64"),
            is_following=True
        )
        for f in firms
    ]
    
    return {"firms": firm_list, "total": len(firm_list)}


# Seed data endpoint (for development)
@api_router.post("/seed-data")
async def seed_data():
    # Check if data already exists
    vendor_count = await db.vendors.count_documents({})
    firm_count = await db.firms.count_documents({})
    
    if vendor_count > 0 or firm_count > 0:
        return {"message": "Data already seeded", "vendors": vendor_count, "firms": firm_count}
    
    # Seed Vendors
    vendors_data = [
        {
            "email": f"vendor{i}@example.com",
            "password": "password123",
            "vendor_name": f"Vendor Company {i}",
            "phone": f"+9198765432{i}",
            "gst_no": f"29ABCDE1234F{i}Z5",
            "revenue": 1000000 + (i * 500000),
            "employee_count": 10 + (i * 5),
            "categories": [["civil"], ["mechanical"], ["electrical"], ["transport"], ["civil", "mechanical"]][i % 5],
            "service_locations": [f"Maharashtra - Mumbai", f"Karnataka - Bangalore"],
            "short_bio": f"Leading contractor in {['civil', 'mechanical', 'electrical', 'transport'][i % 4]} sector with {10 + (i * 5)} years of experience."
        }
        for i in range(1, 9)
    ]
    
    for vd in vendors_data:
        hashed_pw = hash_password(vd["password"])
        user_doc = {
            "email": vd["email"],
            "password_hash": hashed_pw,
            "role": UserRole.VENDOR,
            "created_at": datetime.utcnow()
        }
        user_result = await db.users.insert_one(user_doc)
        
        vendor_doc = {
            "user_id": str(user_result.inserted_id),
            "vendor_name": vd["vendor_name"],
            "phone": vd["phone"],
            "gst_no": vd["gst_no"],
            "revenue": vd["revenue"],
            "employee_count": vd["employee_count"],
            "categories": vd["categories"],
            "service_locations": vd["service_locations"],
            "short_bio": vd["short_bio"],
            "avatar_base64": None,
            "created_at": datetime.utcnow()
        }
        await db.vendors.insert_one(vendor_doc)
    
    # Seed Firms
    firms_data = [
        {
            "name": "Metro Rail Corporation",
            "category": "transport",
            "office_location": "Maharashtra - Mumbai",
            "description": "Major infrastructure company handling metro rail projects across India."
        },
        {
            "name": "National Highways Authority",
            "category": "civil",
            "office_location": "Delhi - New Delhi",
            "description": "Government body responsible for national highway development and maintenance."
        },
        {
            "name": "Power Grid Corporation",
            "category": "electrical",
            "office_location": "Haryana - Gurugram",
            "description": "India's largest electric power transmission utility."
        },
        {
            "name": "Heavy Industries Ltd",
            "category": "mechanical",
            "office_location": "Gujarat - Ahmedabad",
            "description": "Leading manufacturer of heavy machinery and industrial equipment."
        },
        {
            "name": "Smart City Development",
            "category": "civil",
            "office_location": "Karnataka - Bangalore",
            "description": "Urban development company focusing on smart city initiatives."
        },
        {
            "name": "Railway Electrification",
            "category": "electrical",
            "office_location": "West Bengal - Kolkata",
            "description": "Specializes in railway electrification and signaling systems."
        },
        {
            "name": "Airport Authority",
            "category": "transport",
            "office_location": "Maharashtra - Mumbai",
            "description": "Manages and develops airports across major cities."
        },
        {
            "name": "Industrial Equipment Co",
            "category": "mechanical",
            "office_location": "Tamil Nadu - Chennai",
            "description": "Supplies and maintains industrial machinery for manufacturing plants."
        }
    ]
    
    for fd in firms_data:
        firm_doc = {
            "name": fd["name"],
            "category": fd["category"],
            "office_location": fd["office_location"],
            "description": fd["description"],
            "logo_base64": None
        }
        await db.firms.insert_one(firm_doc)
    
    return {
        "message": "Seed data created successfully",
        "vendors": len(vendors_data),
        "firms": len(firms_data)
    }


@api_router.get("/")
async def root():
    return {
        "message": "Contractor Hub API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/*",
            "vendors": "/api/vendors",
            "firms": "/api/firms"
        }
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Contractor Hub API...")
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.vendors.create_index("user_id", unique=True)
    await db.firm_followers.create_index([("firm_id", 1), ("vendor_id", 1)], unique=True)
    logger.info("Database indexes created")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
