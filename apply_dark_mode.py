#!/usr/bin/env python3
"""
Update all index.html files with dark mode and animated starfield background.
"""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def get_dark_mode_css():
    """Return the dark mode CSS with animated background."""
    return """
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700&display=swap');
        
        @font-face {
            font-family: 'Junicode';
            src: url('https://chf.sourceforge.io/chf/download/Junicode-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        
        @font-face {
            font-family: 'Junicode';
            src: url('https://chf.sourceforge.io/chf/download/Junicode-Bold.ttf') format('truetype');
            font-weight: bold;
            font-style: normal;
        }
        
        @font-face {
            font-family: 'Junicode';
            src: url('https://chf.sourceforge.io/chf/download/Junicode-Italic.ttf') format('truetype');
            font-weight: normal;
            font-style: italic;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        
        @keyframes rotate-planet-1 {
            0% { transform: rotate(0deg) translateX(150px) rotate(0deg); }
            100% { transform: rotate(360deg) translateX(150px) rotate(-360deg); }
        }
        
        @keyframes rotate-planet-2 {
            0% { transform: rotate(120deg) translateX(200px) rotate(0deg); }
            100% { transform: rotate(480deg) translateX(200px) rotate(-360deg); }
        }
        
        @keyframes rotate-planet-3 {
            0% { transform: rotate(240deg) translateX(250px) rotate(0deg); }
            100% { transform: rotate(600deg) translateX(250px) rotate(-360deg); }
        }
        
        body {
            font-family: 'Junicode', 'EB Garamond', 'Palatino Linotype', 'Book Antiqua', serif;
            line-height: 1.7;
            color: #d4d4d4;
            background: #1a1a1a;
            overflow-x: hidden;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(1px 1px at 10% 20%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 20% 30%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 50% 50%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 80% 10%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 90% 60%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 30% 80%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 60% 90%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 15% 70%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 75% 75%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 40% 40%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 88% 30%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 25% 15%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 70% 20%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 35% 60%, white, rgba(255,255,255,0)),
                radial-gradient(1px 1px at 65% 45%, white, rgba(255,255,255,0));
            background-size: 200% 200%;
            background-position: 0% 0%;
            background-repeat: repeat;
            animation: twinkle 3s ease-in-out infinite, twinkle 4.5s ease-in-out 1s infinite, twinkle 5.5s ease-in-out 0.5s infinite;
            opacity: 0.3;
            z-index: 0;
            pointer-events: none;
        }
        
        body::after {
            content: '';
            position: fixed;
            top: 50%;
            left: 50%;
            width: 500px;
            height: 500px;
            margin-left: -250px;
            margin-top: -250px;
            z-index: 1;
            pointer-events: none;
        }
        
        .planet-container {
            position: fixed;
            top: 50%;
            left: 50%;
            width: 500px;
            height: 500px;
            margin-left: -250px;
            margin-top: -250px;
            z-index: 1;
            pointer-events: none;
        }
        
        .planet {
            position: absolute;
            border-radius: 0;
        }
        
        .planet-1 {
            width: 30px;
            height: 30px;
            background: radial-gradient(circle at 30% 30%, #ff6b9d, #c44569);
            animation: rotate-planet-1 20s linear infinite;
            box-shadow: 0 0 20px rgba(255, 107, 157, 0.6);
        }
        
        .planet-2 {
            width: 45px;
            height: 45px;
            background: radial-gradient(circle at 35% 35%, #ffd89b, #f9a825);
            animation: rotate-planet-2 30s linear infinite;
            box-shadow: 0 0 25px rgba(249, 168, 37, 0.5);
        }
        
        .planet-3 {
            width: 25px;
            height: 25px;
            background: radial-gradient(circle at 40% 40%, #6bcbf3, #2d9cdb);
            animation: rotate-planet-3 25s linear infinite;
            box-shadow: 0 0 15px rgba(107, 203, 243, 0.6);
        }
        
        .container {
            background: #2a2a2a;
            padding: 40px;
            border-radius: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
            max-width: 850px;
            margin: 40px auto;
            position: relative;
            z-index: 10;
            border: 1px solid #404040;
        }
        
        h1 {
            color: #c0a080;
            border-bottom: 2px solid #c0a080;
            padding: 12px 0;
            text-shadow: none;
            letter-spacing: 1px;
            font-size: 2em;
            font-weight: normal;
        }
        
        h2 {
            color: #c0a080;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.4em;
            text-shadow: none;
            border-left: none;
            padding-left: 0;
            font-weight: normal;
        }
        
        h3 {
            color: #a89070;
            text-shadow: none;
            font-size: 1.1em;
            font-weight: normal;
            font-style: italic;
        }
        
        .metadata {
            background: #1f1f1f;
            padding: 15px;
            border-radius: 0;
            margin: 20px 0;
            border-left: 3px solid #a89070;
            box-shadow: none;
        }
        
        .metadata p {
            margin: 8px 0;
            color: #b0b0b0;
        }
        
        .metadata strong {
            color: #00ffff;
        }
        
        a {
            color: #8fa8b8;
            text-decoration: underline;
            transition: all 0.2s ease;
            font-weight: normal;
        }
        
        a:hover {
            color: #c0a080;
            text-decoration: underline;
            text-shadow: none;
            filter: none;
        }
        
        .level-tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 0;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .language {
            background: #1b4332;
            color: #52b788;
        }
        
        .dialect {
            background: #664e00;
            color: #ffb703;
        }
        
        section {
            margin: 20px 0;
        }
        
        ul {
            color: #b0b0b0;
            padding-left: 20px;
        }
        
        li {
            margin: 8px 0;
        }
        
        .breadcrumb-tree {
            background: #1f1f1f;
            border: 1px solid #404040;
            border-radius: 0;
            padding: 15px 20px;
            margin: 20px 0;
            font-size: 0.95em;
            line-height: 1.8;
            color: #999;
        }
        
        .breadcrumb-tree a {
            color: #8fa8b8;
            font-weight: normal;
        }
        
        .breadcrumb-tree a:hover {
            color: #c0a080;
            text-shadow: none;
        }
        
        .breadcrumb-tree span.current {
            color: #c0a080;
            font-weight: normal;
            background: transparent;
            padding: 0;
            border: none;
            border-radius: 0;
            text-shadow: none;
            box-shadow: none;
        }
        
        .dialects-section {
            background: #1f1f1f;
            border: 1px solid #404040;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0;
            box-shadow: none;
        }
        
        .dialects-section h3 {
            margin-top: 0;
            color: #a89070;
            text-shadow: none;
            font-size: 1.1em;
        }
        
        .dialects-list {
            list-style: none;
            padding: 0;
            margin: 10px 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 8px;
        }
        
        .dialect-group {
            margin: 12px 0;
            padding: 10px;
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            border-radius: 0;
        }
        
        .dialect-group strong {
            display: block;
            margin-bottom: 8px;
            color: #a89070;
            font-size: 0.95em;
            text-shadow: none;
            font-weight: normal;
        }
        
        .dialect-group ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 4px;
        }
        
        .dialects-list li, .dialect-group ul li {
            padding: 0;
        }
        
        .dialects-list a, .dialect-group a {
            color: #8fa8b8;
            padding: 6px 0;
            transition: color 0.2s ease;
            display: block;
        }
        
        .dialects-list a:hover, .dialect-group a:hover {
            color: #c0a080;
            text-shadow: none;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #404040;
            margin-top: 40px;
            font-size: 0.9em;
        }
        
        footer small {
            color: #555;
            display: block;
            margin-top: 10px;
        }
        
        hr {
            border: none;
            border-top: 1px solid #404040;
            margin: 20px 0;
            opacity: 1;
        }
    """

def update_index_file(file_path):
    """Update a single index.html file with dark mode CSS."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove all style tags
        import re
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Find head tag and add single style
        head_end = content.find('</head>')
        if head_end != -1:
            new_style = f'<style>{get_dark_mode_css()}</style>\n    '
            content = content[:head_end] + new_style + content[head_end:]
        
        # Remove duplicate planet containers
        content = re.sub(r'<div class="planet-container">.*?</div>\s*', '', content, flags=re.DOTALL)
        
        # Add planet container after body tag
        body_tag_end = content.find('<body>') + 6
        if body_tag_end > 5:
            planet_container = '''
    <div class="planet-container">
        <div class="planet planet-1"></div>
        <div class="planet planet-2"></div>
        <div class="planet planet-3"></div>
    </div>
'''
            content = content[:body_tag_end] + planet_container + content[body_tag_end:]
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main execution."""
    print("=" * 70)
    print("Updating all pages to dark mode with animated background")
    print("=" * 70)
    
    # Find all index.html files
    index_files = list(LANGUAGES_DIR.rglob('index.html'))
    print(f"Found {len(index_files)} index.html files")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, file_path in enumerate(index_files):
        result = update_index_file(file_path)
        
        if result is True:
            updated_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1
        
        if (i + 1) % 2000 == 0:
            print(f"  Processed {i + 1} files...")
    
    print(f"\nUpdated {updated_count} files")
    print(f"⊘ Skipped {skipped_count} already updated files")
    if error_count > 0:
        print(f"{error_count} errors")
    
    print("\n" + "=" * 70)
    print("Done! All pages are now in dark mode with animated starfield.")
    print("=" * 70)

if __name__ == '__main__':
    main()
