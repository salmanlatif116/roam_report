import requests


def get_str_and_mtr(latitude, longitude, price, city, zip_code):


    url = "https://www.mashvisor.com/api/v1.1/rento-calculator/lookup"
    
    params = {
        "_t": "QcG6kP3yDnUHD67hWAAQyqrDdFm4gBPW",
        "property_price": f"{price}",
        "currency": "USD",
        "country": "US",
        "state": "TX",
        "city": f"{city}",
        "zip_code": f"{zip_code}",
        "lat": f"{latitude}",
        "lng": f"{longitude}",
        "address": "4930 Eldorado Rose Pl"
    }
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "baggage": "sentry-environment=PROD,sentry-release=mashvisor-spa-CSR@2.184.2,sentry-public_key=d71b0e1be3d944ffb128307fd94aea52,sentry-trace_id=a9c6cfc24a1e44798af8daf7b2dd11a0",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.mashvisor.com/data/lake-jackson-texas?location=%7B%22zipCode%22%3A%2277566%22%2C%22lat%22%3A29.0470948%2C%22lng%22%3A-95.4325008%2C%22routeLong%22%3A%22Redbud+Street%22%2C%22streetNumber%22%3A%22101%22%2C%22propertyType%22%3A%22all%22%2C%22bedrooms%22%3A5%7D",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sentry-trace": "a9c6cfc24a1e44798af8daf7b2dd11a0-842cae702b2feb72",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36"
    }
    
    cookies = {
        "_gcl_gs": "2.1.k1$i1743672227$u168890045",
        "_gcl_au": "1.1.1740466854.1743672236",
        "_mvid": "mv.1.1743672236079.1786618872",
        "_fbp": "fb.1.1743672241780.870943206957164352",
        "intercom-id-o8bzwj24": "cf81392c-8b00-44be-b03b-7bb4353f8b2e",
        "intercom-device-id-o8bzwj24": "ce7bb5f1-c8f6-479d-965f-a12d266ee07f",
        "_gcl_aw": "GCL.1743672251.CjwKCAjw47i_BhBTEiwAaJfPpjsdQpPd58GYtswuy_l0_vbqljFZRbamtNZoMWwR2gNlEA8k3J398BoCLBAQAvD_BwE",
        "hubspotutk": "dfb7a0951da53b42cf8cc4c167a2b4cc",
        "mv_sample_market_10_2024_exp": "sample_market_10_2024_exp.0",
        "__insp_wid": "726421115",
        "__insp_nv": "true",
        "__insp_targlpu": "aHR0cHM6Ly93d3cubWFzaHZpc29yLmNvbS9hdXRoP2Rlc3RpbmF0aW9uPSUyRmV4cGxvcmUlMkZkYXNoYm9hcmQ%3D",
        "__insp_targlpt": "TWFzaHZpc29yIDo6IExvZ2lu",
        "__insp_identity": "dW5kZWZpbmVk",
        "__insp_pad": "1",
        "__insp_sid": "2038966607",
        "__insp_uid": "1643583137",
        "__insp_slim": "1743672489745",
        "mv_airbnb_calculator_search_data_04_25": "airbnb_calculator_search_data_04_25.1",
        "lantern": "92c14186-fc6c-4a7d-aa9e-cbd0c809e7cb",
        "bestLocationCity": "Atlanta",
        "bestLocationState": "GA",
        "bestLocationLng": "-84.3879824",
        "bestLocationLat": "33.7489954",
        "UserTrackingSessionId-0000": "093a80d1-744f-44ac-b909-de38a70d54d3",
        "_gid": "GA1.2.499859588.1749636319",
        "intercom-session-o8bzwj24": "",
        "__hstc": "72298316.dfb7a0951da53b42cf8cc4c167a2b4cc.1743672258246.1747902273925.1749636322511.6",
        "__hssrc": "1",
        "_clck": "u3psxs%7C2%7Cfwo%7C0%7C1919",
        "_uetsid": "92a958e046ab11f09aa6450e95dbc444",
        "_uetvid": "62a07960106d11f0b5dea96ca42d00f3",
        "_ga": "GA1.2.869052084.1743672236",
        "__hssc": "72298316.4.1749636322511",
        "_ga_LN3DSNQBEN": "GS2.1.s1749636309$o6$g1$t1749637749$j5$l0$h0",
        "_clsk": "1qf3t2y%7C1749637755470%7C6%7C1%7Cj.clarity.ms%2Fcollect",
        "_ga_PDTZ8DNJ6M": "GS2.1.s1749636313$o8$g1$t1749637807$j60$l0$h0"
    }
    
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    
    json_response = response.json()
    short_term_rental, mid_term_rental, utilities = calculate_str_and_mtr(json_response)
    return short_term_rental, mid_term_rental, utilities
    
    
    
    
def calculate_str_and_mtr(raw_json):
    try:
    
        utilities = float(raw_json["content"]["expenses_map"].get("utilities", 0))
        occupancy = float(raw_json["content"]["median_occupancy_rate"]) / 100 
        adr = float(raw_json["content"]["median_night_rate"])
        days_in_month = 30
    
        # Short-term rental revenue (Airbnb style)
        short_term = occupancy * adr * days_in_month
    
        # Mid-term discount (15% less than short-term)
        discount_rate = 0.15
        mid_term = short_term * (1 - discount_rate)
    

        short_term_rental = f"${short_term:.2f}"
        mid_term_rental = f"${mid_term:.2f}"
        utilities = f"${utilities:.2f}"
    
        print("Short-Term Revenue:", short_term_rental)
        print("Mid-Term Revenue:", mid_term_rental)

        return short_term_rental, mid_term_rental, utilities

    except Exception as e:
        print("Error:", str(e))



