#!/usr/bin/env python3
"""
Index all text content (OCR, transcriptions, annotations) for word search.
Creates content-index.js which can be used for full-text search.
"""

import os
import json
import re
import html
from pathlib import Path

TEXTS_DIR = Path(__file__).parent / "texts"
OUTPUT_FILE = Path(__file__).parent / "content-index.js"

def clean_text(text):
    """Clean text for indexing - remove HTML tags, normalize whitespace."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_info(text_dir):
    """Extract all searchable text from a text directory."""
    info = {
        "id": text_dir.name,
        "path": str(text_dir.relative_to(TEXTS_DIR.parent)),
        "content": [],
        "works": []
    }
    
    # Get text title, works, and transcriptions from data.json first (preferred)
    data_json = text_dir / "data.json"
    if data_json.exists():
        try:
            with open(data_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("title"):
                    info["title"] = data["title"]
                # Extract unique works from pages
                works_seen = set()
                for page in data.get("pages", []):
                    for work in page.get("works", []):
                        work_id = work.get("id", "")
                        work_title = work.get("title", work_id)
                        if work_id and work_id not in works_seen:
                            works_seen.add(work_id)
                            info["works"].append({"id": work_id, "title": work_title})
                    # Extract transcription text from page regions
                    page_label = page.get("label", page.get("id", ""))
                    for region in page.get("regions", []):
                        region_text = region.get("text", "")
                        if region_text:
                            region_title = region.get("title", "")
                            work_id = region.get("workId", "")
                            info["content"].append({
                                "type": "transcription",
                                "page": str(page_label),
                                "title": region_title,
                                "workId": work_id,
                                "text": clean_text(region_text)
                            })
        except Exception as e:
            print(f"  Error reading {data_json}: {e}")
    
    # Fallback: try index.html
    if "title" not in info:
        index_html = text_dir / "index.html"
        if index_html.exists():
            try:
                with open(index_html, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    # Extract title from <title> tag
                    title_match = re.search(r'<title>([^<]+)</title>', html_content)
                    if title_match:
                        title = clean_text(title_match.group(1))
                        # Remove " - Babel Archive" suffix if present
                        title = re.sub(r'\s*[-–]\s*Babel Archive$', '', title)
                        if title and title != "Loading...":
                            info["title"] = title
            except Exception as e:
                print(f"  Error reading {index_html}: {e}")
    
    # Get OCR text from images.json
    images_json = text_dir / "images.json"
    if images_json.exists():
        try:
            with open(images_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                images = data.get("images", [])
                for img in images:
                    if isinstance(img, dict):
                        ocr_text = img.get("ocrText", "")
                        if ocr_text:
                            label = img.get("label", "")
                            info["content"].append({
                                "type": "ocr",
                                "page": label,
                                "text": clean_text(ocr_text)
                            })
        except Exception as e:
            print(f"  Error reading {images_json}: {e}")
    
    # Check for separate OCR files
    ocr_dir = text_dir / "ocr"
    if ocr_dir.exists():
        for ocr_file in sorted(ocr_dir.glob("*.json")):
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ocr_text = data.get("ocrText", "")
                    if ocr_text:
                        label = ocr_file.stem  # e.g., "001"
                        info["content"].append({
                            "type": "ocr",
                            "page": label,
                            "text": clean_text(ocr_text)
                        })
            except Exception as e:
                print(f"  Error reading {ocr_file}: {e}")
    
    # Get transcriptions from pages.json
    pages_json = text_dir / "pages.json"
    if pages_json.exists():
        try:
            with open(pages_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pages = data.get("pages", {})
                for page_label, page_data in pages.items():
                    regions = page_data.get("regions", [])
                    for region in regions:
                        transcription = region.get("transcription", "")
                        if transcription:
                            region_title = region.get("title", "")
                            info["content"].append({
                                "type": "transcription",
                                "page": page_label,
                                "title": region_title,
                                "text": clean_text(transcription)
                            })
        except Exception as e:
            print(f"  Error reading {pages_json}: {e}")
    
    return info if info["content"] else None

def main():
    print("Indexing text content for word search...")
    
    content_index = []
    
    # Walk through all text directories
    for root, dirs, files in os.walk(TEXTS_DIR):
        root_path = Path(root)
        
        # Check if this is a text directory (has index.html or images.json)
        if "index.html" in files or "images.json" in files:
            print(f"Processing: {root_path.relative_to(TEXTS_DIR)}")
            
            info = extract_text_info(root_path)
            if info:
                content_index.append(info)
    
    print(f"\nIndexed {len(content_index)} texts with searchable content")
    
    # Calculate stats
    total_ocr = sum(1 for t in content_index for c in t["content"] if c["type"] == "ocr")
    total_trans = sum(1 for t in content_index for c in t["content"] if c["type"] == "transcription")
    print(f"  OCR pages: {total_ocr}")
    print(f"  Transcriptions: {total_trans}")
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated content index for word search\n")
        f.write("// Generated by index_content.py\n")
        f.write("const CONTENT_INDEX = ")
        json.dump(content_index, f, ensure_ascii=False)
        f.write(";\n")
    
    print(f"\nWritten to {OUTPUT_FILE}")
    
    # Show file size
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"Index size: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
