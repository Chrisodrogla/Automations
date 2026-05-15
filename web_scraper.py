import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

start_time = time.time()

# Specify the website to visit
website = 'https://www.onlinejobs.ph/jobseekers/jobsearch'
# website ='https://www.onlinejobs.ph/jobseekers/jobsearch/960'

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # This line makes Chrome run in headless mode

# Initialize the webdriver with the specified options
driver = webdriver.Chrome(options=chrome_options)

logger.info("Starting web scraper...")
logger.info(f"Navigating to {website}")

# Navigate to the website
driver.get(website)

link_visit = []

while True:
    # Find and store the links on the current page
    post_links = name_elements = driver.find_elements("xpath", '//div[@class="desc fs-14 d-none d-sm-block"]/a[1]')
    logger.info(f"Found {len(post_links)} links on current page")
    
    for post in post_links:
        href = post.get_attribute("href")
        link_visit.append(href)

    try:
        pagination = driver.find_element("xpath", '//a[@rel="next"]')
        logger.info("Next page found, clicking...")
        pagination.click()

    except NoSuchElementException:
        # If the next page link is not found, exit the loop
        logger.info("No more pages to visit")
        break

logger.info(f"Total links collected: {len(link_visit)}")

# use this code below to limit pagination

"""
num_pages_to_visit = 10

for _ in range(num_pages_to_visit):
    # Find and store the links on the current page
    post_links = name_elements = driver.find_elements("xpath", '//div[@class="desc fs-14 d-none d-sm-block"]/a[1]')
    for post in post_links:
        href = post.get_attribute("href")
        link_visit.append(href)

    try:
        pagination = driver.find_element("xpath", '//a[@rel="next"]')
        pagination.click()
    except NoSuchElementException:
        # If the next page link is not found, exit the loop
        break
"""

# Function to scrape information from a given URL
def scrape_data(url, partial_words):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check and extract description
    description_elem = soup.find('p', {'id': 'job-description'})
    if description_elem:
        description = description_elem.text
        logger.debug(f"[{url}] ✓ Description found")
    else:
        description = ''
        logger.warning(f"[{url}] ✗ Description element not found (id='job-description')")
    
    # Check and extract date
    date_elems = soup.find_all('p', {'class': 'fs-18'})
    if len(date_elems) > 3:
        date = date_elems[3].text
        logger.debug(f"[{url}] ✓ Date found at index [3]")
    else:
        date = ''
        logger.warning(f"[{url}] ✗ Date element not found - Expected at least 4 'fs-18' elements, found {len(date_elems)}")
    
    # Check and extract title
    title_wrapper = soup.find('div', class_=lambda x: x and 'col-12' in x and 'text-center' in x)
    if title_wrapper:
        h1_elem = title_wrapper.find('h1')
        if h1_elem:
            title = h1_elem.text.strip()
            logger.debug(f"[{url}] ✓ Title found")
        else:
            title = ''
            logger.warning(f"[{url}] ✗ H1 element not found inside title wrapper")
    else:
        title = ''
        logger.warning(f"[{url}] ✗ Title wrapper not found (div with 'col-12' and 'text-center')")

    # Check if any of the partial words are present in the description (case-insensitive)
    found_keywords = [word.lower() for word in partial_words if word.lower() in description.lower()]

    return {
        'url': url,
        'title': title,
        'date': date,
        'description': description,
        'found_keywords': found_keywords
    }

# List to store the scraped data dictionaries
data_list = []

# Load existing data from the JSON file
existing_data = []
try:
    with open('data_gathered.json', 'r') as json_file:
        existing_data = json.load(json_file)
        logger.info(f"Loaded {len(existing_data)} existing entries")
except FileNotFoundError:
    logger.info("No existing data file found, starting fresh")

# Set to store existing URLs for quick lookup
existing_urls = set(entry['url'] for entry in existing_data)

# Read keywords from the file
keywords_file_path = 'Keyword_Target.txt'
try:
    with open(keywords_file_path, 'r') as keywords_file:
        partial_words = [line.strip() for line in keywords_file]
    logger.info(f"Loaded {len(partial_words)} keywords: {partial_words}")
except FileNotFoundError:
    logger.error("Keyword_Target.txt not found!")
    partial_words = []

logger.info(f"Starting to scrape {len(link_visit)} URLs...")

for idx, url in enumerate(link_visit, 1):
    # Skip if URL already exists
    if url in existing_urls:
        logger.debug(f"[{idx}/{len(link_visit)}] Skipping URL (already scraped): {url}")
        continue

    logger.info(f"[{idx}/{len(link_visit)}] Scraping: {url}")
    
    try:
        data = scrape_data(url, partial_words)

        # Append new data to existing data only if keywords are found
        if data['found_keywords']:
            data_list.append(data)
            logger.info(f"[{idx}/{len(link_visit)}] ✓ Keywords found: {data['found_keywords']}")
        else:
            logger.info(f"[{idx}/{len(link_visit)}] ✗ No keywords found")

        time.sleep(2)  # Add a delay to avoid being blocked
    except Exception as e:
        logger.error(f"[{idx}/{len(link_visit)}] Error scraping data from {url}: {e}")


logger.info(f"Total new entries to add: {len(data_list)}")

# Append new data to existing data
existing_data.extend(data_list)

# Save the data to a JSON file
with open('data_gathered.json', 'w') as json_file:
    json.dump(existing_data, json_file, indent=2)

logger.info(f"Saved {len(existing_data)} total entries to data_gathered.json")

# Close the webdriver
driver.quit()
logger.info("Webdriver closed")

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

logger.info(f"Script completed in {elapsed_time:.4f} seconds")
print(f"\n{'='*60}")
print(f"Your code took {elapsed_time:.4f} seconds to run.")
print(f"Total links scraped: {len(link_visit)}")
print(f"New entries added: {len(data_list)}")
print(f"Total entries in database: {len(existing_data)}")
print(f"{'='*60}")
