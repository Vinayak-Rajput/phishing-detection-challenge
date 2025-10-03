import dnstwist
import pandas as pd
import os
import json

# --- Configuration ---
CSE_DOMAINS_CSV = 'data/external/stage1_cse_domains.csv'
OUTPUT_FILE = 'data/raw/typosquat_domains.txt'

def load_target_domains(file_path):
    """Loads the list of official domains from our CSE list."""
    print(f"--> Loading target domains from {file_path}")
    try:
        df = pd.read_csv(file_path)
        # Clean the domains (remove www.) for better results
        domains = [d.lower().split('www.')[-1] for d in df['Whitelisted Domains']]
        return domains
    except Exception as e:
        print(f"[!] Error loading or parsing CSV: {e}")
        return []

def find_typosquats(domain):
    """
    Uses dnstwist to find registered variations of a single domain.
    """
    print(f"[*] Scanning for variations of '{domain}'... (This may take a few minutes)")
    try:
        # Run dnstwist programmatically
        # 'registered=True' tells it to only return domains with live DNS records
        # 'format='list'' gives us a simple list of dictionaries
        results = dnstwist.run(domain=domain, registered=True, format='list')
        
        # Extract just the domain names from the results
        found_domains = [item.get('domain') for item in results if 'domain' in item]
        print(f"--> Found {len(found_domains)} registered variations for '{domain}'.")
        return found_domains
    except Exception as e:
        print(f"[!] An error occurred while scanning '{domain}': {e}")
        return []

# --- Main execution block ---
if __name__ == "__main__":
    target_domains = load_target_domains(CSE_DOMAINS_CSV)
    
    if target_domains:
        all_found_typosquats = set()

        for official_domain in target_domains:
            squatted_domains = find_typosquats(official_domain)
            # Add the new findings to our master set
            all_found_typosquats.update(squatted_domains)
            
        print(f"\n[+] Scan complete. Total unique registered variations found: {len(all_found_typosquats)}")

        # Save the final list to the output file
        if all_found_typosquats:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                for domain in sorted(list(all_found_typosquats)):
                    f.write(domain + '\n')
            print(f"--> Results saved to {OUTPUT_FILE}")