#!/usr/bin/env python3
"""
Monitor the extinction scraper and proceed to integration when complete.
"""

import json
import time
import os
from pathlib import Path

CACHE_FILE = 'extinction_cache.json'
CSV_FILE = 'languoid.csv'

def count_cache_entries():
    """Count entries in the cache."""
    if not Path(CACHE_FILE).exists():
        return 0
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            return len(data)
    except:
        return 0

def count_csv_entries():
    """Count total entries needed."""
    import csv
    count = 0
    with open(CSV_FILE, 'r') as f:
        count = sum(1 for _ in csv.DictReader(f))
    return count

def get_extinct_count():
    """Count extinct entries in cache."""
    if not Path(CACHE_FILE).exists():
        return 0
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            return sum(1 for v in data.values() if v == 'extinct')
    except:
        return 0

print("Monitoring extinction scraper...")
print("=" * 60)

total_needed = count_csv_entries()
print(f"Total languoids to scrape: {total_needed}")
print()

# Monitor until complete
check_interval = 60  # seconds
last_count = 0

while True:
    current_count = count_cache_entries()
    extinct_count = get_extinct_count()
    pct = 100 * current_count / total_needed if total_needed > 0 else 0
    
    if current_count > last_count:
        rate = (current_count - last_count) / check_interval * 60  # per minute
        remaining = (total_needed - current_count) / rate if rate > 0 else 0
        print(f"[{current_count}/{total_needed} ({pct:.1f}%)] Extinct: {extinct_count} | Rate: {rate:.0f}/min | ETA: {remaining/60:.1f} hours")
        last_count = current_count
    
    if current_count >= total_needed and current_count > 0:
        print()
        print("Scraping complete!")
        print(f"  Total cached: {current_count}")
        print(f"  Extinct: {extinct_count}")
        break
    
    time.sleep(check_interval)
