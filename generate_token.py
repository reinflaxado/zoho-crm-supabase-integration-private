import requests

# Your Zoho client credentials from .env
client_id = "1000.UNB58ZS0C379RPF1XNZTQN1WR53VOA"
client_secret = "ed1831881558014810e42f3aa6f85ee85c0500008b"
redirect_uri = "http://localhost:8000/api/auth/callback"

# Step 1: Generate authorization URL
auth_url = f"https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL,ZohoCRM.settings.ALL&client_id={client_id}&response_type=code&access_type=offline&redirect_uri={redirect_uri}"

print(f"Visit this URL in your browser to authorize:\n{auth_url}")

# Step 2: After authorization, you'll be redirected to your callback URL with a code parameter
code = input("Enter the 'code' parameter from the redirect URL: ")

# Step 3: Exchange authorization code for refresh token
token_url = "https://accounts.zoho.com/oauth/v2/token"
params = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "redirect_uri": redirect_uri
}

response = requests.post(token_url, params=params)
tokens = response.json()

print(f"\nResponse from Zoho: {tokens}")
print(f"\nYour refresh token is: {tokens.get('refresh_token')}")
print("Add this to your .env file as ZOHO_REFRESH_TOKEN") 