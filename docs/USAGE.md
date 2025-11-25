# Usage Guide

## Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/imslp-downloader.git
cd imslp-downloader

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

#### Generate HTML Report for Default Works

```bash
python url_report_generator.py
```

This will:
- Process the works defined in `works_config.json`
- Generate `imslp_download_links.html`
- Extract up to 3 download links per composition

#### Open the HTML Report

Double-click the generated HTML file or open it in any web browser to access clickable download links.

## Configuration

### Adding New Compositions

Edit `works_config.json`:

```json
{
  "works_to_process": [
    {
      "composer": "Composer, Name",
      "title": "Work Title",
      "url": "https://imslp.org/wiki/Work_Title_(Composer,_Name)"
    }
  ]
}
```

### Finding IMSLP URLs

1. Go to [IMSLP.org](https://imslp.org)
2. Search for your desired composition
3. Copy the URL from the work's main page
4. The URL format is: `https://imslp.org/wiki/Work_Title_(Composer_Name)`

**Example**: 
- Work: "Moonlight Sonata by Beethoven"
- URL: `https://imslp.org/wiki/Piano_Sonata_No.14,_Op.27_No.2_(Beethoven,_Ludwig_van)`

### Configuration Options

```json
{
  "settings": {
    "links_per_work": 3,              // Max versions per work
    "output_filename": "my_report.html", // Output file name
    "delay_between_requests": {        // Respectful delays
      "min_seconds": 3,
      "max_seconds": 6
    }
  }
}
```

## Advanced Usage

### Using the API Wrapper

```python
from enhanced_imslp_api import IMSLPClient

client = IMSLPClient()

# Search for composers
composers = client.get_composers(start=0, amount=10)
print(f"Found {len(composers)} composers")

# Search for works
works = client.get_works(start=0, amount=10) 
print(f"Found {len(works)} works")

# Get PDF links from a specific work
url = "https://imslp.org/wiki/Work_Name_(Composer)"
pdf_links = client.get_pdf_links_from_work(url)
print(f"Found {len(pdf_links)} PDF files")
```

### Batch Processing with Different Strategies

```python
from practical_downloader import IMSLPBatchDownloader

downloader = IMSLPBatchDownloader("my_config.json")

# Process specific works
results = downloader.process_specific_works()

# Search and download by composer
bach_results = downloader.search_and_download_by_composer("Bach", limit=5)

# Generate report
report = downloader.generate_report(results)
print(report)
```

## Tips and Best Practices

### 1. Respectful Usage

- The tool includes automatic delays between requests
- Don't modify delays to be faster than 2-3 seconds
- Avoid running multiple instances simultaneously

### 2. Finding the Right URLs

- Always use the main work page URL, not individual file URLs
- Check that URLs work by visiting them in your browser first
- Some works have multiple pages (e.g., multi-movement works)

### 3. Handling Large Collections

- Process works in batches of 10-20 at a time
- Use the configuration file to manage different collections
- Save successful configurations for future use

### 4. Troubleshooting Downloads

If direct downloads don't work:
1. Click the "View on IMSLP" link in the HTML report
2. Download manually from the IMSLP page
3. Some files may require solving a CAPTCHA

## Common Use Cases

### Building a Personal Library

```json
{
  "works_to_process": [
    // Favorite piano pieces
    {"composer": "Chopin, Frédéric", "title": "...", "url": "..."},
    {"composer": "Debussy, Claude", "title": "...", "url": "..."},
    // String quartets
    {"composer": "Mozart, Wolfgang Amadeus", "title": "...", "url": "..."},
    {"composer": "Beethoven, Ludwig van", "title": "...", "url": "..."}
  ]
}
```

### Academic Research

```json
{
  "settings": {
    "links_per_work": 5,  // More versions for comparison
    "output_filename": "research_sources.html"
  },
  "works_to_process": [
    // All works by a specific composer
    // Or works from a specific time period
  ]
}
```

### Performance Preparation

```json
{
  "works_to_process": [
    // Upcoming concert program
    {"composer": "...", "title": "Concert Piece 1", "url": "..."},
    {"composer": "...", "title": "Concert Piece 2", "url": "..."}
  ]
}
```

## File Organization

The tool organizes downloads as:
```
downloads/
├── Composer_Name_-_Work_Title/
│   ├── 01_Version_Name.pdf
│   ├── 02_Another_Version.pdf
│   └── 03_Third_Version.pdf
└── Another_Composer_-_Work/
    └── ...
```

## Error Handling

### Common Issues

1. **No PDF links found**
   - The work page may not have direct PDF downloads
   - Try the IMSLP page link for manual inspection

2. **Download failures**
   - IMSLP's anti-bot protection is very sophisticated
   - Use the HTML report for manual downloading

3. **Invalid URLs**
   - Check URL format and spelling
   - Ensure the work exists on IMSLP

4. **Rate limiting**
   - Increase delays in configuration
   - Reduce batch sizes

### Getting Help

- Check the error messages in the console
- Verify your configuration file syntax
- Test with a single work first
- Open an issue on GitHub if problems persist