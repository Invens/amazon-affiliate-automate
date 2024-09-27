import pymysql
import schedule
import time
from amazon_scraper import scrape_amazon_products  # Scrapes Amazon for product data
from telegram_poster import post_to_telegram       # Posts product to Telegram channel
from threading import Lock

# Create a lock to ensure no two campaigns run at the same time
campaign_lock = Lock()

# MySQL connection function
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        db="campaign_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to check if the product is already fetched (by URL and title)
def is_duplicate_product(product):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check for products with the same title or URL
        query = """
        SELECT id FROM fetched_products
        WHERE product_url = %s OR product_title = %s
        """
        cursor.execute(query, (product['affiliate_link'], product['title']))
        result = cursor.fetchone()
    conn.close()
    return result is not None  # Return True if product is a duplicate

# Function to save a fetched product to the database
def save_fetched_product(product, campaign_name):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = "INSERT INTO fetched_products (product_url, product_title, campaign_name, fetch_time) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query, (product['affiliate_link'], product['title'], campaign_name))
    conn.commit()
    conn.close()

# Function to run the campaign
def run_campaign(campaign):
    print(f"Running campaign: {campaign['campaign_name']}")
    keywords = campaign['keywords']
    max_posts = campaign['max_posts']

    # Fetch products from Amazon based on campaign keywords
    products, fetched_urls = scrape_amazon_products(keywords, max_products=max_posts)
    print(f"Fetched {len(products)} products for campaign: {campaign['campaign_name']}")

    # Sequentially post each product to Telegram
    posted_count = 0
    for product in products:
        if posted_count >= max_posts:
            break
        
        # Check if the product has already been fetched (using both URL and title)
        if is_duplicate_product(product):
            print(f"Skipping duplicate product (by URL or title): {product['title']}")
            continue  # Skip duplicate product
        
        # Post the product to Telegram
        try:
            print(f"Posting product to Telegram: {product['title']}")
            post_to_telegram(product)  # Post product to Telegram channel
            time.sleep(2)  # Add a small delay to avoid spamming or rate-limiting
            
            # Save the fetched product to the database to avoid duplicates later
            save_fetched_product(product, campaign['campaign_name'])
            posted_count += 1
        except Exception as e:
            print(f"Error posting product to Telegram: {e}")
            continue

    # Update last fetch time in the campaigns table
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE campaigns SET last_fetch = NOW() WHERE id = %s", (campaign['id'],))
    conn.commit()
    conn.close()

# Setup scheduler for campaigns
def setup_campaign_scheduler():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM campaigns")
        campaigns = cursor.fetchall()

    # Set up schedule based on interval for each campaign
    for campaign in campaigns:
        schedule.every(int(campaign['intervals'])).minutes.do(run_campaign_safe, campaign=campaign)

    conn.close()

# Function to run campaigns in a thread-safe way
def run_campaign_safe(campaign):
    if not campaign_lock.acquire(blocking=False):
        print(f"Campaign {campaign['campaign_name']} is already running. Skipping this run.")
        return
    
    try:
        run_campaign(campaign)  # Run the campaign safely
    finally:
        campaign_lock.release()

# Run the scheduler
def run_scheduler():
    setup_campaign_scheduler()
    while True:
        schedule.run_pending()  # Keeps running the scheduler for pending jobs
        time.sleep(1)

if __name__ == '__main__':
    run_scheduler()
