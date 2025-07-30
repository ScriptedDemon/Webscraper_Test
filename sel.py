import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
 
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
 
def scrape_table(driver, url, expected_columns, tags_column=False):
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table")
    if not table:
        raise Exception(f"Table not found at {url}")
   
    data = []
    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < expected_columns:
            continue
        row_data = {
            "Substance Name": cols[0].text.strip(),
            "EC Number": cols[1].text.strip(),
            "CAS Number": cols[2].text.strip()
        }
        if tags_column:  # Candidate List only
            row_data.update({
                "Reason for Inclusion": cols[3].text.strip(),
                "Date of Inclusion": cols[4].text.strip(),
                "Tags": cols[5].text.strip() if len(cols) > 5 else ""
            })
        else:
            row_data.update({
                "Column 4": cols[3].text.strip()
            })
        data.append(row_data)
    return data
 
if __name__ == "__main__":
    driver = setup_driver()
 
    print(" Scraping Candidate List...")
    candidate_url = "https://echa.europa.eu/candidate-list-table"
    candidate_data = scrape_table(driver, candidate_url, expected_columns=5, tags_column=True)
    with open("candidate_list.json", "w", encoding="utf-8") as f:
        json.dump(candidate_data, f, indent=2, ensure_ascii=False)
 
    print(" Scraping Authorization List...")
    auth_url = "https://echa.europa.eu/authorisation-list"
    auth_data = scrape_table(driver, auth_url, expected_columns=4)
    with open("authorization_list.json", "w", encoding="utf-8") as f:
        json.dump(auth_data, f, indent=2, ensure_ascii=False)
 
    print(" Scraping Restricted List...")
    restrict_url = "https://echa.europa.eu/substances-restricted-under-reach"
    restrict_data = scrape_table(driver, restrict_url, expected_columns=4)
    with open("restricted_list.json", "w", encoding="utf-8") as f:
        json.dump(restrict_data, f, indent=2, ensure_ascii=False)
 
    driver.quit()
    print(" All 3 JSON files saved!")
 