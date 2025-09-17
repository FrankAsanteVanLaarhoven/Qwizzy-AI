# Render Deployment Guide

## Quick Deploy to Render

### Option 1: One-Click Deploy
1. Click this button: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/FrankAsanteVanLaarhoven/Qwizzy-AI)

### Option 2: Manual Deploy
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `FrankAsanteVanLaarhoven/Qwizzy-AI`
4. Configure:
   - **Name**: `qwizzy-ai-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k gthread -t 120 -b 0.0.0.0:$PORT wsgi:app`
   - **Plan**: Starter (Free)

### Environment Variables
Set these in Render dashboard:
- `CLOUD_DEPLOYMENT=1` (automatically set)
- `PYTHON_VERSION=3.11.0` (automatically set)

### Health Check
- **Health Check Path**: `/health`
- Render will monitor this endpoint to ensure your app is running

### Custom Domain (Optional)
1. In your service settings, go to "Custom Domains"
2. Add your domain and follow DNS instructions
3. Update `vercel.json` with your new domain

### After Deployment
1. Get your Render URL (e.g., `https://qwizzy-ai-backend.onrender.com`)
2. Update `vercel.json` to proxy `/api/*` to your Render URL
3. Redeploy Vercel frontend

## Features Enabled
- ✅ Cloud-safe microphone handling
- ✅ Health check endpoint
- ✅ Optimized Gunicorn configuration
- ✅ Automatic environment detection
- ✅ CORS enabled for frontend integration

## Troubleshooting
- **Build fails**: Check Python version compatibility
- **App crashes**: Check logs in Render dashboard
- **Health check fails**: Ensure `/health` endpoint returns 200
- **CORS issues**: Verify frontend domain is allowed
