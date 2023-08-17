import requests
from . import BASE_URL

def sandbox_create_user(ref_id, key, provider_callback_host: str = "string") -> bool:
    """
        
    """
    res = requests.post(BASE_URL + "/v1_0/apiuser", headers={
        "X-Reference-Id": ref_id,
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
        }, json={
            "providerCallbackHost": provider_callback_host
    }, )
    
    if res.status_code == 201:
        return True
    
    return False


def sandbox_get_user(ref_id, key) -> bool:
    res = requests.get(BASE_URL + "/v1_0/apiuser/" + ref_id, headers={
        "Ocp-Apim-Subscription-Key": key,
        }, 
    )    

    if res.status_code == 200:
        return True
    
    elif res.status_code == 400 or res.status_code == 404:
        ...

    return False


def sandbox_create_api_key(ref_id, key) -> str | bool:
    """
        Used to create an API key for an API user in the sandbox target environment.
    """
    
    res = requests.post(BASE_URL + "/v1_0/apiuser/" + ref_id + "/apikey", headers={
        "Ocp-Apim-Subscription-Key": key,
        }, 
    )

    if res.status_code == 201:
        return res.json()["apiKey"]
    
    elif res.status_code == 400 or res.status_code == 404:
        print(res.json())

    return False
