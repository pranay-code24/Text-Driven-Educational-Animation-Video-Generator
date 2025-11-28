# Quick CORS Fix - Step by Step

## The Problem
Your frontend at `http://localhost:3000` is being blocked by CORS when trying to access Appwrite.

## The Solution (5 minutes)

### Step 1: Open Appwrite Console
1. Go to **https://cloud.appwrite.io**
2. Log in
3. Select your project

### Step 2: Add Your Frontend as a Platform
1. Click **Settings** in the left sidebar
2. Click **Platforms** (or look for "Web" or "Web Apps")
3. Click **Add Platform** button
4. Select **Web App**

### Step 3: Enter Your Frontend URL
- **Name**: `Local Development` (or any name you like)
- **Hostname**: `localhost` (just "localhost", no http:// or port)
- **Port**: `3000` (if the form asks for it)

### Step 4: Save
Click **Create** or **Save**

### Step 5: Test
1. Go back to your frontend
2. Refresh the page
3. The CORS error should be gone!

## Visual Guide

```
Appwrite Console
├── Settings
    ├── Platforms
        ├── [Add Platform Button]
            └── Web App
                ├── Name: Local Development
                ├── Hostname: localhost
                └── Port: 3000
```

## Important Notes

- ✅ You can add multiple platforms (localhost for dev, yourdomain.com for production)
- ✅ Changes take effect immediately (no restart needed)
- ✅ Make sure the platform shows as "Enabled" after adding

## Still Not Working?

1. **Double-check the hostname**: Should be just `localhost` (not `localhost:3000` or `http://localhost`)
2. **Check if platform is enabled**: It should show a green checkmark or "Enabled" status
3. **Clear browser cache**: Sometimes browsers cache CORS responses
4. **Try incognito mode**: To rule out browser extensions interfering

## For Production

When you deploy, add your production domain:
- **Hostname**: `yourdomain.com` (without www, http, or https)
- Or: `*.yourdomain.com` for all subdomains

