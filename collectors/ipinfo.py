from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError
from core.json_utils import safe_json_dump

def get_ip_info(ip_address):
    """
    Retrieves information for a given IP address.
    """
    try:
        obj = IPWhois(ip_address)
        results = obj.lookup_whois()
        return results
    except IPDefinedError as e:
        print(f"IP address is private: {ip_address}. Error: {e}")
        return None
    except Exception as e:
        print(f"Error retrieving IP info for {ip_address}: {e}")
        return None
