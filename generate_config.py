import pandas as pd
import json

# Define file paths
CSE_DOMAINS_CSV = 'data/external/stage1_cse_domains.csv'
CONFIG_JSON_OUTPUT = 'src/crawlers/config.json'

def generate_and_save_config(csv_path, json_path):
    """
    Reads the CSE data from CSV and saves it as a JSON config file.
    """
    print(f"--> Loading CSE data from {csv_path}")
    keywords = set()
    whitelisted_domains = set()
    try:
        df = pd.read_csv(csv_path)
        for domain in df['Whitelisted Domains']:
            clean_domain = domain.lower().split('www.')[-1]
            whitelisted_domains.add(clean_domain)
            base_name = clean_domain.split('.')[0]
            keywords.add(base_name)
        
        for cse_name in df['Organisation Name']:
            name_parts = cse_name.lower().split(' ')
            if len(name_parts) > 1:
                acronym = "".join(part[0] for part in name_parts)
                keywords.add(acronym)
            keywords.add(name_parts[0])
        
        config_data = {
            "keywords": list(keywords),
            "whitelisted_domains": list(whitelisted_domains)
        }

        with open(json_path, 'w') as f:
            json.dump(config_data, f, indent=4)
            
        print(f"--> Successfully created config file at {json_path}")
        print(f"--> Found {len(keywords)} keywords and {len(whitelisted_domains)} whitelisted domains.")

    except Exception as e:
        print(f"[!] An error occurred: {e}")

if __name__ == "__main__":
    generate_and_save_config(CSE_DOMAINS_CSV, CONFIG_JSON_OUTPUT)