import re
import sys

import requests
from markdown_table_parser import parse_markdown_table


def validate_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def validate_table_row(row):
    errors = []
    
    # Check if all required fields are present
    required_fields = ['Agent', 'Framework', 'Source', 'Character File', 'Developer']
    for field in required_fields:
        if not row.get(field) or row[field].strip() == '':
            errors.append(f"Missing {field}")
    
    # Validate GitHub links
    if 'Source' in row:
        source_url = re.findall(r'\((.*?)\)', row['Source'])
        if source_url and not source_url[0].startswith('https://github.com/'):
            errors.append("Source must be a GitHub URL")
        if source_url and not validate_url(source_url[0]):
            errors.append("Source URL is not accessible")
    
    # Validate Character File link
    if 'Character File' in row:
        char_url = re.findall(r'\((.*?)\)', row['Character File'])
        if char_url and not validate_url(char_url[0]):
            errors.append("Character File URL is not accessible")
    
    return errors

def main():
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Parse the markdown table
    tables = parse_markdown_table(content)
    if not tables:
        print("ERROR: No table found in README.md")
        sys.exit(1)
    
    table = tables[0]  # Assume first table is our target
    
    has_errors = False
    for row in table:
        errors = validate_table_row(row)
        if errors:
            print(f"Errors in row for {row.get('Agent', 'Unknown Agent')}:")
            for error in errors:
                print(f"  - {error}")
            has_errors = True
    
    if has_errors:
        sys.exit(1)
    else:
        print("Table validation passed!")

if __name__ == "__main__":
    main()