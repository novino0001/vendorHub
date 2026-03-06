# Building APK for Contractor Hub - Demo Distribution Guide

## 📱 Creating APK for Demo/Testing

Your Contractor Hub app is now configured for building an APK that you can share with others for testing before Play Store deployment.

### Option 1: EAS Build (Recommended - Cloud Build)

**Prerequisites:**
- Expo account (free) - Sign up at https://expo.dev
- EAS CLI installed (already done ✅)

**Steps:**

1. **Login to your Expo account:**
```bash
cd /app/frontend
eas login
```

2. **Configure your project:**
```bash
eas build:configure
```

3. **Build the APK (Preview/Internal Distribution):**
```bash
# For demo/testing APK
eas build --platform android --profile preview

# This will:
# - Upload your code to Expo servers
# - Build the APK in the cloud
# - Provide a download link when complete (~15-20 minutes)
```

4. **Download and Share:**
- After build completes, EAS will provide a download URL
- Download the APK from the Expo dashboard or the link
- Share this APK file directly with testers
- They can install it on Android devices (Settings > Security > Install from Unknown Sources)

**Build Profiles Available:**
- `preview` - For internal testing/demo (generates APK)
- `production` - For Play Store submission (generates AAB)

---

### Option 2: Local Build with Expo (Alternative)

If you prefer local builds:

1. **Install Android Studio & SDK:**
   - Download from https://developer.android.com/studio
   - Set up ANDROID_HOME environment variable

2. **Build locally:**
```bash
cd /app/frontend
npx expo run:android --variant release
```

This will create an APK in:
```
/app/frontend/android/app/build/outputs/apk/release/app-release.apk
```

---

## 🔧 Configuration Files Created

### 1. `eas.json` - Build Configuration
```json
{
  "build": {
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"  // Creates APK for direct install
      }
    },
    "production": {
      "android": {
        "buildType": "apk"  // Can be changed to "aab" for Play Store
      }
    }
  }
}
```

### 2. `app.json` - Updated Android Config
- **Package Name:** com.contractorhub.app
- **App Name:** Contractor Hub
- **Version:** 1.0.0
- **Permissions:** Camera, Storage (for profile pictures)

---

## 📦 What Gets Built

The APK will include:
- ✅ Complete mobile app (all screens)
- ✅ Authentication system
- ✅ Vendor & Firm listings
- ✅ Profile management
- ✅ Image upload capability
- ✅ API integration (connects to your backend)

**Important:** The APK will connect to:
```
https://contractor-hub-125.preview.emergentagent.com/api
```

If you want the APK to connect to a different backend URL (production server), update the `.env` file before building:
```
EXPO_PUBLIC_BACKEND_URL=https://your-production-api.com
```

---

## 🚀 Quick Start Commands

### Build APK for Demo (Recommended):
```bash
cd /app/frontend
eas login
eas build --platform android --profile preview
```

### Check Build Status:
```bash
eas build:list
```

### Download APK:
- Go to https://expo.dev/accounts/[your-username]/projects/contractor-hub/builds
- Or use the direct link provided in terminal after build

---

## 📱 Installing the APK on Android Devices

**For Testers:**
1. Enable "Install from Unknown Sources" on Android device
2. Download the APK file you shared
3. Tap to install
4. Grant required permissions (Camera, Storage)
5. Launch "Contractor Hub" app

**Test Accounts:**
- Email: test@example.com
- Password: password123

Or create new account via signup.

---

## 🔐 Important Notes

1. **APK vs AAB:**
   - APK: Can be installed directly on devices (for demo/testing)
   - AAB: Required for Google Play Store (production)

2. **Signing:**
   - EAS Build handles signing automatically
   - For Play Store, you'll need to set up proper keystore

3. **Updates:**
   - After building, if you make code changes, build again
   - New APK version needs to be redistributed to testers

4. **Backend URL:**
   - Current APK connects to preview URL
   - For production, update EXPO_PUBLIC_BACKEND_URL before building

---

## 🎯 Next Steps After Demo

1. **Collect Feedback** from testers using the APK
2. **Fix Issues** based on feedback
3. **Build Production APK/AAB** for Play Store:
   ```bash
   eas build --platform android --profile production
   ```
4. **Submit to Google Play Console**

---

## 📊 Build Timeline

- **EAS Cloud Build:** ~15-20 minutes
- **Local Build:** ~10-15 minutes (requires Android Studio)

---

## 🆘 Troubleshooting

**Build Fails:**
- Check package.json dependencies
- Ensure all environment variables are set
- Review build logs in EAS dashboard

**APK Won't Install:**
- Enable "Unknown Sources" in Android settings
- Check device has sufficient storage
- Try uninstalling any previous version first

**App Crashes on Launch:**
- Check backend API is accessible from mobile network
- Review permissions are granted
- Check logs using `adb logcat`

---

## 📞 Support Resources

- EAS Build Docs: https://docs.expo.dev/build/introduction/
- Expo Forums: https://forums.expo.dev/
- Android Testing: https://developer.android.com/studio/debug/dev-options

---

**Your app is ready to build! Run the commands above to create your demo APK. 🚀**
