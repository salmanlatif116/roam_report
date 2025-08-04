import requests

def get_hoa_insrance_taxes_fields(zpid):

    url = f"https://www.zillow.com/zg-graph?zpid={zpid}&operationName=getAffordabilityEstimateFromPersonalizedPaymentChipMVP"
    
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "client-id": "monthly-payment-chip",
        "content-type": "application/json",
        "cookie": (
            "zguid=24|$8df75fa7-2b88-4175-9dc6-ad8239ff2f54; _ga=GA1.2.21898912.1734073934; "
            "zjs_anonymous_id=$8df75fa7-2b88-4175-9dc6-ad8239ff2f54; ..."
            # Add the full cookie string here as needed
        ),
        "origin": "https://www.zillow.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.zillow.com/homedetails/4325-E-Bayou-Maison-Cir-Dickinson-TX-77539/250992805_zpid/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "x-caller-id": "FR_HDP_PP_chip",
        "x-z-enable-oauth-conversion": "true",
        "x-z-fr-allowed-client-id": "FR_HDP_PP_chip",
    }
    
    payload = {
        "operationName": "getAffordabilityEstimateFromPersonalizedPaymentChipMVP",
        "variables": {
            "zpid": zpid
        },
        "query": (
            "query getAffordabilityEstimateFromPersonalizedPaymentChipMVP($zpid: ID!, $userOverrides: UserMortgagePreferences) {"
            "  property(zpid: $zpid) {"
            "    affordabilityEstimate(params: $userOverrides) {"
            "      monthly {"
            "        homeownersInsurance"
            "        principalAndInterest"
            "        privateMortgageInterest"
            "        propertyTax"
            "        hoaFees"
            "      }"
            "      monthlyCostCalculatorData {"
            "        mortgageCTA {"
            "          routingURL"
            "        }"
            "      }"
            "    }"
            "  }"
            "}"
        )
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


