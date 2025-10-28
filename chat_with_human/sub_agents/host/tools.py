def find_sponsors_with_apollo(criteria: str, api_key: str) -> str:
    """
    Find sponsor leads using Apollo API.
    
    Args:
        criteria: Search criteria (e.g., "tech companies in San Francisco")
        api_key: Apollo API key
    
    Returns:
        JSON string of lead data
    """
    try:
        result = _call_service('POST', '/leads/apollo/find-leads', json={
            'criteria': criteria,
            'api_key': api_key
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


def enrich_leads_with_clay(leads_json: str, api_key: str) -> str:
    """
    Enrich lead data using Clay API.
    
    Args:
        leads_json: JSON string of leads from Apollo
        api_key: Clay API key
    
    Returns:
        JSON string of enriched lead data
    """
    try:
        result = _call_service('POST', '/leads/clay/enrich-leads', json={
            'leads_json': leads_json,
            'api_key': api_key
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


def upload_contacts_to_hubspot_json(contacts_json: str) -> str:
    """
    Upload contacts to HubSpot CRM.
    
    Args:
        contacts_json: JSON string of enriched contacts
    
    Returns:
        Success message
    """
    try:
        result = _call_service('POST', '/leads/hubspot/sync-contacts', json={
            'contacts_json': contacts_json
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e), "message": "Failed to sync to HubSpot. Make sure HubSpot is connected in Settings."})