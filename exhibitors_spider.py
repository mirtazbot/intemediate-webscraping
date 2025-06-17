from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import Spider
import scrapy
from bs4 import BeautifulSoup

class ExhibitorsSpider(scrapy.Spider):
    name = "exhibitors"
    
    def __init__(self, *args, **kwargs):
        super(ExhibitorsSpider, self).__init__(*args, **kwargs)
        # Open the file for writing results in the constructor
        self.output_file = open("scraped_data.txt", "w", encoding="utf-8")
    
    # Close the file when spider finishes
    def close(self, reason):
        if hasattr(self, 'output_file'):
            self.output_file.close()

    def start_requests(self):
        # URL to scrape
        url = "https://www.automateshow.com/exhibitors/4ir-solutions"
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # Log the URL to confirm we're scraping the right page
        self.log(f"Scraping page: {response.url}")
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <p> tags in the page
        p_tags = soup.find_all('p')
        
        website_found = False  # Flag to track if a website is found
        
        # Loop through each <p> tag
        for p_tag in p_tags:
            # Write the raw HTML of each <p> tag to the file
            self.output_file.write(f"Found <p> tag: {p_tag.prettify()}\n")
            
            # Check if it contains an <a> tag with href
            a_tag = p_tag.find('a', href=True)  # Find <a> tag with href attribute
            if a_tag:
                website = a_tag['href']  # Get the href value
                self.output_file.write(f"Found website: {website}\n")  # Write the website link to the file
                website_found = True
                break  # Exit the loop once a link is found
        
        # If no link is found, print that
        if not website_found:
            self.output_file.write("No website link found in any <p> tag\n")

        # Return the result
        yield {
            "website": website if website_found else 'N/A'
        }

# Run Scrapy from within the script
if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(ExhibitorsSpider)
    process.start()