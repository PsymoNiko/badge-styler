import os
import json
import re
import glob
from pathlib import Path

def find_markdown_files(directory="."):
    """
    Find all markdown files in the specified directory
    """
    markdown_files = []
    patterns = ["*.md", "*.markdown", "README", "README.*"]
    
    for pattern in patterns:
        markdown_files.extend(glob.glob(os.path.join(directory, pattern)))
    
    # Also check for files with .md extension that might not match the pattern
    for file in os.listdir(directory):
        if file.endswith(('.md', '.markdown')) or file.lower().startswith('readme'):
            full_path = os.path.join(directory, file)
            if full_path not in markdown_files and os.path.isfile(full_path):
                markdown_files.append(full_path)
    
    return markdown_files

def read_markdown_file(file_path):
    """
    Read content from a markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def extract_badges_from_content(content, source_file=""):
    """
    Extract badge information from markdown content
    """
    if not content:
        return []
    
    badges = []
    
    # Pattern for markdown images: ![alt text](url)
    badge_pattern = r'!\[(.*?)\]\((.*?)\)'
    
    lines = content.split('\n')
    current_section = "General"
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Detect section headers
        if line.startswith('# '):
            current_section = line.lstrip('# ').strip()
        elif line.startswith('## '):
            current_section = line.lstrip('# ').strip()
        elif line.startswith('### '):
            current_section = line.lstrip('# ').strip()
        
        # Find badges in the current line
        matches = re.finditer(badge_pattern, line)
        for match in matches:
            alt_text = match.group(1)
            badge_url = match.group(2)
            
            # Skip if it's not a badge (simple heuristic)
            if is_likely_badge(badge_url, alt_text):
                badge_info = {
                    "technology": extract_tech_name(alt_text),
                    "badge_url": badge_url,
                    "markdown": match.group(0),
                    "alt_text": alt_text,
                    "section": current_section,
                    "source_file": source_file,
                    "line_number": line_num
                }
                badges.append(badge_info)
    
    return badges

def is_likely_badge(url, alt_text):
    """
    Determine if the image is likely a badge (not a regular image)
    """
    badge_indicators = [
        'shields.io', 'badge', 'img.shields', 'badges', 
        'travis-ci', 'github.io', 'coveralls', 'codacy',
        'version', 'license', 'downloads', 'stars'
    ]
    
    url_lower = url.lower()
    alt_lower = alt_text.lower()
    
    # Check URL for badge indicators
    for indicator in badge_indicators:
        if indicator in url_lower:
            return True
    
    # Check alt text for badge-related terms
    badge_alt_terms = ['badge', 'version', 'license', 'build', 'coverage']
    for term in badge_alt_terms:
        if term in alt_lower:
            return True
    
    # If it's a very short alt text and URL looks like a badge service
    if len(alt_text) < 30 and any(service in url_lower for service in ['shields', 'badge']):
        return True
    
    return False

def extract_tech_name(alt_text):
    """
    Extract technology name from alt text
    """
    if not alt_text:
        return "Unknown"
    
    # Remove common badge-related words
    remove_words = ['badge', 'icon', 'logo', 'shield', 'style', 
                   'for-the-badge', 'version', 'license', 'build',
                   'coverage', 'status', 'downloads']
    
    tech_name = alt_text.lower()
    for word in remove_words:
        tech_name = tech_name.replace(word, '')
    
    # Clean up: remove extra spaces, dashes, and special characters
    tech_name = re.sub(r'[^\w\s-]', '', tech_name)
    tech_name = re.sub(r'[-\s]+', ' ', tech_name).strip()
    
    # Capitalize if it looks like a proper name
    if tech_name and len(tech_name) > 1:
        if ' ' in tech_name:
            tech_name = ' '.join(word.capitalize() for word in tech_name.split())
        else:
            tech_name = tech_name.capitalize()
    
    return tech_name if tech_name else "Unknown Technology"

def categorize_badges(badges):
    """
    Organize badges into categories based on technology type
    """
    categories = {
        "programming_languages": [],
        "frameworks": [],
        "tools": [],
        "services": [],
        "devops": [],
        "social": [],
        "other": []
    }
    
    # Technology keywords for categorization
    programming_langs = ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 
                        'php', 'ruby', 'swift', 'kotlin', 'typescript', 'html', 'css']
    
    frameworks = ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'laravel',
                 'express', 'rails', 'bootstrap', 'tailwind', 'jquery']
    
    tools = ['git', 'github', 'gitlab', 'vscode', 'visual studio', 'docker', 'kubernetes',
            'postman', 'figma', 'photoshop', 'illustrator']
    
    services = ['aws', 'azure', 'google cloud', 'firebase', 'mongodb', 'mysql', 
               'postgresql', 'redis', 'nginx', 'apache']
    
    devops = ['docker', 'kubernetes', 'jenkins', 'travis', 'circleci', 'github actions',
             'gitlab ci', 'ansible', 'terraform', 'prometheus', 'grafana']
    
    social = ['twitter', 'linkedin', 'facebook', 'instagram', 'youtube', 'discord',
             'telegram', 'slack', 'reddit']
    
    for badge in badges:
        tech_name = badge["technology"].lower()
        categorized = False
        
        # Check each category
        for lang in programming_langs:
            if lang in tech_name:
                categories["programming_languages"].append(badge)
                categorized = True
                break
        
        if not categorized:
            for framework in frameworks:
                if framework in tech_name:
                    categories["frameworks"].append(badge)
                    categorized = True
                    break
        
        if not categorized:
            for tool in tools:
                if tool in tech_name:
                    categories["tools"].append(badge)
                    categorized = True
                    break
        
        if not categorized:
            for service in services:
                if service in tech_name:
                    categories["services"].append(badge)
                    categorized = True
                    break
        
        if not categorized:
            for devop in devops:
                if devop in tech_name:
                    categories["devops"].append(badge)
                    categorized = True
                    break
        
        if not categorized:
            for social_media in social:
                if social_media in tech_name:
                    categories["social"].append(badge)
                    categorized = True
                    break
        
        if not categorized:
            categories["other"].append(badge)
    
    # Remove empty categories
    return {category: badges for category, badges in categories.items() if badges}

def save_badges_to_json(categorized_badges, output_dir="badge_data"):
    """
    Save categorized badges to JSON files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    
    for category, badges in categorized_badges.items():
        filename = f"{category}.json"
        filepath = os.path.join(output_dir, filename)
        
        category_data = {
            "category": category.replace('_', ' ').title(),
            "badges_count": len(badges),
            "badges": badges
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        saved_files.append(filepath)
        print(f"✓ Saved {len(badges)} badges to {filepath}")
    
    return saved_files

def generate_summary(all_badges, categorized_badges, output_dir="badge_data"):
    """
    Generate a summary file with statistics
    """
    summary = {
        "total_badges_found": len(all_badges),
        "files_processed": list(set(badge["source_file"] for badge in all_badges)),
        "categories_summary": {
            category: len(badges) for category, badges in categorized_badges.items()
        },
        "unique_technologies": list(set(badge["technology"] for badge in all_badges))
    }
    
    summary_path = os.path.join(output_dir, "extraction_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Summary saved to {summary_path}")
    return summary_path

def main():
    """
    Main function to extract badges from local markdown files
    """
    print("🔍 Scanning for markdown files in current directory...")
    
    markdown_files = find_markdown_files()
    
    if not markdown_files:
        print("❌ No markdown files found in the current directory.")
        return
    
    print(f"📁 Found {len(markdown_files)} markdown file(s):")
    for file in markdown_files:
        print(f"  - {file}")
    
    all_badges = []
    
    for file_path in markdown_files:
        print(f"\n📖 Reading {file_path}...")
        content = read_markdown_file(file_path)
        
        if content:
            badges = extract_badges_from_content(content, os.path.basename(file_path))
            all_badges.extend(badges)
            print(f"  Found {len(badges)} badges")
        else:
            print(f"  ❌ Could not read file")
    
    if not all_badges:
        print("\n❌ No badges found in any markdown files.")
        return
    
    print(f"\n🎯 Total badges found: {len(all_badges)}")
    
    # Categorize badges
    print("📂 Categorizing badges...")
    categorized_badges = categorize_badges(all_badges)
    
    # Save to JSON files
    print("\n💾 Saving badges to JSON files...")
    saved_files = save_badges_to_json(categorized_badges)
    
    # Generate summary
    generate_summary(all_badges, categorized_badges)
    
    # Print final statistics
    print(f"\n✅ Extraction completed!")
    print(f"📊 Total badges extracted: {len(all_badges)}")
    print(f"📁 Categories created: {len(categorized_badges)}")
    print(f"📄 JSON files saved to: badge_data/")
    
    # Show category breakdown
    print("\n📋 Category breakdown:")
    for category, badges in categorized_badges.items():
        category_name = category.replace('_', ' ').title()
        print(f"  - {category_name}: {len(badges)} badges")

if __name__ == "__main__":
    main()
