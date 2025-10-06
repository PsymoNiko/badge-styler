import re
import json

def extract_badge_categories(readme_content):
    """
    Extract all badge categories and their badges from the README.md content
    """
    categories = {}
    
    # Split content by category headers (###)
    category_sections = re.split(r'### .+', readme_content)
    category_headers = re.findall(r'### (.+)', readme_content)
    
    # The first section is the header/content before badges
    # Align categories with their content
    for i, header in enumerate(category_headers):
        if i < len(category_sections) - 1:
            category_content = category_sections[i + 1]
            badges = extract_badges_from_section(category_content)
            if badges:  # Only add categories that have badges
                categories[header.strip()] = badges
    
    return categories

def extract_badges_from_section(section_content):
    """
    Extract badge information from a category section
    """
    badges = []
    
    # Find table rows in the section
    table_rows = re.findall(r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \|', section_content)
    
    for row in table_rows:
        name = row[0].strip()
        badge_markdown = row[2].strip().strip('`')
        
        # Extract badge URL from markdown
        badge_url_match = re.search(r'!\[.*?\]\((.*?)\)', badge_markdown)
        if badge_url_match:
            badge_url = badge_url_match.group(1)
            badges.append({
                "name": name,
                "badge_url": badge_url,
                "markdown": badge_markdown
            })
    
    return badges

def main():
    # Read the README.md file
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the start of the badges section
    badges_start = content.find('# Badges')
    if badges_start == -1:
        print("Badges section not found!")
        return
    
    badges_content = content[badges_start:]
    
    # Extract all categories and badges
    categories = extract_badge_categories(badges_content)
    
    # Print summary
    print(f"Total categories found: {len(categories)}")
    print("\nCategories:")
    for category_name, badges in categories.items():
        print(f"  - {category_name}: {len(badges)} badges")
    
    # Save to JSON file
    with open('badges_categories.json', 'w', encoding='utf-8') as json_file:
        json.dump(categories, json_file, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to badges_categories.json")
    
    # Also create a simplified version with just category names and counts
    category_summary = {
        category: len(badges) for category, badges in categories.items()
    }
    
    with open('categories_summary.json', 'w', encoding='utf-8') as summary_file:
        json.dump(category_summary, summary_file, indent=2, ensure_ascii=False)
    
    print(f"Summary saved to categories_summary.json")

if __name__ == "__main__":
    main()
