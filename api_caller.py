import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
import settings

BASE_URL = settings.API_URL + "/api/v1"

def make_request(url, method="GET", post_fields={}):
    full_url = f"{BASE_URL}/{url}"
    request = Request(full_url)
    request.add_header("Authorization", f"Bearer {settings.API_KEY}")
    request.method = method
    if post_fields:
        request.data = urlencode(post_fields, doseq=True).encode()
    
    try:
        response = urlopen(request)
        response_data = response.read().decode("utf-8")
        return json.loads(response_data)
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error details: {error_message}")
        print(f"URL: {full_url}")
        raise