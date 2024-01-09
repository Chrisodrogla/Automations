import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Specify the website to visit
website = 'https://www.onlinejobs.ph/jobseekers/jobsearch'

# Initialize the webdriver
driver = webdriver.Chrome()

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
        break """

# Function to scrape information from a given URL
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    description = soup.find('p', {'id': 'job-description'}).text
    date = soup.find_all('p', {'class': 'fs-18'})[3].text
    title = soup.find('h1', {'class': 'fs-24 fw-600 text-white text-center mb-40'}).text

    return {
        'url': url,
        'title': title,
        'date': date,
        'description': description
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

# Loop through each link and scrape data
for url in link_visit:
    # Skip if URL already exists
    if url in existing_urls:
        continue

    try:
        data = scrape_data(url)

        # Check if any of the partial words are present in the description (case-insensitive)
        if any(word.lower() in data['description'].lower() for word in partial_words):
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
