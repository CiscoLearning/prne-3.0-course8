import os
import json

import requests
from requests.exceptions import HTTPError, RequestException
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MERAKI_API_KEY")
BASE_URL = os.getenv("MERAKI_BASE_URL", "https://api.meraki.com/api/v1")

HEADERS = {
    "X-Cisco-Meraki-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def make_api_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response is not None:
            print(f"Response content: {response.text}")
    except RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from: {url}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    return None

def get_organizations():
    url = f"{BASE_URL}/organizations"
    return make_api_request(url) or []

def get_networks(org_id):
    url = f"{BASE_URL}/organizations/{org_id}/networks"
    return make_api_request(url) or []

def get_network_inventory(network_id):
    url = f"{BASE_URL}/networks/{network_id}/devices"
    inventory = make_api_request(url) or []
    if inventory:
        print(f"\nNetwork Inventory: {len(inventory)} devices found")
    return inventory

def main():
    if not API_KEY:
        print("Error: MERAKI_API_KEY environment variable not set.")
        return

    organizations = get_organizations()
    if not organizations:
        print("Failed to retrieve organizations.")
        return

    org = organizations[0]
    org_id = org["id"]
    org_name = org.get("name", "Unknown Organization")

    networks = get_networks(org_id)
    if not networks:
        print(f"No networks found for organization: {org_name}")
        return

    first_network = networks[0]
    network_id = first_network["id"]
    network_name = first_network.get("name", "Unknown Network")

    print(f"\nOrganization: {org_name}")
    print(f"Network: {network_name}")

    inventory = get_network_inventory(network_id)
    
    if inventory:
        print("\nInventory Devices:")
        for device in inventory:
            print(f"Serial: {device.get('serial')} - Model: {device.get('model')}")

if __name__ == "__main__":
    main()
