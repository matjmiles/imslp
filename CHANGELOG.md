# Changelog

All notable changes to the IMSLP Downloader project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-25

### Added
- Initial release of IMSLP Downloader
- Core functionality for generating HTML reports with clickable download links
- Support for extracting PDF links from IMSLP work pages
- Professional HTML report generation with responsive design
- Configuration-based work management via JSON files
- Enhanced IMSLP API wrapper for metadata access
- Multiple download strategies with anti-bot protection awareness
- Comprehensive documentation and usage guides
- Examples and sample configurations
- Respectful rate limiting and delay management

### Features
- **HTML Report Generation**: Creates professional, clickable reports
- **Multiple Versions**: Extracts up to 3 different editions per work
- **Batch Processing**: Handles multiple compositions efficiently  
- **Configurable**: JSON-based configuration for easy customization
- **Scalable**: Designed for large music library management
- **Educational Focus**: Respects IMSLP's terms and infrastructure

### Components
- `url_report_generator.py` - Main HTML report generator
- `enhanced_imslp_api.py` - Core IMSLP API wrapper
- `practical_downloader.py` - Advanced batch downloader
- `works_config.json` - Configuration file for compositions
- Comprehensive documentation in `docs/` directory
- Example configurations and outputs

### Documentation
- Complete README with quick start guide
- Detailed usage instructions in `docs/USAGE.md`
- Full API documentation in `docs/API.md`
- Example configurations and sample outputs
- License and legal compliance information

### Technical Details
- Python 3.7+ compatibility
- Dependencies: requests, beautifulsoup4, lxml
- Cross-platform support (Windows, macOS, Linux)
- Respectful web scraping with automatic delays
- Error handling and graceful degradation
- Professional code structure and documentation

## [Unreleased]

### Planned Features
- GUI interface for non-technical users
- Browser automation with CAPTCHA handling
- Integration with music notation software
- Advanced search and filtering capabilities
- Playlist and collection management features
- Export formats (CSV, JSON, XML)
- Performance optimizations
- Enhanced error reporting and diagnostics

---

## Release Notes

### Version 1.0.0 Release Notes

This initial release provides a complete solution for generating HTML reports with clickable download links from IMSLP. The focus is on practical utility for musicians, researchers, and classical music enthusiasts who need efficient access to multiple versions of classical scores.

**Key Benefits:**
- Saves time by eliminating manual searches on IMSLP
- Provides multiple versions/editions per composition
- Creates bookmarkable HTML reports for future reference
- Respects IMSLP's infrastructure with appropriate delays
- Easily scalable for large music collections

**Use Cases:**
- Building personal classical music libraries
- Academic research requiring multiple score editions  
- Performance preparation with easy access to scores
- Educational projects needing public domain sheet music
- Comparative analysis of different musical editions

The project emphasizes ethical usage and compliance with IMSLP's terms of service while providing maximum utility for legitimate educational and research purposes.