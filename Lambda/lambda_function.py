import json
import boto3
import datetime
from botocore.vendored import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
import csv
from io import BytesIO

def lambda_handler(event, context):
    """
    This lambda function calls the yelp api to fetch restaurants in DynamoDB table 
    yelp-restaurants and indexes it in elastic search.
    """
    resultData = []
    cuisines = ['indian', 'mexican', 'chinese', 'thai', 'japanese']
    # Change this location to New York, Manhattan.
    location = "manhattan"
    if event['data_origin'] == 'yelp':
        restaurantIterations = 8
        for cuisine in cuisines:
            
            for i in range(restaurantIterations):
                requestData = {
                                "term": cuisine + " restaurants",
                                "location": location,
                                "limit": 50,
                                "offset": 50*i
                            }
                result = get_yelp(requestData)
                resultData = resultData + result
        
        # Add data to DynamodDB
        dynamoInsert(resultData)
        
        # Add index data to the ElasticSearch
        addElasticIndex(resultData)   
        
    return {
        'statusCode': 200,
        'body': json.dumps('success')
    }

def get_yelp(requestData):
    
    yelp_rest_endpoint = "https://api.yelp.com/v3/businesses/search"
    
    querystring = requestData
    
    payload = ""
    headers = {
        "Authorization": "Bearer GALd5l4Y7ID64YGczovQg-obqcnq0qGJci9p5aykkGllZsx9vxSeyMqKThSiHFjrH1OhIoAbgDfD2laMks0hJhmS9I994PPnPy1oF4PB8pbQ0IveYXOv8W4BK6ueXXYx"
        }
    
    response = requests.request("GET", yelp_rest_endpoint, data=payload, headers=headers, params=querystring)
    message = json.loads(response.text)
    
    if len(message['businesses']) <= 0:
        return []
    
    return message['businesses']

def dynamoInsert(restaurants):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    
    
    for restaurant in restaurants:
        
        tableEntry = {
            'id': restaurant['id'],
            'alias': restaurant['alias'],
            'name': restaurant['name'],
            'is_closed': restaurant['is_closed'],
            'categories': restaurant['categories'],
            'rating': int(restaurant['rating']),
            'review_count': int(restaurant['review_count']),
            'address': restaurant['location']['display_address']
        }        
        table.put_item(
            Item={
                'insertedAtTimestamp': str(datetime.datetime.now()),
                'id': tableEntry['id'],
                'name': tableEntry['name'],
                'address': tableEntry['address'],
                'latitude': tableEntry.get('latitude', None),
                'longitude': tableEntry.get('longitude', None),
                'review_count': tableEntry['review_count'],
                'rating': tableEntry['rating'],
                'zip_code': tableEntry.get('zip_code', None),
                'categories': tableEntry['categories']
               }
            )
    

def addElasticIndex(restaurants):
    host = 'search-restaurants-bpoued5hlvrv4fn74iuqwi7i7y.us-east-1.es.amazonaws.com' 
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    for restaurant in restaurants:
        
        index_data = {
            'id': restaurant['id'],
            'categories': restaurant['categories']
        }                            
        print ('dataObject', index_data)
        
        es.index(index="restaurants", doc_type="Restaurant", id=restaurant['id'], body=index_data, refresh=True)
