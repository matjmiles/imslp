#!/usr/bin/env python3
"""
Simple test script to diagnose CSV processing issues
"""

import csv
import requests
from pathlib import Path

def test_csv_reading():
    """Test reading the CSV file"""
    csv_file = "Form Anthology - Sheet1.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file '{csv_file}' not found!")
        return []
    
    works = []
    print("📋 Reading CSV file...")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            f.seek(0)
            
            csv_reader = csv.reader(f)
            
            # Skip empty first row if present
            if first_line == ',':
                next(csv_reader)
                print("Skipped empty first row")
            
            for row_num, row in enumerate(csv_reader, 1):
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    composer = row[0].strip()
                    title = row[1].strip()
                    
                    work = {
                        'composer': composer,
                        'title': title,
                        'csv_row': row_num
                    }
                    works.append(work)
                    print(f"Row {row_num}: {composer} - {title}")
        
        print(f"\n✅ Successfully read {len(works)} works from CSV")
        return works
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def test_url_construction():
    """Test URL construction for a few sample works"""
    
    # Test cases - some should work, some won't
    test_works = [
        ("Bach, Johann Sebastian", "French Suite No.6, BWV 817"),
        ("Mozart, Wolfgang Amadeus", "Symphony No.40, K.550"), 
        ("Beethoven, Ludwig van", "Piano Sonata No.8, Op.13"),
        ("Schubert, Franz", "Kennst du das Land"),  # This is a song, not typical IMSLP format
        ("Bach, Johann Sebastian", "Cello Suite No.3, BWV 1009")  # Should work
    ]
    
    print("\n🔗 Testing URL construction...")
    
    for composer, title in test_works:
        # Format for IMSLP URL
        composer_url = composer.replace(', ', '_').replace(' ', '_')
        title_url = title.replace(' ', '_').replace(',', ',_').replace('.', '')
        
        test_url = f"https://imslp.org/wiki/{title_url}_({composer_url})"
        print(f"\n🎵 {composer} - {title}")
        print(f"   URL: {test_url}")
        
        # Test if URL exists
        try:
            response = requests.head(test_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ URL exists!")
            else:
                print(f"   ❌ URL returns {response.status_code}")
        except Exception as e:
            print(f"   ❌ URL test failed: {e}")

def analyze_csv_issues():
    """Analyze why the CSV entries might be failing"""
    
    works = test_csv_reading()
    
    print("\n🔍 Analyzing potential issues...")
    
    movement_keywords = ['mvt', 'movement', 'mvt.', 'movement', 'all movements']
    partial_keywords = ['gavottes', 'courante', 'bouree', 'minuet']
    
    issues = {
        'movements': [],
        'partials': [],
        'songs': [],
        'unclear': []
    }
    
    for work in works[:10]:  # Check first 10
        title_lower = work['title'].lower()
        
        if any(keyword in title_lower for keyword in movement_keywords):
            issues['movements'].append(work)
        elif any(keyword in title_lower for keyword in partial_keywords):
            issues['partials'].append(work)
        elif 'kennst du das land' in title_lower:  # Known song
            issues['songs'].append(work)
        else:
            issues['unclear'].append(work)
    
    print(f"\n📊 Issue Analysis:")
    print(f"   🎼 Movement-specific entries: {len(issues['movements'])}")
    print(f"   🎵 Partial/dance movements: {len(issues['partials'])}")
    print(f"   🎤 Songs/Lieder: {len(issues['songs'])}")
    print(f"   ❓ Unclear/might work: {len(issues['unclear'])}")
    
    if issues['movements']:
        print(f"\n❌ Movement entries (likely to fail):")
        for work in issues['movements'][:3]:
            print(f"      • {work['composer']} - {work['title']}")
    
    if issues['unclear']:
        print(f"\n✅ Entries that might work:")
        for work in issues['unclear'][:3]:
            print(f"      • {work['composer']} - {work['title']}")

def main():
    print("=== CSV Processing Diagnostic ===\n")
    
    # Step 1: Test CSV reading
    works = test_csv_reading()
    
    if not works:
        return
    
    # Step 2: Analyze issues
    analyze_csv_issues()
    
    # Step 3: Test URL construction
    test_url_construction()
    
    print(f"\n💡 Key Issues Identified:")
    print(f"   1. Many entries are specific movements, not complete works")
    print(f"   2. IMSLP typically catalogs complete compositions, not individual movements")
    print(f"   3. Some titles use abbreviations that don't match IMSLP format")
    print(f"   4. Songs/Lieder may have different catalog structures")
    
    print(f"\n🛠️  Possible Solutions:")
    print(f"   1. Map movement entries to their parent works")
    print(f"   2. Create a lookup table for common abbreviations")
    print(f"   3. Use IMSLP's search API instead of direct URL construction")
    print(f"   4. Manual curation of the CSV for better matching")

if __name__ == "__main__":
    main()