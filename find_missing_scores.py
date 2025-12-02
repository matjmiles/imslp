#!/usr/bin/env python3
"""
Advanced Score Finder for Unmapped Works
Searches IMSLP using multiple strategies to find missing scores
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
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedScoreFinder:
    """Advanced finder for unmapped musical works on IMSLP"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
        
        # Load original work mappings
        self.work_mappings = self._create_work_mappings()
        
        # Composer name normalization
        self.composer_aliases = {
            'anna magdalena bach': ['bach, johann sebastian', 'bach, j.s.'],
            'fanny mendelssohn': ['hensel, fanny', 'mendelssohn-hensel, fanny'],
            'schubert': ['schubert, franz'],
            'purcell': ['purcell, henry'],
            'brahms': ['brahms, johannes']
        }
    
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
        """Read works from CSV and identify unmapped ones"""
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
    
    def get_unmapped_works(self, csv_file: str) -> List[Dict]:
        """Get list of works that couldn't be mapped"""
        all_works = self.read_csv_works(csv_file)
        unmapped = [work for work in all_works if work['mapped_work'] is None]
        
        logger.info(f"Found {len(unmapped)} unmapped works out of {len(all_works)} total")
        
        return unmapped
    
    def imslp_search(self, composer: str, title: str) -> List[Dict]:
        """Search IMSLP using their search functionality"""
        search_results = []
        
        try:
            # Try different search strategies
            search_terms = [
                f"{composer} {title}",
                title,  # Sometimes composer in title is enough
                f'"{title}"',  # Exact phrase search
            ]
            
            for search_term in search_terms:
                logger.info(f"Searching IMSLP for: {search_term}")
                
                # Use IMSLP's search
                search_url = f"https://imslp.org/wiki/Special:IMSLPSearch"
                params = {
                    'search': search_term,
                    'go': 'Go'
                }
                
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(search_url, params=params, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for search results
                result_links = soup.find_all('a', href=re.compile(r'/wiki/.*\(.*\)'))
                
                for link in result_links[:5]:  # Top 5 results
                    if link.get_text() and link.get('href'):
                        title_text = link.get_text().strip()
                        url = urljoin('https://imslp.org', link.get('href'))
                        
                        # Skip category pages and special pages
                        if ('Category:' not in title_text and 
                            'Special:' not in title_text and 
                            '(' in title_text and ')' in title_text):
                            
                            result = {
                                'title': title_text,
                                'url': url,
                                'search_term': search_term,
                                'confidence': self._calculate_confidence(composer, title, title_text)
                            }
                            search_results.append(result)
                
                if search_results:
                    break  # Found results, no need to try other terms
        
        except Exception as e:
            logger.error(f"Error searching IMSLP for {composer} - {title}: {e}")
        
        # Sort by confidence and return top results
        search_results.sort(key=lambda x: x['confidence'], reverse=True)
        return search_results[:3]  # Top 3 results
    
    def _calculate_confidence(self, original_composer: str, original_title: str, found_title: str) -> float:
        """Calculate confidence score for search results"""
        confidence = 0.0
        
        original_composer_lower = original_composer.lower()
        original_title_lower = original_title.lower()
        found_title_lower = found_title.lower()
        
        # Check composer match
        composer_words = original_composer_lower.split()
        for word in composer_words:
            if word in found_title_lower:
                confidence += 0.3
        
        # Check title match
        title_words = original_title_lower.split()
        for word in title_words:
            if len(word) > 2 and word in found_title_lower:  # Skip short words
                confidence += 0.2
        
        # Bonus for exact matches
        if original_title_lower in found_title_lower:
            confidence += 0.5
        
        # Check for common musical terms
        musical_terms = ['sonata', 'symphony', 'concerto', 'suite', 'prelude', 'fugue', 'variation']
        for term in musical_terms:
            if term in original_title_lower and term in found_title_lower:
                confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def validate_imslp_page(self, url: str) -> Dict:
        """Validate an IMSLP page and extract basic info"""
        try:
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for PDF links
            pdf_links = soup.find_all('span', class_='we_file_info2')
            pdf_count = len(pdf_links)
            
            # Get page title
            page_title = soup.find('h1', class_='firstHeading')
            title = page_title.get_text().strip() if page_title else "Unknown"
            
            return {
                'valid': True,
                'title': title,
                'pdf_count': pdf_count,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error validating {url}: {e}")
            return {
                'valid': False,
                'title': "Error",
                'pdf_count': 0,
                'url': url
            }
    
    def find_missing_scores(self, csv_file: str) -> Dict:
        """Main function to find missing scores"""
        unmapped_works = self.get_unmapped_works(csv_file)
        results = {
            'total_unmapped': len(unmapped_works),
            'found_works': [],
            'still_missing': [],
            'search_attempts': []
        }
        
        logger.info(f"Starting search for {len(unmapped_works)} unmapped works...")
        
        for i, work in enumerate(unmapped_works, 1):
            logger.info(f"\n=== Searching {i}/{len(unmapped_works)}: {work['original_composer']} - {work['original_title']} ===")
            
            search_results = self.imslp_search(work['original_composer'], work['original_title'])
            
            work_result = {
                'original_work': work,
                'search_results': [],
                'best_match': None
            }
            
            for result in search_results:
                # Validate the page
                page_info = self.validate_imslp_page(result['url'])
                
                if page_info['valid'] and page_info['pdf_count'] > 0:
                    validated_result = {**result, **page_info}
                    work_result['search_results'].append(validated_result)
                    
                    logger.info(f"✅ Found: {validated_result['title']} (Confidence: {validated_result['confidence']:.2f}, PDFs: {validated_result['pdf_count']})")
                    
                    # Set best match (highest confidence with PDFs)
                    if (work_result['best_match'] is None or 
                        validated_result['confidence'] > work_result['best_match']['confidence']):
                        work_result['best_match'] = validated_result
                else:
                    logger.info(f"❌ Invalid or no PDFs: {result['title']}")
            
            results['search_attempts'].append(work_result)
            
            if work_result['best_match']:
                results['found_works'].append(work_result)
                logger.info(f"🎯 BEST MATCH: {work_result['best_match']['title']}")
            else:
                results['still_missing'].append(work_result)
                logger.info(f"❌ No valid matches found")
            
            # Delay between searches
            time.sleep(random.uniform(3, 6))
        
        logger.info(f"\n=== SEARCH COMPLETE ===")
        logger.info(f"Found scores for: {len(results['found_works'])}/{len(unmapped_works)}")
        logger.info(f"Still missing: {len(results['still_missing'])}")
        
        return results
    
    def generate_missing_scores_report(self, results: Dict, output_file: str = "missing_scores_report.html") -> str:
        """Generate HTML report for missing scores search"""
        
        found_count = len(results['found_works'])
        still_missing_count = len(results['still_missing'])
        total_searched = results['total_unmapped']
        success_rate = (found_count / total_searched * 100) if total_searched > 0 else 0
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Missing Scores Search Report</title>
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
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 20px;
        }}
        .stats {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
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
        .work-section.found {{
            border-left: 5px solid #27ae60;
            background: linear-gradient(90deg, rgba(39, 174, 96, 0.1) 0%, rgba(255,255,255,1) 100%);
        }}
        .work-section.missing {{
            border-left: 5px solid #e74c3c;
            background: linear-gradient(90deg, rgba(231, 76, 60, 0.1) 0%, rgba(255,255,255,1) 100%);
        }}
        .original-work {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .best-match {{
            background: #d5f4e6;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            border: 2px solid #27ae60;
        }}
        .search-result {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 3px solid #3498db;
        }}
        .confidence-score {{
            display: inline-block;
            padding: 4px 8px;
            background: #3498db;
            color: white;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .imslp-link {{
            display: inline-block;
            margin: 10px 10px 10px 0;
            padding: 10px 20px;
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        .imslp-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
        }}
        .no-results {{
            color: #e74c3c;
            background: #fdf2f2;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
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
        <h1>🔍 Missing Scores Search Report</h1>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">{total_searched}</span>
                Unmapped Works Searched
            </div>
            <div class="stat-item">
                <span class="stat-number">{found_count}</span>
                New Scores Found
            </div>
            <div class="stat-item">
                <span class="stat-number">{success_rate:.1f}%</span>
                Search Success Rate
            </div>
            <div class="stat-item">
                <span class="stat-number">{still_missing_count}</span>
                Still Missing
            </div>
        </div>
'''
        
        # Found works section
        if results['found_works']:
            html_content += '''
        <h2>🎯 Newly Found Scores</h2>
'''
            for work_result in results['found_works']:
                work = work_result['original_work']
                best_match = work_result['best_match']
                
                html_content += f'''
        <div class="work-section found">
            <div class="original-work">
                <strong>Original CSV Entry #{work['csv_row']}:</strong><br>
                {work['original_composer']} - {work['original_title']}
            </div>
            
            <div class="best-match">
                <h4>🎯 Best Match Found:</h4>
                <strong>{best_match['title']}</strong><br>
                <span class="confidence-score">{best_match['confidence']:.1%} Match</span>
                PDFs Available: {best_match['pdf_count']}<br>
                <a href="{best_match['url']}" class="imslp-link" target="_blank">🔗 View on IMSLP</a>
            </div>
'''
                
                if len(work_result['search_results']) > 1:
                    html_content += '''
            <h4>Other Possible Matches:</h4>
'''
                    for result in work_result['search_results']:
                        if result != best_match:
                            html_content += f'''
            <div class="search-result">
                <strong>{result['title']}</strong><br>
                <span class="confidence-score">{result['confidence']:.1%} Match</span>
                PDFs: {result['pdf_count']}<br>
                <a href="{result['url']}" target="_blank">View on IMSLP</a>
            </div>
'''
                
                html_content += '''
        </div>
'''
        
        # Still missing section
        if results['still_missing']:
            html_content += '''
        <h2>❌ Still Missing Scores</h2>
'''
            for work_result in results['still_missing']:
                work = work_result['original_work']
                
                html_content += f'''
        <div class="work-section missing">
            <div class="original-work">
                <strong>CSV Entry #{work['csv_row']}:</strong><br>
                {work['original_composer']} - {work['original_title']}
            </div>
            
            <div class="no-results">
                ❌ No suitable matches found in IMSLP search<br><br>
                <strong>Possible reasons:</strong><br>
                • Work may not be in IMSLP database<br>
                • Title/composer formatting doesn't match IMSLP<br>
                • Work may be under a different composer or title<br><br>
                <strong>Suggestion:</strong> Try manual search on <a href="https://imslp.org" target="_blank">IMSLP.org</a>
            </div>
        </div>
'''
        
        html_content += f'''
        <div class="generated-info">
            <h3>📊 Search Summary</h3>
            <p><strong>Search Success:</strong> Found {found_count} out of {total_searched} previously unmapped works ({success_rate:.1f}%)</p>
            <p><strong>Method:</strong> Advanced IMSLP search with confidence scoring and validation</p>
            <p><strong>Total Coverage:</strong> Combined with original mappings, this significantly increases the available scores</p>
            <br>
            <p><em>Generated by Advanced Score Finder - {datetime.now().strftime("%Y-%m-%d %H:%M")}</em></p>
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
    
    print("=== Advanced Score Finder for Missing Works ===")
    print("🔍 This will search IMSLP for works that couldn't be mapped automatically")
    print()
    
    # Ask if user wants to proceed
    response = input("Start searching for missing scores? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Search cancelled.")
        return
    
    finder = AdvancedScoreFinder()
    
    try:
        results = finder.find_missing_scores(csv_file)
        output_file = finder.generate_missing_scores_report(results)
        
        print("\n" + "="*70)
        print("✅ MISSING SCORES SEARCH COMPLETED!")
        print("="*70)
        print(f"📁 Report: {output_file}")
        
        # Statistics
        total_searched = results['total_unmapped']
        found = len(results['found_works'])
        still_missing = len(results['still_missing'])
        
        print(f"\n📊 Search Results:")
        print(f"   • Works searched: {total_searched}")
        print(f"   • New scores found: {found}")
        print(f"   • Still missing: {still_missing}")
        print(f"   • Success rate: {found/total_searched*100:.1f}%")
        
        if found > 0:
            print(f"\n🎯 Found these works:")
            for work_result in results['found_works']:
                work = work_result['original_work']
                best_match = work_result['best_match']
                print(f"   • {work['original_composer']} - {work['original_title']}")
                print(f"     → {best_match['title']} ({best_match['confidence']:.1%} confidence)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()