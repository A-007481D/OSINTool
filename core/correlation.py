def find_correlations(identity):
    """
    Analyzes a TargetIdentity to find correlations within the collected data.
    """
    correlations = {
        "emails": set(),
        "registrant_info": {},
        "registrar": None,
        "name_servers": set(),
    }
    all_data = identity.get_all_data()

    # --- Extract from WHOIS Data ---
    whois_data = all_data.get("Domain")
    if whois_data:
        # Extract emails
        emails = whois_data.get("emails")
        if emails:
            if isinstance(emails, list):
                correlations["emails"].update(emails)
            elif isinstance(emails, str):
                correlations["emails"].add(emails)

        # Extract Registrant Info
        registrant_fields = ['name', 'org', 'address', 'city', 'state', 'zipcode', 'country']
        for field in registrant_fields:
            if whois_data.get(field):
                correlations["registrant_info"][field.title()] = whois_data[field]
        
        # Extract Registrar
        if whois_data.get("registrar"):
            correlations["registrar"] = whois_data["registrar"]

        # Extract Name Servers
        name_servers = whois_data.get("name_servers")
        if name_servers:
            if isinstance(name_servers, list):
                correlations["name_servers"].update(name_servers)
            elif isinstance(name_servers, str):
                correlations["name_servers"].add(name_servers)

    # Convert sets to lists for consistent data structure
    correlations["emails"] = sorted(list(correlations["emails"]))
    correlations["name_servers"] = sorted(list(correlations["name_servers"]))

    # Filter out empty correlations to keep the display clean
    final_correlations = {k: v for k, v in correlations.items() if v}

    return final_correlations
