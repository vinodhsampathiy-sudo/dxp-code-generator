# Railway Deployment Guide for DXP Component Generator Studio

This guide provides step-by-step instructions for deploying the DXP Component Generator Studio to Railway.

## 🚀 Quick Deploy

### Option 1: One-Click Deploy (Coming Soon)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_ID)

### Option 2: Manual Deployment

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: OpenAI API key (required), Anthropic API key (optional)

## 🛠️ Step-by-Step Deployment

### Step 1: Install Railway CLI

```bash
# Using npm
npm install -g @railway/cli

# Using yarn
yarn global add @railway/cli

# Using homebrew (macOS)
brew install railway
```

### Step 2: Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

### Step 3: Create New Project

```bash
# Navigate to your project directory
cd DXP-COMPONENT-GENERATOR

# Create new Railway project
railway new dxp-component-generator

# Link to your local project
railway link
```

### Step 4: Add MongoDB Service

1. Go to your Railway dashboard
2. Click "New Service"
3. Select "Add from template"
4. Choose "MongoDB"
5. Railway will automatically configure the database connection

### Step 5: Set Environment Variables

In your Railway dashboard, go to the Variables tab and add:

**Required Variables:**
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Optional Variables:**
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NODE_ENV=production
```

**Auto-configured by Railway:**
- `PORT` - Automatically set by Railway
- `DATABASE_URL` - Automatically set when MongoDB service is added

### Step 6: Deploy

```bash
# Deploy your application
railway up

# Or deploy with logs
railway up --detach
```

## 🔧 Configuration Files

The project includes several Railway-specific files:

### `railway.json`
Main Railway configuration file that defines build and deployment settings.

### `Dockerfile.railway`
Production-optimized Dockerfile for Railway deployment.

### `.env.railway`
Template for Railway environment variables.

### `Procfile`
Process definition for Railway.

## 🌐 Accessing Your Application

After successful deployment:

1. **Application URL**: `https://your-project-name.railway.app`
2. **Dashboard**: Monitor at `https://railway.app/dashboard`
3. **Logs**: View real-time logs in Railway dashboard

## 🔍 Monitoring and Troubleshooting

### Viewing Logs

```bash
# View application logs
railway logs

# View logs for specific service
railway logs --service web

# Follow logs in real-time
railway logs --follow
```

### Health Check

Your application includes a health endpoint at `/health` that Railway uses for monitoring:

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AEM Component Generator API",
  "version": "1.0.0",
  "mongodb": "connected",
  "timestamp": "2025-01-20T10:00:00Z"
}
```

### Common Issues and Solutions

#### 1. Build Failures

**Problem**: Build fails due to missing dependencies
```bash
# Solution: Check logs and rebuild
railway logs
railway up --detach
```

#### 2. Environment Variables

**Problem**: Application can't access environment variables
```bash
# Solution: Set variables via CLI
railway variables set OPENAI_API_KEY=your_key
railway variables set NODE_ENV=production

# List all variables
railway variables
```

#### 3. Database Connection Issues

**Problem**: Cannot connect to MongoDB
- Ensure MongoDB service is running in Railway dashboard
- Check if DATABASE_URL is set automatically
- Verify MongoDB service logs

#### 4. Port Configuration

**Problem**: Application not accessible
- Railway automatically assigns PORT environment variable
- Ensure your app listens on `process.env.PORT`
- Default fallback should be port 8000

## 🔒 Security Best Practices

### Environment Variables
- Never commit `.env` files to git
- Use Railway's environment variables for secrets
- Rotate API keys regularly

### HTTPS
- Railway provides automatic HTTPS certificates
- All traffic is encrypted by default

### Database Security
- MongoDB connection is automatically secured
- Use Railway's managed MongoDB for production

## 🔄 Continuous Deployment

### Automatic Deployments

1. Connect your GitHub repository to Railway
2. Enable automatic deployments
3. Every push to main branch triggers deployment

### Manual Deployments

```bash
# Deploy current branch
railway up

# Deploy specific commit
railway up --commit abc123

# Deploy with build logs
railway up --verbose
```

## 📊 Scaling and Performance

### Auto-scaling
- Railway automatically scales based on traffic
- No configuration required for basic scaling

### Resource Monitoring
- Monitor CPU and memory usage in dashboard
- Set up alerts for resource thresholds

### Database Scaling
- MongoDB scales automatically with Railway
- Monitor database performance in dashboard

## 💰 Cost Management

### Usage Monitoring
- Track usage in Railway dashboard
- Set up billing alerts
- Monitor resource consumption

### Optimization Tips
- Use production builds to reduce resource usage
- Implement caching strategies
- Monitor and optimize database queries

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] MongoDB service added and connected
- [ ] Health check endpoint responding
- [ ] Application accessible via Railway URL
- [ ] Logs showing successful startup
- [ ] Database connection verified
- [ ] API endpoints responding correctly
- [ ] SSL certificate active
- [ ] Custom domain configured (if needed)

## 🔗 Useful Links

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/reference/cli-api)
- [Railway Templates](https://railway.app/templates)
- [Railway Community](https://help.railway.app/)

## 📞 Support

If you encounter issues:

1. Check Railway documentation
2. Review application logs
3. Verify environment variables
4. Test health endpoint
5. Contact Railway support if needed

## 🚀 Advanced Configuration

### Custom Domain

```bash
# Add custom domain
railway domain add yourdomain.com
```

### Environment-specific Deployments

```bash
# Deploy to specific environment
railway up --environment production
```

### Database Backup

Use Railway's built-in backup features or implement custom backup scripts.

---

For more information about the DXP Component Generator Studio, see the main [README.md](README.md).
