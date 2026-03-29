#!/usr/bin/env python3
"""
Scrape Glottolog pages to get extinction status for all languages.
Creates a JSON cache file to avoid re-scraping.
"""

import requests
import json
import csv
import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

CACHE_FILE = 'extinction_cache.json'
CSV_FILE = 'languoid.csv'
BASE_URL = 'https://glottolog.org/resource/languoid/id'
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 0.0  # No per-thread delay; let ThreadPoolExecutor manage concurrency
MAX_WORKERS = 20  # Number of concurrent requests
lock = threading.Lock()  # For thread-safe cache updates

def load_cache():
    """Load existing extinction cache if it exists."""
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save extinction cache to file."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)
    print(f"Cache saved with {len(cache)} entries")

def parse_extinction_status(html):
    """Extract AES status from Glottolog page HTML."""
    try:
        # Look for the AES status field
        match = re.search(
            r'<dt>AES status:</dt>\s*<dd>([^<]+)</dd>',
            html,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            status = match.group(1).strip()
            return status.lower()
    except Exception as e:
        print(f"Error parsing HTML: {e}")
    
    return None

def scrape_language_status(lang_id):
    """Fetch and parse a single language's status from Glottolog."""
    url = f'{BASE_URL}/{lang_id}'
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            status = parse_extinction_status(response.text)
            return (lang_id, status)
        elif response.status_code == 404:
            return (lang_id, None)
        else:
            return (lang_id, None)
    except requests.Timeout:
        return (lang_id, None)
    except Exception as e:
        return (lang_id, None)

def scrape_with_threading(to_fetch, cache, progress_interval=100):
    """Scrape using ThreadPoolExecutor for parallel requests."""
    extinct_count = 0
    active_count = 0
    unknown_count = 0
    processed = 0
    
    print(f"Starting parallel scrape with {MAX_WORKERS} workers...")
    print(f"Estimated time: ~{len(to_fetch) / (MAX_WORKERS * 20):.1f} minutes")
    print()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {executor.submit(scrape_language_status, lid): lid for lid in to_fetch}
        
        # Process completed tasks as they finish
        for future in as_completed(futures):
            lang_id, status = future.result()
            
            with lock:
                cache[lang_id] = status
                processed += 1
                
                if status == 'extinct':
                    extinct_count += 1
                elif status and status != 'extinct':
                    active_count += 1
                else:
                    unknown_count += 1
                
                # Progress indicator
                if processed % progress_interval == 0:
                    pct = 100 * processed / len(to_fetch)
                    print(f"  [{processed}/{len(to_fetch)} ({pct:.1f}%)] Extinct: {extinct_count}, Active: {active_count}, Unknown: {unknown_count}")
            
            # No per-thread rate limiting; let concurrent requests flow
    
    return extinct_count, active_count, unknown_count

def get_unique_languoid_ids():
    """Extract unique languoid IDs from CSV."""
    ids = set()
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.add(row['id'])
    return sorted(ids)

def main():
    print("Scraping Glottolog extinction status...")
    print(f"CSV File: {CSV_FILE}")
    print(f"Cache File: {CACHE_FILE}")
    print(f"Base URL: {BASE_URL}")
    print(f"Parallel workers: {MAX_WORKERS}")
    print()
    
    # Load existing cache
    cache = load_cache()
    print(f"Loaded cache with {len(cache)} existing entries")
    
    # Get all unique IDs from CSV
    all_ids = get_unique_languoid_ids()
    print(f"Total unique languoid IDs: {len(all_ids)}")
    
    # Determine what needs to be fetched
    to_fetch = [lid for lid in all_ids if lid not in cache]
    print(f"Need to fetch: {len(to_fetch)}")
    print()
    
    if not to_fetch:
        print("All entries already cached!")
        return
    
    # Scrape with threading
    extinct_count, active_count, unknown_count = scrape_with_threading(to_fetch, cache)
    
    # Save cache
    print()
    save_cache(cache)
    
    # Statistics
    print("\nExtinction Status Summary:")
    print("-" * 40)
    extinct_list = [k for k, v in cache.items() if v == 'extinct']
    print(f"Extinct languages: {len(extinct_list)}")
    
    statuses = set(v for v in cache.values() if v)
    print(f"Found statuses: {sorted(statuses)}")
    
    print(f"Total cached: {len(cache)}")
    print(f"Still unknown: {sum(1 for v in cache.values() if v is None)}")
    
    # Show some examples
    print("\nExample extinct languages:")
    for lang_id in extinct_list[:10]:
        print(f"  {lang_id}")

if __name__ == '__main__':
    main()
