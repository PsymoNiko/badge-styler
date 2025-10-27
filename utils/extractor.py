import json
import re
import os

def parse_markdown_badges(markdown_content):
    """
    More robust parser for the markdown badges format
    """
    categories = {}
    
    # Find all category sections
    pattern = r'### (.*?)\n\n(.*?)(?=### |\Z)'
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    
    for category_header, section_content in matches:
        # Clean category name
        category_name = re.sub(r'[^\w\s]', '', category_header).strip()
        
        # Extract badges from table
        badges = []
        table_pattern = r'\| [^\n]+\n\| [^\n]+\n((?:\| [^\n]+\n)*)'
        table_match = re.search(table_pattern, section_content)
        
        if table_match:
            rows = table_match.group(1).strip().split('\n')
            
            for row in rows:
                if row.strip() and '|' in row:
                    cells = [cell.strip() for cell in row.split('|')[1:-1]]
                    
                    if len(cells) >= 3:
                        name = cells[0]
                        badge = extract_badge_url(cells[1])
                        markdown = cells[2]
                        
                        if name and badge:
                            badges.append({
                                "name": name,
                                "badge": badge,
                                "markdown": markdown
                            })
        
        if badges:
            categories[category_name] = {
                "category": category_name,
                "badges": badges
            }
    
    return categories

def extract_badge_url(text):
    """
    Extract URL from various markdown formats
    """
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    
    # Try to extract from markdown image syntax first
    img_match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', text)
    if img_match:
        return img_match.group(1)
    
    # If no markdown syntax, return cleaned text
    return text.strip()

def save_categories(categories, output_dir="badge_categories"):
    """
    Save categories to JSON files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for category_name, data in categories.items():
        # Create safe filename
        filename = re.sub(r'[^a-zA-Z0-9_]', '_', category_name)
        filename = filename.lower() + '.json'
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Created: {filepath}")

# Usage
if __name__ == "__main__":
    # Read your markdown file
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract categories
    categories = parse_markdown_badges(content)
    
    # Save to JSON files
    save_categories(categories)
    
    print(f"\nTotal categories processed: {len(categories)}")
    for cat_name, cat_data in categories.items():
        print(f"  {cat_name}: {len(cat_data['badges'])} badge")
