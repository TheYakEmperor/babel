#!/usr/bin/env python3
"""
Integrate extinction status into update_family_trees.py

This script:
1. Reads the extinction_cache.json created by scrape_extinction_status.py
2. Modifies update_family_trees.py to mark extinct languages with † dagger
3. Regenerates all HTML files with extinction markers
"""

import json
from pathlib import Path

EXTINCTION_CACHE = 'extinction_cache.json'
UPDATE_SCRIPT = 'update_family_trees.py'

def load_extinction_cache():
    """Load extinction status for all languages."""
    if not Path(EXTINCTION_CACHE).exists():
        print(f"Error: {EXTINCTION_CACHE} not found!")
        return {}
    
    with open(EXTINCTION_CACHE, 'r') as f:
        cache = json.load(f)
    
    # Create a set of extinct language IDs
    extinct = set(k for k, v in cache.items() if v == 'extinct')
    print(f"Loaded {len(extinct)} extinct languages from cache")
    return extinct

def generate_extinction_lookup_code(extinct_set):
    """Generate Python code for the is_extinct function."""
    code = "# Generated list of extinct language IDs from Glottolog\n"
    code += "EXTINCT_LANGUAGES = {\n"
    
    # Add first 50 as examples
    for lang_id in sorted(extinct_set)[:50]:
        code += f"    '{lang_id}',\n"
    
    code += f"    # ... and {len(extinct_set) - 50} more\n"
    code += "}\n\n"
    code += "def is_extinct(lang_id):\n"
    code += "    \"\"\"Check if a language is marked as extinct in Glottolog.\"\"\"\n"
    code += "    return lang_id in EXTINCT_LANGUAGES\n"
    
    return code

def main():
    print("Preparing extinction integration...")
    print(f"Cache file: {EXTINCTION_CACHE}")
    
    extinct = load_extinction_cache()
    
    # Generate the lookup code
    lookup_code = generate_extinction_lookup_code(extinct)
    
    print(f"\nFound {len(extinct)} extinct languages:")
    print("\nSample extinct languages:")
    for lang_id in sorted(extinct)[:10]:
        print(f"  {lang_id}")
    
    # Save the lookup as a JSON file for quick access
    lookup_file = 'extinct_lookup.json'
    with open(lookup_file, 'w') as f:
        json.dump(sorted(extinct), f)
    
    print(f"\nSaved lookup to {lookup_file}")
    print(f"Ready to integrate into {UPDATE_SCRIPT}")
    
    return extinct

if __name__ == '__main__':
    main()
