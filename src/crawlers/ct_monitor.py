import certstream
import datetime
import sys
import json
import os

# Define file paths
CONFIG_FILE = 'src/crawlers/config.json'
OUTPUT_FILE = 'data/raw/discovered_urls.txt'

# A set to keep track of domains found in this session
found_domains_session = set()

def load_config(file_path):
    """
    Loads keywords and whitelist from the generated JSON config file.
    """
    print(f"--> Loading configuration from {file_path}")
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config['keywords'], set(config['whitelisted_domains'])
    except FileNotFoundError:
        print(f"[!] Error: Config file not found at {file_path}")
        print("[!] Please run generate_config.py first.")
        sys.exit(1)

def is_whitelisted(domain, whitelisted_set):
    """
    Checks if a domain is a subdomain of any domain in the whitelist.
    """
    for whitelisted_domain in whitelisted_set:
        if domain == whitelisted_domain or domain.endswith('.' + whitelisted_domain):
            return True
    return False

def process_certificate(message, context):
    """
    This function is called for every new certificate update.
    """
    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']
        for domain in all_domains:
            domain = domain.lower()
            if domain.startswith("*."):
                domain = domain[2:]
            
            if domain not in found_domains_session and any(keyword in domain for keyword in TARGET_KEYWORDS):
                if not is_whitelisted(domain, WHITELISTED_DOMAINS):
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_message = f"[{timestamp}] Found: {domain}"
                    print(log_message)
                    found_domains_session.add(domain)
                    with open(OUTPUT_FILE, 'a') as f:
                        f.write(domain + '\n')

# --- Main execution block ---
if __name__ == "__main__":
    TARGET_KEYWORDS, WHITELISTED_DOMAINS = load_config(CONFIG_FILE)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    print("\n--> Starting CT Log monitor...")
    print(f"--> Monitoring for {len(TARGET_KEYWORDS)} keywords.")
    print(f"--> Saving output to: {OUTPUT_FILE}")

    try:
        certstream.listen_for_events(process_certificate, url='wss://certstream.com/')
    except KeyboardInterrupt:
        print("\n--> Monitor stopped.")
        sys.exit(0)