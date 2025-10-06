import requests
import json
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_readme_content(repo_url):
    """
    Fetch README content from a GitHub repository
    """
    # Convert GitHub repo URL to raw README content URL
    repo_url = repo_url.rstrip('/')
    if repo_url.startswith('https://github.com/'):
        username_repo = repo_url.replace('https://github.com/', '')
        raw_url = f"https://raw.githubusercontent.com/{username_repo}/main/README.md"
        # Try common branch names if main fails
        for branch in ['main', 'master', 'trunk']:
            test_url = f"https://raw.githubusercontent.com/{username_repo}/{branch}/README.md"
            response = requests.get(test_url)
            if response.status_code == 200:
                return response.text
    else:
        response = requests.get(repo_url)
        if response.status_code == 200:
            return response.text
    
    print(f"Error: Could not fetch README from {repo_url}")
    return None

def extract_badges_by_category(readme_content):
    """
    Extract badge information organized by category from README content
    """
    if not readme_content:
        return {}
    
    categories = {}
    current_category = "Uncategorized"
    
    # Split content by lines for processing
    lines = readme_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect category headings (usually H2 or H3 in markdown)
        if line.startswith('## ') or line.startswith('### '):
            current_category = line.lstrip('# ').strip()
            if current_category not in categories:
                categories[current_category] = []
        
        # Look for markdown images (badges) - pattern: ![alt](url)
        badge_match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
        if badge_match:
            alt_text = badge_match.group(1)
            badge_url = badge_match.group(2)
            
            # Extract technology name from alt text or surrounding context
            tech_name = extract_tech_name(alt_text, line)
            
            badge_info = {
                "technology": tech_name,
                "badge_url": badge_url,
                "markdown": badge_match.group(0),
                "alt_text": alt_text
            }
            
            categories[current_category].append(badge_info)
        
        i += 1
    
    # Remove empty categories
    return {category: badges for category, badges in categories.items() if badges}

def extract_tech_name(alt_text, full_line):
    """
    Extract technology name from alt text or surrounding context
    """
    # Clean the alt text
    tech_name = alt_text.lower()
    
    # Remove common badge-related words
    remove_words = ['badge', 'icon', 'logo', 'shield', 'style', 'for-the-badge']
    for word in remove_words:
        tech_name = tech_name.replace(word, '')
    
    # Clean up extra spaces and dashes
    tech_name = re.sub(r'[-\s]+', ' ', tech_name).strip()
    
    # If alt text doesn't give good name, try to extract from surrounding text
    if not tech_name or len(tech_name) < 2:
        # Look for technology names in the line
        tech_pattern = r'\[(.*?)\]'  # Text in brackets before badge
        bracket_match = re.search(tech_pattern, full_line)
        if bracket_match:
            tech_name = bracket_match.group(1).strip()
    
    # Capitalize first letter of each word if it's multi-word
    if tech_name and ' ' in tech_name:
        tech_name = ' '.join(word.capitalize() for word in tech_name.split())
    elif tech_name:
        tech_name = tech_name.capitalize()
    
    return tech_name if tech_name else "Unknown Technology"

def save_badges_to_json(categories_badges, output_dir="badge_categories"):
    """
    Save badges to separate JSON files organized by category
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    
    for category, badges in categories_badges.items():
        # Create safe filename from category name
        safe_category = re.sub(r'[^\w\s-]', '', category)
        safe_category = re.sub(r'[-\s]+', '_', safe_category)
        filename = f"{safe_category.lower()}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Prepare data for JSON
        category_data = {
            "category_name": category,
            "badges_count": len(badges),
            "badges": badges
        }
        
        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        saved_files.append(filepath)
        print(f"Saved {len(badges)} badges to {filepath}")
    
    return saved_files

def generate_summary(categories_badges, output_dir="badge_categories"):
    """
    Generate a summary file with overview of all categories
    """
    summary = {
        "total_categories": len(categories_badges),
        "total_badges": sum(len(badges) for badges in categories_badges.values()),
        "categories": {}
    }
    
    for category, badges in categories_badges.items():
        summary["categories"][category] = len(badges)
    
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Summary saved to {summary_path}")
    return summary_path

def main():
    """
    Main function to orchestrate the badge extraction process
    """
    #target_repo = "https://github.com/PsymoNiko/badge-styler"
    target_repo = "https://github.com/Ileriayo/markdown-badges"
    
    print(f"Fetching README from: {target_repo}")
    readme_content = fetch_readme_content(target_repo)
    
    if not readme_content:
        print("Failed to fetch README content. Exiting.")
        return
    
    print("Extracting badges by category...")
    categories_badges = extract_badges_by_category(readme_content)
    
    if not categories_badges:
        print("No badges found in the README.")
        return
    
    print(f"Found {len(categories_badges)} categories with badges")
    
    # Save badges to JSON files
    saved_files = save_badges_to_json(categories_badges)
    
    # Generate summary
    generate_summary(categories_badges)
    
    print(f"\nExtraction completed successfully!")
    print(f"Total categories processed: {len(categories_badges)}")
    print(f"Total badges found: {sum(len(badges) for badges in categories_badges.values())}")
    print(f"JSON files saved to 'badge_categories' directory")

if __name__ == "__main__":
    main()
