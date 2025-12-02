#!/usr/bin/env python3
"""
IMSLP URL Report Generator
Creates an HTML report with clickable download links for manual downloading
Provides multiple versions of each composition for easy access
"""

import requests
import time
import json
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import random
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IMSLPReportGenerator:
    """Generate HTML reports with clickable PDF download links"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_pdf_links_from_work(self, work_url: str, limit: int = 3) -> List[Dict]:
        """
        Extract PDF download links from a work page
        
        Args:
            work_url: URL of the IMSLP work page
            limit: Maximum number of PDF links to return
            
        Returns:
            List of PDF link dictionaries with title, download_url, and description
        """
        pdf_links = []
        
        try:
            logger.info(f"Extracting PDF links from: {work_url}")
            
            # Add delay to be respectful
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(work_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PDF links in spans with class 'we_file_info2'
            pdf_spans = soup.find_all('span', class_='we_file_info2')
            
            for span in pdf_spans:
                link = span.find('a')
                if link and link.get('href'):
                    href = link.get('href')
                    if href.endswith('.pdf') or 'pdf' in href.lower():
                        # Get additional context/description
                        description = self._extract_pdf_description(span)
                        
                        pdf_info = {
                            'title': link.get_text(strip=True),
                            'download_url': urljoin('https://imslp.org', href),
                            'description': description,
                            'file_size': self._extract_file_size(span)
                        }
                        pdf_links.append(pdf_info)
                        
                        # Stop when we have enough links
                        if len(pdf_links) >= limit:
                            break
            
            logger.info(f"Found {len(pdf_links)} PDF links (limited to {limit})")
            
        except Exception as e:
            logger.error(f"Error extracting PDF links from {work_url}: {e}")
        
        return pdf_links
    
    def _extract_pdf_description(self, span) -> str:
        """Extract description/context for a PDF file"""
        description_parts = []
        
        # Look for parent elements that might contain description
        parent = span.parent
        while parent and len(description_parts) < 3:
            # Look for text nodes or specific classes that indicate metadata
            text = parent.get_text(strip=True)
            if text and text not in description_parts and len(text) > 5:
                # Filter out common noise
                if not any(noise in text.lower() for noise in ['click', 'download', 'file', 'pdf']):
                    description_parts.append(text[:100])  # Limit length
            parent = parent.parent
            
            if len(' '.join(description_parts)) > 200:  # Stop if we have enough
                break
        
        return ' | '.join(description_parts[:2]) if description_parts else "PDF Score"
    
    def _extract_file_size(self, span) -> str:
        """Extract file size if available"""
        # Look for file size in nearby text
        parent = span.parent
        if parent:
            text = parent.get_text()
            # Look for patterns like "1.5MB" or "500KB"
            import re
            size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|KB|GB)', text, re.IGNORECASE)
            if size_match:
                return f"{size_match.group(1)} {size_match.group(2).upper()}"
        
        return "Unknown size"
    
    def generate_html_report(self, works: List[Dict], output_file: str = "imslp_download_links.html"):
        """
        Generate an HTML report with clickable download links
        
        Args:
            works: List of work dictionaries with composer, title, and url
            output_file: Output HTML file name
        """
        logger.info(f"Generating HTML report for {len(works)} works...")
        
        html_content = self._generate_html_header()
        
        for i, work in enumerate(works, 1):
            logger.info(f"Processing work {i}/{len(works)}: {work['title']}")
            
            pdf_links = self.get_pdf_links_from_work(work['url'], limit=3)
            
            html_content += self._generate_work_section(work, pdf_links, i)
            
            # Add delay between requests to be respectful
            if i < len(works):
                time.sleep(random.uniform(3, 6))
        
        html_content += self._generate_html_footer()
        
        # Write HTML file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path.absolute()}")
        return str(output_path.absolute())
    
    def _generate_html_header(self) -> str:
        """Generate HTML header with styling"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMSLP Download Links Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        .work-section {{
            margin: 30px 0;
            padding: 25px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .work-title {{
            color: #2c3e50;
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .composer {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 15px;
        }}
        .pdf-links {{
            margin-top: 20px;
        }}
        .pdf-link {{
            display: block;
            margin: 15px 0;
            padding: 15px;
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            text-decoration: none;
            color: #2c3e50;
            transition: all 0.3s ease;
        }}
        .pdf-link:hover {{
            background-color: #3498db;
            color: white;
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
        }}
        .pdf-title {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .pdf-description {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .pdf-size {{
            color: #95a5a6;
            font-size: 0.8em;
        }}
        .no-pdfs {{
            color: #e74c3c;
            font-style: italic;
            padding: 15px;
            background-color: #fdf2f2;
            border: 1px solid #e74c3c;
            border-radius: 5px;
        }}
        .imslp-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background-color: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .imslp-link:hover {{
            background-color: #229954;
        }}
        .stats {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .generated-info {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎼 IMSLP Download Links Report</h1>
        <div class="stats">
            <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
            <strong>Purpose:</strong> Manual download with clickable links | 
            <strong>Note:</strong> Up to 3 versions per composition
        </div>
'''
    
    def _generate_work_section(self, work: Dict, pdf_links: List[Dict], work_number: int) -> str:
        """Generate HTML section for a single work"""
        html = f'''
        <div class="work-section">
            <div class="work-title">{work_number}. {work['title']}</div>
            <div class="composer">by {work['composer']}</div>
            
            <a href="{work['url']}" class="imslp-link" target="_blank">🔗 View on IMSLP</a>
            
            <div class="pdf-links">
'''
        
        if pdf_links:
            html += f"<strong>📥 Download Links ({len(pdf_links)} versions available):</strong><br><br>"
            
            for i, pdf in enumerate(pdf_links, 1):
                html += f'''
                <a href="{pdf['download_url']}" class="pdf-link" target="_blank">
                    <div class="pdf-title">Version {i}: {pdf['title']}</div>
                    <div class="pdf-description">{pdf['description']}</div>
                    <div class="pdf-size">File size: {pdf['file_size']}</div>
                </a>
'''
        else:
            html += '''
                <div class="no-pdfs">
                    ❌ No PDF download links found for this work.<br>
                    You may need to visit the IMSLP page manually to check for available scores.
                </div>
'''
        
        html += '''
            </div>
        </div>
'''
        
        return html
    
    def _generate_html_footer(self) -> str:
        """Generate HTML footer"""
        return '''
        <div class="generated-info">
            <p><strong>How to use this report:</strong></p>
            <p>• Click any "Version X" link to download that PDF directly</p>
            <p>• If a download doesn't work, try the IMSLP page link to download manually</p>
            <p>• Multiple versions may include different editions, arrangements, or quality levels</p>
            <p>• Some links may require solving a CAPTCHA on IMSLP's website</p>
        </div>
    </div>
</body>
</html>'''


def load_works_config(config_file: str = "works_config.json") -> Dict:
    """Load works configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found, using default works")
        return get_default_config()
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file: {e}")
        return get_default_config()

def get_default_config() -> Dict:
    """Return default configuration if config file is missing"""
    return {
        "works_to_process": [
            {
                "composer": "Bach, Johann Sebastian",
                "title": "Prelude and Fugue in F major, BWV 856",
                "url": "https://imslp.org/wiki/Prelude_and_Fugue_in_F_major,_BWV_856_(Bach,_Johann_Sebastian)"
            },
            {
                "composer": "Beethoven, Ludwig van", 
                "title": "Piano Sonata No.8, Op.13 (Pathétique)",
                "url": "https://imslp.org/wiki/Piano_Sonata_No.8,_Op.13_(Beethoven,_Ludwig_van)"
            },
            {
                "composer": "Brahms, Johannes",
                "title": "Variations on a Theme by Haydn, Op.56", 
                "url": "https://imslp.org/wiki/Variations_on_a_Theme_by_Haydn,_Op.56_(Brahms,_Johannes)"
            },
            {
                "composer": "Schumann, Robert",
                "title": "8 Novelletten, Op.21",
                "url": "https://imslp.org/wiki/8_Novelletten,_Op.21_(Schumann,_Robert)"
            }
        ],
        "settings": {
            "links_per_work": 3,
            "output_filename": "imslp_download_links.html"
        }
    }

def main():
    """Generate HTML report for the configured works or CSV file"""
    
    import sys
    
    # Check if CSV file argument is provided
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        print("🔄 CSV file detected - redirecting to CSV processor...")
        print(f"Run: python csv_imslp_processor.py")
        print("Or use the CSV processor directly for better CSV handling.")
        return
    
    # Load configuration
    config = load_works_config()
    works_to_process = config.get("works_to_process", [])
    settings = config.get("settings", {})
    
    output_filename = settings.get("output_filename", "imslp_download_links.html")
    
    print("=== IMSLP URL Report Generator ===")
    print(f"Processing {len(works_to_process)} musical works...")
    print("This will create an HTML file with clickable download links.")
    print()
    
    generator = IMSLPReportGenerator()
    
    try:
        output_file = generator.generate_html_report(works_to_process, output_filename)
        
        print("\n" + "="*60)
        print("✅ HTML REPORT GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"📁 File location: {output_file}")
        print()
        print("📋 What's in the report:")
        print("  • Clickable download links for each composition")
        print("  • Up to 3 different versions/editions per work")
        print("  • Direct links to IMSLP pages for manual access")
        print("  • File size information where available")
        print()
        print("🖱️  How to use:")
        print("  1. Open the HTML file in your web browser")
        print("  2. Click any 'Version X' link to download directly")
        print("  3. If blocked, use the 'View on IMSLP' link for manual download")
        print()
        print("💡 For future use:")
        print(f"  • Edit 'works_config.json' to add more compositions")
        print(f"  • Re-run this script to regenerate the HTML report")
        print(f"  • Each work will show up to 3 different versions/editions")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        logger.error(f"Report generation failed: {e}")


if __name__ == "__main__":
    main()