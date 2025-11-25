#!/usr/bin/env python3
"""
Enhanced IMSLP API - Python version inspired by josefleventon/imslp-api
Combines official API access with PDF download capabilities
Handles anti-bot protection through multiple strategies
"""

import requests
import time
import json
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import random
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IMSLPClient:
    """Enhanced IMSLP client for metadata and downloads"""
    
    def __init__(self):
        self.api_base = "https://imslp.org/imslpscripts/API.ISCR.php"
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
    
    def get_composers(self, start: int = 0, amount: int = 10) -> List[Dict]:
        """
        Get list of composers from IMSLP API
        
        Args:
            start: Starting index
            amount: Number of composers to retrieve
            
        Returns:
            List of composer dictionaries with id, name, and link
        """
        composers = []
        
        for i in range(amount):
            try:
                params = {
                    'account': 'worklist',
                    'disclaimer': 'accepted',
                    'sort': 'id',
                    'type': '1',  # Type 1 = composers
                    'start': start + i,
                    'retformat': 'json'
                }
                
                response = self.session.get(self.api_base, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data and len(data) > 0:
                    composer_data = data[0]
                    composer = {
                        'id': composer_data['id'],
                        'name': composer_data['id'].replace('Category:', ''),
                        'link': composer_data['permlink']
                    }
                    composers.append(composer)
                    logger.info(f"Retrieved composer: {composer['name']}")
                
                # Respectful delay
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error retrieving composer at index {start + i}: {e}")
                continue
        
        return composers
    
    def get_works(self, start: int = 0, amount: int = 10) -> List[Dict]:
        """
        Get list of works from IMSLP API
        
        Args:
            start: Starting index
            amount: Number of works to retrieve
            
        Returns:
            List of work dictionaries with id, composer, title, and links
        """
        works = []
        
        try:
            params = {
                'account': 'worklist',
                'disclaimer': 'accepted',
                'sort': 'id',
                'type': '2',  # Type 2 = works
                'start': start,
                'retformat': 'json'
            }
            
            response = self.session.get(self.api_base, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for i in range(min(amount, len(data))):
                try:
                    work_data = data[i]
                    work = {
                        'id': work_data['id'],
                        'composer': work_data['intvals']['composer'],
                        'title': work_data['intvals']['worktitle'],
                        'links': {
                            'work': work_data['permlink'],
                            'composer': f"https://imslp.org/wiki/{work_data['parent']}".replace(' ', '_')
                        }
                    }
                    works.append(work)
                    logger.info(f"Retrieved work: {work['title']} by {work['composer']}")
                    
                except KeyError as e:
                    logger.warning(f"Missing data in work entry {i}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error retrieving works: {e}")
        
        return works
    
    def search_composer_works(self, composer_name: str) -> List[Dict]:
        """
        Search for works by a specific composer
        
        Args:
            composer_name: Name of the composer to search for
            
        Returns:
            List of works by that composer
        """
        # This is a simple implementation - could be enhanced with better search
        works = []
        start = 0
        batch_size = 50
        max_batches = 20  # Limit search to avoid excessive API calls
        
        logger.info(f"Searching for works by {composer_name}...")
        
        for batch in range(max_batches):
            batch_works = self.get_works(start=start, amount=batch_size)
            
            if not batch_works:
                break
            
            # Filter works by composer
            matching_works = [
                work for work in batch_works 
                if composer_name.lower() in work['composer'].lower()
            ]
            
            works.extend(matching_works)
            
            if len(matching_works) > 0:
                logger.info(f"Found {len(matching_works)} works in batch {batch + 1}")
            
            start += batch_size
            time.sleep(1)  # Respectful delay between batches
        
        logger.info(f"Total works found for {composer_name}: {len(works)}")
        return works
    
    def get_pdf_links_from_work(self, work_url: str) -> List[Dict]:
        """
        Extract PDF download links from a work page
        
        Args:
            work_url: URL of the IMSLP work page
            
        Returns:
            List of PDF link dictionaries with title and download_url
        """
        pdf_links = []
        
        try:
            # Add delay and headers to appear more human-like
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
                        pdf_info = {
                            'title': link.get_text(strip=True),
                            'download_url': urljoin('https://imslp.org', href)
                        }
                        pdf_links.append(pdf_info)
            
            logger.info(f"Found {len(pdf_links)} PDF links on {work_url}")
            
        except Exception as e:
            logger.error(f"Error extracting PDF links from {work_url}: {e}")
        
        return pdf_links
    
    def download_with_browser_simulation(self, url: str, filename: str, work_title: str = "") -> bool:
        """
        Attempt to download a PDF with browser simulation to avoid anti-bot detection
        
        Args:
            url: Download URL
            filename: Local filename to save as
            work_title: Title of the work (for logging)
            
        Returns:
            True if download successful, False otherwise
        """
        strategies = [
            self._download_direct,
            self._download_with_referrer,
            self._download_with_session_warmup,
            self._download_slow_request
        ]
        
        for i, strategy in enumerate(strategies, 1):
            logger.info(f"Attempting download strategy {i} for {work_title}")
            
            if strategy(url, filename):
                logger.info(f"✅ Successfully downloaded {filename}")
                return True
            
            # Progressive delay between strategies
            time.sleep(i * 3)
        
        logger.error(f"❌ All download strategies failed for {work_title}")
        return False
    
    def _download_direct(self, url: str, filename: str) -> bool:
        """Direct download attempt"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if self._is_valid_pdf_response(response):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            
        except Exception as e:
            logger.debug(f"Direct download failed: {e}")
        
        return False
    
    def _download_with_referrer(self, url: str, filename: str) -> bool:
        """Download with referrer header"""
        try:
            headers = {
                'Referer': 'https://imslp.org/',
                'Accept': 'application/pdf,*/*'
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if self._is_valid_pdf_response(response):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            
        except Exception as e:
            logger.debug(f"Referrer download failed: {e}")
        
        return False
    
    def _download_with_session_warmup(self, url: str, filename: str) -> bool:
        """Download after warming up the session"""
        try:
            # Warm up session with main page visit
            self.session.get('https://imslp.org/')
            time.sleep(2)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if self._is_valid_pdf_response(response):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            
        except Exception as e:
            logger.debug(f"Session warmup download failed: {e}")
        
        return False
    
    def _download_slow_request(self, url: str, filename: str) -> bool:
        """Very slow download with extended delays"""
        try:
            time.sleep(random.uniform(10, 15))
            
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            if self._is_valid_pdf_response(response):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            
        except Exception as e:
            logger.debug(f"Slow request download failed: {e}")
        
        return False
    
    def _is_valid_pdf_response(self, response: requests.Response) -> bool:
        """Check if response contains a valid PDF"""
        content_type = response.headers.get('content-type', '').lower()
        
        # Check for HTML responses (CAPTCHA pages)
        if 'text/html' in content_type:
            logger.warning("Received HTML page instead of PDF (likely CAPTCHA)")
            return False
        
        # Check for PDF content type
        if 'application/pdf' in content_type:
            return True
        
        # Check content size (HTML CAPTCHA pages are typically small)
        if len(response.content) < 5000:  # Less than 5KB is suspicious for a PDF
            logger.warning(f"Response too small ({len(response.content)} bytes) for PDF")
            return False
        
        # Check for PDF magic bytes
        if response.content.startswith(b'%PDF'):
            return True
        
        logger.warning("Response doesn't appear to be a valid PDF")
        return False


def main():
    """Example usage of the enhanced IMSLP client"""
    client = IMSLPClient()
    
    print("=== Enhanced IMSLP API Demo ===\n")
    
    # Example 1: Get some composers
    print("1. Getting composers...")
    composers = client.get_composers(start=0, amount=3)
    for composer in composers:
        print(f"   - {composer['name']}: {composer['link']}")
    
    print()
    
    # Example 2: Get some works
    print("2. Getting works...")
    works = client.get_works(start=0, amount=3)
    for work in works:
        print(f"   - '{work['title']}' by {work['composer']}")
        print(f"     URL: {work['links']['work']}")
    
    print()
    
    # Example 3: Search for Bach works
    print("3. Searching for Bach works...")
    bach_works = client.search_composer_works("Bach")
    print(f"   Found {len(bach_works)} works by Bach")
    
    if bach_works:
        example_work = bach_works[0]
        print(f"   Example: '{example_work['title']}'")
        
        # Example 4: Get PDF links for a work
        print("4. Getting PDF links for the example work...")
        pdf_links = client.get_pdf_links_from_work(example_work['links']['work'])
        print(f"   Found {len(pdf_links)} PDF files")
        
        if pdf_links:
            print("   Sample PDF links:")
            for pdf in pdf_links[:3]:  # Show first 3
                print(f"     - {pdf['title']}")
                print(f"       URL: {pdf['download_url']}")


if __name__ == "__main__":
    main()