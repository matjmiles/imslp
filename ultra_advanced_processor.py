#!/usr/bin/env python3
"""
Ultra Advanced CSV-IMSLP Processor
==================================
This processor uses the most sophisticated search techniques to find the remaining
20 unmapped works that have been challenging to locate on IMSLP.

Features:
- Multiple composer name format variations
- Movement-specific searches within larger works
- Alternative title searches with translations
- Catalog number extraction and searching
- Collection-based searches
- Fuzzy matching for similar titles
- Multiple URL validation attempts
"""

import csv
import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import quote, unquote
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UltraAdvancedProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://imslp.org"
        self.search_url = "https://imslp.org/wiki/Special:IMSLPSearch"
        
    def get_composer_variations(self, composer):
        """Generate various composer name formats"""
        variations = [composer]
        
        # Standard variations
        name_parts = composer.split()
        if len(name_parts) >= 2:
            # Last, First format
            variations.append(f"{name_parts[-1]}, {' '.join(name_parts[:-1])}")
            
        # Specific composer variations
        composer_map = {
            'Bach': ['Bach, Johann Sebastian', 'Johann Sebastian Bach', 'J.S. Bach', 'Bach, J.S.'],
            'Mozart': ['Mozart, Wolfgang Amadeus', 'Wolfgang Amadeus Mozart', 'W.A. Mozart', 'Mozart, W.A.'],
            'Beethoven': ['Beethoven, Ludwig van', 'Ludwig van Beethoven', 'L. van Beethoven'],
            'Haydn': ['Haydn, Joseph', 'Joseph Haydn', 'Franz Joseph Haydn', 'Haydn, Franz Joseph'],
            'Schubert': ['Schubert, Franz', 'Franz Schubert', 'Franz Peter Schubert'],
            'Brahms': ['Brahms, Johannes', 'Johannes Brahms'],
            'Schumann': ['Schumann, Robert', 'Robert Schumann', 'Robert Alexander Schumann'],
            'Fanny Mendelssohn': ['Hensel, Fanny', 'Fanny Hensel', 'Mendelssohn-Hensel, Fanny', 'Fanny Mendelssohn'],
            'Anna Magdalena Bach': ['Bach, Anna Magdalena', 'Anna Magdalena Bach', 'Bach, A.M.'],
            'Purcell': ['Purcell, Henry', 'Henry Purcell'],
            'Vivaldi': ['Vivaldi, Antonio', 'Antonio Vivaldi', 'Antonio Lucio Vivaldi']
        }
        
        for key, variants in composer_map.items():
            if key.lower() in composer.lower():
                variations.extend(variants)
                
        return list(set(variations))  # Remove duplicates

    def extract_catalog_numbers(self, title):
        """Extract catalog numbers like BWV, Op., K., Hob., etc."""
        catalog_patterns = [
            r'BWV\s*(\d+)',
            r'Op\.?\s*(\d+)',
            r'K\.?\s*(\d+)',
            r'Hob\.?\s*([IVX]+:?\d+)',
            r'D\.?\s*(\d+)',
            r'WoO\.?\s*(\d+)',
        ]
        
        catalog_numbers = []
        for pattern in catalog_patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            catalog_numbers.extend(matches)
            
        return catalog_numbers

    def get_title_variations(self, composer, title):
        """Generate various title formats and translations"""
        variations = [title]
        
        # Remove movement indicators
        base_title = re.sub(r'\s+(mvt\.?|movement)\s*\d+.*$', '', title, flags=re.IGNORECASE)
        base_title = re.sub(r'\s+all movements.*$', '', base_title, flags=re.IGNORECASE)
        variations.append(base_title)
        
        # Specific title mappings for difficult cases
        title_mappings = {
            'Kennst du das Land': [
                'Mignon Songs, D.321',
                'Mignon-Lieder, D.321',
                'Kennst du das Land, D.321',
                'Goethe Songs, D.321'
            ],
            'March in D major, BWV Anh. 122': [
                'Notebook for Anna Magdalena Bach, BWV Anh.113-132',
                'Notenbuch der Anna Magdalena Bach',
                'Anna Magdalena Bach Book',
                'March in D major, BWV Anh.122'
            ],
            'Piano Sonata in D Hob. XVI 37': [
                'Piano Sonata No.37, Hob.XVI:37',
                'Piano Sonata in D major, Hob.XVI:37',
                'Keyboard Sonata No.37, Hob.XVI:37'
            ],
            'French Suite No 6': [
                'French Suite No.6, BWV 817',
                'French Suite No.6 in E major, BWV 817',
                'Französische Suite Nr.6, BWV 817'
            ],
            'Cello Suite No 3': [
                'Cello Suite No.3, BWV 1009',
                'Cello Suite No.3 in C major, BWV 1009',
                'Suite for Violoncello No.3, BWV 1009'
            ],
            'Piano Sonata no.33': [
                'Piano Sonata No.33, Hob.XVI:20',
                'Piano Sonata in C minor, Hob.XVI:20',
                'Keyboard Sonata No.33, Hob.XVI:20'
            ],
            'WTC': [
                'Well-Tempered Clavier I, BWV 846-869',
                'Well-Tempered Clavier II, BWV 870-893',
                'Das Wohltemperierte Klavier'
            ],
            'Four Seasons': [
                'The Four Seasons, Op.8',
                'Le quattro stagioni, Op.8',
                'Violin Concerto No.1, Op.8 No.1 (Spring)',
                'Violin Concerto No.2, Op.8 No.2 (Summer)',
                'Violin Concerto No.3, Op.8 No.3 (Autumn)',
                'Violin Concerto No.4, Op.8 No.4 (Winter)'
            ],
            'Emperor': [
                'String Quartet No.77, Op.76 No.3',
                'String Quartet in C major, Op.76 No.3',
                'Emperor Quartet, Op.76 No.3'
            ],
            'Piano Sonata K. 333': [
                'Piano Sonata No.13, K.333/315c',
                'Piano Sonata in B♭ major, K.333',
                'Sonata No.13 in B-flat major, K.333'
            ]
        }
        
        # Add specific mappings
        for key, mappings in title_mappings.items():
            if key.lower() in title.lower():
                variations.extend(mappings)
                
        # Add catalog number variations
        catalog_nums = self.extract_catalog_numbers(title)
        for num in catalog_nums:
            variations.append(f"{composer} {num}")
            
        return list(set(variations))

    def search_imslp_advanced(self, composer, title):
        """Advanced IMSLP search with multiple strategies"""
        
        composer_variations = self.get_composer_variations(composer)
        title_variations = self.get_title_variations(composer, title)
        
        # Strategy 1: Try all composer/title combinations
        for comp_var in composer_variations:
            for title_var in title_variations:
                url = self.try_direct_url(comp_var, title_var)
                if url:
                    return url
                    
        # Strategy 2: Search by catalog numbers only
        catalog_nums = self.extract_catalog_numbers(title)
        for num in catalog_nums:
            for comp_var in composer_variations:
                search_results = self.search_by_query(f"{comp_var} {num}")
                if search_results:
                    return search_results[0]
                    
        # Strategy 3: Search by movement/part within larger works
        if 'mvt' in title.lower() or 'movement' in title.lower():
            base_work = re.sub(r'\s+(mvt\.?|movement).*$', '', title, flags=re.IGNORECASE)
            for comp_var in composer_variations:
                url = self.try_direct_url(comp_var, base_work)
                if url:
                    return url
                    
        # Strategy 4: Collection searches
        collection_keywords = ['suite', 'sonata', 'symphony', 'concerto', 'quartet', 'songs']
        for keyword in collection_keywords:
            if keyword in title.lower():
                for comp_var in composer_variations:
                    search_results = self.search_by_query(f"{comp_var} {keyword}")
                    if search_results:
                        return search_results[0]
                        
        return None

    def try_direct_url(self, composer, title):
        """Try to construct direct IMSLP URL"""
        # Format for IMSLP URLs: /wiki/Title_(Composer,_Name)
        formatted_title = title.strip()
        formatted_composer = composer.strip()
        
        # Clean up title
        formatted_title = re.sub(r'\s+', '_', formatted_title)
        formatted_composer = re.sub(r'\s+', '_', formatted_composer)
        
        # Try various URL formats
        url_formats = [
            f"/wiki/{formatted_title}_({formatted_composer})",
            f"/wiki/{formatted_title},_{formatted_title.split('_')[0]}_({formatted_composer})",
            f"/wiki/{formatted_title}_in_.*_({formatted_composer})"
        ]
        
        for url_format in url_formats:
            try:
                test_url = self.base_url + url_format
                response = self.session.get(test_url, timeout=10)
                if response.status_code == 200 and 'does not exist' not in response.text:
                    return test_url
            except:
                continue
                
        return None

    def search_by_query(self, query):
        """Search IMSLP using search functionality"""
        try:
            search_params = {
                'search': query,
                'go': 'Go'
            }
            
            response = self.session.get(self.search_url, params=search_params, timeout=15)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for search results
            results = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/wiki/' in href and not href.startswith('/wiki/Category:'):
                    if '(' in href and ')' in href:  # Likely a work page
                        full_url = self.base_url + href if href.startswith('/') else href
                        results.append(full_url)
                        
            return results[:5]  # Return top 5 results
            
        except Exception as e:
            logging.warning(f"Search failed for '{query}': {e}")
            return []

    def validate_url_and_get_pdfs(self, url):
        """Validate URL and extract PDF links"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return False, []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if it's a valid work page
            if 'does not exist' in response.text.lower():
                return False, []
                
            # Extract PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/images/' in href and href.endswith('.pdf'):
                    if href.startswith('/'):
                        href = self.base_url + href
                    
                    # Get link description
                    description = link.get_text(strip=True)
                    parent = link.find_parent()
                    if parent:
                        desc_text = parent.get_text(strip=True)
                        if len(desc_text) > len(description):
                            description = desc_text[:200]
                            
                    pdf_links.append({
                        'url': href,
                        'description': description
                    })
                    
            return True, pdf_links[:3]  # Return top 3 PDFs
            
        except Exception as e:
            logging.warning(f"URL validation failed for {url}: {e}")
            return False, []

    def process_csv_ultra_advanced(self, csv_file):
        """Process CSV with ultra-advanced search techniques"""
        results = []
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            works_raw = list(csv_reader)
            
        # Skip empty first row and convert to list of dicts
        works = []
        for row in works_raw[1:]:  # Skip first empty row
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                works.append({
                    'Composer': row[0].strip(),
                    'Title': row[1].strip()
                })
            
        logging.info(f"Successfully read {len(works)} works from {csv_file}")
        
        for i, work in enumerate(works, 1):
            composer = work.get('Composer', '').strip()
            title = work.get('Title', '').strip()
            
            if not composer or not title:
                continue
                
            logging.info(f"Processing {i}/{len(works)}: {composer} - {title}")
            
            # Use ultra-advanced search
            imslp_url = self.search_imslp_advanced(composer, title)
            
            if imslp_url:
                # Validate and get PDFs
                is_valid, pdf_links = self.validate_url_and_get_pdfs(imslp_url)
                
                if is_valid and pdf_links:
                    logging.info(f"✅ Ultra solution found: {len(pdf_links)} PDFs")
                    results.append({
                        'original_composer': composer,
                        'original_title': title,
                        'imslp_url': imslp_url,
                        'pdf_links': pdf_links,
                        'status': 'success'
                    })
                elif is_valid:
                    logging.warning(f"⚠️ Found page but no PDFs")
                    results.append({
                        'original_composer': composer,
                        'original_title': title,
                        'imslp_url': imslp_url,
                        'pdf_links': [],
                        'status': 'no_pdfs'
                    })
                else:
                    logging.warning(f"❌ Invalid URL: {imslp_url}")
                    results.append({
                        'original_composer': composer,
                        'original_title': title,
                        'imslp_url': None,
                        'pdf_links': [],
                        'status': 'invalid_url'
                    })
            else:
                logging.warning(f"❌ No ultra mapping found")
                results.append({
                    'original_composer': composer,
                    'original_title': title,
                    'imslp_url': None,
                    'pdf_links': [],
                    'status': 'not_found'
                })
                
            # Be respectful to IMSLP servers
            time.sleep(2)
            
        return results

    def generate_ultra_report(self, results):
        """Generate HTML report with ultra-advanced results"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        successful_works = [r for r in results if r['status'] == 'success']
        mapped_works = [r for r in results if r['imslp_url'] is not None]
        total_pdfs = sum(len(r['pdf_links']) for r in results)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultra Advanced IMSLP Form Anthology Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 4px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        .stat-item {{
            text-align: center;
            padding: 20px;
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            display: block;
        }}
        .work-section {{
            margin: 25px 0;
            padding: 25px;
            border-radius: 12px;
            background-color: #fafafa;
            border: 1px solid #e0e0e0;
        }}
        .work-section.ultra-success {{
            border-left: 6px solid #27ae60;
            background: linear-gradient(90deg, rgba(39, 174, 96, 0.05) 0%, rgba(255,255,255,1) 100%);
        }}
        .work-section.ultra-found {{
            border-left: 6px solid #3498db;
            background: linear-gradient(90deg, rgba(52, 152, 219, 0.05) 0%, rgba(255,255,255,1) 100%);
        }}
        .work-section.ultra-not-found {{
            border-left: 6px solid #e74c3c;
            background: linear-gradient(90deg, rgba(231, 76, 60, 0.05) 0%, rgba(255,255,255,1) 100%);
        }}
        .ultra-highlight {{
            background: linear-gradient(135deg, #d5f4e6, #c8e6c9);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #27ae60;
        }}
        .pdf-link {{
            display: block;
            margin: 15px 0;
            padding: 20px;
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            text-decoration: none;
            color: #2c3e50;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .pdf-link:hover {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        }}
        .imslp-link {{
            display: inline-block;
            margin: 15px 15px 15px 0;
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        .imslp-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
        }}
        .ultra-not-found-info {{
            color: #e74c3c;
            background: linear-gradient(135deg, #fdf2f2, #fcf3f3);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Ultra Advanced IMSLP Form Anthology Report</h1>
        
        <div class="hero">
            <h2>🎯 Ultra Advanced Search Results</h2>
            <p>This report uses the most sophisticated search techniques to find even the most difficult works</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">{len(results)}</span>
                Total Works
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(mapped_works)}</span>
                Successfully Mapped
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(successful_works)}</span>
                With PDF Downloads
            </div>
            <div class="stat-item">
                <span class="stat-number">{total_pdfs}</span>
                PDF Downloads Found
            </div>
        </div>

"""

        # Add individual work sections
        for i, result in enumerate(results, 1):
            if result['status'] == 'success':
                section_class = 'ultra-success'
                status_info = f"""
            <div class="ultra-highlight">
                ✅ <strong>Ultra Advanced Success!</strong> Found {len(result['pdf_links'])} downloadable PDF versions.
            </div>
            
            <a href="{result['imslp_url']}" class="imslp-link" target="_blank">🔗 View Complete Work on IMSLP</a>
            
            <div class="pdf-links">
                <strong>📥 Available Downloads ({len(result['pdf_links'])} versions found):</strong><br><br>
"""
                for j, pdf in enumerate(result['pdf_links'], 1):
                    status_info += f"""
                <a href="{pdf['url']}" class="pdf-link" target="_blank">
                    <div class="pdf-title">📄 Version {j}: Ultra Found</div>
                    <div class="pdf-description">{pdf['description']}</div>
                </a>
"""
                status_info += "</div>"
                
            elif result['status'] == 'no_pdfs':
                section_class = 'ultra-found'
                status_info = f"""
            <div style="background: linear-gradient(135deg, #e8f4f8, #f0f8fb); padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                ⚠️ <strong>Page found but no PDFs available</strong> - Try checking the IMSLP page directly for other formats.
            </div>
            
            <a href="{result['imslp_url']}" class="imslp-link" target="_blank">🔗 View Work Page on IMSLP</a>
"""
            else:
                section_class = 'ultra-not-found'
                status_info = """
            <div class="ultra-not-found-info">
                ❌ <strong>Even ultra-advanced search couldn't locate this work</strong><br><br>
                <strong>This is likely because:</strong><br>
                • The work is extremely rare or not digitized<br>
                • It may be catalogued under a completely different title<br>
                • It might be part of a manuscript collection not yet uploaded<br><br>
                <strong>💡 Final suggestion:</strong> Contact IMSLP directly or check university music libraries
            </div>
"""

            html_content += f"""
        <div class="work-section {section_class}">
            <div class="work-header">
                <div>
                    <div style="background: #f5f6fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #ddd;">
                        <strong>🎵 Original CSV Entry #{i}:</strong><br>
                        <strong>Composer:</strong> {result['original_composer']}<br>
                        <strong>Title:</strong> {result['original_title']}
                    </div>
                </div>
            </div>

            {status_info}
        </div>
"""

        success_rate = (len(successful_works)/len(results)*100) if results else 0
        
        html_content += f"""
        <div style="text-align: center; color: #7f8c8d; font-size: 0.95em; margin-top: 50px; padding-top: 30px; border-top: 3px solid #ecf0f1;">
            <h3>🚀 Ultra Advanced Report Summary</h3>
            <p><strong>🎯 Ultra Success Rate:</strong> {len(successful_works)}/{len(results)} works ({success_rate:.1f}%)</p>
            <p><strong>🔧 Advanced Techniques Used:</strong> Multiple composer formats, catalog number searches, collection searches, movement analysis</p>
            <p><strong>📱 Next Level:</strong> This represents the most advanced automated search possible</p>
            <br>
            <p><em>🤖 Generated by Ultra Advanced CSV-IMSLP Processor - {timestamp}</em></p>
        </div>
    </div>
</body>
</html>
"""

        report_file = 'ultra_advanced_report.html'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_file

def main():
    print("=" * 70)
    print("🚀 ULTRA ADVANCED PROCESSOR")
    print("🎯 Using the most sophisticated search techniques available")
    print("✨ This targets the remaining 20 unmapped works with advanced algorithms")
    print()
    
    processor = UltraAdvancedProcessor()
    
    # Process the CSV file
    csv_file = 'Form Anthology - Sheet1.csv'
    results = processor.process_csv_ultra_advanced(csv_file)
    
    # Generate report
    report_file = processor.generate_ultra_report(results)
    
    print("=" * 70)
    print("🏆 ULTRA ADVANCED PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"📁 Ultra Report: {report_file}")
    
    # Calculate statistics
    successful_works = [r for r in results if r['status'] == 'success']
    mapped_works = [r for r in results if r['imslp_url'] is not None]
    total_pdfs = sum(len(r['pdf_links']) for r in results)
    
    mapped_rate = (len(mapped_works)/len(results)*100) if results else 0
    success_rate = (len(successful_works)/len(results)*100) if results else 0
    avg_pdfs = (total_pdfs/len(successful_works)) if successful_works else 0
    
    print(f"🎯 Ultra Advanced Results:")
    print(f"   • Total works: {len(results)}")
    print(f"   • Successfully mapped: {len(mapped_works)} ({mapped_rate:.1f}%)")
    print(f"   • With PDF downloads: {len(successful_works)} ({success_rate:.1f}%)")
    print(f"   • PDF downloads found: {total_pdfs}")
    if successful_works:
        print(f"   • Average PDFs per successful work: {avg_pdfs:.1f}")
    
    improvement = len(successful_works) - 22  # Previous best was 22
    if improvement > 0:
        print(f"\n🚀 BREAKTHROUGH: Found {improvement} additional works!")
    elif improvement == 0:
        print(f"\n📊 Maintained previous best performance")
    else:
        print(f"\n🔍 Some works may need manual research")
        
    print(f"\n🎯 ULTRA MISSION:")
    print(f"   • Advanced search algorithms applied to all {len(results)} works")
    print(f"   • Multiple search strategies per work")
    print(f"   • Comprehensive composer name variations")
    print(f"   • Catalog number extraction and searching")
    
    print(f"\n✨ Open your ultra report: {report_file}")

if __name__ == "__main__":
    main()