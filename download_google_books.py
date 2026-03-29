#!/usr/bin/env python3
"""
Download pages from Google Books as JPG images.
Usage: python3 download_google_books.py
"""

import os
import time
import urllib.request
import urllib.error
import ssl

# Bypass SSL certificate verification (needed on some macOS systems)
ssl._create_default_https_context = ssl._create_unverified_context

# Book ID from URL: https://books.google.de/books?id=AhzQ9R8ZjvEC
BOOK_ID = "AhzQ9R8ZjvEC"
OUTPUT_DIR = "texts/00/00/luther-juden-1543/images"
TOTAL_PAGES = 286  # From the book info
ZOOM = 3  # Higher zoom = better quality (1-3)
WIDTH = 1280  # Image width

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_page_id(page_num):
    """Convert page number to Google Books page ID."""
    if page_num == 1:
        return "PP1"
    elif page_num == 2:
        return "PP2"
    elif page_num <= 10:
        return f"PR{page_num - 2}"
    else:
        return f"PA{page_num - 10}"

def download_page(page_num, retries=3):
    """Download a single page from Google Books."""
    page_id = get_page_id(page_num)
    
    # Google Books image URL format
    url = f"https://books.google.de/books/content?id={BOOK_ID}&pg={page_id}&img=1&zoom={ZOOM}&w={WIDTH}"
    
    output_file = os.path.join(OUTPUT_DIR, f"{page_num:04d}.jpg")
    
    if os.path.exists(output_file):
        print(f"  Page {page_num} already exists, skipping")
        return True
    
    for attempt in range(retries):
        try:
            # Add headers to look like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'https://books.google.de/books?id={BOOK_ID}',
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
                # Check if we got actual image data
                if len(content) < 1000:
                    print(f"  Page {page_num}: Got small response ({len(content)} bytes), may be blocked")
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return False
                
                with open(output_file, 'wb') as f:
                    f.write(content)
                
                print(f"  Page {page_num}: Downloaded ({len(content)} bytes)")
                return True
                
        except urllib.error.HTTPError as e:
            print(f"  Page {page_num}: HTTP Error {e.code}")
            if attempt < retries - 1:
                time.sleep(2)
        except urllib.error.URLError as e:
            print(f"  Page {page_num}: URL Error - {e.reason}")
            if attempt < retries - 1:
                time.sleep(2)
        except Exception as e:
            print(f"  Page {page_num}: Error - {e}")
            if attempt < retries - 1:
                time.sleep(2)
    
    return False

def main():
    print("=" * 60)
    print("Google Books Downloader")
    print("=" * 60)
    print(f"Book ID: {BOOK_ID}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Pages: {TOTAL_PAGES}")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for page_num in range(1, TOTAL_PAGES + 1):
        if download_page(page_num):
            success += 1
        else:
            failed += 1
        
        # Be nice to Google's servers
        time.sleep(0.5)
    
    print("=" * 60)
    print(f"Done! Success: {success}, Failed: {failed}")
    print(f"Images saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
