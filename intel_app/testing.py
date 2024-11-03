import requests

url = f"https://console.hubnet.app/live/api/context/business/transaction/mtn-new-transaction"

headers = {
    "Authorization": "Token QilxVwYRMoXLFQ2m1W4RJ4cLnR7g0b4xDKQ",
    "Content-Type": "application/json"
}

payload = {
    "phone": "0272266444",
    "volume": 1000,
    "reference": "rxstyftftcfxfdxffcfrcf"
}

# Sending the POST request to the API
response = requests.post(url, headers=headers, json=payload)

# Check for the response status and content
if response.ok:
    print("Transaction initialized successfully:", response.json())
else:
    print("Failed to initialize transaction:", response.status_code, response.text)