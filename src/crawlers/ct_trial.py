import certstream
import datetime
import sys

# We'll use the CSEs from the training/mock sets as keywords.
# Let's start with a few examples.
TARGET_KEYWORDS = ["sbi", "pnb", "icici", "hdfc"]

def process_certificate(message, context):
    """
    This function is called for every new certificate update.
    """
    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        for domain in all_domains:
            # Remove the wildcard '*' if it exists
            if domain.startswith("*."):
                domain = domain[2:]

            # Check if any of our keywords are in the domain name
            if any(keyword in domain.lower() for keyword in TARGET_KEYWORDS):
                print(f"[*] Potential phishing domain found: {domain}")

# Start listening to the stream
print("--> Starting CT Log monitor...")
print(f"--> Monitoring for keywords: {TARGET_KEYWORDS}")
try:
    certstream.listen_for_events(process_certificate, url='wss://certstream.calidog.io/')
except KeyboardInterrupt:
    print("\n--> Monitor stopped.")
    sys.exit(0)