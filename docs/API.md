# API Documentation

## Overview

The IMSLP Downloader provides a clean Python API for interacting with IMSLP (International Music Score Library Project) to extract metadata and download links for classical music scores.

## Core Classes

### IMSLPClient

The main client for interacting with IMSLP's API and web pages.

```python
from enhanced_imslp_api import IMSLPClient

client = IMSLPClient()
```

#### Methods

##### `get_composers(start: int = 0, amount: int = 10) -> List[Dict]`

Retrieve a list of composers from IMSLP's API.

**Parameters:**
- `start` (int): Starting index for pagination
- `amount` (int): Number of composers to retrieve

**Returns:**
- List of dictionaries with keys: `id`, `name`, `link`

**Example:**
```python
composers = client.get_composers(start=0, amount=5)
for composer in composers:
    print(f"{composer['name']}: {composer['link']}")
```

##### `get_works(start: int = 0, amount: int = 10) -> List[Dict]`

Retrieve a list of musical works from IMSLP's API.

**Parameters:**
- `start` (int): Starting index for pagination  
- `amount` (int): Number of works to retrieve

**Returns:**
- List of dictionaries with keys: `id`, `composer`, `title`, `links`

**Example:**
```python
works = client.get_works(start=0, amount=10)
for work in works:
    print(f"'{work['title']}' by {work['composer']}")
    print(f"URL: {work['links']['work']}")
```

##### `search_composer_works(composer_name: str) -> List[Dict]`

Search for works by a specific composer.

**Parameters:**
- `composer_name` (str): Name of the composer to search for

**Returns:**
- List of work dictionaries matching the composer

**Example:**
```python
bach_works = client.search_composer_works("Bach")
print(f"Found {len(bach_works)} works by Bach")
```

##### `get_pdf_links_from_work(work_url: str) -> List[Dict]`

Extract PDF download links from a specific IMSLP work page.

**Parameters:**
- `work_url` (str): Full URL to the IMSLP work page

**Returns:**
- List of dictionaries with keys: `title`, `download_url`

**Example:**
```python
url = "https://imslp.org/wiki/Piano_Sonata_No.8,_Op.13_(Beethoven,_Ludwig_van)"
pdf_links = client.get_pdf_links_from_work(url)

for pdf in pdf_links:
    print(f"Title: {pdf['title']}")
    print(f"Download: {pdf['download_url']}")
```

##### `download_with_browser_simulation(url: str, filename: str, work_title: str = "") -> bool`

Attempt to download a PDF file using multiple anti-bot evasion strategies.

**Parameters:**
- `url` (str): PDF download URL
- `filename` (str): Local filename to save as
- `work_title` (str, optional): Work title for logging

**Returns:**
- `True` if download successful, `False` otherwise

**Example:**
```python
success = client.download_with_browser_simulation(
    url="https://imslp.org/images/...",
    filename="beethoven_sonata.pdf",
    work_title="Piano Sonata No.8"
)

if success:
    print("Download completed!")
else:
    print("Download failed - try manual download")
```

### IMSLPReportGenerator

Generates HTML reports with clickable download links.

```python
from url_report_generator import IMSLPReportGenerator

generator = IMSLPReportGenerator()
```

#### Methods

##### `get_pdf_links_from_work(work_url: str, limit: int = 3) -> List[Dict]`

Extract PDF links with enhanced metadata and descriptions.

**Parameters:**
- `work_url` (str): IMSLP work page URL
- `limit` (int): Maximum number of links to return

**Returns:**
- List of dictionaries with keys: `title`, `download_url`, `description`, `file_size`

##### `generate_html_report(works: List[Dict], output_file: str) -> str`

Generate a professional HTML report with clickable download links.

**Parameters:**
- `works` (List[Dict]): List of work dictionaries with `composer`, `title`, `url`
- `output_file` (str): Output HTML filename

**Returns:**
- Absolute path to the generated HTML file

**Example:**
```python
works = [
    {
        "composer": "Bach, Johann Sebastian",
        "title": "Brandenburg Concerto No.1",
        "url": "https://imslp.org/wiki/Brandenburg_Concerto_No.1,_BWV_1046_(Bach,_Johann_Sebastian)"
    }
]

html_file = generator.generate_html_report(works, "my_report.html")
print(f"Report generated: {html_file}")
```

### IMSLPBatchDownloader

Advanced batch processing with configuration support.

```python
from practical_downloader import IMSLPBatchDownloader

downloader = IMSLPBatchDownloader("config.json")
```

#### Methods

##### `process_specific_works() -> Dict`

Process works defined in the configuration file.

**Returns:**
- Dictionary with processing statistics and results

##### `search_and_download_by_composer(composer_name: str, limit: int = 10) -> Dict`

Search for and process works by a specific composer.

**Parameters:**
- `composer_name` (str): Composer to search for
- `limit` (int): Maximum number of works to process

**Returns:**
- Dictionary with search and processing results

##### `generate_report(results: Dict) -> str`

Generate a text summary report of processing results.

**Parameters:**
- `results` (Dict): Results from processing operations

**Returns:**
- Formatted text report string

## Data Structures

### Work Dictionary

```python
{
    "id": "Work_Title_(Composer_Name)",
    "composer": "Composer, Name",
    "title": "Work Title",
    "links": {
        "work": "https://imslp.org/wiki/...",
        "composer": "https://imslp.org/wiki/Category:..."
    }
}
```

### PDF Link Dictionary

```python
{
    "title": "PDF filename or description",
    "download_url": "https://imslp.org/images/...",
    "description": "Additional metadata about the PDF",
    "file_size": "File size string (e.g., '1.5 MB')"
}
```

### Configuration Schema

```python
{
    "works_to_process": [
        {
            "composer": "Last, First",
            "title": "Work Title",
            "url": "https://imslp.org/wiki/..."
        }
    ],
    "settings": {
        "links_per_work": 3,
        "output_filename": "report.html",
        "delay_between_requests": {
            "min_seconds": 3,
            "max_seconds": 6
        }
    }
}
```

## Error Handling

### Common Exceptions

- **`requests.RequestException`**: Network or HTTP errors
- **`json.JSONDecodeError`**: Invalid JSON configuration
- **`FileNotFoundError`**: Missing configuration files
- **`BeautifulSoup` parsing errors**: Invalid HTML structure

### Best Practices

1. **Always handle network errors:**
```python
try:
    works = client.get_works()
except requests.RequestException as e:
    print(f"Network error: {e}")
```

2. **Check for empty results:**
```python
pdf_links = client.get_pdf_links_from_work(url)
if not pdf_links:
    print("No PDF links found")
```

3. **Validate configurations:**
```python
try:
    with open("config.json") as f:
        config = json.load(f)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

## Rate Limiting and Ethics

### Built-in Rate Limiting

All methods include automatic delays:
- **Between requests**: 2-4 seconds  
- **Between works**: 3-6 seconds
- **After failures**: Progressive backoff

### Respectful Usage

```python
# Good: Respects rate limits
client = IMSLPClient()
works = client.get_works(amount=10)

# Bad: Don't do this
# for i in range(1000):
#     client.get_works(start=i)  # Too aggressive
```

### IMSLP Terms Compliance

- Only access public domain works
- Respect IMSLP's robots.txt
- Don't overwhelm their servers
- Use for educational/research purposes

## Integration Examples

### Flask Web App

```python
from flask import Flask, render_template
from enhanced_imslp_api import IMSLPClient

app = Flask(__name__)
client = IMSLPClient()

@app.route('/composer/<name>')
def composer_works(name):
    works = client.search_composer_works(name)
    return render_template('works.html', works=works)
```

### Command Line Tool

```python
import argparse
from enhanced_imslp_api import IMSLPClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--composer', help='Search for composer')
    parser.add_argument('--limit', type=int, default=10)
    
    args = parser.parse_args()
    
    client = IMSLPClient()
    works = client.search_composer_works(args.composer)
    
    for work in works[:args.limit]:
        print(f"{work['title']} by {work['composer']}")

if __name__ == '__main__':
    main()
```

### Jupyter Notebook

```python
# Cell 1: Setup
from enhanced_imslp_api import IMSLPClient
import pandas as pd

client = IMSLPClient()

# Cell 2: Data Collection
works = client.search_composer_works("Mozart")
df = pd.DataFrame(works)

# Cell 3: Analysis
print(f"Found {len(df)} Mozart works")
df.head()
```

## Performance Considerations

### Memory Usage

- Large batch operations store results in memory
- Consider processing in chunks for huge datasets
- Use generators for streaming operations

### Network Efficiency  

- Reuse the same `IMSLPClient` instance
- Don't create new sessions for each request
- Monitor rate limiting to avoid blocking

### Storage

- HTML reports can be large with many works
- PDF downloads require substantial disk space
- Consider cleanup strategies for temporary files