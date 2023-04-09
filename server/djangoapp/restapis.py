import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, api_key=False, **kwargs):
    print(f"GET from {url}")
    if api_key:
        
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        except:
            print("Error has occurred while making GET request... ")
    else:
        
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        except:
            print("Error has occurred while making GET request... ")

    status_code = response.status_code
    print(f"With status {status_code}")
    json_data = json.loads(response.text)

    return json_data

def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Error has occurred while making POST request... ")
    status_code = response.status_code
    print(f"With status {status_code}")

    return response

def get_dealers_from_cf(url):
    results = []
    json_result = get_request(url)
    dealers = json_result

    for dealer in dealers:

        dealer_doc = dealer["doc"]

        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                               id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                               short_name=dealer_doc["short_name"],
                               st=dealer_doc["st"], zip=dealer_doc["zip"])
        results.append(dealer_obj)

    return results

def get_dealer_by_id(url, dealer_id):

    json_result = get_request(url, dealerId=dealer_id)

    dealer = json_result
    dealer_obj = CarDealer(address=dealer, city=dealer, full_name=dealer,
                           id=dealer, lat=dealer, long=dealer,
                           short_name=dealer,
                           st=dealer, zip=dealer)

    return dealer_obj

def get_dealers_by_state(url, state):
    results = []

    json_result = get_request(url, state=state)
    dealers = json_result["body"]["docs"]

    for dealer in dealers:

        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
        results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []

    json_result = get_request(url, dealerId=dealer_id)

    if json_result:

        reviews = json_result

        for review in reviews:

            review_content = review
            id = review
            name = review
            purchase = review
            dealership = review

            try:
     
                car_make = review
                car_model = review
                car_year = review
                purchase_date = review

                review_obj = DealerReview(dealership=dealership, id=id, name=name, 
                                          purchase=purchase, review=review_content, car_make=car_make, 
                                          car_model=car_model, car_year=car_year, purchase_date=purchase_date
                                          )

            except KeyError:
                print("Something is missing. Using default values.")
               
                review_obj = DealerReview(
                    dealership=dealership, id=id, name=name, purchase=purchase, review=review_content)

            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            print(f"sentiment: {review_obj.sentiment}")

            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(review_text):
    try:
        if os.environ['env_type'] == 'PRODUCTION':
            url = os.environ['https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/70bac3e1-be9e-4377-ad7b-65b95373e5ac']
            api_key = os.environ["iXIXC9JqfDqvXHI5IeDG_L7tuPR62EmJXxjYQtINqw88"]
    except KeyError:
        url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/70bac3e1-be9e-4377-ad7b-65b95373e5ac'
        api_key = 'iXIXC9JqfDqvXHI5IeDG_L7tuPR62EmJXxjYQtINqw88'

    version = '2022-03-30'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)

    try:
        response = nlu.analyze(text=review_text, features=Features(
            sentiment=SentimentOptions())).get_result()
        print(json.dumps(response))
        sentiment_label = response
    except:
        print("Review is too short for sentiment analysis.")
        sentiment_label = "neutral"

    print(sentiment_label)

    return sentiment_label



