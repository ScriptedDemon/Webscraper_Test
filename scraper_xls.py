import time
import pandas as pd
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
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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
        if tags_column:
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
    return pd.DataFrame(data)

if __name__ == "__main__":
    driver = setup_driver()

    print(" Scraping Candidate List...")
    candidate_url = "https://echa.europa.eu/candidate-list-table"
    df_candidate = scrape_table(driver, candidate_url, expected_columns=5, tags_column=True)

    print(" Scraping Authorization List...")
    auth_url = "https://echa.europa.eu/authorisation-list"
    df_auth = scrape_table(driver, auth_url, expected_columns=4)

    print(" Scraping Restricted List...")
    restrict_url = "https://echa.europa.eu/substances-restricted-under-reach"
    df_restrict = scrape_table(driver, restrict_url, expected_columns=4)

    driver.quit()

    # Save to Excel (multiple sheets)
    with pd.ExcelWriter("echa_lists.xlsx", engine="openpyxl") as writer:
        df_candidate.to_excel(writer, sheet_name="Candidate List", index=False)
        df_auth.to_excel(writer, sheet_name="Authorization List", index=False)
        df_restrict.to_excel(writer, sheet_name="Restricted List", index=False)

    print("✅ All 3 lists saved to 'echa_lists.xlsx'")
