import pandas as pd
import os
from urllib.parse import urlparse

# --- Configuration ---
CT_LOGS_INPUT = 'data/raw/discovered_urls.txt'
TYPOSQUAT_INPUT = 'data/raw/typosquat_domains.txt'
FEATURES_OUTPUT = 'data/processed/url_features.csv'

def load_domains_from_file(file_path):
    """Loads a list of domains from a text file."""
    if not os.path.exists(file_path):
        print(f"[!] Warning: Input file not found at {file_path}. Skipping.")
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_domain_from_url(url):
    """Extracts the domain/hostname from a full URL."""
    try:
        # Prepending http:// if no scheme is present, to allow urlparse to work correctly
        if '://' not in url:
            url = 'http://' + url
        parsed_url = urlparse(url)
        return parsed_url.hostname or ''
    except Exception:
        return ''

# --- Feature Extraction Functions (based on Annexure A) ---

def get_url_length(url):
    """Calculates the total length of the URL string."""
    return len(url)

def count_dots(url):
    """Counts the number of dots in the URL."""
    return url.count('.')

def count_hyphens(url):
    """Counts the number of hyphens in the URL."""
    return url.count('-')

def count_special_chars(url):
    """Counts various special characters in the URL."""
    special_chars = ['@', '?', '=', '&', '%', '$', '#', '/']
    return sum(url.count(char) for char in special_chars)

# --- Main execution block ---
if __name__ == "__main__":
    print("--> Starting feature extraction process...")

    # Load domains from both sources
    ct_domains = load_domains_from_file(CT_LOGS_INPUT)
    typo_domains = load_domains_from_file(TYPOSQUAT_INPUT)
    
    # Combine and get unique domains
    all_domains = sorted(list(set(ct_domains + typo_domains)))
    
    if not all_domains:
        print("[!] No domains found in source files. Exiting.")
    else:
        print(f"--> Loaded a total of {len(all_domains)} unique domains.")
        df = pd.DataFrame(all_domains, columns=['url'])

        # --- Apply feature extraction functions ---
        print("--> Extracting URL-based features...")
        df['url_length'] = df['url'].apply(get_url_length)
        df['domain'] = df['url'].apply(get_domain_from_url)
        df['domain_length'] = df['domain'].apply(lambda x: len(x))
        df['dots_count'] = df['url'].apply(count_dots)
        df['hyphens_count'] = df['url'].apply(count_hyphens)
        df['special_chars_count'] = df['url'].apply(count_special_chars)

        # --- Save results ---
        os.makedirs(os.path.dirname(FEATURES_OUTPUT), exist_ok=True)
        df.to_csv(FEATURES_OUTPUT, index=False)

        print(f"\n[+] Feature extraction complete!")
        print(f"--> Results saved to {FEATURES_OUTPUT}")
        print("\n--- Feature DataFrame Head ---")
        print(df.head())