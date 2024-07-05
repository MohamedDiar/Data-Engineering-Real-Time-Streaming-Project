import json
import random
import string

import requests
from bs4 import BeautifulSoup
from writing_to_env import update_env_file


def word_gen():
    """
    Generates a random word with a length between 5 and 9 characters.
    
    Returns:
        str: A randomly generated word.
    """
    return ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 9)))

def sentence_generator():
    """
    Generates a random sentence with a length between 5 and 9 words.
    
    Returns:
        str: A randomly generated sentence.
    """
    return ' '.join(word_gen() for _ in range(random.randint(5, 9)))

def get_api_details():
    """
    Logs into Telegram's my.telegram.org, checks for existing API details, and creates a new application if necessary.
    
    Returns:
        dict: A dictionary containing 'id' and 'hash' keys with the API ID and API Hash values.
    """
    headers = {
        "authority": "my.telegram.org",
        "method": "POST",
        "path": "/auth/send_password",
        "scheme": "https",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://my.telegram.org",
        "Referer": "https://my.telegram.org/auth?to=apps",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    phone_number = input('Please Enter your number Including Country Code: ')
    num_url = 'https://my.telegram.org/auth/send_password'
    num_data = {'phone': phone_number}

    # Step 1: Request a random hash by sending the phone number
    random_hash_response = session.post(num_url, data=num_data, headers=headers)
    if 'random_hash' in random_hash_response.text:
        random_hash = json.loads(random_hash_response.content.decode("utf-8"))["random_hash"]
        otp = input("Please enter the login code here: ")
        otp_url = 'https://my.telegram.org/auth/login'
        otp_data = {'phone': phone_number, 'random_hash': random_hash, 'password': otp}
        
        # Step 2: Log in using the OTP
        login_response = session.post(otp_url, data=otp_data, headers=headers)

        if 'true' in login_response.text:
            app_page_url = 'https://my.telegram.org/apps'
            res = session.get(app_page_url)
            soup = BeautifulSoup(res.content, 'html.parser')
            span_tags = soup.find_all('span', {'class': 'form-control input-xlarge uneditable-input', 'onclick': 'this.select();'})

            # Step 3: Check if API details already exist
            if span_tags:
                api_id, api_hash = span_tags[0].text, span_tags[1].text
                return {'id': api_id, 'hash': api_hash}
            else:
                # Step 4: Create a new application if no API details exist
                create_app_url = 'https://my.telegram.org/apps/create'
                hash_value = soup.find('input', {'name': 'hash'})['value']
                app_data = {
                    'hash': hash_value,
                    'app_title': word_gen(),
                    'app_shortname': word_gen(),
                    'app_url': 'www.telegram.org',
                    'app_platform': 'other',
                    'app_desc': sentence_generator()
                }
                session.post(create_app_url, data=app_data, headers=headers)
                
                # Step 5: Retrieve the newly created API details
                res = session.get(app_page_url)
                soup = BeautifulSoup(res.content, 'html.parser')
                span_tags = soup.find_all('span', {'class': 'form-control input-xlarge uneditable-input', 'onclick': 'this.select();'})
                api_id, api_hash = span_tags[0].text, span_tags[1].text
                return {'id': api_id, 'hash': api_hash}
    else:
        print("Failed to get random hash.")
        return None

# Get API details and print them
details = get_api_details()
if details:
    print(f"API ID: {details['id']}, API Hash: {details['hash']}")
    update_env_file('API_ID', details['id'])
    update_env_file('API_HASH', details['hash'])
