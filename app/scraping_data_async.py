from playwright.async_api import async_playwright
import asyncio
from scraping_func import *


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://auto.ria.com/uk/",
    "Origin": "https://auto.ria.com",
}

async def get_amount(browser):
    url = "https://auto.ria.com/uk/search/?indexName=auto&plateNumber.length.gte=1&verified.VIN=1&abroad=2&custom=3&page=0&countpage=10"
    context = await browser.new_context(extra_http_headers=HEADERS)
    page = await context.new_page()
    
    await page.goto(url)
    await page.wait_for_selector("ul.pagination-inner a.page-link")
    
    last_link = page.locator("ul.pagination-inner a.page-link").last
    href = await last_link.get_attribute("href")
    total_pages = int(href.split("page=")[1])
    
    await context.close()
    return total_pages


async def collect_urls(browser, total_pages) -> list:
    tasks = [collect_urls_from_page(browser, number) for number in range(total_pages + 1)]
    results = await asyncio.gather(*tasks)
    
    all_hrefs = [href for page_hrefs in results for href in page_hrefs]
    return all_hrefs


async def scrape_single_car(browser, url):
    context = await browser.new_context(extra_http_headers=HEADERS)
    page = await context.new_page()
    
    try:
        await page.goto(url)
        
        # Checking if the listing has been deleted
        # if it was skipping it and going for the next car
        try:
            deleted_message = await page.locator("text=/видалене і не бере участі в пошуку/").first.inner_text(timeout=2000)
            if deleted_message:
                logger.info(f"Skipping deleted listing: {url}")
                return None
        except:
            pass
        
        await page.wait_for_selector("span.picture")
        
        title, price_usd, odometer = await car_details(page, url)
        image_url, images_count = await collect_images(page, url)
        username, phone_number = await collect_user_info(page, url)
        car_number, car_vin = await collect_car_info(page, url)
        
        car_data = {
            "url": url,
            "title": title,
            "price_usd": price_usd,
            "odometer": odometer,
            "username": username,
            "phone_number": phone_number,
            "image_url": image_url,
            "images_count": images_count,
            "car_number": car_number,
            "car_vin": car_vin
        }
        
        return car_data
    finally:
        await context.close()

async def get_info_about_car(browser, links, batch_size=10) -> list:
    details = []
    
    for i in range(0, len(links), batch_size):
        batch = links[i:i + batch_size]
        tasks = [scrape_single_car(browser, url) for url in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Error scraping car: {result}")
            elif result is not None: 
                details.append(result)
    
    return details

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            total_pages = await get_amount(browser)
            logger.info(f"Total pages to scrape: {total_pages}")
            
            all_urls = await collect_urls(browser, total_pages)
            logger.info(f"Total URLs collected: {len(all_urls)}")
            
            car_details_list = await get_info_about_car(browser, all_urls, batch_size=10)
            logger.info(f"Total cars scraped: {len(car_details_list)}")
            
            return car_details_list
        finally:
            await browser.close()

if __name__ == "__main__":
    from db import save_cars_to_db
    
    async def runner():
        results = await main()  
        await save_cars_to_db(results)  

    asyncio.run(runner())