# IMSLP Downloader & URL Report Generator

A Python-based tool for generating HTML reports with clickable download links from IMSLP (International Music Score Library Project). This tool helps musicians and researchers quickly access multiple versions of classical music scores without manually searching through IMSLP's website.

## 🎯 Features

- **Automated URL Extraction**: Scrapes IMSLP pages to find PDF download links
- **Multiple Versions**: Provides up to 3 different editions/versions per composition
- **Professional HTML Reports**: Generates clean, clickable reports for easy downloading
- **Configurable**: Easy-to-modify JSON configuration for adding new works
- **Scalable**: Designed for batch processing of large music libraries
- **Anti-Bot Aware**: Respects IMSLP's rate limits and includes appropriate delays

## 📁 Project Structure

```
imslp-downloader/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── works_config.json            # Configuration file for compositions
├── url_report_generator.py      # Main script for generating HTML reports
├── enhanced_imslp_api.py        # Core IMSLP API wrapper
├── practical_downloader.py      # Advanced batch downloader
├── init_git.bat/.sh             # Repository initialization scripts
├── examples/
│   └── sample_config.json       # Example configuration
└── docs/
    ├── USAGE.md                 # Detailed usage instructions
    └── API.md                   # API documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection
- Web browser for viewing HTML reports

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/imslp-downloader.git
cd imslp-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Configure your compositions** in `works_config.json`:
```json
{
  "works_to_process": [
    {
      "composer": "Bach, Johann Sebastian",
      "title": "Prelude and Fugue in F major, BWV 856",
      "url": "https://imslp.org/wiki/Prelude_and_Fugue_in_F_major,_BWV_856_(Bach,_Johann_Sebastian)"
    }
  ]
}
```

2. **Generate HTML report**:
```bash
python url_report_generator.py
```

3. **Open the generated HTML file** in your browser and click to download!

## 📋 Example Output

The tool generates professional HTML reports with:
- ✅ Clickable download links for each composition
- ✅ Multiple versions/editions per work (up to 3)
- ✅ File size information
- ✅ Direct links to IMSLP pages
- ✅ Mobile-responsive design

## ⚙️ Configuration

### Adding New Compositions

Edit `works_config.json` to add new works:

```json
{
  "works_to_process": [
    {
      "composer": "Composer Name (Last, First)",
      "title": "Work Title with Opus Number",
      "url": "https://imslp.org/wiki/Work_Title_(Composer_Name)"
    }
  ],
  "settings": {
    "links_per_work": 3,
    "output_filename": "imslp_download_links.html"
  }
}
```

### Finding IMSLP URLs

IMSLP URLs follow this pattern:
- Base: `https://imslp.org/wiki/`
- Format: `Work_Title_(Composer_Name)`
- Spaces become underscores
- Special characters may need encoding

## 🔧 Advanced Usage

### Using the API Wrapper

```python
from enhanced_imslp_api import IMSLPClient

client = IMSLPClient()

# Search for composers
composers = client.get_composers(start=0, amount=10)

# Search for works
works = client.get_works(start=0, amount=10)

# Get PDF links from a work page
pdf_links = client.get_pdf_links_from_work(work_url)
```

### Batch Processing

Use `practical_downloader.py` for automated batch processing with anti-bot protection strategies.

## 🤖 Anti-Bot Considerations

This tool respects IMSLP's infrastructure by:
- Adding delays between requests (3-6 seconds)
- Using realistic browser headers
- Limiting concurrent requests
- Providing manual download options when automated methods fail

**Note**: IMSLP has robust anti-bot protection. This tool focuses on URL extraction and manual downloading rather than fully automated downloads.

## 📊 Supported Formats

- **Input**: IMSLP wiki URLs
- **Output**: HTML reports with clickable links
- **Files**: PDF scores and sheet music
- **Metadata**: File sizes, editions, arrangements

## 🎵 Example Composers & Works

The tool has been tested with works by:
- Johann Sebastian Bach
- Ludwig van Beethoven  
- Johannes Brahms
- Robert Schumann
- Wolfgang Amadeus Mozart
- And many others...

## 🐛 Troubleshooting

### Common Issues

1. **No PDF links found**: The work may not have publicly available scores
2. **Download blocked**: Use the "View on IMSLP" link for manual download
3. **Rate limiting**: Increase delays in configuration
4. **Invalid URLs**: Check IMSLP URL format and spelling

### Getting Help

- Check the [Usage Guide](docs/USAGE.md)
- Review [API Documentation](docs/API.md)
- Open an issue on GitHub

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This tool is for educational and research purposes. Users must comply with:
- IMSLP's Terms of Service
- Copyright laws in their jurisdiction
- Respectful usage of IMSLP's resources

Only download public domain scores and respect composer/publisher rights.

## 🙏 Acknowledgments

- [IMSLP](https://imslp.org) - International Music Score Library Project
- [Petrucci Music Library](https://imslp.org) - For providing free access to public domain scores
- All contributors and users of this project

## 📈 Roadmap

- [ ] GUI interface
- [ ] Browser automation for CAPTCHA handling
- [ ] Integration with music notation software
- [ ] Playlist/collection management
- [ ] Advanced search and filtering
- [ ] Export formats (CSV, JSON, etc.)

---

**Made with ♪ for the classical music community**