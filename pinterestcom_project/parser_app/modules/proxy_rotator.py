import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# File to track last rotation time
LAST_ROTATION_FILE = 'last_rotation.txt'
# File to track current IP
CURRENT_IP_FILE = 'current_ip.txt'

def get_current_time():
    """Get current time in seconds since epoch."""
    return int(time.time())

def get_last_rotation_time():
    """Get the timestamp of the last rotation."""
    if os.path.exists(LAST_ROTATION_FILE):
        with open(LAST_ROTATION_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def update_last_rotation_time():
    """Update the last rotation timestamp."""
    with open(LAST_ROTATION_FILE, 'w') as f:
        f.write(str(get_current_time()))

def get_last_ip():
    """Get the last used IP."""
    if os.path.exists(CURRENT_IP_FILE):
        with open(CURRENT_IP_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_current_ip(ip):
    """Save the current IP."""
    with open(CURRENT_IP_FILE, 'w') as f:
        f.write(ip)

def check_current_ip():
    """Check and return the current IP using the proxy."""
    proxy_config = {
        'http': f'http://{os.getenv("PROXY_USERNAME")}:{os.getenv("PROXY_PASSWORD")}@{os.getenv("PROXY_IP")}:{os.getenv("PROXY_HTTP_PORT")}',
        'https': f'http://{os.getenv("PROXY_USERNAME")}:{os.getenv("PROXY_PASSWORD")}@{os.getenv("PROXY_IP")}:{os.getenv("PROXY_HTTP_PORT")}'
    }
    
    try:
        response = requests.get('https://api.ipify.org?format=json', proxies=proxy_config, timeout=10)
        return response.json()['ip']
    except Exception as e:
        print(f"Error checking current IP: {e}")
        return None

def rotate_ip():
    """Rotate the proxy IP with time check and retry logic."""
    # Check if we need to wait before rotating
    last_rotation = get_last_rotation_time()
    current_time = get_current_time()
    time_since_last_rotation = current_time - last_rotation
    
    wait_time_for_rotation = 130
     
    if time_since_last_rotation < wait_time_for_rotation:
        wait_time = wait_time_for_rotation - time_since_last_rotation
        print(f"Waiting {wait_time} seconds before rotating IP...")
        time.sleep(wait_time)
    
    # Get the IP before rotation
    last_ip = get_last_ip()
    
    # Rotate the IP
    rotate_url = os.getenv('PROXY_ROTATE_IP_URL')
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Rotating IP, attempt {attempt}/{max_attempts}...")
            rotation_response = requests.get(rotate_url, timeout=45)
            
            if rotation_response.status_code != 200:
                print(f"Rotation failed: {rotation_response.text}")
                if attempt < max_attempts:
                    time.sleep(5)
                    continue
                return False
            
            # Wait a bit for the rotation to take effect
            time.sleep(35)
            
            # Check the new IP
            new_ip = check_current_ip()
            
            if not new_ip:
                print("Could not verify new IP")
                if attempt < max_attempts:
                    time.sleep(15)
                    continue
                return False
            
            # Check if IP actually changed
            if last_ip and new_ip == last_ip:
                print(f"IP didn't change: {new_ip}")
                if attempt < max_attempts:
                    time.sleep(10)
                    continue
                return False
            
            # Success! Update files and return
            print(f"Successfully rotated IP to: {new_ip}")
            save_current_ip(new_ip)
            update_last_rotation_time()
            return True
            
        except Exception as e:
            print(f"Error during rotation attempt {attempt}: {e}")
            if attempt < max_attempts:
                time.sleep(5)
            else:
                return False
    
    return False

# For testing the module directly
if __name__ == "__main__":
    print("Testing proxy rotation...")
    success = rotate_ip()
    print(f"Rotation {'successful' if success else 'failed'}")