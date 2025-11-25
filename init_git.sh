#!/bin/bash
# Git repository initialization script for IMSLP Downloader

echo "🚀 Initializing IMSLP Downloader Git Repository..."
echo

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Add all files
echo "📋 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: IMSLP Downloader v1.0.0

✨ Features:
- HTML report generation with clickable download links
- Support for multiple versions/editions per composition
- Configuration-based work management
- Enhanced IMSLP API wrapper
- Comprehensive documentation and examples
- Respectful rate limiting and anti-bot awareness

🎵 Ready for classical music score collection and research!"

echo
echo "✅ Git repository initialized successfully!"
echo
echo "📋 Next steps to publish on GitHub:"
echo "1. Create a new repository on GitHub.com"
echo "2. Copy the repository URL (HTTPS or SSH)"
echo "3. Run these commands:"
echo
echo "   git remote add origin <your-github-repo-url>"
echo "   git branch -M main"
echo "   git push -u origin main" 
echo
echo "🎯 Example:"
echo "   git remote add origin https://github.com/yourusername/imslp-downloader.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo
echo "💡 Pro tip: After pushing, add topics/tags on GitHub:"
echo "   classical-music, imslp, sheet-music, music-scores, python, html-reports"