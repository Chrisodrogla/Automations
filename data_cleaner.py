import json
from datetime import datetime

# Define the date threshold (January 2025)
date_threshold = datetime(2025, 1, 1)

# Function to clean and filter data based on the date
def clean_data(data, threshold_date):
    cleaned_data = []
    
    for item in data:
        # Remove leading/trailing spaces and parse the date
        job_date_str = item['date'].strip()
        
        # Try to parse the date, if the format is invalid, skip the item
        try:
            # Adjusted date format: "%b %d, %Y" (e.g., Mar 11, 2025)
            job_date = datetime.strptime(job_date_str, "%b %d, %Y")
            # Add the item if the date is after the threshold
            if job_date >= threshold_date:
                cleaned_data.append(item)
        except ValueError:
            # If date parsing fails, skip this item
            print(f"Invalid date format for {item['title']}")

    return cleaned_data

# Load the JSON data from the file
with open('data_gathered.json', 'r') as file:
    data = json.load(file)

# Clean the data by removing outdated entries
filtered_data = clean_data(data, date_threshold)

# Save the filtered data to a new file
with open('cleaned_HELLOJSON.json', 'w') as file:
    json.dump(filtered_data, file, indent=4)

print("Data cleaned and saved to 'cleaned_HELLOJSON.json'.")
