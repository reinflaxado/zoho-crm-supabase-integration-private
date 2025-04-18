import requests

# Your Zoho client credentials
client_id = "1000.UNB58ZS0C379RPF1XNZTQN1WR53VOA"
client_secret = "ed1831881558014810e42f3aa6f85ee85c0500008b"
redirect_uri = "http://localhost:8000/api/auth/callback"

# Enter the code you received after authorizing the app
code = input("Enter the 'code' parameter from the redirect URL: ")

# Exchange authorization code for refresh token
token_url = "https://accounts.zoho.com/oauth/v2/token"
params = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "redirect_uri": redirect_uri
}

try:
    response = requests.post(token_url, params=params)
    tokens = response.json()
    
    print(f"\nResponse from Zoho: {tokens}")
    
    if "refresh_token" in tokens:
        print(f"\nYour refresh token is: {tokens['refresh_token']}")
        print("Add this to your .env file as ZOHO_REFRESH_TOKEN")
    else:
        print("\nNo refresh token in the response. Check the error message above.")
except Exception as e:
    print(f"Error: {e}") 