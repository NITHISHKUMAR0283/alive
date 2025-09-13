# ARGO RAG Web System - Deployment Guide

Your RAG system will be accessible 24/7 on the web for **FREE** for 10+ days!

## Project Structure
```
your-repo/
├── working_enhanced_rag.py           ← Your existing RAG system
├── working_enhanced_chroma_db/       ← Your existing ChromaDB
├── parquet_data/                     ← Your data files
├── interactive_test.py               ← Your existing CLI
├── web/
│   ├── backend/
│   │   ├── main.py                   ← Web interface (uses your RAG)
│   │   └── requirements.txt          ← Dependencies
│   └── .env.example                  ← Environment template
├── Dockerfile                        ← Container config
├── railway.json                      ← Deployment config
└── DEPLOYMENT.md                     ← This guide
```

## 🔧 Quick Setup (5 Minutes)

### 1. Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Add ARGO RAG web interface"

# Push to GitHub
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Deploy to Railway (FREE)

1. **Go to**: https://railway.app
2. **Login** with GitHub
3. **Click**: "New Project" → "Deploy from GitHub repo"
4. **Select**: Your repository
5. **Railway automatically**:
   - Detects Dockerfile
   - Builds container
   - Deploys your app
   - Gives you a public URL

### 3. Set Environment Variables (In Railway Dashboard)

```
GROQ_API_KEY = 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
HF_TOKEN = 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
PORT = 8000
```

## 🌐 Access Your Web App

After deployment (5-10 minutes):

1. **Railway gives you URL**: `https://your-app-name.railway.app`
2. **Open URL in browser**
3. **Wait 2-3 minutes** for RAG system to load
4. **Start querying**! Same as your CLI but on web

## 🔄 Auto-Sync with GitHub

Every time you update ChromaDB:

```bash
# Update your ChromaDB locally
python interactive_test.py

# Push changes to GitHub
git add working_enhanced_chroma_db/
git commit -m "Updated ChromaDB data"
git push

# Railway automatically redeploys (2-3 minutes)
# Website uses new ChromaDB data
```

## 📊 System Status

Your web app has:
- ✅ **Always-on RAG**: Loads once, stays in memory
- ✅ **Same performance**: 2-3 seconds per query (like CLI)
- ✅ **Concurrent users**: Multiple people can use simultaneously
- ✅ **Auto-updates**: GitHub push → Railway redeploy
- ✅ **Free hosting**: 500 hours/month (16+ hours/day)

## 🐳 Local Testing (Optional)

Test locally before deploying:

```bash
# Build Docker image
docker build -t argo-rag-web .

# Run container
docker run -p 8000:8000 argo-rag-web

# Open: http://localhost:8000
```

## 🔍 Usage Examples

Once deployed, users can query like your CLI:

**Web Interface Queries:**
- "show me temperature data for each profile"
- "average temperature across all floats"
- "salinity distribution by depth"
- "temperature statistics"

**Same Results as CLI!** ✅

## 📈 Monitoring

Check your app status:
- **Health**: `https://your-app.railway.app/api/status`
- **Railway Dashboard**: View logs, metrics, uptime
- **Usage**: Monitor in Railway dashboard

## 🆓 FREE Tier Details

**Railway Free Tier:**
- ✅ **500 hours/month** (enough for 16+ hours/day)
- ✅ **Automatic HTTPS**
- ✅ **Custom domains** (optional)
- ✅ **GitHub integration**
- ✅ **Persistent storage**

**Cost after 10+ days:** Free tier resets monthly!

## 🔧 Advanced Configuration

### Custom Domain (Optional)
1. Buy domain from Namecheap (~$1/year for .tk domains)
2. Add domain in Railway dashboard
3. Update DNS settings
4. Automatic SSL certificate

### Scaling (If needed)
```bash
# Railway automatically scales, but you can configure:
# - Memory limits
# - CPU allocation
# - Multiple replicas
```

## ❓ Troubleshooting

**RAG System Not Loading?**
- Check Railway logs for errors
- Verify API keys in environment variables
- Ensure all files are in GitHub repo

**Slow Queries?**
- Normal on first query (RAG warmup)
- Subsequent queries should be 2-3 seconds

**Need Help?**
- Check Railway logs: Dashboard → Your App → Logs
- Monitor system: `/api/status` endpoint
- GitHub Issues: Open issue with error details

## 🎯 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway connected to GitHub repo
- [ ] Environment variables set
- [ ] App deployed and accessible
- [ ] RAG system loads successfully
- [ ] Queries work same as CLI
- [ ] Auto-deployment on GitHub push works

**Your RAG system is now live on the web! 🌊🚀**