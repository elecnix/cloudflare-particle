import os
import sys
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PARTICLE_IPS_URL = "https://infra.particle.io/v2/data/ips/device-service.json"
POLICY_NAME = "Particle Cloud"

def get_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        print(f"Missing required environment variable: {var}", file=sys.stderr)
        sys.exit(1)
    return value

def fetch_particle_ips() -> list[str]:
    resp = requests.get(PARTICLE_IPS_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    tcp_ips = data.get("tcp", {}).get("ip_addresses", [])
    udp_ips = data.get("udp", {}).get("ip_addresses", [])
    all_ips = set(tcp_ips + udp_ips)
    return sorted(all_ips)

def get_cf_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def find_policy(cf_token: str, account_id: str, policy_name: str):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/policies"
    resp = requests.get(url, headers=get_cf_headers(cf_token), timeout=10)
    resp.raise_for_status()
    for policy in resp.json().get("result", []):
        if policy.get("name") == policy_name:
            return policy
    return None

def build_ip_rules(ip_list: list[str]) -> list[dict]:
    return [{"ip": {"ip": ip}} for ip in ip_list]

def update_policy(cf_token: str, account_id: str, policy_id: str, policy_name: str, ip_rules: list[dict]):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/policies/{policy_id}"
    payload = {
        "name": policy_name,
        "decision": "allow",
        "include": ip_rules,
        "exclude": [],
        "require": [],
    }
    resp = requests.put(url, headers=get_cf_headers(cf_token), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

def create_policy(cf_token: str, account_id: str, policy_name: str, ip_rules: list[dict]):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/policies"
    payload = {
        "name": policy_name,
        "decision": "allow",
        "include": ip_rules,
        "exclude": [],
        "require": [],
    }
    resp = requests.post(url, headers=get_cf_headers(cf_token), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

def main():
    cf_token = get_env("CLOUDFLARE_API_TOKEN")
    account_id = get_env("CLOUDFLARE_ACCOUNT_ID")

    print("Fetching Particle IPs...")
    ip_list = fetch_particle_ips()
    ip_rules = build_ip_rules(ip_list)
    print(f"Found {len(ip_rules)} IP rules.")

    print("Checking for existing Cloudflare policy...")
    policy = find_policy(cf_token, account_id, POLICY_NAME)
    if policy:
        print(f"Policy '{POLICY_NAME}' found. Updating...")
        update_policy(cf_token, account_id, policy["id"], POLICY_NAME, ip_rules)
        print("Policy updated.")
    else:
        print(f"Policy '{POLICY_NAME}' not found. Creating...")
        create_policy(cf_token, account_id, POLICY_NAME, ip_rules)
        print("Policy created.")

if __name__ == "__main__":
    main()
