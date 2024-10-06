import os
import requests
import json

url = 'https://google.serper.dev/search'

def get_search_data(query):
    payload = json.dumps({ 'q': query })

    headers = {
      'X-API-KEY': os.getenv('SERPER_API_KEY'),
      'Content-Type': 'application/json'
    }

    response = requests.request('POST', url, headers=headers, data=payload)
    
    # json_formatted_str = json.dumps(response.text, indent=2)

    return response.text

if __name__ == '__main__':
    print(get_search_data('What is the capital of France?'))
