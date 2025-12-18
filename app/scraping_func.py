import re
import logging

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://auto.ria.com/uk/",
    "Origin": "https://auto.ria.com",
}

async def collect_urls_from_page(browser, page_number):
    """Collect URLs from a single page"""
    hrefs = []
    url = f"https://auto.ria.com/uk/search/?indexName=auto&plateNumber.length.gte=1&verified.VIN=1&abroad=2&custom=3&page={page_number}&countpage=10"
    
    context = await browser.new_context(extra_http_headers=HEADERS)
    page = await context.new_page()
    
    try:
        await page.goto(url)
        await page.wait_for_selector("a.product-card")
        
        elements = await page.query_selector_all("a.product-card")
        for el in elements:
            href = await el.get_attribute("href")
            if href:
                hrefs.append("https://auto.ria.com" + href)
    finally:
        await context.close()
    
    return hrefs

async def car_details(page, url):
    """Extract car title, price, and odometer"""
    title = None
    price_usd = 1
    odometer = None
    
    try:
        title = await page.locator("h1").inner_text()
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of car title from {url}")
    
    try:
        price_text = await page.locator("strong.common-text.ws-pre-wrap.titleL").first.inner_text()
        price_usd = int(re.sub(r"[^\d]", "", price_text))
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of car price from {url}")
    
    try:
        odometer_text = await page.locator("span:has-text('тис. км')").first.inner_text()
        odometer = int(odometer_text.split()[0].replace(" ", "")) * 1000
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of car odometer from {url}")
    
    return title, price_usd, odometer

async def collect_images(page, url) -> tuple:
    """Extract image URL and count"""
    image_url = None
    images_count = 1
    
    try:
        first_img = page.locator("ol.carousel__track li img").first
        image_url = await first_img.get_attribute("src") if first_img else None
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of image_url from {url}")
    
    try:
        liveregion_text = await page.locator("div.carousel__liveregion").first.inner_text()
        match = re.search(r"of\s+(\d+)", liveregion_text)
        images_count = int(match.group(1)) if match else 1
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of image_count from {url}")
    
    return image_url, images_count

async def collect_user_info(page, url):
    """Extract username and phone number(s)"""
    username = None
    phone_numbers = []
    
    try:
        username = await page.locator('#sellerInfoUserName span.common-text.ws-pre-wrap.titleM').first.inner_text()
        username = username.strip()
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of username from {url}")
    
    try:
        await page.locator('button.size-large.conversion[data-action="showBottomPopUp"]').first.click()
        await page.wait_for_timeout(500)  # Wait for popup to appear
        
        phone_links = await page.locator('a.action-wrapper-link[href^="tel:"]').all()
        for phone_link in phone_links:
            phone_href = await phone_link.get_attribute("href")
            if phone_href:
                phone_number = phone_href[4:].strip()
                phone_numbers.append(phone_number)
        
        phone_number = phone_numbers[0] if phone_numbers else None
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of user's phone number from {url}")
        phone_number = None
    
    return username, phone_number

async def collect_car_info(page, url):
    """Extract car number and VIN"""
    car_number = None
    car_vin = None
    
    try:
        car_number = await page.locator("div.car-number span.common-text.ws-pre-wrap.body").first.inner_text()
        car_number = car_number.strip()
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of car number from {url}")
    
    try:
        car_vin = await page.locator("span.common-text.ws-pre-wrap.badge").first.inner_text()
    except Exception as e:
        logger.error(f"{e} Error happened during scraping of car VIN from {url}")
    
    return car_number, car_vin