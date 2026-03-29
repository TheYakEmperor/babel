#!/usr/bin/env python3
"""
Upload all images from texts/ to Backblaze B2
Preserves folder structure: texts/00/01/book/images/1.jpg -> texts/00/01/book/images/1.jpg
"""

import os
import sys
import boto3
from botocore.config import Config
from pathlib import Path
import mimetypes

# Configuration
BUCKET_NAME = 'babel-images'
ENDPOINT = 'https://s3.us-east-005.backblazeb2.com'
BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'

# Image extensions to upload
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def get_credentials():
    """Get credentials from environment or prompt"""
    key_id = os.environ.get('B2_KEY_ID')
    app_key = os.environ.get('B2_APP_KEY')
    
    if not key_id:
        key_id = input('Enter B2 Application Key ID: ').strip()
    if not app_key:
        app_key = input('Enter B2 Application Key: ').strip()
    
    return key_id, app_key

def get_content_type(filepath):
    """Get MIME type for file"""
    mime_type, _ = mimetypes.guess_type(str(filepath))
    return mime_type or 'application/octet-stream'

def upload_images():
    key_id, app_key = get_credentials()
    
    # Create S3 client for B2
    s3 = boto3.client(
        's3',
        endpoint_url=ENDPOINT,
        aws_access_key_id=key_id,
        aws_secret_access_key=app_key,
        config=Config(signature_version='s3v4')
    )
    
    # Find all images
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(TEXTS_DIR.rglob(f'*{ext}'))
        images.extend(TEXTS_DIR.rglob(f'*{ext.upper()}'))
    
    images = list(set(images))  # Remove duplicates
    total = len(images)
    
    print(f'Found {total} images to upload')
    
    uploaded = 0
    skipped = 0
    errors = []
    
    for i, img_path in enumerate(sorted(images)):
        # Key is relative path from Babel root
        key = str(img_path.relative_to(BASE_DIR))
        
        try:
            # Check if already exists (optional - comment out to re-upload all)
            try:
                s3.head_object(Bucket=BUCKET_NAME, Key=key)
                skipped += 1
                print(f'[{i+1}/{total}] SKIP (exists): {key}')
                continue
            except:
                pass  # File doesn't exist, upload it
            
            # Upload
            content_type = get_content_type(img_path)
            s3.upload_file(
                str(img_path),
                BUCKET_NAME,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000'  # 1 year cache
                }
            )
            uploaded += 1
            print(f'[{i+1}/{total}] OK: {key}')
            
        except Exception as e:
            errors.append((key, str(e)))
            print(f'[{i+1}/{total}] ERROR: {key} - {e}')
    
    print(f'\n=== DONE ===')
    print(f'Uploaded: {uploaded}')
    print(f'Skipped (already exists): {skipped}')
    print(f'Errors: {len(errors)}')
    
    if errors:
        print('\nErrors:')
        for key, err in errors[:10]:
            print(f'  {key}: {err}')
        if len(errors) > 10:
            print(f'  ... and {len(errors) - 10} more')
    
    # Print the base URL for reference
    print(f'\nYour images will be at:')
    print(f'  https://{BUCKET_NAME}.s3.us-east-005.backblazeb2.com/texts/...')
    print(f'\nOr with Cloudflare (after setup):')
    print(f'  https://your-subdomain.yourdomain.com/texts/...')

if __name__ == '__main__':
    upload_images()
