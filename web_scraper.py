import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re

start_time = time.time()

# Specify the website to visit
website = 'https://www.onlinejobs.ph/jobseekers/jobsearch'
# website ='https://www.onlinejobs.ph/jobseekers/jobsearch/960'

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # This line makes Chrome run in headless mode
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

# Initialize the webdriver with the specified options
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

print("Starting web scraper...")
print(f"Navigating to {website}")

# Navigate to the website
driver.get(website)

link_visit = []

while True:
    try:
        # Wait for job links to load
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@class="desc fs-14 d-none d-sm-block"]/a[1]')
        ))
        
        # Find and store the links on the current page
        post_links = driver.find_elements(By.XPATH, '//div[@class="desc fs-14 d-none d-sm-block"]/a[1]')
        print(f"Found {len(post_links)} links on current page")
        
        for post in post_links:
            href = post.get_attribute("href")
            if href and href not in link_visit:
                link_visit.append(href)

        try:
            pagination = driver.find_element(By.XPATH, '//a[@rel="next"]')
            print("Next page found, clicking...")
            pagination.click()
            time.sleep(2)
        except NoSuchElementException:
            # If the next page link is not found, exit the loop
            print("No more pages to visit")
            break
            
    except TimeoutException:
        print("Timeout waiting for elements")
        break
    except Exception as e:
        print(f"Error during pagination: {e}")
        break

print(f"Total links collected: {len(link_visit)}")


# Function to scrape information from a given URL using Selenium
def scrape_data(url, partial_words):
    """
    Scrape job data by loading the page with Selenium 
    to ensure JavaScript is rendered before parsing with BeautifulSoup
    """
    driver2 = None
    try:
        # Open the URL with Selenium
        driver2 = webdriver.Chrome(options=chrome_options)
        driver2.get(url)
        
        # Wait for the page to load
        try:
            wait2 = WebDriverWait(driver2, 10)
            # Wait for job description to be present
            wait2.until(EC.presence_of_element_located(
                (By.ID, 'job-description')
            ))
            time.sleep(1)  # Extra wait for all content to render
        except TimeoutException:
            print(f"Timeout waiting for job description")
        
        # Now parse with BeautifulSoup
        soup = BeautifulSoup(driver2.page_source, 'html.parser')
        
        # Print first 100 characters of the response HTML
        print(soup.prettify()[:100])
        
        # Extract description
        description = ''
        description_elem = soup.find('p', {'id': 'job-description'})
        if description_elem:
            description = description_elem.text.strip()
        else:
            print(f"Description not found")
        
        # Extract date
        date = ''
        date_elems = soup.find_all('p', {'class': 'fs-18'})
        
        if len(date_elems) > 3:
            date = date_elems[3].text.strip()
        elif len(date_elems) > 0:
            date = date_elems[-1].text.strip()
        else:
            # Try regex to find date
            all_text = soup.get_text()
            date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
            date_match = re.search(date_pattern, all_text)
            if date_match:
                date = date_match.group(0)
        
        # Extract title
        title = ''
        
        # Method 1: Look for h1 with job__title class
        h1_job = soup.find('h1', {'class': 'job__title'})
        if h1_job:
            title = h1_job.text.strip()
        else:
            # Method 2: Look for h1 in div with col-12 and text-center
            title_wrapper = soup.find('div', class_=lambda x: x and 'col-12' in x and 'text-center' in x)
            if title_wrapper:
                h1_elem = title_wrapper.find('h1')
                if h1_elem:
                    title = h1_elem.text.strip()
            else:
                # Method 3: Look for any h1 tag
                h1_any = soup.find('h1')
                if h1_any:
                    title = h1_any.text.strip()

        # Check if any of the partial words are present in the description (case-insensitive)
        found_keywords = [
            word.lower() for word in partial_words 
            if word.lower() in description.lower()
        ]

        return {
            'url': url,
            'title': title,
            'date': date,
            'description': description,
            'found_keywords': found_keywords
        }
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            'url': url,
            'title': '',
            'date': '',
            'description': '',
            'found_keywords': []
        }
    
    finally:
        if driver2:
            try:
                driver2.quit()
            except:
                pass


# List to store the scraped data dictionaries
data_list = []

# Load existing data from the JSON file
existing_data = []
try:
    with open('data_gathered.json', 'r') as json_file:
        existing_data = json.load(json_file)
        print(f"Loaded {len(existing_data)} existing entries")
except FileNotFoundError:
    print("No existing data file found, starting fresh")

# Set to store existing URLs for quick lookup
existing_urls = set(entry['url'] for entry in existing_data)

# Read keywords from the file
keywords_file_path = 'Keyword_Target.txt'
try:
    with open(keywords_file_path, 'r') as keywords_file:
        partial_words = [line.strip() for line in keywords_file if line.strip()]
    print(f"Loaded {len(partial_words)} keywords")
except FileNotFoundError:
    print("Keyword_Target.txt not found!")
    partial_words = []

print(f"Starting to scrape {len(link_visit)} URLs...")

for idx, url in enumerate(link_visit, 1):
    # Skip if URL already exists
    if url in existing_urls:
        print(f"[{idx}/{len(link_visit)}] Skipping URL (already scraped)")
        continue

    print(f"[{idx}/{len(link_visit)}] Scraping: {url}")
    
    data = scrape_data(url, partial_words)

    # Append new data to existing data only if keywords are found
    if data['found_keywords']:
        data_list.append(data)
        print(f"[{idx}/{len(link_visit)}] ✓ Keywords found: {data['found_keywords']}")
    else:
        print(f"[{idx}/{len(link_visit)}] ✗ No keywords found")

    time.sleep(2)  # Add a delay to avoid being blocked


print(f"Total new entries: {len(data_list)}")

# Append new data to existing data
existing_data.extend(data_list)

# Save the data to a JSON file
with open('data_gathered.json', 'w') as json_file:
    json.dump(existing_data, json_file, indent=2)

print(f"Saved {len(existing_data)} total entries to data_gathered.json")

# Close the webdriver
driver.quit()
print("Webdriver closed")

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Your code took {elapsed_time:.4f} seconds to run.")
