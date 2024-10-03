import requests
import hashlib
import hmac
import datetime
import json

# Replace with your credentials
AWS_ACCESS_KEY = "AKIAIP44GOIBWVLYSWZA"
AWS_SECRET_KEY = "0C8w4UrxrfT5U8lG26630DGM3m17XgCuO3dTsviH"
PARTNER_TAG = "lifelens0f7-21"
REGION = "us-west-2"  # Use the region for PAAPI for India
SERVICE = "ProductAdvertisingAPI"
HOST = "webservices.amazon.in"
ENDPOINT = "https://webservices.amazon.in/paapi5/searchitems"
REQUEST_URI = "/paapi5/searchitems"

# Function to sign the request
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

# Function to get the signing key
def get_signature_key(key, date_stamp, region, service):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

# Function to create signed headers
def get_amazon_signed_headers(payload):
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')  # Date without time

    # Create canonical request
    canonical_uri = REQUEST_URI
    canonical_querystring = ''
    canonical_headers = f'host:{HOST}\nx-amz-date:{amz_date}\n'
    signed_headers = 'host;x-amz-date'
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    canonical_request = f'POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

    # Create string to sign
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{REGION}/{SERVICE}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'

    # Create signature
    signing_key = get_signature_key(AWS_SECRET_KEY, date_stamp, REGION, SERVICE)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # Add signing information to the request
    headers = {
        'Content-Type': 'application/json',
        'X-Amz-Date': amz_date,
        'Authorization': f'{algorithm} Credential={AWS_ACCESS_KEY}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
    }

    return headers

# Function to search Amazon products
def search_amazon_products(keywords, max_results=5):
    # Prepare the payload for the request
    payload = {
        "Keywords": keywords,
        "PartnerTag": PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.in",
        "Resources": [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ],
        "ItemCount": max_results
    }
    
    payload_json = json.dumps(payload)

    # Get the signed headers for the request
    headers = get_amazon_signed_headers(payload_json)

    # Make the POST request
    try:
        response = requests.post(ENDPOINT, headers=headers, data=payload_json)

        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            # Parse the returned product data
            products = []
            if 'ItemsResult' in data and 'Items' in data['ItemsResult']:
                for item in data['ItemsResult']['Items']:
                    title = item['ItemInfo']['Title']['DisplayValue']
                    image_url = item['Images']['Primary']['Medium']['URL']
                    price = item.get('Offers', {}).get('Listings', [{}])[0].get('Price', {}).get('DisplayAmount', 'Price unavailable')
                    affiliate_link = item['DetailPageURL']

                    products.append({
                        'title': title,
                        'affiliate_link': affiliate_link,
                        'image_url': image_url,
                        'price': price
                    })
            return products
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

# Example usage
if __name__ == "__main__":
    keywords = "laptop"
    max_products = 5
    products = search_amazon_products(keywords, max_products)

    # Print fetched products
    for product in products:
        print(f"Title: {product['title']}")
        print(f"Affiliate Link: {product['affiliate_link']}")
        print(f"Image URL: {product['image_url']}")
        print(f"Price: {product['price']}")
        print("\n")
