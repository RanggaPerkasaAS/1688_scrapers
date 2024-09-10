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

product_detail = []

try:
    link = f"https://s.1688.com/selloffer/offer_search.htm?keywords=%B1%A6%B1%A6%C4%CC%C6%BF&spm=a260k.home2024.searchbox.0&beginPage=1&sortType=va_sales360&descendOrder=true&tags=458114"
    driver.get(link)

    # Wait until the product listings are present
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'offer-tag-row')))

    # Scroll down to load all content
    scroll_height = 500
    for scroll_step in range(1, 13):
        scroll_to = scroll_height * scroll_step
        driver.execute_script(f"window.scrollTo(0, {scroll_to})")
        print(f"Scrolling to {scroll_to}px")
        time.sleep(2)  # Adjust sleep time as necessary    

    # Parse the page source with BeautifulSoup
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Iterate over each company offer
    for area in soup.find_all('a', class_='ocms-fusion-1688-pc-pc-ad-common-offer-2024'):
        product_link = area['href'] 

        # Handling the title text with conditions
        title_tag = area.find('div', class_='title-text text-row-1')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title_tag = area.find('div', class_='title-text')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

        price_tag = area.find('div', class_='price-item')
        price = price_tag.text.strip() if price_tag else "N/A"

        # Initialize sold and return rate
        sold = "N/A"
        return_rate = "N/A"

        # Extract 'sold' from the appropriate div
        sold_tag = area.find('div', class_='offer-price-row')
        if sold_tag:
            sold_item = sold_tag.find('div', class_='desc-text')
            sold = sold_item.get_text(strip=True) if sold_item else "N/A"

        # Extract 'return rate' from the appropriate div
        return_rate_tag = area.find('div', class_='offer-tag-row')
        if return_rate_tag:
            return_rate_items = return_rate_tag.find_all('div', class_='desc-text')
            for item in return_rate_items:
                if '回头率' in item.get_text(strip=True):
                    return_rate = item.get_text(strip=True)
                    break

        shop_tag = area.find('div', class_='offer-shop-row')
        shop = shop_tag.text.strip() if shop_tag else "N/A"

        # Add to product_detail list
        product_detail.append({
            'title': title,
            'link': product_link,
            'price': price,
            'sold': sold,
            'return rate': return_rate,
            'shop': shop
        })

    for area in soup.find_all('a', class_='search-offer-wrapper cardui-normal search-offer-item major-offer'):
        product_link = area['href']

        # Handling the title text with conditions
        title_tag = area.find('div', class_='title-text text-row-1')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title_tag = area.find('div', class_='title-text')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

        price_tag = area.find('div', class_='price-item')
        price = price_tag.text.strip() if price_tag else "N/A"

        # Initialize sold and return rate
        sold = "N/A"
        return_rate = "N/A"

        # Extract 'sold' from the appropriate div
        sold_tag = area.find('div', class_='offer-price-row')
        if sold_tag:
            sold_item = sold_tag.find('div', class_='desc-text')
            sold = sold_item.get_text(strip=True) if sold_item else "N/A"

        # Extract 'return rate' from the appropriate div
        return_rate_tag = area.find('div', class_='offer-tag-row')
        if return_rate_tag:
            return_rate_items = return_rate_tag.find_all('div', class_='desc-text')
            for item in return_rate_items:
                if '回头率' in item.get_text(strip=True):
                    return_rate = item.get_text(strip=True)
                    break

        shop_tag = area.find('div', class_='offer-shop-row')
        shop = shop_tag.text.strip() if shop_tag else "N/A"

        # Add to product_detail list
        product_detail.append({
            'title': title,
            'link': product_link,
            'price': price,
            'sold': sold,
            'return rate': return_rate,
            'shop': shop
        })

    # Convert to DataFrame
    df = pd.DataFrame(product_detail)
    df.to_csv('1688_product_sales.csv', index=False, encoding='utf-8-sig')
    print(df)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
