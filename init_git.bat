@echo off
REM Git repository initialization script for IMSLP Downloader

echo 🚀 Initializing IMSLP Downloader Git Repository...
echo.

REM Initialize git repository
echo 📁 Initializing git repository...
git init

REM Add all files
echo 📋 Adding files to git...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: IMSLP Downloader v1.0.0" -m "" -m "✨ Features:" -m "- HTML report generation with clickable download links" -m "- Support for multiple versions/editions per composition" -m "- Configuration-based work management" -m "- Enhanced IMSLP API wrapper" -m "- Comprehensive documentation and examples" -m "- Respectful rate limiting and anti-bot awareness" -m "" -m "🎵 Ready for classical music score collection and research!"

echo.
echo ✅ Git repository initialized successfully!
echo.
echo 📋 Next steps to publish on GitHub:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL (HTTPS or SSH)
echo 3. Run these commands:
echo.
echo    git remote add origin ^<your-github-repo-url^>
echo    git branch -M main
echo    git push -u origin main
echo.
echo 🎯 Example:
echo    git remote add origin https://github.com/yourusername/imslp-downloader.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 💡 Pro tip: After pushing, add topics/tags on GitHub:
echo    classical-music, imslp, sheet-music, music-scores, python, html-reports
echo.
pause