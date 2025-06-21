import whois

def get_whois_info(domain):
    """
    Retrieves WHOIS information for a given domain.
    """
    try:
        w = whois.whois(domain)
        return w
    except Exception as e:
        print(f"Error retrieving WHOIS for {domain}: {e}")
        return None
