from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import io
import selenium.common.exceptions

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize the ChromeOptions
options = webdriver.ChromeOptions()
# Uncomment the line below to run headless (without opening a browser window)
# options.add_argument("--headless")  
driver = webdriver.Chrome(options=options)

# List to store all extracted data
extracted_data = []

try:
    for page_num in range(1, 11):  
        link = f"https://s.1688.com/company/pc/factory_search.htm?keywords=%CD%E6%BE%DF%CD%AF%D7%B0&spm=a26352.13672862.searchbox.input&sortType=lookback&n=y&beginPage={page_num}#sm-filtbar"

        driver.get(link)
        print(f"Processing page {page_num}")

        # Wait until the product listings are present
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'company-offer-contain')))

        # Scroll down to load all content
        scroll_height = 500
        for scroll_step in range(1, 13):
            scroll_to = scroll_height * scroll_step
            driver.execute_script(f"window.scrollTo(0, {scroll_to})")
            print(f"Scrolling to {scroll_to}px")
            time.sleep(1)  # Adjust sleep time as necessary

        # Parse the page source with BeautifulSoup
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')

        # Iterate over each company offer
        for area in soup.find_all('div', class_='company-offer-contain'):
            # Extract basic information
            factory_name_tag = area.find('div', class_='title')
            factory_name = factory_name_tag.text.strip() if factory_name_tag else "N/A"

            city_tag = area.find('div', class_='city')
            city = city_tag.text.strip() if city_tag else "N/A"

            year_tag = area.find('span', class_='year-text')
            year = year_tag.text.strip() if year_tag else "N/A"

            category_tag = area.find('div', class_='desc')
            category = category_tag.text.strip() if category_tag else "N/A"

            image_tag = area.find('img', class_='img')
            image = image_tag['src'] if image_tag else "N/A"

            link_tag = area.find('a', class_='ww-link ww-inline ww-online')
            link = link_tag['href'] if link_tag else "N/A"

            # Initialize rate variables
            response_rate = "N/A"
            fulfillment_rate = "N/A"
            return_rate = "N/A"

            # Extract rates
            rates_container = area.find('div', class_='rate-container')
            if rates_container:
                rate_elements = rates_container.find_all('div', class_='rate')
                for rate in rate_elements:
                    rate_text = rate.text.strip()
                    if '响应率' in rate_text:
                        response_rate = rate_text
                    elif '履约率' in rate_text:
                        fulfillment_rate = rate_text
                    elif '回头率' in rate_text:
                        return_rate = rate_text
                    # Tambahkan elif tambahan jika ada jenis rate lainnya


            # Simpan data ke dalam dictionary
            company_data = {
                'Factory Name': factory_name,
                'City': city,
                'Years Active': year,
                'Category': category,
                'Image': image,
                'Response Rate': response_rate,
                'Fulfillment Rate': fulfillment_rate,
                'Return Rate': return_rate
            }

            # Tambahkan ke list data yang diekstrak
            extracted_data.append(company_data)

            # (Opsional) Cetak data yang diekstrak
            print(f"Factory Name: {factory_name}")
            print(f"City: {city}")
            print(f"Years Active: {year}")
            print(f"Category: {category}")
            print(f"Response Rate: {response_rate}")
            print(f"Fulfillment Rate: {fulfillment_rate}")
            print(f"Return Rate: {return_rate}")
            print("-" * 40)

except selenium.common.exceptions.TimeoutException:
    print("TimeoutException: Gagal memuat halaman atau elemen yang ditunggu tidak ditemukan.")

finally:
    driver.quit()

    # (Opsional) Simpan data ke dalam CSV menggunakan pandas
    df = pd.DataFrame(extracted_data)
    df.to_csv('1688_factory_rates.csv', index=False, encoding='utf-8-sig')
    print("Data berhasil disimpan ke '1688_factory_rates.csv'")
