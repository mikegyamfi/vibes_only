import secrets
import json
import requests
from datetime import datetime
from decouple import config

ishare_map = {
    2: 50,
    4: 52,
    7: 2000,
    10: 3000,
    12: 4000,
    15: 5000,
    18: 6000,
    22: 7000,
    25: 8000,
    30: 10000,
    45: 15000,
    60: 20000,
    75: 25000,
    90: 30000,
    120: 40000,
    145: 50000,
    285: 100000,
    560: 200000
}


import secrets
import itertools
import random

# Initialize a counter to generate unique numbers within the session
counter = itertools.count()

def ref_generator(length=30):
    # Get the next unique counter and generate a random component
    unique_number = next(counter)
    random_part = secrets.token_hex((length - 10) // 2).upper()  # Adjusted length for prefix, counter, and suffix
    suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))  # Random 3-character suffix

    return f"DT{unique_number:04}-{random_part}-{suffix}"

def top_up_ref_generator(length=25):
    unique_number = next(counter)
    random_part = secrets.token_hex((length - 10) // 2).upper()  # Adjusted length for prefix and counter
    suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=2))  # Random 2-character suffix

    return f"TOPUP-{unique_number:04}-{random_part}-{suffix}"


def send_bundle(user, network, bundle_amount, reference, receiver_phone):
    url = f"https://console.hubnet.app/live/api/context/business/transaction/{network}-new-transaction"

    headers = {
        "token": config("BEARER_TOKEN"),
    }

    payload = {
        "phone": str(receiver_phone),
        "volume": str(bundle_amount),
        "reference": reference
    }

    # Sending the POST request to the API
    response = requests.post(url, headers=headers, json=payload)

    # Check for the response status and content
    if response.ok:
        print("Transaction initialized successfully:", response.json())
    else:
        print("Failed to initialize transaction:", response.status_code, response.text)

    return response



# def controller_send_bundle(receiver, bundle_amount, reference):
#     url = "https://controller.geosams.com/api/v1/new_transaction"
#     print(receiver, bundle_amount, reference)
#
#     payload = json.dumps({
#         "account_number": receiver,
#         "reference": reference,
#         "bundle_amount": bundle_amount
#     })
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': config('TOKEN')
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     print(response.text)
#     return response
#
#
# def value_4_moni_send_bundle(receiver, bundle_amount, reference):
#     url = "https://www.value4moni.com/api/v1/inititate_transaction"
#
#     # Payload data to send in the request
#     data = {
#         "API_Key": config("VALUE_API_KEY"),
#         "Receiver": str(receiver),
#         "Volume": str(bundle_amount),
#         "Reference": str(reference),
#         "Package_Type": "AirtelTigo"
#     }
#
#     # Make the POST request
#     response = requests.post(url, json=data)
#
#     # Print the response from the server
#     print(f"Status Code: {response.status_code}")
#     print(f"Response: {response.json()}")
#
#     return response


def verify_paystack_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": "Bearer sk_test_d8585b8c1c61a364640e9acbb3bc8046f5fb9acd"
    }

    response = requests.request("GET", url, headers=headers)

    print(response.json())

    return response

