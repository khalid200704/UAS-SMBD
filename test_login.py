import requests
import json

# URL for the login endpoint
url = 'http://localhost:5000/api/login'

# Login credentials
payload = {
    'username': 'admin',
    'password': 'admin123'
}

# Headers for the request
headers = {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5000'
}

# Make the login request
print("Attempting to log in...")
try:
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers,
        allow_redirects=True
    )
    
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    for header, value in response.headers.items():
        print(f"  {header}: {value}")
    
    print("\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    
    # Check for session cookie
    if 'session' in response.cookies:
        print("\nSession cookie found!")
        print(f"Session cookie: {response.cookies['session']}")
    else:
        print("\nNo session cookie in response!")
        
except Exception as e:
    print(f"Error: {e}")
