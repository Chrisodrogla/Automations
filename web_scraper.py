import time
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
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

# Print all collected links
print(link_visit)
print(len(link_visit))