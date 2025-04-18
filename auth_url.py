client_id = "1000.UNB58ZS0C379RPF1XNZTQN1WR53VOA"
redirect_uri = "http://localhost:8000/api/auth/callback"

# Generate authorization URL
auth_url = f"https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL,ZohoCRM.settings.ALL&client_id={client_id}&response_type=code&access_type=offline&redirect_uri={redirect_uri}"

print(f"Visit this URL in your browser to authorize:\n{auth_url}") 