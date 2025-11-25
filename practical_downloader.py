#!/usr/bin/env python3
"""
Practical IMSLP Downloader
Enhanced solution combining API metadata access with download capabilities
Designed for batch processing and future scalability
"""

import json
import logging
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from enhanced_imslp_api import IMSLPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IMSLPBatchDownloader:
    """Batch downloader for IMSLP scores with configuration support"""
    
    def __init__(self, config_path: str = "enhanced_config.json"):
        """Initialize with configuration file"""
        self.config = self._load_config(config_path)
        self.client = IMSLPClient()
        self.output_dir = Path(self.config['download_settings']['output_directory'])
        self.output_dir.mkdir(exist_ok=True)
        
        # Set logging level from config
        log_level = getattr(logging, self.config['download_settings']['log_level'])
        logging.getLogger().setLevel(log_level)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "download_settings": {
                "base_delay": 5,
                "max_delay": 15,
                "download_timeout": 60,
                "max_retries": 3,
                "output_directory": "downloads",
                "log_level": "INFO"
            },
            "batch_operations": {
                "search_composers": [],
                "specific_works": []
            },
            "filtering": {
                "preferred_formats": ["pdf"],
                "exclude_arrangements": False,
                "min_file_size_kb": 50,
                "max_file_size_mb": 100
            }
        }
    
    def process_specific_works(self) -> Dict:
        """Process specific works defined in configuration"""
        results = {
            'total_works': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'pdf_links_found': 0,
            'details': []
        }
        
        specific_works = self.config['batch_operations']['specific_works']
        enabled_works = [work for work in specific_works if work.get('enabled', True)]
        
        logger.info(f"Processing {len(enabled_works)} specific works...")
        
        for work in enabled_works:
            work_result = self._process_single_work(work)
            results['details'].append(work_result)
            results['total_works'] += 1
            results['pdf_links_found'] += work_result['pdf_links_found']
            results['successful_downloads'] += work_result['successful_downloads']
            results['failed_downloads'] += work_result['failed_downloads']
            
            # Delay between works
            delay = random.uniform(
                self.config['download_settings']['base_delay'],
                self.config['download_settings']['max_delay']
            )
            time.sleep(delay)
        
        return results
    
    def _process_single_work(self, work: Dict) -> Dict:
        """Process a single work (find PDFs and attempt downloads)"""
        result = {
            'composer': work['composer'],
            'title': work['title'],
            'url': work['url'],
            'pdf_links_found': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'pdf_files': []
        }
        
        logger.info(f"Processing: {work['title']} by {work['composer']}")
        
        try:
            # Get PDF links from the work page
            pdf_links = self.client.get_pdf_links_from_work(work['url'])
            result['pdf_links_found'] = len(pdf_links)
            
            if not pdf_links:
                logger.warning(f"No PDF links found for {work['title']}")
                return result
            
            # Create work-specific directory
            work_dir = self.output_dir / self._sanitize_filename(f"{work['composer']} - {work['title']}")
            work_dir.mkdir(exist_ok=True)
            
            # Process each PDF link
            for i, pdf_info in enumerate(pdf_links, 1):
                pdf_result = self._attempt_pdf_download(pdf_info, work_dir, work['title'], i)
                result['pdf_files'].append(pdf_result)
                
                if pdf_result['success']:
                    result['successful_downloads'] += 1
                else:
                    result['failed_downloads'] += 1
                
                # Delay between downloads
                if i < len(pdf_links):  # Don't delay after the last file
                    delay = random.uniform(3, 8)
                    time.sleep(delay)
        
        except Exception as e:
            logger.error(f"Error processing work {work['title']}: {e}")
            result['failed_downloads'] = 1
        
        return result
    
    def _attempt_pdf_download(self, pdf_info: Dict, work_dir: Path, work_title: str, file_number: int) -> Dict:
        """Attempt to download a single PDF file"""
        result = {
            'title': pdf_info['title'],
            'url': pdf_info['download_url'],
            'success': False,
            'filename': None,
            'error': None
        }
        
        try:
            # Create filename
            filename = self._sanitize_filename(f"{file_number:02d}_{pdf_info['title']}.pdf")
            filepath = work_dir / filename
            
            # Skip if file already exists
            if filepath.exists():
                logger.info(f"File already exists: {filename}")
                result['success'] = True
                result['filename'] = str(filepath)
                return result
            
            # Attempt download
            logger.info(f"Attempting download: {pdf_info['title']}")
            success = self.client.download_with_browser_simulation(
                pdf_info['download_url'], 
                str(filepath), 
                work_title
            )
            
            if success and filepath.exists():
                result['success'] = True
                result['filename'] = str(filepath)
                logger.info(f"✅ Downloaded: {filename}")
            else:
                result['error'] = "Download failed - anti-bot protection likely blocked request"
                logger.warning(f"❌ Download failed: {pdf_info['title']}")
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error downloading {pdf_info['title']}: {e}")
        
        return result
    
    def search_and_download_by_composer(self, composer_name: str, limit: int = 10) -> Dict:
        """Search for works by composer and download them"""
        logger.info(f"Searching for {limit} works by {composer_name}...")
        
        try:
            works = self.client.search_composer_works(composer_name)
            
            if not works:
                logger.warning(f"No works found for {composer_name}")
                return {'error': f'No works found for {composer_name}'}
            
            # Limit results
            works = works[:limit]
            
            # Process each work
            results = []
            for work in works:
                # Convert API work format to our format
                work_config = {
                    'composer': work['composer'],
                    'title': work['title'],
                    'url': work['links']['work'],
                    'enabled': True
                }
                
                work_result = self._process_single_work(work_config)
                results.append(work_result)
                
                # Delay between works
                delay = random.uniform(
                    self.config['download_settings']['base_delay'],
                    self.config['download_settings']['max_delay']
                )
                time.sleep(delay)
            
            return {
                'composer': composer_name,
                'works_processed': len(results),
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Error searching for {composer_name}: {e}")
            return {'error': str(e)}
    
    def generate_report(self, results: Dict) -> str:
        """Generate a summary report of download results"""
        report = []
        report.append("=== IMSLP Download Report ===\n")
        
        if 'total_works' in results:
            # Specific works report
            report.append(f"Total Works Processed: {results['total_works']}")
            report.append(f"PDF Links Found: {results['pdf_links_found']}")
            report.append(f"Successful Downloads: {results['successful_downloads']}")
            report.append(f"Failed Downloads: {results['failed_downloads']}")
            
            if results['total_works'] > 0:
                success_rate = (results['successful_downloads'] / results['pdf_links_found']) * 100 if results['pdf_links_found'] > 0 else 0
                report.append(f"Success Rate: {success_rate:.1f}%")
            
            report.append("\nDetails by Work:")
            for detail in results['details']:
                report.append(f"\n• {detail['title']} by {detail['composer']}")
                report.append(f"  PDF Links Found: {detail['pdf_links_found']}")
                report.append(f"  Successful Downloads: {detail['successful_downloads']}")
                report.append(f"  Failed Downloads: {detail['failed_downloads']}")
        
        report.append(f"\nFiles saved to: {self.output_dir.absolute()}")
        report.append("\nNote: Download failures are typically due to IMSLP's anti-bot protection.")
        report.append("Consider manual download for failed files or using browser automation.")
        
        return "\n".join(report)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows compatibility"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:195] + ('.' + ext if ext else '')
        
        return filename.strip()


def main():
    """Main execution function"""
    downloader = IMSLPBatchDownloader()
    
    print("=== IMSLP Batch Downloader ===\n")
    
    # Process specific works from configuration
    results = downloader.process_specific_works()
    
    # Generate and display report
    report = downloader.generate_report(results)
    print(report)
    
    # Save report to file
    report_file = downloader.output_dir / "download_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Offer additional options
    print("\n=== Additional Options ===")
    print("1. To add more works, edit 'enhanced_config.json'")
    print("2. To search by composer, modify the 'search_composers' section")
    print("3. For better download success, consider using browser automation")
    print("4. Manual download may be necessary for files blocked by anti-bot protection")


if __name__ == "__main__":
    main()