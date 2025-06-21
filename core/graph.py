import networkx as nx

def create_graph_from_identity(identity, correlations):
    """
    Creates a NetworkX graph from a TargetIdentity and its correlations.
    """
    G = nx.Graph()
    target_name = identity.name

    # Add the central target node
    G.add_node(target_name, type='target')

    # Add nodes and edges for emails
    for email in correlations.get("emails", []):
        G.add_node(email, type='email')
        G.add_edge(target_name, email)

    # Add node and edge for registrar
    registrar = correlations.get("registrar")
    if registrar:
        G.add_node(registrar, type='registrar')
        G.add_edge(target_name, registrar)

    # Add nodes and edges for name servers
    for ns in correlations.get("name_servers", []):
        G.add_node(ns, type='name_server')
        G.add_edge(target_name, ns)

    # Add node and edges for registrant information
    registrant_info = correlations.get("registrant_info")
    if registrant_info:
        # Create a single representative node for the registrant
        registrant_name = registrant_info.get("Name", "Unknown Registrant")
        G.add_node(registrant_name, type='registrant', details=registrant_info)
        G.add_edge(target_name, registrant_name)

    return G
