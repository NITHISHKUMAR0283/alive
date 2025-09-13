#!/bin/bash
# Quick deployment script for ARGO RAG Web System

echo "🚀 ARGO RAG Web System - Quick Deploy Script"
echo "=============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: ARGO RAG web interface"
else
    echo "✅ Git repository found"
fi

# Add and commit current changes
echo "📦 Committing current changes..."
git add .
git commit -m "Deploy ARGO RAG web interface - $(date)"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "❗ Please add your GitHub repository remote:"
    echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    echo "   git push -u origin main"
    echo ""
    echo "Then go to: https://railway.app"
    echo "1. Login with GitHub"
    echo "2. Deploy from GitHub repo"
    echo "3. Select your repository"
    echo "4. Set environment variables:"
    echo "   GROQ_API_KEY=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"
    echo "   HF_TOKEN=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"
    exit 1
fi

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🌐 Next Steps:"
echo "1. Go to: https://railway.app"
echo "2. Login with GitHub"
echo "3. Deploy from GitHub repo"
echo "4. Select your repository"
echo "5. Set environment variables:"
echo "   GROQ_API_KEY=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"
echo "   HF_TOKEN=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"
echo ""
echo "🚀 Your RAG system will be live in 5-10 minutes!"
echo "📖 Check DEPLOYMENT.md for detailed instructions"