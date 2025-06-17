import pandas as pd
import json

with open("automatica_final.json", "r", encoding="utf-8") as file:
        data = json.load(file)

# Converting to DataFrame
companies = []
links = []
websites = []

for company, info in data.items():
    companies.append(company)
    links.append(info["innerlink"])
    websites.append(info["website"])

df = pd.DataFrame({
    'Company': companies,
    'Link': links,
    'Website': websites
})

# Display the DataFrame
df.to_csv("automatica_exhibitor.csv", index=False)
