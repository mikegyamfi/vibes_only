import requests
from decouple import config


url = f"https://console.hubnet.app/live/api/context/business/transaction/at-new-transaction"

headers = {
    "token": config("BEARER_TOKEN"),
}

payload = {
    "phone": "0242442147",
    "volume": "1000",
    "reference": "zxseewsesxrdrdcrderdx"
}

# Sending the POST request to the API
response = requests.post(url, headers=headers, json=payload)

# Check for the response status and content
if response.ok:
    print("Transaction initialized successfully:", response.json())
else:
    print("Failed to initialize transaction:", response.status_code, response.text)
