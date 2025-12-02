#!/usr/bin/env python3
"""
CSV-Integrated IMSLP Report Generator
Reads a CSV file with composer and work information to generate HTML reports
"""

import csv
import requests
import time
import json
import logging
import re
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from pathlib import Path
import random
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CSVIMSLPProcessor:
    """Process CSV files and generate IMSLP reports"""
    
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
    
    def read_csv_works(self, csv_file: str) -> List[Dict]:
        """
        Read works from CSV file
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of work dictionaries
        """
        works = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect if there's a header
                first_line = f.readline().strip()
                f.seek(0)
                
                csv_reader = csv.reader(f)
                
                # Skip empty first row if present
                if first_line == ',':
                    next(csv_reader)
                
                for row_num, row in enumerate(csv_reader, 1):
                    if len(row) >= 2 and row[0].strip() and row[1].strip():
                        composer = row[0].strip()
                        title = row[1].strip()
                        
                        # Skip if this looks like a header
                        if composer.lower() == 'composer' or title.lower() == 'title':
                            continue
                        
                        work = {
                            'composer': composer,
                            'title': title,
                            'csv_row': row_num,
                            'url': None,  # Will be searched for
                            'search_attempted': False,
                            'pdf_links_found': 0
                        }
                        works.append(work)
                        
            logger.info(f"Successfully read {len(works)} works from {csv_file}")
            
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_file}: {e}")
            return []
        
        return works
    
    def normalize_composer_name(self, composer: str) -> str:
        """Normalize composer name for IMSLP search"""
        # Handle common variations
        composer = composer.strip()
        
        # Common name mappings
        name_mappings = {
            'Bach': 'Bach, Johann Sebastian',
            'Mozart': 'Mozart, Wolfgang Amadeus',
            'Beethoven': 'Beethoven, Ludwig van',
            'Haydn': 'Haydn, Joseph',
            'Schubert': 'Schubert, Franz',
            'Brahms': 'Brahms, Johannes',
            'Schumann': 'Schumann, Robert',
            'Anna Magdalena Bach': 'Bach, Johann Sebastian',  # Often attributed works
            'Fanny Mendelssohn': 'Hensel, Fanny'
        }
        
        if composer in name_mappings:
            return name_mappings[composer]
        
        # If already in "Last, First" format, keep it
        if ',' in composer:
            return composer
        
        # Try to convert "First Last" to "Last, First"
        parts = composer.split()
        if len(parts) >= 2:
            return f"{parts[-1]}, {' '.join(parts[:-1])}"
        
        return composer
    
    def normalize_work_title(self, title: str) -> str:
        """Normalize work title for IMSLP search"""
        title = title.strip()
        
        # Common replacements for IMSLP format
        replacements = {
            'mvt.': '',
            'mvt': '',
            'Mvt.': '',
            'Mvt': '',
            'movement': '',
            'Movement': '',
            'all movements': '',
            'WTC': 'Well-Tempered Clavier',
            'Op.': 'Op.',
            'No.': 'No.',
            'Hob.': 'Hob.',
            'BWV': 'BWV',
            'K.': 'K.',
            'K ': 'K.',
        }
        
        for old, new in replacements.items():
            title = title.replace(old, new)
        
        # Clean up extra spaces
        title = ' '.join(title.split())
        
        return title
    
    def search_imslp_url(self, composer: str, title: str) -> Optional[str]:
        """
        Search for IMSLP URL for a given composer and work
        
        Args:
            composer: Composer name
            title: Work title
            
        Returns:
            IMSLP URL if found, None otherwise
        """
        normalized_composer = self.normalize_composer_name(composer)
        normalized_title = self.normalize_work_title(title)
        
        # Generate possible IMSLP URL formats
        url_attempts = []
        
        # Format 1: Direct construction
        composer_for_url = normalized_composer.replace(', ', '_').replace(' ', '_')
        title_for_url = normalized_title.replace(' ', '_').replace(',', ',_')
        
        possible_url = f"https://imslp.org/wiki/{title_for_url}_({composer_for_url})"
        url_attempts.append(possible_url)
        
        # Format 2: Try with different composer format
        if ',' in normalized_composer:
            last, first = normalized_composer.split(', ', 1)
            alt_composer = f"{first}_{last}"
            alt_url = f"https://imslp.org/wiki/{title_for_url}_({alt_composer})"
            url_attempts.append(alt_url)
        
        # Format 3: Try simplified title
        simple_title = re.sub(r'[^\w\s]', '', normalized_title).replace(' ', '_')
        simple_url = f"https://imslp.org/wiki/{simple_title}_({composer_for_url})"
        url_attempts.append(simple_url)
        
        # Test each URL attempt
        for url in url_attempts:
            try:
                logger.debug(f"Trying URL: {url}")
                
                response = self.session.head(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Found IMSLP page: {composer} - {title}")
                    return url
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.debug(f"URL test failed for {url}: {e}")
                continue
        
        # If direct URL construction fails, try search
        return self.search_imslp_via_search(composer, title)
    
    def search_imslp_via_search(self, composer: str, title: str) -> Optional[str]:
        """
        Search IMSLP using their search functionality
        """
        try:
            search_query = f"{composer} {title}"
            search_url = f"https://imslp.org/wiki/Special:Search"
            
            params = {
                'search': search_query,
                'go': 'Go'
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                # If redirected to a specific page, we found it
                if 'Special:Search' not in response.url:
                    logger.info(f"✅ Found via search: {composer} - {title}")
                    return response.url
                
                # Parse search results
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='mw-search-result-heading')
                
                for result in results[:3]:  # Check first 3 results
                    link = result.find('a')
                    if link and link.get('href'):
                        result_url = urljoin('https://imslp.org', link.get('href'))
                        result_title = link.get_text().strip()
                        
                        # Simple relevance check
                        if (composer.split()[-1].lower() in result_title.lower() and 
                            any(word.lower() in result_title.lower() for word in title.split()[:3])):
                            logger.info(f"✅ Found via search results: {composer} - {title}")
                            return result_url
            
            time.sleep(2)  # Be respectful of search
            
        except Exception as e:
            logger.debug(f"Search failed for {composer} - {title}: {e}")
        
        logger.warning(f"❌ Could not find IMSLP page for: {composer} - {title}")
        return None
    
    def get_pdf_links_from_work(self, work_url: str, limit: int = 3) -> List[Dict]:
        """Extract PDF links from IMSLP work page"""
        pdf_links = []
        
        try:
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(work_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PDF links
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
                        
                        if len(pdf_links) >= limit:
                            break
            
            logger.info(f"Found {len(pdf_links)} PDF links for {work_url}")
            
        except Exception as e:
            logger.error(f"Error extracting PDF links from {work_url}: {e}")
        
        return pdf_links
    
    def _extract_pdf_description(self, span) -> str:
        """Extract description/context for a PDF file"""
        description_parts = []
        
        parent = span.parent
        while parent and len(description_parts) < 3:
            text = parent.get_text(strip=True)
            if text and text not in description_parts and len(text) > 5:
                if not any(noise in text.lower() for noise in ['click', 'download', 'file', 'pdf']):
                    description_parts.append(text[:100])
            parent = parent.parent
            
            if len(' '.join(description_parts)) > 200:
                break
        
        return ' | '.join(description_parts[:2]) if description_parts else "PDF Score"
    
    def _extract_file_size(self, span) -> str:
        """Extract file size if available"""
        parent = span.parent
        if parent:
            text = parent.get_text()
            import re
            size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|KB|GB)', text, re.IGNORECASE)
            if size_match:
                return f"{size_match.group(1)} {size_match.group(2).upper()}"
        
        return "Unknown size"
    
    def process_csv_works(self, csv_file: str, max_works: int = None) -> List[Dict]:
        """
        Process works from CSV file - search for URLs and get PDF links
        
        Args:
            csv_file: Path to CSV file
            max_works: Maximum number of works to process (for testing)
            
        Returns:
            List of processed work dictionaries
        """
        works = self.read_csv_works(csv_file)
        
        if max_works:
            works = works[:max_works]
            logger.info(f"Limited processing to first {max_works} works for testing")
        
        processed_works = []
        
        for i, work in enumerate(works, 1):
            logger.info(f"Processing work {i}/{len(works)}: {work['composer']} - {work['title']}")
            
            # Search for IMSLP URL
            work['url'] = self.search_imslp_url(work['composer'], work['title'])
            work['search_attempted'] = True
            
            if work['url']:
                # Get PDF links
                pdf_links = self.get_pdf_links_from_work(work['url'])
                work['pdf_links'] = pdf_links
                work['pdf_links_found'] = len(pdf_links)
            else:
                work['pdf_links'] = []
                work['pdf_links_found'] = 0
            
            processed_works.append(work)
            
            # Respectful delay between works
            time.sleep(random.uniform(3, 6))
        
        return processed_works
    
    def generate_csv_html_report(self, works: List[Dict], output_file: str = "csv_imslp_report.html") -> str:
        """Generate HTML report from processed CSV works"""
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMSLP CSV Report - Form Anthology</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
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
        .stats {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: center;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .work-section {{
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .work-section.found {{
            border-left: 5px solid #27ae60;
        }}
        .work-section.not-found {{
            border-left: 5px solid #e74c3c;
        }}
        .work-header {{
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: center;
            margin-bottom: 15px;
        }}
        .work-title {{
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
        }}
        .composer {{
            color: #7f8c8d;
            font-size: 1em;
            margin: 5px 0;
        }}
        .csv-info {{
            color: #95a5a6;
            font-size: 0.9em;
        }}
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .status-found {{
            background-color: #d5f4e6;
            color: #27ae60;
        }}
        .status-not-found {{
            background-color: #fdf2f2;
            color: #e74c3c;
        }}
        .pdf-links {{
            margin-top: 15px;
        }}
        .pdf-link {{
            display: block;
            margin: 10px 0;
            padding: 12px;
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
        .imslp-link {{
            display: inline-block;
            margin: 10px 10px 10px 0;
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
        .no-results {{
            color: #e74c3c;
            font-style: italic;
            padding: 15px;
            background-color: #fdf2f2;
            border: 1px solid #e74c3c;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .generated-info {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .search-summary {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎼 IMSLP Form Anthology Report</h1>
        
        <div class="search-summary">
            <strong>📋 CSV Processing Summary:</strong> This report was generated from your CSV file containing musical works. 
            Each work was automatically searched on IMSLP and up to 3 download links were extracted when available.
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <strong>Total Works:</strong><br>{len(works)}
            </div>
            <div class="stat-item">
                <strong>IMSLP Pages Found:</strong><br>{len([w for w in works if w['url']])}
            </div>
            <div class="stat-item">
                <strong>PDF Links Found:</strong><br>{sum(w['pdf_links_found'] for w in works)}
            </div>
            <div class="stat-item">
                <strong>Generated:</strong><br>{datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
        </div>
'''
        
        # Add each work
        for i, work in enumerate(works, 1):
            status_class = "found" if work['url'] else "not-found"
            status_badge_class = "status-found" if work['url'] else "status-not-found"
            status_text = f"✅ {work['pdf_links_found']} PDFs found" if work['url'] else "❌ Not found on IMSLP"
            
            html_content += f'''
        <div class="work-section {status_class}">
            <div class="work-header">
                <div>
                    <div class="work-title">{i}. {work['title']}</div>
                    <div class="composer">by {work['composer']}</div>
                    <div class="csv-info">CSV Row: {work['csv_row']}</div>
                </div>
                <div class="status-badge {status_badge_class}">{status_text}</div>
            </div>
'''
            
            if work['url']:
                html_content += f'''
            <a href="{work['url']}" class="imslp-link" target="_blank">🔗 View on IMSLP</a>
            
            <div class="pdf-links">
'''
                
                if work['pdf_links']:
                    html_content += f"<strong>📥 Download Links ({len(work['pdf_links'])} versions available):</strong><br><br>"
                    
                    for j, pdf in enumerate(work['pdf_links'], 1):
                        html_content += f'''
                <a href="{pdf['download_url']}" class="pdf-link" target="_blank">
                    <div class="pdf-title">Version {j}: {pdf['title']}</div>
                    <div class="pdf-description">{pdf['description']}</div>
                    <div class="pdf-size">File size: {pdf['file_size']}</div>
                </a>
'''
                else:
                    html_content += '''
                <div class="no-results">
                    ⚠️ IMSLP page found but no PDF download links detected.<br>
                    Visit the IMSLP page above to check for available scores manually.
                </div>
'''
                
                html_content += '''
            </div>
'''
            else:
                html_content += '''
            <div class="no-results">
                ❌ Could not locate this work on IMSLP.<br>
                • The work may not be available in IMSLP's database<br>
                • The title or composer name may need adjustment<br>
                • Try searching manually on <a href="https://imslp.org" target="_blank">IMSLP.org</a>
            </div>
'''
            
            html_content += '''
        </div>
'''
        
        html_content += '''
        <div class="generated-info">
            <p><strong>How to use this report:</strong></p>
            <p>• Click any "Version X" link to download that PDF directly</p>
            <p>• If a download doesn't work, try the IMSLP page link for manual download</p>
            <p>• Works marked "Not found" may need manual searching or may not be available on IMSLP</p>
            <p>• Some links may require solving a CAPTCHA on IMSLP's website</p>
            <br>
            <p><em>Generated by CSV-Integrated IMSLP Downloader</em></p>
        </div>
    </div>
</body>
</html>'''
        
        # Write HTML file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path.absolute()}")
        return str(output_path.absolute())


def main():
    """Process the Form Anthology CSV file"""
    
    csv_file = "Form Anthology - Sheet1.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file '{csv_file}' not found!")
        print("Please make sure the file exists in the current directory.")
        return
    
    print("=== CSV-Integrated IMSLP Report Generator ===")
    print(f"📁 Processing: {csv_file}")
    print("🔍 This will search IMSLP for each work and generate a comprehensive report...")
    print()
    
    # Ask user about processing scope
    response = input("Process all works? (y/n, or enter number to limit for testing): ").strip().lower()
    
    max_works = None
    if response.isdigit():
        max_works = int(response)
        print(f"🧪 Processing first {max_works} works for testing")
    elif response == 'n':
        max_works = 5
        print(f"🧪 Processing first {max_works} works for testing")
    else:
        print("📊 Processing all works - this may take a while...")
    
    print()
    
    processor = CSVIMSLPProcessor()
    
    try:
        # Process the CSV file
        works = processor.process_csv_works(csv_file, max_works=max_works)
        
        # Generate HTML report
        output_file = processor.generate_csv_html_report(works)
        
        print("\n" + "="*70)
        print("✅ CSV PROCESSING COMPLETED!")
        print("="*70)
        print(f"📁 Report file: {output_file}")
        print()
        
        # Summary statistics
        total_works = len(works)
        found_works = len([w for w in works if w['url']])
        total_pdfs = sum(w['pdf_links_found'] for w in works)
        
        print("📊 Processing Summary:")
        print(f"  • Total works processed: {total_works}")
        print(f"  • IMSLP pages found: {found_works} ({found_works/total_works*100:.1f}%)")
        print(f"  • PDF download links: {total_pdfs}")
        print(f"  • Average PDFs per found work: {total_pdfs/found_works:.1f}" if found_works > 0 else "  • No PDFs found")
        print()
        
        if found_works < total_works:
            not_found = total_works - found_works
            print(f"⚠️  {not_found} works were not found on IMSLP:")
            print("   • They may not be in IMSLP's database")
            print("   • The titles may need manual adjustment")
            print("   • They may be under copyright restrictions")
            print()
        
        print("🖱️  Next steps:")
        print("  1. Open the HTML file in your web browser")
        print("  2. Click download links for available scores")
        print("  3. Use IMSLP page links for works that need manual searching")
        print()
        print("💡 Tip: Bookmark the HTML file for future reference!")
        
    except Exception as e:
        print(f"❌ Error processing CSV file: {e}")
        logger.error(f"CSV processing failed: {e}")


if __name__ == "__main__":
    main()