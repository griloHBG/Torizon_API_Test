# to deal with Rest API (HTTP requests)
import requests
# to deal with enviroment variables
import os
# to have Python's type hints
from typing import Dict, List, Text, NamedTuple

# Meant for Torizon API V1: https://developer.toradex.com/torizon-platform-services/torizon-platform-api/


torizon_api_client:Dict[str, Dict[str, str]] = {
    "TORIZON_API_CLIENT_ID": "",
    "TORIZON_API_CLIENT_SECRET": "",
}
'''set of environment variables that this script expects to be set beforehand'''

current_env_variables:Dict = dict(os.environ.items());
'''holds environment variables current set'''

env_variable_missing:List[str] = []
'''name of environment variables that should've be set but aren't'''

# iterates through the required environement variables and check if they are set or not
for env_variable_name in torizon_api_client.keys():
    if not env_variable_name in current_env_variables.keys():
        # stores names of environment variables not set
        env_variable_missing.append(env_variable_name)
    else:
        # stores the values of the required environemt variables
        torizon_api_client[env_variable_name] = current_env_variables[env_variable_name]
        #print(f"{env_variable_name}={torizon_api_client[env_variable_name]}")

# Warns about the missing environment variables and exits
if len(env_variable_missing) > 0:
    print("One or more environment variables are not set. Please set them before running this script")
    print()
    print("List of environment variables not set:",", ".join(env_variable_missing))
    exit()

# next step
print(f"Now that we have {', '.join(torizon_api_client.keys())} set, let's ask for the token needed to perform the other requests to the Torizon API!")

url_token_post:str = "https://kc.torizon.io/auth/realms/ota-users/protocol/openid-connect/token"
payload:Dict[str, str] = {
    "client_id":torizon_api_client["TORIZON_API_CLIENT_ID"],
    "client_secret": torizon_api_client["TORIZON_API_CLIENT_SECRET"],
    "grant_type":"client_credentials"
}
# this header came from Postman... but seems like it is not needed
#headers = {
#  'Content-Type': 'application/x-www-form-urlencoded'
#}

# executing the request
response:requests.request = requests.request("POST", url_token_post, data=payload)
'''holds the response of the request'''

response_json:Dict[str, str] = response.json()
'''holds the response body as a Dict'''

expected_fields:List[str] = ["expires_in", "refresh_expires_in", "token_type", "not-before-policy", "scope"]
'''all the fields expected to be present in the response of the token request'''

# checking if any of the expected fields from token response is missing (actually the access_token is the one required :) )
for field in expected_fields:
    if not field in response_json.keys():
        print(f"The '{field}' is not present in the token response. WTF HAPPENED?! Wrong URL?!\n EXITING!")
        exit()

# access_token = response_json["access_token"]
# expires_in = response_json["expires_in"]
# refresh_expires_in = response_json["refresh_expires_in"]
# token_type = response_json["token_type"]
# not_before_policy = response_json["not-before-policy"]
# scope = response_json["scope"]

access_token = response_json["access_token"]
'''holds access_token that we got from the server'''

print("Now that we got the access token, let's perform some interesting requests")

header_bearer_auth = {"Authorization":fr"Bearer {access_token}"}
'''header that hold the authorization header. could be reused'''

response = requests.request("GET", "https://app.torizon.io/api/v1/admin/devices/hardware_identifiers", headers=header_bearer_auth)

print(response.text)