import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import re

# List of ScraperAPI keys
scraperapi_keys = [                      
    '<YOUR_API_KEY_1>',  # Replace with actual ScraperAPI keys when running the code
    '<YOUR_API_KEY_2>',
    '<YOUR_API_KEY_3>',
    '<YOUR_API_KEY_4>',
]

def get_random_scraperapi_key():
    return random.choice(scraperapi_keys)

# Function to send a request with retries, random user agents, and ScraperAPI
def send_request_with_scraperapi(url):
    headers = {
        "User-Agent": random.choice([
            "<YOUR_USER_AGENT_1>",
            "<YOUR_USER_AGENT_2>",
            "<YOUR_USER_AGENT_3>",
            "<YOUR_USER_AGENT_4>",
        ])
    }

    for _ in range(5):  # Try up to 5 times
        try:
            scraperapi_key = get_random_scraperapi_key()
            response = requests.get(f'http://api.scraperapi.com?api_key={scraperapi_key}&url={url}', headers=headers, timeout=30)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                return response
        except Exception as e:
            print(f"Error with ScraperAPI: {e}")
        time.sleep(random.uniform(1, 5))  # Random sleep between 1 to 5 seconds

    return None

# Function to scrape
def scrape_page(page_number):
    url = f"https://resume.jobpub.com/new_xsearch_resume2.asp?no={page_number}"
    response = send_request_with_scraperapi(url)

    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        data = []

        # Extract resume entries
        resume_entries = soup.find_all('tr')
        print(f"Found {len(resume_entries)} job entries on page {page_number}.")

        for idx, entry in enumerate(resume_entries):
            try:
                resume_title = 'N/A'
                resume_url = 'N/A'
                gender = 'N/A'
                age = 'N/A'
                highest_education_level = 'N/A'
                field_of_study = 'N/A'
                institution = 'N/A'
                gpa = 'N/A'
                experience_year = 'N/A'
                desired_salary = 'N/A'
                location = 'N/A'
                latest_active_date = 'N/A'

                # Extract resume title & resume url
                resume_title_info = entry.find('a', target="_blank", style="text-decoration: none")
                resume_title = resume_title_info.find('font').text.strip()
                if resume_title_info and 'href' in resume_title_info.attrs:
                    resume_url = resume_title_info['href']

                # Extract gender
                gender = entry.find('font', color="#0000ff").text.strip()

                # Extract age (year): regular expression (regex)
                age_text = entry.get_text()  # Extract all text for inspection
                match = re.search(r'อายุ\s+(\d+)\s*ปี', age_text)  # Adjusted regex for flexibility
                if match:
                    age = match.group(1)

                # Extract the highest_education_level: regular expression (regex)
                education1 = entry.get_text()  # Extract all text for inspection
                match = re.search(r'วุฒิ\s*(.*?)\s*สาขา', education1)  # Adjusted regex for flexibility
                if match:
                    highest_education_level = match.group(1)

                # Extract the field_of_study
                field_of_study_u = entry.find('u')
                field_of_study = field_of_study_u.find('font', color="#008080").text.strip()

                # Extract the institution name: regex (pattern matching)
                html_content = str(entry)  # str(entry) converts the full HTML structure into a string format

                pattern = r'<font color="#0066ff">\s*<b>\s*(.*?)\s*</b>\s*</font>'  # regex (pattern matching)
                institutions = re.findall(pattern, html_content)

                if institutions:  # Keep only the first institution & remove brackets if it's in a list format
                    institution = institutions[0]

                # Extract gpa
                gpa = entry.find('font', color="#ff0000").text.strip()

                # Extract experience_year
                experience_year = entry.find('font', color="#cc0000").text.strip()

                # Extract desired_salary
                salary_text = entry.find(text=re.compile(r'ระดับเงินเดือนที่ต้องการ'))
                if salary_text:
                    desired_salary = salary_text.strip()

                # Extract location
                location = entry.find('font', color="#990000").text.strip()

                # Extract latest_active_date
                latest_active_date_font = entry.find('font', color="steelblue")
                latest_active_date = latest_active_date_font.find('span', style="font-size: 11pt").text.strip()

                data.append([resume_title, resume_url, gender, age, highest_education_level,
                             field_of_study, institution, gpa, experience_year, desired_salary, location, latest_active_date])
            except Exception:
                continue

        return data

    print(f"Failed to retrieve data for page {page_number}.")
    return []

# Main loop to scrape pages
all_data = []
for page_number in range(1, 6480):  # scrape from page 1 to 6479
    page_data = scrape_page(page_number)
    all_data.extend(page_data)

# Convert the data to a pandas DataFrame
df = pd.DataFrame(all_data, columns=['resume_title', 'resume_url', 'gender', 'age', 'highest_education_level',
                                     'field_of_study', 'institution', 'gpa', 'experience_year', 'desired_salary', 'location', 'latest_active_date'])

# Remove duplicate rows based on the 'resume_url' column, keeping only the first occurrence
df = df.drop_duplicates(subset='resume_url', keep='first')

# Save the data to a CSV file with UTF-8 encoding
df.to_csv('<YOUR_OUTPUT_FILENAME>.csv', index=False, encoding='utf-8-sig')  # Replace with desired filename

print("Data scraped successfully!")
