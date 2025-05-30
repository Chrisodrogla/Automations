import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

start_time = time.time()

# Specify the website to visit
website = 'https://www.onlinejobs.ph/jobseekers/jobsearch'
# website ='https://www.onlinejobs.ph/jobseekers/jobsearch/960'

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # This line makes Chrome run in headless mode

# Initialize the webdriver with the specified options
driver = webdriver.Chrome(options=chrome_options)


# Navigate to the website
driver.get(website)

link_visit = []



while True:
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

    description = soup.find('p', {'id': 'job-description'}).text
    date = soup.find_all('p', {'class': 'fs-18'})[3].text
    # title = soup.find('div', {'class': 'col-12 text-center'}).find('h1').text
    title_wrapper = soup.find('div', class_=lambda x: x and 'col-12' in x and 'text-center' in x)
    title = title_wrapper.find('h1').text.strip() if title_wrapper else ''


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
except FileNotFoundError:
    pass

# Set to store existing URLs for quick lookup
existing_urls = set(entry['url'] for entry in existing_data)

# Read keywords from the file
keywords_file_path = 'Keyword_Target.txt'
with open(keywords_file_path, 'r') as keywords_file:
    partial_words = [line.strip() for line in keywords_file]

for url in link_visit:
    # Skip if URL already exists
    if url in existing_urls:
        continue

    try:
        data = scrape_data(url, partial_words)

        # Append new data to existing data only if keywords are found
        if data['found_keywords']:
            data_list.append(data)

        time.sleep(2)  # Add a delay to avoid being blocked
    except Exception as e:
        print(f"Error scraping data from {url}: {e}")


# Append new data to existing data
existing_data.extend(data_list)

# Save the data to a JSON file
with open('data_gathered.json', 'w') as json_file:
    json.dump(existing_data, json_file, indent=2)

# Close the webdriver
driver.quit()
# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Your code took {elapsed_time:.4f} seconds to run.")