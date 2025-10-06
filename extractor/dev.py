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
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def extract_badges_by_exact_categories(content, source_file=""):
    """
    Extract badges using the exact category structure provided
    """
    if not content:
        return {}
    
    # Define the exact categories from your list
    exact_categories = {
        "artificial_intelligence_and_bots": "Artificial Intelligence and Bots",
        "blog": "Blog",
        "blockchain": "Blockchain", 
        "browsers": "Browsers",
        "cd": "CD",
        "ci": "CI",
        "cloud_storage": "Cloud Storage",
        "cryptocurrency": "Cryptocurrency",
        "databases": "Databases",
        "design": "Design",
        "developer_forums": "Developer/Forums",
        "documentation_platforms": "Documentation Platforms",
        "education": "Education",
        "funding": "Funding",
        "frameworks_platforms_and_libraries": "Frameworks, Platforms and Libraries",
        "gaming": "Gaming",
        "game_consoles": "Game Consoles",
        "hosting_saas": "Hosting/SaaS",
        "ides_editors": "IDEs/Editors",
        "languages": "Languages",
        "ml_dl": "ML/DL",
        "music": "Music",
        "office": "Office",
        "operating_system": "Operating System",
        "orm": "ORM",
        "other": "Other",
        "quantum_programming_frameworks_and_libraries": "Quantum Programming Frameworks and Libraries",
        "search_engines": "Search Engines",
        "servers": "Servers",
        "smartphone_brands": "Smartphone Brands",
        "social": "Social",
        "store": "Store",
        "streaming": "Streaming",
        "testing": "Testing",
        "version_control": "Version Control",
        "wearables": "Wearables",
        "work_jobs": "Work/Jobs"
    }
    
    categories_badges = {key: [] for key in exact_categories.keys()}
    current_category = None
    
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check if this line matches any of our exact categories
        for category_key, category_name in exact_categories.items():
            # Look for category headers in various markdown formats
            patterns = [
                f"# {category_name}",
                f"## {category_name}", 
                f"### {category_name}",
                f"#### {category_name}",
                f"**{category_name}**",
                f"- {category_name}",
                f"* {category_name}"
            ]
            
            for pattern in patterns:
                if pattern in line:
                    current_category = category_key
                    break
            
            # Also check for category in table of contents links
            if f"[{category_name}]" in line:
                current_category = category_key
                break
        
        # If we found a category, look for badges in subsequent lines
        if current_category:
            badge_match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if badge_match:
                alt_text = badge_match.group(1)
                badge_url = badge_match.group(2)
                
                if is_likely_badge(badge_url, alt_text):
                    badge_info = {
                        "technology": extract_tech_name(alt_text),
                        "badge_url": badge_url,
                        "markdown": badge_match.group(0),
                        "alt_text": alt_text,
                        "source_file": source_file,
                        "line_number": line_num
                    }
                    
                    categories_badges[current_category].append(badge_info)
    
    return categories_badges

def is_likely_badge(url, alt_text):
    """
    Determine if the image is likely a badge
    """
    badge_indicators = [
        'shields.io', 'badge', 'img.shields', 'badges', 
        'travis-ci', 'github.io', 'coveralls', 'codacy',
        'version', 'license', 'downloads', 'stars'
    ]
    
    url_lower = url.lower()
    alt_lower = alt_text.lower()
    
    for indicator in badge_indicators:
        if indicator in url_lower:
            return True
    
    badge_alt_terms = ['badge', 'version', 'license', 'build', 'coverage']
    for term in badge_alt_terms:
        if term in alt_lower:
            return True
    
    if len(alt_text) < 30 and any(service in url_lower for service in ['shields', 'badge']):
        return True
    
    return False

def extract_tech_name(alt_text):
    """
    Extract technology name from alt text
    """
    if not alt_text:
        return "Unknown"
    
    remove_words = ['badge', 'icon', 'logo', 'shield', 'style', 
                   'for-the-badge', 'version', 'license', 'build',
                   'coverage', 'status', 'downloads']
    
    tech_name = alt_text.lower()
    for word in remove_words:
        tech_name = tech_name.replace(word, '')
    
    tech_name = re.sub(r'[^\w\s-]', '', tech_name)
    tech_name = re.sub(r'[-\s]+', ' ', tech_name).strip()
    
    if tech_name and len(tech_name) > 1:
        if ' ' in tech_name:
            tech_name = ' '.join(word.capitalize() for word in tech_name.split())
        else:
            tech_name = tech_name.capitalize()
    
    return tech_name if tech_name else "Unknown Technology"

def save_badges_to_json(categories_badges, output_dir="badge_categories"):
    """
    Save badges to JSON files using the exact category names
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    
    # Map of internal keys to display names
    category_display_names = {
        "artificial_intelligence_and_bots": "Artificial Intelligence and Bots",
        "blog": "Blog",
        "blockchain": "Blockchain", 
        "browsers": "Browsers",
        "cd": "CD",
        "ci": "CI",
        "cloud_storage": "Cloud Storage",
        "cryptocurrency": "Cryptocurrency",
        "databases": "Databases",
        "design": "Design",
        "developer_forums": "Developer/Forums",
        "documentation_platforms": "Documentation Platforms",
        "education": "Education",
        "funding": "Funding",
        "frameworks_platforms_and_libraries": "Frameworks, Platforms and Libraries",
        "gaming": "Gaming",
        "game_consoles": "Game Consoles",
        "hosting_saas": "Hosting/SaaS",
        "ides_editors": "IDEs/Editors",
        "languages": "Languages",
        "ml_dl": "ML/DL",
        "music": "Music",
        "office": "Office",
        "operating_system": "Operating System",
        "orm": "ORM",
        "other": "Other",
        "quantum_programming_frameworks_and_libraries": "Quantum Programming Frameworks and Libraries",
        "search_engines": "Search Engines",
        "servers": "Servers",
        "smartphone_brands": "Smartphone Brands",
        "social": "Social",
        "store": "Store",
        "streaming": "Streaming",
        "testing": "Testing",
        "version_control": "Version Control",
        "wearables": "Wearables",
        "work_jobs": "Work/Jobs"
    }
    
    for category_key, badges in categories_badges.items():
        if badges:  # Only create files for categories that have badges
            display_name = category_display_names.get(category_key, category_key)
            filename = f"{category_key}.json"
            filepath = os.path.join(output_dir, filename)
            
            category_data = {
                "category_name": display_name,
                "badges_count": len(badges),
                "badges": badges
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
            
            saved_files.append(filepath)
            print(f"✓ Saved {len(badges)} badges to {filepath}")
    
    return saved_files

def generate_summary(categories_badges, output_dir="badge_categories"):
    """
    Generate a summary file with overview of all categories
    """
    total_badges = sum(len(badges) for badges in categories_badges.values())
    categories_with_badges = {cat: len(badges) for cat, badges in categories_badges.items() if badges}
    
    summary = {
        "total_categories_with_badges": len(categories_with_badges),
        "total_badges_found": total_badges,
        "categories_breakdown": categories_with_badges,
        "files_processed": list(set(
            badge["source_file"] 
            for badges in categories_badges.values() 
            for badge in badges
        ))
    }
    
    summary_path = os.path.join(output_dir, "extraction_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Summary saved to {summary_path}")
    return summary_path

def main():
    """
    Main function to extract badges using exact categories
    """
    print("🔍 Scanning for markdown files in current directory...")
    
    markdown_files = find_markdown_files()
    
    if not markdown_files:
        print("❌ No markdown files found in the current directory.")
        return
    
    print(f"📁 Found {len(markdown_files)} markdown file(s):")
    for file in markdown_files:
        print(f"  - {file}")
    
    all_categories_badges = {}
    
    # Initialize all categories with empty lists
    exact_categories = [
        "artificial_intelligence_and_bots", "blog", "blockchain", "browsers", "cd", "ci",
        "cloud_storage", "cryptocurrency", "databases", "design", "developer_forums",
        "documentation_platforms", "education", "funding", "frameworks_platforms_and_libraries",
        "gaming", "game_consoles", "hosting_saas", "ides_editors", "languages", "ml_dl",
        "music", "office", "operating_system", "orm", "other", 
        "quantum_programming_frameworks_and_libraries", "search_engines", "servers",
        "smartphone_brands", "social", "store", "streaming", "testing", "version_control",
        "wearables", "work_jobs"
    ]
    
    for category in exact_categories:
        all_categories_badges[category] = []
    
    for file_path in markdown_files:
        print(f"\n📖 Reading {file_path}...")
        content = read_markdown_file(file_path)
        
        if content:
            file_categories = extract_badges_by_exact_categories(content, os.path.basename(file_path))
            
            # Merge badges from this file into the main collection
            for category, badges in file_categories.items():
                all_categories_badges[category].extend(badges)
            
            badges_count = sum(len(badges) for badges in file_categories.values())
            print(f"  Found {badges_count} badges across categories")
        else:
            print(f"  ❌ Could not read file")
    
    total_badges = sum(len(badges) for badges in all_categories_badges.values())
    
    if total_badges == 0:
        print("\n❌ No badges found in any markdown files.")
        return
    
    print(f"\n🎯 Total badges found: {total_badges}")
    
    # Save to JSON files
    print("\n💾 Saving badges to JSON files by category...")
    saved_files = save_badges_to_json(all_categories_badges)
    
    # Generate summary
    generate_summary(all_categories_badges)
    
    # Print final statistics
    categories_with_badges = {cat: len(badges) for cat, badges in all_categories_badges.items() if badges}
    
    print(f"\n✅ Extraction completed!")
    print(f"📊 Total badges extracted: {total_badges}")
    print(f"📁 Categories with badges: {len(categories_with_badges)}")
    print(f"📄 JSON files saved to: badge_categories/")
    
    print("\n📋 Categories with badges found:")
    for category, count in categories_with_badges.items():
        category_name = category.replace('_', ' ').title()
        print(f"  - {category_name}: {count} badges")

if __name__ == "__main__":
    main()
