#!/usr/bin/env python3
"""
Admin server for Babel - handles creating texts, works, and authors directly on disk.
Run this instead of the regular http.server when you want to use the admin interface.

Usage: python3 admin_server.py
Then visit http://localhost:8000/admin.html
"""

import http.server
import socketserver
import json
import os
import shutil
import base64
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# B2 Configuration for image hosting
B2_ENABLED = True  # Set to False to use local storage only
B2_BUCKET_NAME = 'babel-images'
B2_ENDPOINT = 'https://s3.us-east-005.backblazeb2.com'
B2_KEY_ID = '00509c8683970ee0000000001'
B2_APP_KEY = 'K0058TrmHhioyjUFihUUEnmDf+0+doU'

# Initialize B2 client if credentials available
_b2_client = None
def get_b2_client():
    global _b2_client
    if _b2_client is None and B2_ENABLED and B2_KEY_ID and B2_APP_KEY:
        try:
            import boto3
            _b2_client = boto3.client(
                's3',
                endpoint_url=B2_ENDPOINT,
                aws_access_key_id=B2_KEY_ID,
                aws_secret_access_key=B2_APP_KEY
            )
        except ImportError:
            print('Warning: boto3 not installed, B2 uploads disabled')
    return _b2_client

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)
    
    def do_POST(self):
        """Handle POST requests for creating/updating content."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            self.send_error_response(400, f'Invalid JSON: {e}')
            return
        
        path = urlparse(self.path).path
        
        try:
            if path == '/api/text':
                result = self.create_text(data)
            elif path == '/api/upload-images':
                result = self.upload_images(data)
            elif path == '/api/work':
                result = self.create_work(data)
            elif path == '/api/author':
                result = self.create_author(data)
            elif path == '/api/collection':
                result = self.create_collection(data)
            elif path == '/api/source':
                result = self.create_source(data)
            elif path == '/api/provenance':
                result = self.create_provenance(data)
            elif path == '/api/group':
                result = self.create_group(data)
            elif path == '/api/delete-text':
                result = self.delete_text(data)
            elif path == '/api/delete-pages':
                result = self.delete_pages(data)
            elif path == '/api/delete-work':
                result = self.delete_work(data)
            elif path == '/api/delete-author':
                result = self.delete_author(data)
            elif path == '/api/delete-collection':
                result = self.delete_collection(data)
            elif path == '/api/delete-source':
                result = self.delete_source(data)
            elif path == '/api/delete-provenance':
                result = self.delete_provenance(data)
            elif path == '/api/delete-group':
                result = self.delete_group(data)
            elif path == '/api/list-texts':
                result = self.list_texts()
            elif path == '/api/list-works':
                result = self.list_works()
            elif path == '/api/list-authors':
                result = self.list_authors()
            elif path == '/api/list-collections':
                result = self.list_collections()
            elif path == '/api/list-sources':
                result = self.list_sources()
            elif path == '/api/list-provenances':
                result = self.list_provenances()
            elif path == '/api/list-groups':
                result = self.list_groups()
            elif path == '/api/get-text':
                result = self.get_text(data)
            elif path == '/api/get-work':
                result = self.get_work(data)
            elif path == '/api/get-author':
                result = self.get_author(data)
            elif path == '/api/get-collection':
                result = self.get_collection(data)
            elif path == '/api/get-source':
                result = self.get_source(data)
            elif path == '/api/get-provenance':
                result = self.get_provenance(data)
            elif path == '/api/get-group':
                result = self.get_group(data)
            elif path == '/api/save-regions':
                result = self.save_regions(data)
            elif path == '/api/save-page-order':
                result = self.save_page_order(data)
            elif path == '/api/rebuild-indexes':
                result = self.rebuild_indexes()
            else:
                self.send_error_response(404, f'Unknown endpoint: {path}')
                return
            
            self.send_json_response(200, result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))
    
    # =========================================
    # TEXT OPERATIONS
    # =========================================
    def create_text(self, data):
        """Create or update a text with all its files."""
        text_id = data.get('id')
        if not text_id:
            raise ValueError('Text ID is required')
        
        # Sanitize ID for filesystem
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', text_id.lower())
        
        # Check if we're editing an existing text - find by original ID in data.json
        existing_dir = None
        texts_base = BASE_DIR / 'texts' / '00' / '00'
        if texts_base.exists():
            for d in texts_base.iterdir():
                if d.is_dir():
                    data_file = d / 'data.json'
                    if data_file.exists():
                        try:
                            with open(data_file, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                                if existing_data.get('id') == text_id:
                                    existing_dir = d
                                    break
                        except:
                            pass
        
        # Use existing directory if found, otherwise create new one
        text_dir = existing_dir if existing_dir else (BASE_DIR / 'texts' / '00' / '00' / safe_id)
        text_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data to preserve page-specific data (regions, etc.)
        existing_pages_data = {}
        data_path = text_dir / 'data.json'
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    existing_json = json.load(f)
                    # Build map of existing page data by label/id
                    for p in existing_json.get('pages', []):
                        key = p.get('label') or p.get('id')
                        if key:
                            existing_pages_data[key] = p
            except:
                pass
        
        # Prepare data.json (remove internal fields)
        json_data = {k: v for k, v in data.items() if not k.startswith('_') and v}
        
        # Merge new pages with existing page data (PRESERVE regions and other page-specific data)
        if 'pages' in json_data:
            merged_pages = []
            for new_page in json_data['pages']:
                # Works-only page entry (no label/id) - keep as is
                if not new_page.get('label') and not new_page.get('id'):
                    merged_pages.append(new_page)
                    continue
                
                key = new_page.get('label') or new_page.get('id')
                if key and key in existing_pages_data:
                    # Merge: start with existing data, overlay new data (but KEEP regions)
                    merged = existing_pages_data[key].copy()
                    # Only update specific fields from new_page, NEVER delete regions
                    if 'label' in new_page:
                        merged['label'] = new_page['label']
                    if 'id' in new_page:
                        merged['id'] = new_page['id']
                    if 'isBlank' in new_page:
                        merged['isBlank'] = new_page['isBlank']
                    elif 'isBlank' in merged and not new_page.get('isBlank'):
                        del merged['isBlank']
                    if 'works' in new_page:
                        merged['works'] = new_page['works']
                    merged_pages.append(merged)
                else:
                    merged_pages.append(new_page)
            
            # Also preserve any existing pages that weren't in the new list
            new_keys = set()
            for p in json_data['pages']:
                key = p.get('label') or p.get('id')
                if key:
                    new_keys.add(key)
            for key, existing_page in existing_pages_data.items():
                if key not in new_keys and existing_page.get('regions'):
                    # This page has regions but wasn't in new list - preserve it!
                    merged_pages.append(existing_page)
            
            json_data['pages'] = merged_pages
        
        # Ensure pages array exists (required by text-reader.js)
        if 'pages' not in json_data:
            json_data['pages'] = []
        
        # Auto-create author pages if they don't exist
        authors = data.get('author', [])
        if isinstance(authors, str):
            authors = [authors]
        for author_id in authors:
            if author_id:
                self._ensure_author_exists(author_id)
        
        # Handle images
        images = data.get('_images', [])
        if images:
            images_dir = text_dir / 'images'
            images_dir.mkdir(exist_ok=True)
            
            for i, img in enumerate(images, 1):
                # Decode base64 image
                if img.get('data', '').startswith('data:'):
                    # Extract base64 data
                    header, b64data = img['data'].split(',', 1)
                    img_bytes = base64.b64decode(b64data)
                    
                    # Use original filename if available, otherwise generate numbered filename
                    original_name = img.get('name', '')
                    if original_name:
                        # Keep the original filename
                        filename = original_name
                    else:
                        # Determine extension from data header
                        if 'png' in header:
                            ext = 'png'
                        elif 'webp' in header:
                            ext = 'webp'
                        else:
                            ext = 'jpg'
                        filename = f'{i:03d}_{i}.{ext}'
                    
                    with open(images_dir / filename, 'wb') as f:
                        f.write(img_bytes)
        
        # Write data.json
        with open(text_dir / 'data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Copy template index.html if it doesn't exist
        # Copy dynamic index.html template (not TEMPLATE.html which is for manual editing)
        index_path = text_dir / 'index.html'
        if not index_path.exists():
            self._create_text_index_html(index_path)
        
        # Auto-rebuild indexes
        self._auto_rebuild_indexes()
        
        return {
            'success': True,
            'id': safe_id,
            'path': str(text_dir.relative_to(BASE_DIR)),
            'message': f'Text "{safe_id}" created/updated successfully'
        }
    
    def upload_images(self, data):
        """Upload a batch of images to an existing text (to B2 or local)."""
        text_id = data.get('id')
        if not text_id:
            raise ValueError('Text ID is required')
        
        images = data.get('images', [])
        if not images:
            return {'success': True, 'message': 'No images to upload'}
        
        # Find the text directory
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', text_id.lower())
        text_dir = None
        texts_base = BASE_DIR / 'texts' / '00' / '00'
        
        # First check by safe_id
        potential_dir = texts_base / safe_id
        if potential_dir.exists():
            text_dir = potential_dir
        else:
            # Search by data.json id field
            if texts_base.exists():
                for d in texts_base.iterdir():
                    if d.is_dir():
                        data_file = d / 'data.json'
                        if data_file.exists():
                            try:
                                with open(data_file, 'r', encoding='utf-8') as f:
                                    existing_data = json.load(f)
                                    if existing_data.get('id') == text_id:
                                        text_dir = d
                                        break
                            except:
                                pass
        
        if not text_dir:
            raise ValueError(f'Text "{text_id}" not found')
        
        # Get relative path for B2 key construction
        text_rel_path = text_dir.relative_to(BASE_DIR)
        
        b2 = get_b2_client()
        saved_count = 0
        b2_count = 0
        new_images = []  # Track for manifest update
        
        for img in images:
            if img.get('data', '').startswith('data:'):
                header, b64data = img['data'].split(',', 1)
                img_bytes = base64.b64decode(b64data)
                
                filename = img.get('name', f'image_{saved_count + 1}.jpg')
                
                # Upload to B2 if available
                if b2:
                    try:
                        b2_key = f'{text_rel_path}/images/{filename}'
                        # Determine content type
                        ext = filename.lower().split('.')[-1]
                        content_types = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}
                        content_type = content_types.get(ext, 'application/octet-stream')
                        
                        b2.put_object(
                            Bucket=B2_BUCKET_NAME,
                            Key=b2_key,
                            Body=img_bytes,
                            ContentType=content_type,
                            CacheControl='public, max-age=31536000'
                        )
                        b2_count += 1
                    except Exception as e:
                        print(f'B2 upload failed for {filename}: {e}')
                        # Fall back to local storage
                        images_dir = text_dir / 'images'
                        images_dir.mkdir(exist_ok=True)
                        with open(images_dir / filename, 'wb') as f:
                            f.write(img_bytes)
                else:
                    # Local storage fallback
                    images_dir = text_dir / 'images'
                    images_dir.mkdir(exist_ok=True)
                    with open(images_dir / filename, 'wb') as f:
                        f.write(img_bytes)
                
                # Track for manifest
                label = filename.rsplit('.', 1)[0].replace('_', ' ')
                new_images.append({'url': f'images/{filename}', 'label': label})
                saved_count += 1
        
        # Update images.json manifest
        if new_images:
            self._update_image_manifest(text_dir, new_images)
        
        msg = f'Uploaded {saved_count} images'
        if b2_count > 0:
            msg += f' ({b2_count} to B2)'
        
        return {
            'success': True,
            'message': msg
        }
    
    def _update_image_manifest(self, text_dir, new_images):
        """Update or create images.json manifest with new images."""
        manifest_path = text_dir / 'images.json'
        
        # Load existing manifest or create new
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            except:
                manifest = {'images': []}
        else:
            manifest = {'images': []}
        
        # Add new images (avoid duplicates)
        existing_urls = {img['url'] for img in manifest.get('images', [])}
        for img in new_images:
            if img['url'] not in existing_urls:
                manifest['images'].append(img)
        
        # Sort naturally by label
        try:
            from natsort import natsorted
            manifest['images'] = natsorted(manifest['images'], key=lambda x: x.get('label', ''))
        except ImportError:
            manifest['images'].sort(key=lambda x: x.get('label', ''))
        
        # Save updated manifest
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    def _create_text_index_html(self, path):
        """Create a basic text index.html from the existing template structure."""
        # Read an existing text's index.html as template
        sample_texts = list((BASE_DIR / 'texts' / '00' / '00').glob('*/index.html'))
        if sample_texts:
            shutil.copy(sample_texts[0], path)
        else:
            # Minimal fallback
            html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <link rel="icon" type="image/webp" href="../../../../favicon.webp">
    <link rel="stylesheet" href="../../../../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" class="search-bar" id="searchInput" placeholder="Search languages..." autocomplete="off">
        <div class="search-results" id="searchResults"></div>
    </div>
    <div class="page-wrapper">
        <div class="container">
            <h1 id="page-title">Loading...</h1>
            <div id="text-body"></div>
        </div>
    </div>
    <script src="../../../../search-index.js"></script>
    <script src="../../../../search.js"></script>
    <script>
        fetch('data.json')
            .then(r => r.json())
            .then(data => {
                document.title = data.title;
                document.getElementById('page-title').textContent = data.title;
            });
    </script>
</body>
</html>'''
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
    
    def delete_text(self, data):
        """Delete a text and all its files."""
        text_id = data.get('id')
        if not text_id:
            raise ValueError('Text ID is required')
        
        text_dir = BASE_DIR / 'texts' / '00' / '00' / text_id
        if text_dir.exists():
            shutil.rmtree(text_dir)
            return {'success': True, 'message': f'Text "{text_id}" deleted'}
        else:
            raise ValueError(f'Text "{text_id}" not found')
    
    def delete_pages(self, data):
        """Delete specific page images from a text."""
        text_id = data.get('id')
        if not text_id:
            raise ValueError('Text ID is required')
        
        pages = data.get('pages', [])  # List of filenames to delete
        if not pages:
            raise ValueError('No pages specified for deletion')
        
        text_dir = BASE_DIR / 'texts' / '00' / '00' / text_id
        images_dir = text_dir / 'images'
        
        if not text_dir.exists():
            raise ValueError(f'Text "{text_id}" not found')
        
        if not images_dir.exists():
            raise ValueError(f'No images directory found for "{text_id}"')
        
        deleted = []
        not_found = []
        
        for page_name in pages:
            # Security: only allow filenames, no path traversal
            safe_name = Path(page_name).name
            page_path = images_dir / safe_name
            
            if page_path.exists() and page_path.is_file():
                page_path.unlink()
                deleted.append(safe_name)
            else:
                not_found.append(safe_name)
        
        # Optionally renumber remaining images to maintain sequence
        remaining = sorted([f.name for f in images_dir.glob('*.*')])
        
        # Update data.json pages count if needed
        data_path = text_dir / 'data.json'
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                text_data = json.load(f)
            # If pages array was tracking images, we might need to update it
            # For now, let the client handle page array management
        
        message_parts = []
        if deleted:
            message_parts.append(f'{len(deleted)} page(s) deleted')
        if not_found:
            message_parts.append(f'{len(not_found)} not found')
        
        return {
            'success': True,
            'deleted': deleted,
            'notFound': not_found,
            'remaining': remaining,
            'message': '; '.join(message_parts) if message_parts else 'No changes made'
        }
    
    def list_texts(self):
        """List all texts."""
        texts_dir = BASE_DIR / 'texts' / '00' / '00'
        texts = []
        
        if texts_dir.exists():
            for item in texts_dir.iterdir():
                if item.is_dir() and (item / 'data.json').exists():
                    try:
                        with open(item / 'data.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Count pages from images.json manifest if it exists, otherwise count local images or pages array
                        page_count = 0
                        images_json = item / 'images.json'
                        local_images = item / 'images'
                        
                        if images_json.exists():
                            try:
                                with open(images_json, 'r', encoding='utf-8') as imgf:
                                    img_data = json.load(imgf)
                                    page_count = len(img_data.get('images', []))
                            except:
                                pass
                        
                        if page_count == 0 and local_images.exists():
                            try:
                                page_count = len([f for f in local_images.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.gif')])
                            except:
                                pass
                        
                        if page_count == 0:
                            page_count = len(data.get('pages', []))
                        
                        texts.append({
                            'id': item.name,
                            'title': data.get('title', item.name),
                            'date': data.get('date', ''),
                            'pages': page_count,
                            'hasImages': page_count > 0
                        })
                    except:
                        texts.append({
                            'id': item.name,
                            'title': item.name,
                            'date': '',
                            'pages': 0,
                            'hasImages': False
                        })
        
        return {'texts': sorted(texts, key=lambda x: x['title'].lower())}
    
    def get_text(self, data):
        """Get a text's full data."""
        text_id = data.get('id')
        if not text_id:
            raise ValueError('Text ID is required')
        
        # Try direct folder name match first
        text_dir = BASE_DIR / 'texts' / '00' / '00' / text_id
        
        # If folder doesn't exist, search by data.json id
        if not text_dir.exists() or not (text_dir / 'data.json').exists():
            text_dir = None
            texts_base = BASE_DIR / 'texts' / '00' / '00'
            for d in texts_base.iterdir():
                if d.is_dir():
                    data_file = d / 'data.json'
                    if data_file.exists():
                        try:
                            with open(data_file, 'r', encoding='utf-8') as f:
                                existing = json.load(f)
                                if existing.get('id') == text_id:
                                    text_dir = d
                                    break
                        except:
                            pass
        
        if not text_dir:
            raise ValueError(f'Text "{text_id}" not found')
        
        data_path = text_dir / 'data.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        # Include folder name for building URLs
        text_data['_folderName'] = text_dir.name
        
        # Include image info from manifest (images are on B2, not local)
        manifest_path = text_dir / 'images.json'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                images_list = manifest.get('images', [])
                text_data['_imageCount'] = len(images_list)
                # Extract filenames from URLs like "images/001.jpg"
                text_data['_imageFiles'] = [img['url'].split('/')[-1] for img in images_list]
            except:
                text_data['_imageCount'] = 0
                text_data['_imageFiles'] = []
        else:
            # Fallback to scanning local directory (for local dev without B2)
            images_dir = text_dir / 'images'
            if images_dir.exists():
                import re
                def natural_sort_key(s):
                    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
                text_data['_imageCount'] = len(list(images_dir.glob('*.*')))
                text_data['_imageFiles'] = sorted([f.name for f in images_dir.glob('*.*')], key=natural_sort_key)
        
        return text_data
    
    def save_regions(self, data):
        """Save transcription regions for a text's pages."""
        text_id = data.get('textId')
        if not text_id:
            raise ValueError('Text ID is required')
        
        regions_data = data.get('regions', {})  # Dict of pageLabel -> array of regions
        
        # Find the text directory - first try direct folder name match
        texts_base = BASE_DIR / 'texts' / '00' / '00'
        text_dir = texts_base / text_id
        
        # If folder doesn't exist by name, search by data.json id
        if not text_dir.exists() or not (text_dir / 'data.json').exists():
            text_dir = None
            for d in texts_base.iterdir():
                if d.is_dir():
                    data_file = d / 'data.json'
                    if data_file.exists():
                        try:
                            with open(data_file, 'r', encoding='utf-8') as f:
                                existing = json.load(f)
                                if existing.get('id') == text_id:
                                    text_dir = d
                                    break
                        except:
                            pass
        
        if not text_dir:
            raise ValueError(f'Text "{text_id}" not found')
        
        data_path = text_dir / 'data.json'
        
        # Load existing data
        with open(data_path, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        # Ensure pages array exists
        if 'pages' not in text_data:
            text_data['pages'] = []
        
        # Update or create page entries with regions
        for page_label, page_regions in regions_data.items():
            # Find existing page entry
            page_entry = None
            for p in text_data['pages']:
                if p.get('label') == page_label or p.get('id') == page_label:
                    page_entry = p
                    break
            
            # Create new page entry if not found
            if not page_entry:
                page_entry = {'id': page_label, 'label': page_label}
                text_data['pages'].append(page_entry)
            
            # Set regions (replace existing)
            page_entry['regions'] = page_regions
        
        # Save updated data
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        
        # Auto-commit to git
        import threading
        threading.Thread(target=self._auto_git_commit, daemon=True).start()
        
        return {
            'success': True,
            'message': f'Regions saved for text "{text_id}"',
            'pagesUpdated': len(regions_data)
        }
    
    def save_page_order(self, data):
        """Save the order of pages (including blank pages) for a text."""
        text_id = data.get('textId')
        if not text_id:
            raise ValueError('Text ID is required')
        
        pages_data = data.get('pages', [])  # Array of { label, filename, isBlank }
        
        # Find the text directory
        texts_base = BASE_DIR / 'texts' / '00' / '00'
        text_dir = texts_base / text_id
        
        # If folder doesn't exist by name, search by data.json id
        if not text_dir.exists() or not (text_dir / 'data.json').exists():
            text_dir = None
            for d in texts_base.iterdir():
                if d.is_dir():
                    data_file = d / 'data.json'
                    if data_file.exists():
                        try:
                            with open(data_file, 'r', encoding='utf-8') as f:
                                existing = json.load(f)
                                if existing.get('id') == text_id:
                                    text_dir = d
                                    break
                        except:
                            pass
        
        if not text_dir:
            raise ValueError(f'Text "{text_id}" not found')
        
        data_path = text_dir / 'data.json'
        
        # Load existing data
        with open(data_path, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        # Preserve page entries that only contain works (no label/id) - these define works for the text
        works_only_pages = [p for p in text_data.get('pages', []) if 'works' in p and not p.get('label') and not p.get('id')]
        
        # Create a mapping of existing page data (regions, works, etc.) by label
        existing_pages = {(p.get('label') or p.get('id')): p for p in text_data.get('pages', []) if p.get('label') or p.get('id')}
        
        # Build new pages array: start with works-only entries, then add ordered pages
        new_pages = works_only_pages.copy()
        
        for page_info in pages_data:
            label = page_info.get('label')
            is_blank = page_info.get('isBlank', False)
            media_type = page_info.get('mediaType')
            audio_file = page_info.get('audioFile')
            
            # Get existing page data if it exists
            if label in existing_pages:
                page_entry = existing_pages[label].copy()
            else:
                page_entry = {'id': label, 'label': label}
            
            # Always ensure id and label match the current label (handles renames)
            page_entry['id'] = label
            page_entry['label'] = label
            
            # Update blank status
            if is_blank:
                page_entry['isBlank'] = True
            elif 'isBlank' in page_entry:
                del page_entry['isBlank']
            
            # Update media type (video, audio, image-audio, or None for images)
            if media_type:
                page_entry['mediaType'] = media_type
            elif 'mediaType' in page_entry and not media_type:
                # Keep existing mediaType if not explicitly cleared
                pass
            
            # Update audio file for image-audio pages
            if audio_file:
                page_entry['audioFile'] = audio_file
            elif 'audioFile' in page_entry and not audio_file:
                # Keep existing audioFile if not explicitly cleared
                pass
            
            new_pages.append(page_entry)
        
        text_data['pages'] = new_pages
        
        # Also update images.json to reflect the new order (for non-blank pages)
        images_json_path = text_dir / 'images.json'
        if images_json_path.exists():
            with open(images_json_path, 'r', encoding='utf-8') as f:
                images_data = json.load(f)
            
            # Create mapping of filename to image entry
            image_map = {}
            for img in images_data.get('images', []):
                filename = img['url'].split('/')[-1]
                image_map[filename] = img
            
            # Rebuild images array in new order (skip blank pages)
            new_images = []
            for page_info in pages_data:
                if not page_info.get('isBlank'):
                    filename = page_info.get('filename')
                    if filename and filename in image_map:
                        new_images.append(image_map[filename])
            
            # Add any images that weren't in the pages list
            for img in images_data.get('images', []):
                if img not in new_images:
                    new_images.append(img)
            
            images_data['images'] = new_images
            with open(images_json_path, 'w', encoding='utf-8') as f:
                json.dump(images_data, f, indent=2, ensure_ascii=False)
        
        # Save updated data.json
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        
        # Auto-commit to git
        import threading
        threading.Thread(target=self._auto_git_commit, daemon=True).start()
        
        return {
            'success': True,
            'message': f'Page order saved for text "{text_id}"',
            'pagesUpdated': len(new_pages)
        }
    
    # =========================================
    # WORK OPERATIONS
    # =========================================
    def create_work(self, data):
        """Create or update a work."""
        work_id = data.get('id')
        if not work_id:
            raise ValueError('Work ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', work_id.lower())
        
        work_dir = BASE_DIR / 'works' / safe_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare work.json
        work_data = {k: v for k, v in data.items() if k != 'id' and v}
        
        with open(work_dir / 'work.json', 'w', encoding='utf-8') as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        # Auto-rebuild indexes
        self._auto_rebuild_indexes()
        
        return {
            'success': True,
            'id': safe_id,
            'path': str(work_dir.relative_to(BASE_DIR)),
            'message': f'Work "{safe_id}" created/updated successfully'
        }
    
    def delete_work(self, data):
        """Delete a work."""
        work_id = data.get('id')
        if not work_id:
            raise ValueError('Work ID is required')
        
        work_dir = BASE_DIR / 'works' / work_id
        if work_dir.exists():
            shutil.rmtree(work_dir)
            return {'success': True, 'message': f'Work "{work_id}" deleted'}
        else:
            raise ValueError(f'Work "{work_id}" not found')
    
    def list_works(self):
        """List all works."""
        works_dir = BASE_DIR / 'works'
        works = []
        
        if works_dir.exists():
            for item in works_dir.iterdir():
                if item.is_dir() and (item / 'work.json').exists():
                    try:
                        with open(item / 'work.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Get author info for display
                            author = data.get('author', '')
                            if isinstance(author, list):
                                author = ', '.join(author)
                            works.append({
                                'id': item.name,
                                'title': data.get('fullTitle') or data.get('title') or item.name,
                                'date': data.get('date', ''),
                                'author': author,
                                'genre': data.get('genre', ''),
                                'aliases': data.get('alias', [])
                            })
                    except:
                        works.append({
                            'id': item.name,
                            'title': item.name,
                            'date': '',
                            'author': '',
                            'genre': '',
                            'aliases': []
                        })
        
        return {'works': sorted(works, key=lambda x: x['title'].lower())}
    
    def get_work(self, data):
        """Get a work's full data."""
        work_id = data.get('id')
        if not work_id:
            raise ValueError('Work ID is required')
        
        work_path = BASE_DIR / 'works' / work_id / 'work.json'
        
        if not work_path.exists():
            raise ValueError(f'Work "{work_id}" not found')
        
        with open(work_path, 'r', encoding='utf-8') as f:
            work_data = json.load(f)
        
        work_data['id'] = work_id
        return work_data
    
    # =========================================
    # AUTHOR OPERATIONS
    # =========================================
    def _ensure_author_exists(self, author_id):
        """Create a basic author page if it doesn't exist."""
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', author_id.lower())
        author_dir = BASE_DIR / 'authors' / safe_id
        author_json = author_dir / 'author.json'
        author_index = author_dir / 'index.html'
        
        if not author_json.exists():
            author_dir.mkdir(parents=True, exist_ok=True)
            # Use the original author name as-is (preserves casing like "ITV Digital")
            with open(author_json, 'w', encoding='utf-8') as f:
                json.dump({'name': author_id}, f, indent=2, ensure_ascii=False)
        
        # Also create index.html if it doesn't exist
        if not author_index.exists():
            self._create_author_index_html(author_index, author_id, safe_id)
    
    def _create_author_index_html(self, path, author_name, author_id):
        """Create a basic author index.html page."""
        import html
        escaped_name = html.escape(author_name)
        
        content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_name}</title>
    <link rel="icon" type="image/webp" href="../../favicon.webp">
    <link rel="stylesheet" href="../../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="header-logo-container"><a href="../../" class="header-logo"><img src="../../Wikilogo.webp" alt="Babel Archive"></a></div>
    <div class="container">
        <aside class="right-sidebar">
            <a href="../../" class="sidebar-logo">
                <img src="../../background-image/1111babel.png" alt="Babel Archive">
            </a>
            <nav class="sidebar-links">
            <h3>Navigate</h3>
            <ul>
                <li><a href="../../">Home</a></li>
                <li><a href="../../texts-index.html">All Texts</a></li>
                <li><a href="../../languages/">Languages</a></li>
                <li><a href="../../works/">Works Index</a></li>
                <li><a href="../../authors/">Authors</a></li>
                <li><a href="../../sources/">Sources</a></li>
                <li><a href="../../provenances/">Provenances</a></li>
                <li><a href="../../collections/">Collections</a></li>
            </ul>
        </nav>
        </aside>
        <div class="main-content">
        <h1>{escaped_name}</h1>

        <div class="metadata">
            <p><strong>Author ID:</strong> <code>{author_id}</code></p>
        </div>

        <p><em>This author page was auto-generated. Run the indexer to populate works and texts.</em></p>
</div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
</body>
</html>'''
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_author(self, data):
        """Create or update an author."""
        author_id = data.get('id')
        if not author_id:
            raise ValueError('Author ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', author_id.lower())
        
        author_dir = BASE_DIR / 'authors' / safe_id
        author_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare author.json
        author_data = {k: v for k, v in data.items() if k != 'id' and v}
        
        with open(author_dir / 'author.json', 'w', encoding='utf-8') as f:
            json.dump(author_data, f, indent=2, ensure_ascii=False)
        
        # Auto-rebuild indexes
        self._auto_rebuild_indexes()
        
        return {
            'success': True,
            'id': safe_id,
            'path': str(author_dir.relative_to(BASE_DIR)),
            'message': f'Author "{safe_id}" created/updated successfully'
        }
    
    def delete_author(self, data):
        """Delete an author."""
        author_id = data.get('id')
        if not author_id:
            raise ValueError('Author ID is required')
        
        author_dir = BASE_DIR / 'authors' / author_id
        if author_dir.exists():
            shutil.rmtree(author_dir)
            return {'success': True, 'message': f'Author "{author_id}" deleted'}
        else:
            raise ValueError(f'Author "{author_id}" not found')
    
    def list_authors(self):
        """List all authors."""
        authors_dir = BASE_DIR / 'authors'
        authors = []
        
        if authors_dir.exists():
            for item in authors_dir.iterdir():
                if item.is_dir() and (item / 'author.json').exists():
                    try:
                        with open(item / 'author.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            authors.append({
                                'id': item.name,
                                'name': data.get('name', item.name),
                                'birth': data.get('birth', ''),
                                'death': data.get('death', '')
                            })
                    except:
                        authors.append({
                            'id': item.name,
                            'name': item.name,
                            'birth': '',
                            'death': ''
                        })
        
        return {'authors': sorted(authors, key=lambda x: x['name'].lower())}
    
    def get_author(self, data):
        """Get an author's full data."""
        author_id = data.get('id')
        if not author_id:
            raise ValueError('Author ID is required')
        
        author_path = BASE_DIR / 'authors' / author_id / 'author.json'
        
        if not author_path.exists():
            raise ValueError(f'Author "{author_id}" not found')
        
        with open(author_path, 'r', encoding='utf-8') as f:
            author_data = json.load(f)
        
        author_data['id'] = author_id
        return author_data
    
    # =========================================
    # COLLECTION OPERATIONS
    # =========================================
    def create_collection(self, data):
        """Create or update a collection."""
        collection_id = data.get('id')
        if not collection_id:
            raise ValueError('Collection ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', collection_id.lower())
        collection_dir = BASE_DIR / 'collections' / safe_id
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        collection_data = {
            'id': safe_id,
            'name': data.get('name', safe_id.replace('-', ' ').title()),
            'description': data.get('description', '')
        }
        
        with open(collection_dir / 'collection.json', 'w', encoding='utf-8') as f:
            json.dump(collection_data, f, indent=2, ensure_ascii=False)
        
        self._auto_rebuild_indexes()
        return {'message': f'Collection "{safe_id}" saved successfully'}
    
    def delete_collection(self, data):
        """Delete a collection."""
        collection_id = data.get('id')
        if not collection_id:
            raise ValueError('Collection ID is required')
        
        collection_dir = BASE_DIR / 'collections' / collection_id
        if collection_dir.exists():
            import shutil
            shutil.rmtree(collection_dir)
            self._auto_rebuild_indexes()
            return {'message': f'Collection "{collection_id}" deleted'}
        else:
            raise ValueError(f'Collection "{collection_id}" not found')
    
    def list_collections(self):
        """List all collections."""
        collections_dir = BASE_DIR / 'collections'
        collections = []
        
        if collections_dir.exists():
            for item in collections_dir.iterdir():
                if item.is_dir():
                    json_path = item / 'collection.json'
                    if json_path.exists():
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                collections.append({
                                    'id': item.name,
                                    'name': data.get('name', item.name.replace('-', ' ').title())
                                })
                        except:
                            collections.append({
                                'id': item.name,
                                'name': item.name.replace('-', ' ').title()
                            })
                    else:
                        # Directory exists without JSON - still list it
                        collections.append({
                            'id': item.name,
                            'name': item.name.replace('-', ' ').title()
                        })
        
        return {'collections': sorted(collections, key=lambda x: x['name'].lower())}
    
    def get_collection(self, data):
        """Get a collection's full data."""
        collection_id = data.get('id')
        if not collection_id:
            raise ValueError('Collection ID is required')
        
        collection_dir = BASE_DIR / 'collections' / collection_id
        collection_path = collection_dir / 'collection.json'
        
        if collection_path.exists():
            with open(collection_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            collection_data['id'] = collection_id
            return collection_data
        elif collection_dir.exists():
            # Directory exists but no JSON - return default data
            return {
                'id': collection_id,
                'name': collection_id.replace('-', ' ').title(),
                'description': ''
            }
        else:
            raise ValueError(f'Collection "{collection_id}" not found')
    
    # =========================================
    # GROUP OPERATIONS
    # =========================================
    def create_group(self, data):
        """Create or update a group (category)."""
        group_id = data.get('id')
        if not group_id:
            raise ValueError('Group ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', group_id.lower())
        group_dir = BASE_DIR / 'groups' / safe_id
        group_dir.mkdir(parents=True, exist_ok=True)
        
        group_data = {
            'id': safe_id,
            'name': data.get('name', safe_id.replace('-', ' ').title()),
            'description': data.get('description', '')
        }
        
        with open(group_dir / 'group.json', 'w', encoding='utf-8') as f:
            json.dump(group_data, f, indent=2, ensure_ascii=False)
        
        self._auto_rebuild_indexes()
        return {'message': f'Group "{safe_id}" saved successfully'}
    
    def delete_group(self, data):
        """Delete a group."""
        group_id = data.get('id')
        if not group_id:
            raise ValueError('Group ID is required')
        
        group_dir = BASE_DIR / 'groups' / group_id
        if group_dir.exists():
            import shutil
            shutil.rmtree(group_dir)
            self._auto_rebuild_indexes()
            return {'message': f'Group "{group_id}" deleted'}
        else:
            raise ValueError(f'Group "{group_id}" not found')
    
    def list_groups(self):
        """List all groups."""
        groups_dir = BASE_DIR / 'groups'
        groups = []
        
        if groups_dir.exists():
            for item in groups_dir.iterdir():
                if item.is_dir():
                    json_path = item / 'group.json'
                    if json_path.exists():
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                groups.append({
                                    'id': item.name,
                                    'name': data.get('name', item.name.replace('-', ' ').title())
                                })
                        except:
                            groups.append({
                                'id': item.name,
                                'name': item.name.replace('-', ' ').title()
                            })
                    else:
                        # Directory exists without JSON - still list it
                        groups.append({
                            'id': item.name,
                            'name': item.name.replace('-', ' ').title()
                        })
        
        return {'groups': sorted(groups, key=lambda x: x['name'].lower())}
    
    def get_group(self, data):
        """Get a group's full data."""
        group_id = data.get('id')
        if not group_id:
            raise ValueError('Group ID is required')
        
        group_dir = BASE_DIR / 'groups' / group_id
        group_path = group_dir / 'group.json'
        
        if group_path.exists():
            with open(group_path, 'r', encoding='utf-8') as f:
                group_data = json.load(f)
            group_data['id'] = group_id
            return group_data
        elif group_dir.exists():
            # Directory exists but no JSON - return default data
            return {
                'id': group_id,
                'name': group_id.replace('-', ' ').title(),
                'description': ''
            }
        else:
            raise ValueError(f'Group "{group_id}" not found')
    
    # =========================================
    # SOURCE OPERATIONS
    # =========================================
    def create_source(self, data):
        """Create or update a source (institution)."""
        source_id = data.get('id')
        if not source_id:
            raise ValueError('Source ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', source_id.lower())
        source_dir = BASE_DIR / 'sources' / safe_id
        source_dir.mkdir(parents=True, exist_ok=True)
        
        source_data = {
            'id': safe_id,
            'name': data.get('name', safe_id.replace('-', ' ').title()),
            'location': data.get('location', ''),
            'description': data.get('description', '')
        }
        
        with open(source_dir / 'source.json', 'w', encoding='utf-8') as f:
            json.dump(source_data, f, indent=2, ensure_ascii=False)
        
        self._auto_rebuild_indexes()
        return {'message': f'Source "{safe_id}" saved successfully'}
    
    def delete_source(self, data):
        """Delete a source."""
        source_id = data.get('id')
        if not source_id:
            raise ValueError('Source ID is required')
        
        source_dir = BASE_DIR / 'sources' / source_id
        if source_dir.exists():
            import shutil
            shutil.rmtree(source_dir)
            self._auto_rebuild_indexes()
            return {'message': f'Source "{source_id}" deleted'}
        else:
            raise ValueError(f'Source "{source_id}" not found')
    
    def list_sources(self):
        """List all sources."""
        sources_dir = BASE_DIR / 'sources'
        sources = []
        
        if sources_dir.exists():
            for item in sources_dir.iterdir():
                if item.is_dir():
                    json_path = item / 'source.json'
                    if json_path.exists():
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                sources.append({
                                    'id': item.name,
                                    'name': data.get('name', item.name.replace('-', ' ').title()),
                                    'location': data.get('location', '')
                                })
                        except:
                            sources.append({
                                'id': item.name,
                                'name': item.name.replace('-', ' ').title(),
                                'location': ''
                            })
                    else:
                        # Directory exists without JSON - still list it
                        sources.append({
                            'id': item.name,
                            'name': item.name.replace('-', ' ').title(),
                            'location': ''
                        })
        
        return {'sources': sorted(sources, key=lambda x: x['name'].lower())}
    
    def get_source(self, data):
        """Get a source's full data."""
        source_id = data.get('id')
        if not source_id:
            raise ValueError('Source ID is required')
        
        source_dir = BASE_DIR / 'sources' / source_id
        source_path = source_dir / 'source.json'
        
        if source_path.exists():
            with open(source_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            source_data['id'] = source_id
            return source_data
        elif source_dir.exists():
            # Directory exists but no JSON - return default data
            return {
                'id': source_id,
                'name': source_id.replace('-', ' ').title(),
                'location': '',
                'description': ''
            }
        else:
            raise ValueError(f'Source "{source_id}" not found')
    
    # =========================================
    # PROVENANCE OPERATIONS
    # =========================================
    def create_provenance(self, data):
        """Create or update a provenance (origin location)."""
        provenance_id = data.get('id')
        if not provenance_id:
            raise ValueError('Provenance ID is required')
        
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', provenance_id.lower())
        provenance_dir = BASE_DIR / 'provenances' / safe_id
        provenance_dir.mkdir(parents=True, exist_ok=True)
        
        provenance_data = {
            'id': safe_id,
            'name': data.get('name', safe_id.replace('-', ' ').title()),
            'location': data.get('location', ''),
            'description': data.get('description', '')
        }
        
        with open(provenance_dir / 'provenance.json', 'w', encoding='utf-8') as f:
            json.dump(provenance_data, f, indent=2, ensure_ascii=False)
        
        self._auto_rebuild_indexes()
        return {'message': f'Provenance "{safe_id}" saved successfully'}
    
    def delete_provenance(self, data):
        """Delete a provenance."""
        provenance_id = data.get('id')
        if not provenance_id:
            raise ValueError('Provenance ID is required')
        
        provenance_dir = BASE_DIR / 'provenances' / provenance_id
        if provenance_dir.exists():
            import shutil
            shutil.rmtree(provenance_dir)
            self._auto_rebuild_indexes()
            return {'message': f'Provenance "{provenance_id}" deleted'}
        else:
            raise ValueError(f'Provenance "{provenance_id}" not found')
    
    def list_provenances(self):
        """List all provenances."""
        provenances_dir = BASE_DIR / 'provenances'
        provenances = []
        
        if provenances_dir.exists():
            for item in provenances_dir.iterdir():
                if item.is_dir():
                    json_path = item / 'provenance.json'
                    if json_path.exists():
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                provenances.append({
                                    'id': item.name,
                                    'name': data.get('name', item.name.replace('-', ' ').title()),
                                    'location': data.get('location', '')
                                })
                        except:
                            provenances.append({
                                'id': item.name,
                                'name': item.name.replace('-', ' ').title(),
                                'location': ''
                            })
                    else:
                        # Directory exists without JSON - still list it
                        provenances.append({
                            'id': item.name,
                            'name': item.name.replace('-', ' ').title(),
                            'location': ''
                        })
        
        return {'provenances': sorted(provenances, key=lambda x: x['name'].lower())}
    
    def get_provenance(self, data):
        """Get a provenance's full data."""
        provenance_id = data.get('id')
        if not provenance_id:
            raise ValueError('Provenance ID is required')
        
        provenance_dir = BASE_DIR / 'provenances' / provenance_id
        provenance_path = provenance_dir / 'provenance.json'
        
        if provenance_path.exists():
            with open(provenance_path, 'r', encoding='utf-8') as f:
                provenance_data = json.load(f)
            provenance_data['id'] = provenance_id
            return provenance_data
        elif provenance_dir.exists():
            # Directory exists but no JSON - return default data
            return {
                'id': provenance_id,
                'name': provenance_id.replace('-', ' ').title(),
                'location': '',
                'description': ''
            }
        else:
            raise ValueError(f'Provenance "{provenance_id}" not found')
    
    # =========================================
    # INDEX REBUILDING
    # =========================================
    def _auto_rebuild_indexes(self):
        """Silently rebuild indexes in the background after saves."""
        import subprocess
        import threading
        
        def rebuild():
            scripts = ['index_works.py', 'index_authors.py', 'index_texts.py', 'index_sources.py', 'index_provenances.py', 'index_collections.py', 'index_groups.py']
            for script in scripts:
                if (BASE_DIR / script).exists():
                    try:
                        subprocess.run(
                            ['python3', script],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            timeout=60
                        )
                        print(f"  [Auto-rebuild] {script} completed")
                    except Exception as e:
                        print(f"  [Auto-rebuild] {script} failed: {e}")
            
            # Auto-commit after rebuilding indexes
            self._auto_git_commit()
        
        # Run in background thread so save returns quickly
        threading.Thread(target=rebuild, daemon=True).start()
    
    def _auto_git_commit(self):
        """Auto-commit and push changes to git after saves."""
        import subprocess
        try:
            # Stage all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=str(BASE_DIR),
                capture_output=True,
                timeout=30
            )
            # Commit with timestamp
            from datetime import datetime
            msg = f"Auto-commit from Content Manager at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = subprocess.run(
                ['git', 'commit', '-m', msg],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"  [Auto-git] Committed: {msg}")
                # Push to remote
                push_result = subprocess.run(
                    ['git', 'push'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if push_result.returncode == 0:
                    print("  [Auto-git] Pushed to remote")
                else:
                    print(f"  [Auto-git] Push failed: {push_result.stderr}")
            elif 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                print("  [Auto-git] No changes to commit")
            else:
                print(f"  [Auto-git] Commit failed: {result.stderr}")
        except Exception as e:
            print(f"  [Auto-git] Error: {e}")
    
    def rebuild_indexes(self):
        """Rebuild all indexes by running the Python scripts."""
        import subprocess
        
        results = []
        
        # Run index_works.py
        try:
            result = subprocess.run(
                ['python3', 'index_works.py'],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=60
            )
            results.append({
                'script': 'index_works.py',
                'success': result.returncode == 0,
                'output': result.stdout[-500:] if result.stdout else '',
                'error': result.stderr[-500:] if result.stderr else ''
            })
        except Exception as e:
            results.append({
                'script': 'index_works.py',
                'success': False,
                'error': str(e)
            })
        
        # Run index_authors.py if it exists
        if (BASE_DIR / 'index_authors.py').exists():
            try:
                result = subprocess.run(
                    ['python3', 'index_authors.py'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results.append({
                    'script': 'index_authors.py',
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else '',
                    'error': result.stderr[-500:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'script': 'index_authors.py',
                    'success': False,
                    'error': str(e)
                })
        
        # Run index_texts.py if it exists
        if (BASE_DIR / 'index_texts.py').exists():
            try:
                result = subprocess.run(
                    ['python3', 'index_texts.py'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results.append({
                    'script': 'index_texts.py',
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else '',
                    'error': result.stderr[-500:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'script': 'index_texts.py',
                    'success': False,
                    'error': str(e)
                })
        
        # Run index_sources.py if it exists
        if (BASE_DIR / 'index_sources.py').exists():
            try:
                result = subprocess.run(
                    ['python3', 'index_sources.py'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results.append({
                    'script': 'index_sources.py',
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else '',
                    'error': result.stderr[-500:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'script': 'index_sources.py',
                    'success': False,
                    'error': str(e)
                })
        
        # Run index_provenances.py if it exists
        if (BASE_DIR / 'index_provenances.py').exists():
            try:
                result = subprocess.run(
                    ['python3', 'index_provenances.py'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results.append({
                    'script': 'index_provenances.py',
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else '',
                    'error': result.stderr[-500:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'script': 'index_provenances.py',
                    'success': False,
                    'error': str(e)
                })
        
        # Run index_collections.py if it exists
        if (BASE_DIR / 'index_collections.py').exists():
            try:
                result = subprocess.run(
                    ['python3', 'index_collections.py'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results.append({
                    'script': 'index_collections.py',
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else '',
                    'error': result.stderr[-500:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'script': 'index_collections.py',
                    'success': False,
                    'error': str(e)
                })
        
        all_success = all(r['success'] for r in results)
        return {
            'success': all_success,
            'results': results,
            'message': 'All indexes rebuilt successfully' if all_success else 'Some indexes failed to rebuild'
        }


def run_server():
    with socketserver.TCPServer(("", PORT), AdminHandler) as httpd:
        print(f"=" * 50)
        print(f"  Babel Admin Server")
        print(f"=" * 50)
        print(f"  Server running at: http://localhost:{PORT}")
        print(f"  Admin panel:       http://localhost:{PORT}/admin.html")
        print(f"  Base directory:    {BASE_DIR}")
        print(f"=" * 50)
        print(f"  Press Ctrl+C to stop")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == '__main__':
    run_server()
