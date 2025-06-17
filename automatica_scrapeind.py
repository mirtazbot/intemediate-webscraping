import json
import cloudscraper
from bs4 import BeautifulSoup
import concurrent.futures
import requests
from time import sleep

def get_first_link(innerlink):
    """
    Fetch the page at `innerlink` bypassing Cloudflare,
    parse the HTML, find the first <p> tag,
    and then return the href of the first <a> tag within.
    If no valid <a> is found, return None.
    
    Retries 3 times if a read timeout occurs.
    """
    scraper = cloudscraper.create_scraper()  # Bypass Cloudflare protection
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            response = scraper.get(innerlink, timeout=15)
            if response.status_code != 200:
                print(f"Failed to retrieve {innerlink}: HTTP {response.status_code}")
                return None
            # Successfully retrieved the page, so break out of retry loop.
            break
        except Exception as e:
            # Check if the exception is a timeout
            if "Read timed out" in str(e) or isinstance(e, requests.exceptions.ReadTimeout):
                attempt += 1
                print(f"Timeout error on {innerlink}, attempt {attempt} of {max_attempts}: {e}")
                if attempt < max_attempts:
                    sleep(1)  # Optionally, wait one second before retrying
                else:
                    # Raise an exception if maximum attempts are reached.
                    raise Exception(f"Max retries reached for timeout: {innerlink}") from e
            else:
                # If the error is not a read timeout, propagate the exception.
                raise

    soup = BeautifulSoup(response.text, 'html.parser')
    ul = soup.find('ul', class_='exhibitordetails-contactinfo-list')
    if ul:
        li_tags = ul.find_all('li')
        for li in li_tags:
            a_tag = li.find('a')
            if a_tag:
                href = a_tag.get('href', '')
                if href.startswith("https://"):
                    return href
    return None


def process_item(name, info):
    """
    Process a single dictionary entry by scraping its innerlink.
    Returns a tuple (name, website) where website is the scraped link
    or None if not found.
    """
    innerlink = info.get('innerlink')
    if not innerlink:
        return name, None
    website = get_first_link(innerlink)  # May raise exception if retries fail
    return name, website

def main():
    # Load the data from test.json
    with open("automatica_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    total_items = len(data)
    processed = 0
    error_list = []

    # Process each link concurrently using a thread pool.
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_name = {
            executor.submit(process_item, name, info): name
            for name, info in data.items()
        }
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                _, website = future.result()
                data[name]['website'] = website
            except Exception as exc:
                print(f"Error processing {name}: {exc}")
                data[name]['website'] = None
                error_list.append(name)
            processed += 1
            print(f"Progress: {processed} out of {total_items} processed. Remaining: {total_items - processed}")

    # Write the final updated dictionary to final.json
    with open("automatica_final.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    # Write the error list to errors.txt
    with open("errors.txt", "w", encoding="utf-8") as errfile:
        for error_name in error_list:
            errfile.write(error_name + "\n")

if __name__ == "__main__":
    main()
