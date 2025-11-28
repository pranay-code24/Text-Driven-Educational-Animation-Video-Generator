# CORS Error Fix for Appwrite

## Problem
The frontend at `http://localhost:3000` is being blocked by CORS when trying to access Appwrite at `https://cloud.appwrite.io`.

Error message:
```
Access to XMLHttpRequest at 'https://cloud.appwrite.io/v1/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

## Solution: Configure CORS in Appwrite Console

### Step 1: Open Appwrite Console
1. Go to https://cloud.appwrite.io
2. Log in to your account
3. Select your project

### Step 2: Configure Platform Settings
1. In the left sidebar, click **Settings**
2. Click **Platforms** (or **Web**)
3. You should see a list of platforms/web apps

### Step 3: Add Your Frontend Origin
1. Click **Add Platform** (or **Add Web App**)
2. Select **Web App**
3. Enter your frontend URL:
   - **Name**: `Local Development` (or any name)
   - **Hostname**: `localhost:3000` (or `localhost` if port doesn't matter)
   - **Port**: `3000` (optional, some versions don't require this)

4. Click **Create** or **Save**

### Step 4: Verify Configuration
After adding the platform, you should see:
- Platform type: Web
- Hostname: localhost:3000
- Status: Enabled

### Step 5: For Production
When deploying to production, add your production domain:
- **Hostname**: `yourdomain.com` (without http:// or https://)
- Or use wildcard: `*.yourdomain.com` for subdomains

## Alternative: Use Appwrite SDK with Proper Configuration

If you're using the Appwrite SDK, make sure it's configured correctly:

```typescript
import { Client } from 'appwrite';

const client = new Client()
    .setEndpoint('https://cloud.appwrite.io/v1')  // Your Appwrite endpoint
    .setProject('your-project-id');                // Your project ID

// For client-side (browser), don't set API key
// API key should only be used server-side
```

## Important Notes

1. **API Keys vs Client SDK**: 
   - Client-side (browser) should NOT use API keys
   - Use the Appwrite SDK which handles authentication via cookies/sessions
   - API keys are for server-side only

2. **CORS is enforced by Appwrite**:
   - Appwrite checks the `Origin` header of requests
   - Only origins added in the platform settings are allowed
   - This is a security feature

3. **Development vs Production**:
   - Add `localhost:3000` for development
   - Add your production domain for production
   - You can have multiple platforms configured

## Quick Checklist

- [ ] Added `localhost:3000` to Appwrite platform settings
- [ ] Platform is enabled in Appwrite console
- [ ] Frontend is using Appwrite SDK (not direct API calls with API key)
- [ ] Restarted frontend dev server after changes
- [ ] Cleared browser cache if needed

## Testing

After configuring CORS:
1. Restart your frontend dev server
2. Clear browser cache or use incognito mode
3. Try accessing the frontend again
4. Check browser console - CORS errors should be gone

## Still Having Issues?

1. **Check Appwrite Console**: Verify the platform is actually saved and enabled
2. **Check Browser Network Tab**: Look at the request headers - is `Origin: http://localhost:3000` being sent?
3. **Check Appwrite Logs**: In Appwrite console, check if requests are being received
4. **Verify Project ID**: Make sure you're using the correct project ID in your frontend code

## For Production Deployment

When deploying:
1. Add your production domain to Appwrite platforms
2. Update environment variables:
   ```env
   NEXT_PUBLIC_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
   NEXT_PUBLIC_APPWRITE_PROJECT_ID=your-project-id
   ```
3. Remove `localhost:3000` from production builds (or keep it for testing)

