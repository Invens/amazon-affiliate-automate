import requests
from bs4 import BeautifulSoup
import random
import time

# Replace with your Amazon Affiliate Store ID
AFFILIATE_ID = "lifelens0f7-21"

# Randomize user agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
]

# Function to generate affiliate link
def generate_affiliate_link(product_url):
    affiliate_link = f"{product_url}?tag={AFFILIATE_ID}"
    return affiliate_link

# Function to check if product URL is already in the fetched list
def is_product_fetched(product_url, fetched_urls):
    return product_url in fetched_urls

# Scrape Amazon for product data
def scrape_amazon_products(keywords, max_products=5, pages=1, fetched_urls=None):
    if fetched_urls is None:
        fetched_urls = set()  # Initialize an empty set if no previous products

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    products = []
    for page in range(1, pages + 1):
        search_url = f"https://www.amazon.in/s?k={'+'.join(keywords.split())}&page={page}"
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, "html.parser")

            product_listings = soup.find_all("div", {"data-component-type": "s-search-result"}, limit=max_products)

            for product in product_listings:
                try:
                    # Product URL (unique identifier for avoiding duplicates)
                    product_url = "https://www.amazon.in" + product.h2.a['href']

                    # Check if the product was already fetched
                    if is_product_fetched(product_url, fetched_urls):
                        print(f"Skipping already fetched product: {product_url}")
                        continue

                    # Title
                    title = product.h2.a.text.strip()
                    
                    # Generate affiliate link
                    affiliate_link = generate_affiliate_link(product_url)

                    # Image
                    image_tag = product.find('img')
                    image_url = image_tag['src'] if image_tag else "Image unavailable"

                    # Price
                    price_whole = product.find('span', class_='a-price-whole')
                    price_fraction = product.find('span', class_='a-price-fraction')
                    price = f"${price_whole.text}{price_fraction.text}" if price_whole and price_fraction else "Check Prices Now"

                    # Append product data if it's not a duplicate
                    products.append({
                        'title': title,
                        'affiliate_link': affiliate_link,
                        'image_url': image_url,
                        'price': price
                    })

                    # Add the product URL to the fetched list
                    fetched_urls.add(product_url)

                except Exception as e:
                    print(f"Error parsing product data: {e}")
                    continue

            # Random delay between requests to avoid bot detection
            time.sleep(random.uniform(2, 5))

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page: {e}")
            continue

    return products, fetched_urls

# Example usage
if __name__ == "__main__":
    keywords = "laptop"
    max_products = 5
    pages = 2  # Scrape 2 pages
    
    # Initialize an empty set to store fetched URLs
    fetched_urls = set()
    
    # First scrape
    products, fetched_urls = scrape_amazon_products(keywords, max_products, pages, fetched_urls)
    print("First Scrape Fetched Products:", products)
    
    # Simulate a second scrape to check for duplicates
    products, fetched_urls = scrape_amazon_products(keywords, max_products, pages, fetched_urls)
    print("Second Scrape Fetched Products:", products)
