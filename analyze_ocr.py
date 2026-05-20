import json
import os
import glob

def analyze_dir(path):
    print(f"--- Analyzing: {path} ---")
    ocr_dir = os.path.join(path, "ocr")
    ocr_files = glob.glob(os.path.join(ocr_dir, "*.json"))
    total_ocr = len(ocr_files)
    
    missing_ocr_text = 0
    missing_text_layer = 0
    empty_text_layer = 0
    invalid_spans = []
    
    for fpath in sorted(ocr_files):
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            if "textLayer" in data:
                tl = data["textLayer"]
                if isinstance(tl, list):
                    for i, span in enumerate(tl):
                        for key in ['x', 'y', 'w', 'h']:
                            val = span.get(key)
                            if not isinstance(val, (int, float)):
                                invalid_spans.append((os.path.basename(fpath), i, key, val, "not numeric"))
                            elif val < 0 or val > 10000:
                                invalid_spans.append((os.path.basename(fpath), i, key, val, "out of range"))
        except Exception: pass

    print(f"Total OCR files: {total_ocr}")
    print(f"Invalid spans found (negative or >10000): {len(invalid_spans)}")
    if invalid_spans: print(f"Sample invalid: {invalid_spans[0]}")
    print()

analyze_dir("texts/00/00/ufo-magazine-uk-feb-2004")
analyze_dir("texts/00/00/ufo-magazine-us-154")
