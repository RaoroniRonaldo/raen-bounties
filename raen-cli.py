import json
import sys
import os
import urllib.request
import urllib.error
from eth_account import Account
from eth_account.messages import encode_defunct

# Configuration
AGENTS_JSON_URL = "https://bshelby88.github.io/raen-agent-directory/agents.json"

def get_agents():
    """Fetches the list of available RAEN agents."""
    try:
        with urllib.request.urlopen(AGENTS_JSON_URL) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching agents.json: {e}")
        sys.exit(1)

def sign_challenge(challenge, private_key):
    """Signs the x402 challenge using the provided private key."""
    account = Account.from_key(private_key)
    message = encode_defunct(text=challenge)
    signed_message = account.sign_message(message)
    return account.address, signed_message.signature.hex()

def call_service(service_name, prompt):
    """Executes the 402 -> payment -> settled-response loop."""
    agents = get_agents()
    
    # Find the service in agents.json
    agent_info = next((a for a in agents if a['name'] == service_name or a.get('id') == service_name), None)
    
    if not agent_info:
        print(f"Error: Service '{service_name}' not found.")
        print("\nAvailable services:")
        for a in agents:
            print(f" - {a['name']}")
        return

    url = agent_info['endpoint']
    private_key = os.getenv("RAEN_PRIVATE_KEY")
    
    if not private_key:
        print("Error: RAEN_PRIVATE_KEY environment variable not set.")
        sys.exit(1)

    payload = json.dumps({"prompt": prompt}).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    print(f"[*] Calling {service_name} at {url}...")

    # Step 1: Initial Call
    req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print("[+] Service returned immediate success (no payment required):")
            print(response.read().decode())
            return
    except urllib.error.HTTPError as e:
        if e.code == 402:
            print("[!] 402 Payment Required detected. Handling settlement...")
            
            # Step 2: Extract Challenge from headers
            # The x402 protocol typically provides challenge/invoice in headers
            challenge = e.headers.get('X-RAEN-Challenge')
            if not challenge:
                # Fallback: check body if headers are empty
                try:
                    body = json.loads(e.read().decode())
                    challenge = body.get('challenge')
                except:
                    pass
            
            if not challenge:
                print("Error: Could not find X-RAEN-Challenge in 402 response.")
                sys.exit(1)

            # Step 3: Sign the challenge
            address, signature = sign_challenge(challenge, private_key)
            
            # Step 4: Retry with Settlement Headers
            settlement_headers = headers.copy()
            settlement_headers.update({
                "X-RAEN-Address": address,
                "X-RAEN-Signature": signature,
                "X-RAEN-Challenge": challenge
            })
            
            print(f"[*] Submitting settlement proof for address {address}...")
            
            retry_req = urllib.request.Request(url, data=payload, headers=settlement_headers, method='POST')
            
            try:
                with urllib.request.urlopen(retry_req) as response:
                    result = json.loads(response.read().decode())
                    print("\n=== X402 SETTLEMENT RECEIPT ===")
                    print(json.dumps(result, indent=2))
                    print("===============================")
            except urllib.error.HTTPError as e2:
                print(f"Error during settlement: {e2.code} - {e2.read().decode()}")
        else:
            print(f"Error: {e.code} - {e.read().decode()}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List services: python raen-cli.py list")
        print("  Call service:  python raen-cli.py <service_name> <prompt>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        agents = get_agents()
        print(f"{'SERVICE NAME':<20} | {'DESCRIPTION'}")
        print("-" * 50)
        for a in agents:
            print(f"{a['name']:<20} | {a.get('description', 'No description')}")
    else:
        if len(sys.argv) < 3:
            print("Error: Prompt is required.")
            print("Usage: python raen-cli.py <service_name> <prompt>")
            sys.exit(1)
        
        prompt = " ".join(sys.argv[2:])
        call_service(command, prompt)

if __name__ == "__main__":
    main()
