import requests

client_secret = '5f497514233a474422131996e24ee132b554b48d0d7d34feea13d18f81295260'
client_id = '60b41cc7e23a8a143bc914bdd2ef8132d205f12bf2750c104f626bbb2c9e7641'
access_token = ''


def get_auth():
    url = "http://www.healthos.co/api/v1/oauth/token.json"

    payload = "{\n  \"grant_type\": \"client_credentials\",\n  \"client_id\": \"" + client_id + \
              "\",\n  \"client_secret\": " \
              "\"" + client_secret + "\",\n  \"scope\": \"public read write\"\n} "

    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, data=payload, headers=headers)

    if response.status_code == 200:
        global access_token
        access_token = response.json()['access_token']


def get_medicine(page, size):
    global access_token
    if not access_token:
        get_auth()
    url = "http://www.healthos.co/api/v1/medicines/brands"

    querystring = {"page": str(page), "size": str(size)}

    headers = {'Authorization': 'Bearer ' + access_token}

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)


def get_generic(query):
    url = "http://www.healthos.co/api/v1/autocomplete/medicines/generics/" + str(query)

    headers = {'Authorization': 'Bearer ' + access_token}

    response = requests.request("GET", url, headers=headers)

    print(response.text)
