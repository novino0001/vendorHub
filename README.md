# Contractor Hub - Full-Stack Mobile Application

A mobile application for contractors (vendors) to connect with infrastructure firms (BigFirms). Built with Expo (React Native), FastAPI, and MongoDB.

## 🚀 Features

### Vendor Features (Fully Implemented)
- ✅ Complete vendor signup with profile creation
- ✅ JWT-based authentication (email/password)
- ✅ Full vendor profile management (view & edit)
- ✅ Browse and search other vendors by category and location
- ✅ View limited public profiles of other vendors
- ✅ Browse BigFirm listings
- ✅ Follow/Unfollow BigFirms
- ✅ Beautiful Material Design UI with tab navigation
- ✅ Profile picture upload (camera + gallery)
- ✅ Multi-select categories and service locations
- ✅ Real-time data updates

### BigFirm Features
- ✅ Seeded dummy data (8 firms)
- ✅ Follow/Unfollow functionality
- ✅ View firm details
- ✅ Track following status

## 📱 Tech Stack

### Mobile App
- **Framework**: Expo (React Native) 54.0
- **Navigation**: Expo Router with Tab Navigation
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Storage**: AsyncStorage
- **UI Components**: React Native core + Expo Vector Icons
- **Image Handling**: expo-image-picker
- **TypeScript**: Full type safety

### Backend API
- **Framework**: FastAPI 0.110.1
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens (7-day expiry)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **CORS**: Enabled for cross-origin requests

### Database Schema
- **users**: Authentication and role management
- **vendors**: Vendor profile data
- **firms**: BigFirm information
- **firm_followers**: Follow relationships

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB running locally
- Expo CLI

### Backend Setup

1. **Install Python dependencies**:
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Environment variables** (`.env`):
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
JWT_SECRET_KEY="your-secret-key-change-in-production"
```

3. **Start the backend**:
```bash
sudo supervisorctl restart backend
# Or manually:
# uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

4. **Seed sample data**:
```bash
curl -X POST http://localhost:8001/api/seed-data
```

This creates:
- 8 vendor accounts (email: vendor1@example.com - vendor8@example.com, password: password123)
- 8 BigFirm dummy entries

### Frontend Setup

1. **Install dependencies**:
```bash
cd /app/frontend
yarn install
```

2. **Environment variables** (`.env`):
```
EXPO_PUBLIC_BACKEND_URL=https://your-app-url.preview.emergentagent.com
# Or for local development:
# EXPO_PUBLIC_BACKEND_URL=http://localhost:8001
```

3. **Start Expo**:
```bash
sudo supervisorctl restart expo
# Or manually:
# yarn start
```

4. **Access the app**:
- Web: Open the URL shown in terminal
- Mobile: Scan QR code with Expo Go app
- iOS Simulator: Press `i` in terminal
- Android Emulator: Press `a` in terminal

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup/vendor` - Register new vendor
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user profile

### Vendors
- `GET /api/vendors` - List vendors (with pagination & filters)
  - Query params: `category`, `location`, `sort_by`, `page`, `per_page`
- `GET /api/vendors/{id}` - Get vendor public profile (limited fields)
- `GET /api/vendors/me` - Get own full profile
- `PUT /api/vendors/me` - Update own profile

### BigFirms
- `GET /api/firms` - List all firms (paginated)
- `GET /api/firms/{id}` - Get firm details
- `POST /api/firms/{id}/follow` - Follow a firm
- `DELETE /api/firms/{id}/unfollow` - Unfollow a firm
- `GET /api/vendors/me/following` - Get list of followed firms

## 🎨 App Structure

```
/app/frontend/
├── app/                    # Expo Router screens
│   ├── (auth)/            # Authentication screens
│   │   ├── login.tsx      # Login screen
│   │   └── signup.tsx     # Vendor signup form
│   ├── (tabs)/            # Main app tabs
│   │   ├── _layout.tsx    # Tab navigator
│   │   ├── index.tsx      # Home/Dashboard
│   │   ├── vendors.tsx    # Vendors list
│   │   ├── firms.tsx      # BigFirms list
│   │   └── profile.tsx    # User profile
│   ├── _layout.tsx        # Root layout
│   └── index.tsx          # Landing page
├── components/            # Reusable components
├── store/                 # Zustand state management
├── utils/                 # API client & utilities
└── assets/               # Images & static files
```

## 🔐 Security Features

- JWT token authentication
- Password hashing with bcrypt
- GST number validation (Indian format)
- Phone number validation
- Email validation
- Protected API endpoints
- Secure token storage (AsyncStorage)

## 📊 Data Models

### Vendor Profile
- Company name, email, phone
- GST number
- Revenue & employee count
- Categories (civil, mechanical, electrical, transport)
- Service locations (state-district pairs)
- Short bio
- Profile picture (base64)

### BigFirm
- Company name
- Category
- Office location
- Description
- Logo (base64)

## 🧪 Testing

### Test Credentials
- Email: `vendor1@example.com` to `vendor8@example.com`
- Password: `password123`

Or create a new account through the signup flow.

### Manual Testing
1. Sign up as a new vendor
2. Complete profile setup
3. Browse vendors list with filters
4. View vendor profiles
5. Browse BigFirms
6. Follow/unfollow firms
7. Edit your own profile

## 🚀 Deployment

### Backend
The backend runs on port 8001 and is accessible at `/api/*` routes through the proxy.

### Frontend
The Expo app is served on port 3000 and accessible via:
- Web preview
- Expo Go app (scan QR code)
- Native builds (iOS/Android)

## 📝 API Documentation

FastAPI auto-generates OpenAPI documentation:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🎯 MVP Scope

This MVP includes:
- ✅ Complete vendor signup & authentication
- ✅ Full vendor profile management
- ✅ Vendor discovery & search
- ✅ BigFirm listings with dummy data
- ✅ Follow/unfollow functionality
- ✅ Beautiful mobile-first UI
- ✅ Image upload support
- ✅ Pagination & filtering
- ✅ JWT security

## 🔮 Future Enhancements

Potential features for future versions:
- BigFirm signup & authentication
- Project postings by BigFirms
- Vendor bids on projects
- Real-time notifications
- Chat/messaging system
- Portfolio image gallery
- Reviews & ratings
- Advanced search filters
- Analytics dashboard

## 🐛 Known Issues

- None at this time

## 📄 License

This is a demo/MVP application.

## 👥 Support

For issues or questions, please check the API documentation or backend logs.

---

**Built with ❤️ using Expo, FastAPI, and MongoDB**
