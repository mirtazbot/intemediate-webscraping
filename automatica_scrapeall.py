from bs4 import BeautifulSoup
import json

# Read your HTML file
with open('hellcode_clean.txt', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Find all target divs
results = soup.find_all('div', class_='treffer-titel w-100')

# Build dictionary
output = {}
for div in results:
    a_tag = div.find('a')
    if a_tag and a_tag.get('href'):
        name = a_tag.get_text(strip=True)
        link = a_tag['href']
        output[name] = {"innerlink": link}

# Save to JSON
with open('automatica_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
