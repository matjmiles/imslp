#!/usr/bin/env python3
"""
Improved CSV-IMSLP Processor with better work mapping and search
"""

import csv
import requests
import time
import json
import logging
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from pathlib import Path
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedCSVProcessor:
    """Improved CSV processor with better IMSLP matching"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
        
        # Create a mapping from movement entries to complete works
        self.work_mappings = self._create_work_mappings()
    
    def _create_work_mappings(self) -> Dict[str, Dict]:
        """Create mappings from movement/partial entries to complete works"""
        return {
            # Mozart Symphonies
            'mozart symphony 40': {
                'full_title': 'Symphony No.40, K.550',
                'composer': 'Mozart, Wolfgang Amadeus',
                'imslp_url': 'https://imslp.org/wiki/Symphony_No.40,_K.550_(Mozart,_Wolfgang_Amadeus)'
            },
            'mozart symphony 36': {
                'full_title': 'Symphony No.36, K.425',
                'composer': 'Mozart, Wolfgang Amadeus',
                'imslp_url': 'https://imslp.org/wiki/Symphony_No.36,_K.425_(Mozart,_Wolfgang_Amadeus)'
            },
            'mozart symphony 35': {
                'full_title': 'Symphony No.35, K.385',
                'composer': 'Mozart, Wolfgang Amadeus', 
                'imslp_url': 'https://imslp.org/wiki/Symphony_No.35,_K.385_(Mozart,_Wolfgang_Amadeus)'
            },
            'mozart eine kleine nachtmusik': {
                'full_title': 'Eine kleine Nachtmusik, K.525',
                'composer': 'Mozart, Wolfgang Amadeus',
                'imslp_url': 'https://imslp.org/wiki/Eine_kleine_Nachtmusik,_K.525_(Mozart,_Wolfgang_Amadeus)'
            },
            
            # Beethoven Piano Sonatas
            'beethoven piano sonata no 8': {
                'full_title': 'Piano Sonata No.8, Op.13',
                'composer': 'Beethoven, Ludwig van',
                'imslp_url': 'https://imslp.org/wiki/Piano_Sonata_No.8,_Op.13_(Beethoven,_Ludwig_van)'
            },
            'beethoven piano sonata no. 21': {
                'full_title': 'Piano Sonata No.21, Op.53',
                'composer': 'Beethoven, Ludwig van',
                'imslp_url': 'https://imslp.org/wiki/Piano_Sonata_No.21,_Op.53_(Beethoven,_Ludwig_van)'
            },
            'beethoven piano sonata no. 15': {
                'full_title': 'Piano Sonata No.15, Op.28',
                'composer': 'Beethoven, Ludwig van', 
                'imslp_url': 'https://imslp.org/wiki/Piano_Sonata_No.15,_Op.28_(Beethoven,_Ludwig_van)'
            },
            'beethoven piano sonata no. 20': {
                'full_title': 'Piano Sonata No.20, Op.49 No.2',
                'composer': 'Beethoven, Ludwig van',
                'imslp_url': 'https://imslp.org/wiki/Piano_Sonata_No.20,_Op.49_No.2_(Beethoven,_Ludwig_van)'
            },
            
            # Bach Works
            'bach french suite no 6': {
                'full_title': 'French Suite No.6, BWV 817',
                'composer': 'Bach, Johann Sebastian',
                'imslp_url': 'https://imslp.org/wiki/French_Suite_No.6,_BWV_817_(Bach,_Johann_Sebastian)'
            },
            'bach cello suite no 3': {
                'full_title': 'Cello Suite No.3, BWV 1009', 
                'composer': 'Bach, Johann Sebastian',
                'imslp_url': 'https://imslp.org/wiki/Cello_Suite_No.3,_BWV_1009_(Bach,_Johann_Sebastian)'
            },
            'bach well-tempered clavier': {
                'full_title': 'Well-Tempered Clavier I, BWV 846-869',
                'composer': 'Bach, Johann Sebastian',
                'imslp_url': 'https://imslp.org/wiki/Well-Tempered_Clavier_I,_BWV_846-869_(Bach,_Johann_Sebastian)'
            },
            'bach wtc': {
                'full_title': 'Well-Tempered Clavier I, BWV 846-869',
                'composer': 'Bach, Johann Sebastian', 
                'imslp_url': 'https://imslp.org/wiki/Well-Tempered_Clavier_I,_BWV_846-869_(Bach,_Johann_Sebastian)'
            },
            'bach brandenburg concerto no 5': {
                'full_title': 'Brandenburg Concerto No.5, BWV 1050',
                'composer': 'Bach, Johann Sebastian',
                'imslp_url': 'https://imslp.org/wiki/Brandenburg_Concerto_No.5,_BWV_1050_(Bach,_Johann_Sebastian)'
            },
            'bach brandenburg concerto no 2': {
                'full_title': 'Brandenburg Concerto No.2, BWV 1047',
                'composer': 'Bach, Johann Sebastian',
                'imslp_url': 'https://imslp.org/wiki/Brandenburg_Concerto_No.2,_BWV_1047_(Bach,_Johann_Sebastian)'
            },
            
            # Haydn Works  
            'haydn symphony 103': {
                'full_title': 'Symphony No.103, Hob.I:103',
                'composer': 'Haydn, Joseph',
                'imslp_url': 'https://imslp.org/wiki/Symphony_No.103,_Hob.I:103_(Haydn,_Joseph)'
            },
            'haydn symphony 101': {
                'full_title': 'Symphony No.101, Hob.I:101',
                'composer': 'Haydn, Joseph',
                'imslp_url': 'https://imslp.org/wiki/Symphony_No.101,_Hob.I:101_(Haydn,_Joseph)'
            },
            
            # Vivaldi
            'vivaldi winter': {
                'full_title': 'The Four Seasons, Op.8',
                'composer': 'Vivaldi, Antonio',
                'imslp_url': 'https://imslp.org/wiki/The_Four_Seasons,_Op.8_(Vivaldi,_Antonio)'
            },
            'vivaldi summer': {
                'full_title': 'The Four Seasons, Op.8', 
                'composer': 'Vivaldi, Antonio',
                'imslp_url': 'https://imslp.org/wiki/The_Four_Seasons,_Op.8_(Vivaldi,_Antonio)'
            },
            
            # Schumann
            'schumann novelletten': {
                'full_title': '8 Novelletten, Op.21',
                'composer': 'Schumann, Robert',
                'imslp_url': 'https://imslp.org/wiki/8_Novelletten,_Op.21_(Schumann,_Robert)'
            }
        }
    
    def read_csv_works(self, csv_file: str) -> List[Dict]:
        """Read and process works from CSV"""
        works = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                f.seek(0)
                
                csv_reader = csv.reader(f)
                
                if first_line == ',':
                    next(csv_reader)
                
                for row_num, row in enumerate(csv_reader, 1):
                    if len(row) >= 2 and row[0].strip() and row[1].strip():
                        composer = row[0].strip()
                        title = row[1].strip()
                        
                        work = {
                            'original_composer': composer,
                            'original_title': title,
                            'csv_row': row_num,
                            'mapped_work': self._find_work_mapping(composer, title)
                        }
                        works.append(work)
                        
            logger.info(f"Successfully read {len(works)} works from {csv_file}")
            
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_file}: {e}")
            return []
        
        return works
    
    def _find_work_mapping(self, composer: str, title: str) -> Optional[Dict]:
        """Find a work mapping for the given composer/title"""
        search_key = f"{composer.lower()} {title.lower()}"
        
        # Clean up the search key
        search_key = search_key.replace('mvt.', '').replace('mvt', '')
        search_key = search_key.replace('movement', '').replace('all movements', '')
        search_key = ' '.join(search_key.split())  # Clean extra spaces
        
        # Try to find a mapping
        for key, mapping in self.work_mappings.items():
            if key in search_key or any(word in search_key for word in key.split()):
                return mapping
        
        return None
    
    def test_imslp_url(self, url: str) -> bool:
        """Test if an IMSLP URL is valid"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def get_pdf_links_from_work(self, work_url: str, limit: int = 3) -> List[Dict]:
        """Extract PDF links from IMSLP work page"""
        pdf_links = []
        
        try:
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(work_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pdf_spans = soup.find_all('span', class_='we_file_info2')
            
            for span in pdf_spans:
                link = span.find('a')
                if link and link.get('href'):
                    href = link.get('href')
                    if href.endswith('.pdf') or 'pdf' in href.lower():
                        pdf_info = {
                            'title': link.get_text(strip=True),
                            'download_url': urljoin('https://imslp.org', href),
                            'description': self._extract_pdf_description(span),
                            'file_size': self._extract_file_size(span)
                        }
                        pdf_links.append(pdf_info)
                        
                        if len(pdf_links) >= limit:
                            break
            
            logger.info(f"Found {len(pdf_links)} PDF links")
            
        except Exception as e:
            logger.error(f"Error extracting PDF links: {e}")
        
        return pdf_links
    
    def _extract_pdf_description(self, span) -> str:
        """Extract description for PDF"""
        try:
            parent = span.parent
            if parent:
                text = parent.get_text(strip=True)
                return text[:150] + "..." if len(text) > 150 else text
        except:
            pass
        return "PDF Score"
    
    def _extract_file_size(self, span) -> str:
        """Extract file size"""
        try:
            parent = span.parent
            if parent:
                text = parent.get_text()
                import re
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|KB|GB)', text, re.IGNORECASE)
                if size_match:
                    return f"{size_match.group(1)} {size_match.group(2).upper()}"
        except:
            pass
        return "Unknown size"
    
    def process_csv_works(self, csv_file: str, max_works: int = None) -> List[Dict]:
        """Process works from CSV with improved mapping"""
        works = self.read_csv_works(csv_file)
        
        if max_works:
            works = works[:max_works]
        
        processed_works = []
        
        for i, work in enumerate(works, 1):
            logger.info(f"Processing {i}/{len(works)}: {work['original_composer']} - {work['original_title']}")
            
            if work['mapped_work']:
                # Use mapped work
                work['composer'] = work['mapped_work']['composer']
                work['title'] = work['mapped_work']['full_title'] 
                work['url'] = work['mapped_work']['imslp_url']
                work['status'] = 'mapped'
                
                # Test if URL works
                if self.test_imslp_url(work['url']):
                    work['url_valid'] = True
                    # Get PDF links
                    work['pdf_links'] = self.get_pdf_links_from_work(work['url'])
                    work['pdf_links_found'] = len(work['pdf_links'])
                    logger.info(f"✅ Mapped work found: {work['pdf_links_found']} PDFs")
                else:
                    work['url_valid'] = False
                    work['pdf_links'] = []
                    work['pdf_links_found'] = 0
                    logger.warning(f"❌ Mapped URL invalid: {work['url']}")
            else:
                # No mapping found
                work['composer'] = work['original_composer']
                work['title'] = work['original_title']
                work['url'] = None
                work['status'] = 'no_mapping'
                work['url_valid'] = False
                work['pdf_links'] = []
                work['pdf_links_found'] = 0
                logger.warning(f"❌ No mapping found")
            
            processed_works.append(work)
            
            # Delay between works
            time.sleep(random.uniform(2, 4))
        
        return processed_works
    
    def generate_html_report(self, works: List[Dict], output_file: str = "improved_csv_report.html") -> str:
        """Generate improved HTML report"""
        
        total_works = len(works)
        mapped_works = len([w for w in works if w['status'] == 'mapped'])
        valid_urls = len([w for w in works if w['url_valid']])
        total_pdfs = sum(w['pdf_links_found'] for w in works)
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Improved IMSLP Form Anthology Report</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .work-section {{
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .work-section.mapped {{
            border-left: 5px solid #27ae60;
            background: linear-gradient(90deg, rgba(39, 174, 96, 0.1) 0%, rgba(255,255,255,1) 100%);
        }}
        .work-section.no-mapping {{
            border-left: 5px solid #f39c12;
            background: linear-gradient(90deg, rgba(243, 156, 18, 0.1) 0%, rgba(255,255,255,1) 100%);
        }}
        .work-header {{
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: center;
            margin-bottom: 15px;
        }}
        .original-work {{
            background: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }}
        .mapped-work {{
            background: #d5f4e6;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .work-title {{
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .composer {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        .status-badge {{
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .status-mapped {{
            background-color: #d5f4e6;
            color: #27ae60;
        }}
        .status-no-mapping {{
            background-color: #fef9e7;
            color: #f39c12;
        }}
        .pdf-links {{
            margin-top: 15px;
        }}
        .pdf-link {{
            display: block;
            margin: 12px 0;
            padding: 15px;
            background: white;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            text-decoration: none;
            color: #2c3e50;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .pdf-link:hover {{
            background: #3498db;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }}
        .pdf-title {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 8px;
        }}
        .pdf-description {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
            line-height: 1.4;
        }}
        .imslp-link {{
            display: inline-block;
            margin: 10px 10px 10px 0;
            padding: 10px 20px;
            background: linear-gradient(135deg, #27ae60, #229954);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        .imslp-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
        }}
        .no-mapping-info {{
            color: #f39c12;
            background: #fef9e7;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
        }}
        .generated-info {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎼 Improved IMSLP Form Anthology Report</h1>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">{total_works}</span>
                Total Works
            </div>
            <div class="stat-item">
                <span class="stat-number">{mapped_works}</span>
                Successfully Mapped
            </div>
            <div class="stat-item">
                <span class="stat-number">{valid_urls}</span>
                Valid IMSLP Links
            </div>
            <div class="stat-item">
                <span class="stat-number">{total_pdfs}</span>
                PDF Downloads Found
            </div>
        </div>
'''
        
        for i, work in enumerate(works, 1):
            status_class = work['status']
            status_text = "✅ Successfully Mapped" if work['status'] == 'mapped' else "⚠️ No Mapping Found"
            
            html_content += f'''
        <div class="work-section {status_class}">
            <div class="work-header">
                <div>
                    <div class="original-work">
                        <strong>Original CSV Entry #{work['csv_row']}:</strong><br>
                        {work['original_composer']} - {work['original_title']}
                    </div>
'''
            
            if work['status'] == 'mapped':
                html_content += f'''
                    <div class="mapped-work">
                        <div class="work-title">{work['title']}</div>
                        <div class="composer">by {work['composer']}</div>
                    </div>
'''
            
            html_content += f'''
                </div>
                <div class="status-badge status-{status_class}">{status_text}</div>
            </div>
'''
            
            if work['url_valid']:
                html_content += f'''
            <a href="{work['url']}" class="imslp-link" target="_blank">🔗 View Complete Work on IMSLP</a>
            
            <div class="pdf-links">
                <strong>📥 Available Downloads ({work['pdf_links_found']} versions found):</strong><br><br>
'''
                
                for j, pdf in enumerate(work['pdf_links'], 1):
                    html_content += f'''
                <a href="{pdf['download_url']}" class="pdf-link" target="_blank">
                    <div class="pdf-title">Version {j}: {pdf['title']}</div>
                    <div class="pdf-description">{pdf['description']}</div>
                    <div style="color: #95a5a6; font-size: 0.8em;">File size: {pdf['file_size']}</div>
                </a>
'''
                
                html_content += '''
            </div>
'''
            else:
                html_content += '''
            <div class="no-mapping-info">
                ❌ This entry could not be mapped to a complete IMSLP work.<br><br>
                <strong>Possible reasons:</strong><br>
                • The entry refers to a specific movement rather than a complete work<br>
                • The work may not be available in IMSLP's database<br>
                • The title format doesn't match IMSLP's cataloging system<br><br>
                <strong>Suggestion:</strong> Search manually on <a href="https://imslp.org" target="_blank">IMSLP.org</a> for the complete work.
            </div>
'''
            
            html_content += '''
        </div>
'''
        
        success_rate = (valid_urls / total_works * 100) if total_works > 0 else 0
        
        html_content += f'''
        <div class="generated-info">
            <h3>📊 Report Summary</h3>
            <p><strong>Success Rate:</strong> {success_rate:.1f}% of entries successfully found on IMSLP</p>
            <p><strong>Key Improvement:</strong> This version maps movement-specific entries to their complete parent works</p>
            <p><strong>How to use:</strong> Click "Version X" links to download PDFs, or visit IMSLP pages for manual browsing</p>
            <br>
            <p><em>Generated by Improved CSV-IMSLP Processor - {datetime.now().strftime("%Y-%m-%d %H:%M")}</em></p>
        </div>
    </div>
</body>
</html>'''
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path.absolute())


def main():
    """Main function"""
    csv_file = "Form Anthology - Sheet1.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file '{csv_file}' not found!")
        return
    
    print("=== Improved CSV-IMSLP Processor ===")
    print("🔧 This version includes work mappings for better success rates")
    print()
    
    # Ask for processing scope
    response = input("Process all works? (y/n, or enter number to limit): ").strip()
    
    max_works = None
    if response.isdigit():
        max_works = int(response)
    elif response.lower() == 'n':
        max_works = 10
    
    processor = ImprovedCSVProcessor()
    
    try:
        works = processor.process_csv_works(csv_file, max_works)
        output_file = processor.generate_html_report(works)
        
        print("\n" + "="*70)
        print("✅ IMPROVED PROCESSING COMPLETED!")
        print("="*70)
        print(f"📁 Report: {output_file}")
        
        # Statistics
        total = len(works)
        mapped = len([w for w in works if w['status'] == 'mapped'])
        valid = len([w for w in works if w['url_valid']])
        pdfs = sum(w['pdf_links_found'] for w in works)
        
        print(f"\n📊 Results:")
        print(f"   • Total works: {total}")
        print(f"   • Successfully mapped: {mapped} ({mapped/total*100:.1f}%)")
        print(f"   • Valid IMSLP URLs: {valid} ({valid/total*100:.1f}%)")
        print(f"   • PDF downloads found: {pdfs}")
        
        if valid > 0:
            print(f"   • Average PDFs per valid work: {pdfs/valid:.1f}")
        
        print(f"\n💡 This improved version achieved {valid/total*100:.1f}% success rate")
        print(f"   compared to likely 0% with direct URL construction!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()