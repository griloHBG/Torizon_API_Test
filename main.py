# to deal with Rest API (HTTP requests)
import requests
# to deal with enviroment variables
import os
# to have Python's type hints
from typing import Dict, List, Text, NamedTuple
# to pretty print some stuff along the way :)
from pprint import pprint
# to get json!
import json

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
'''URL to get the token'''

payload:Dict[str, str] = {
    "client_id":torizon_api_client["TORIZON_API_CLIENT_ID"],
    "client_secret": torizon_api_client["TORIZON_API_CLIENT_SECRET"],
    "grant_type":"client_credentials"
}
'''payload for getting the token'''

# this header came from Postman... but seems like it is not needed
#headers = {
#  'Content-Type': 'application/x-www-form-urlencoded'
#}

# executing the request
response:requests.request = requests.request("POST", url_token_post, data=payload)
'''holds the response of a request'''

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

access_token:str = response_json["access_token"]
'''holds access_token that we got from the server'''

print("Now that we got the access token, let's perform some interesting requests")

header_bearer_auth:Dict[str,str] = {"Authorization":fr"Bearer {access_token}"}
'''header that hold the authorization header. could be reused'''

url_hardware_list:str = "https://app.torizon.io/api/v1/admin/devices/hardware_identifiers"
'''List all hardwareIds registered in this account
https://developer.toradex.com/torizon-platform-services/torizon-platform-api/#tag/Devices/operation/get-v1-admin-devices-hardware_identifiers'''

response = requests.request("GET", url_hardware_list, headers=header_bearer_auth)

print(response.text)

# Syncing the package list from Torizon feeds (is that right?)
# I don't think we need this to trigger updates to our own containers
#print("Update list of Toradex-published packages to the latest version")
#response = requests.request("GET", "https://app.torizon.io/api/metadata/delegations/sync", headers=header_bearer_auth)
#print(response.text)

# Hardcoding Package IDs of our containers
app1_xeyes_package_id:str = "app1-xeyes-arm64-12.12.22-81523"
app2_weston_package_id:str = "app2-weston-dev-arm64-12.12.22-51158"

# We will get the list of user-uploaded packages to check if our packageIDs above are valid :) 
print("Get list of user-uploaded packages")

url_use_package_list = "https://app.torizon.io/api/v1/user_repo/targets.json"

response = requests.request("GET", url_use_package_list, headers=header_bearer_auth)
response_json = response.json()


# trying to get the packageIDs from the response. Trying because something can be wrong? (paranoid here :p)
try:
    package_id_list:List[str] = list(response_json['signed']['targets'].keys())
except:
    print("Something went wrong when parsing the response")
    print("Here is the response:")
    pprint(response.text)

# Checking the existance of the desired packageIDs
if not app1_xeyes_package_id in package_id_list or not app2_weston_package_id in package_id_list:
    print(f"Package {app1_xeyes_package_id} and/or {app2_weston_package_id} couldn't be found in list of user-uploaded packages in Torizon Platform!")
    print("Here is the list of user-uploaded packages available:")
    pprint(package_id_list)
    print()
    print("EXITING!")
    exit()


app1_xeyes_arm64_info:Dict = response_json['signed']['targets'][app1_xeyes_package_id]
'''holds xeyes package info that came from user-uploaded listing API call'''

app2_weston_arm64_info:Dict = response_json['signed']['targets'][app2_weston_package_id]
'''holds weston-dev package info that came from user-uploaded listing API call'''

url_package_comment = "https://app.torizon.io/api/v1/user_repo/comments"
'''URL to get comment of a package'''

# Getting comment about the desired packageIDs
for package_id in [app1_xeyes_package_id, app2_weston_package_id]:
    response = requests.request("GET", f"{url_package_comment}/{package_id}", headers=header_bearer_auth)
    print(f"Comment about {package_id}:")
    print(response.json()["comment"])

apalis_imx8_uuid:str = "40711183-468b-4f40-b5c5-eba16db8ed15"
'''device uuid to be used in API calls'''

# # Useless, but correct infomation
# apalis_imx8_name:str = "Ratchet-Bacon"
# apalis_imx8_device_id:str = "apalis-imx8-06980209-4071"

url_trigger_update:str = "https://app.torizon.io/api/metadata/targets/update"
'''URL to to trigger updates'''

update_payload_generator:callable = lambda package_info, device_uuid : json.dumps({
	"targets": [
		{
			"generateDiff": False,
			"hardwareType": package_info["custom"]["hardwareIds"][0],
			"targetFormat": package_info["custom"]["targetFormat"],
			"to": {
				"checksum": {
					"hash": package_info["hashes"]["sha256"],
					"method": "sha256"
				},
				"target": f"{package_info['custom']['name']}-{package_info['custom']['version']}",
				"targetLength": package_info["length"],
			}
		}
	],
	"updateDevices": [
		device_uuid,
	]
})
'''Function to generate the payload for a CONTAINER update (not an OS update!)
it needs the package information that API will give you via user-uploaded hardware listing API call
and also a device uuid'''

payload_app1_xeyes:Dict = update_payload_generator(app1_xeyes_arm64_info, apalis_imx8_uuid)

payload_app2_weston_dev:Dict = update_payload_generator(app2_weston_arm64_info, apalis_imx8_uuid)

# # How to check request's head and body without sending it
# myrequest = requests.Request("POST", url_trigger_update, data=payload_app1, headers={**header_bearer_auth,"Content-type":"application/json"})
# prepared_request = myrequest.prepare()
# pprint("Header")
# pprint(prepared_request.headers)
# pprint("Body")
# pprint(prepared_request.body)

perform_update:callable = lambda payload: requests.request("POST", url_trigger_update, data=payload, headers=header_bearer_auth)
'''Function to perform the update request to the API for a given hardware to a given application package'''

choice = ""
'''stores the user's choice'''

print("TODO: use https://app.torizon.io/api/v1/devices/{deviceId}/installation_history to find out about the update status")

# Loop to allow user to perform several updates and quit
while not choice == "quit":
    print("Choose from the options below:")
    print("    xeyes: update module to xeyes application")
    print("    weston: update module to Weston with \"desktop\" environment")
    print("    quit: quit this application")

    choice = input().strip()

    if choice == "xeyes":
        response = perform_update(payload_app1_xeyes)
        print(response.headers)
        print(response.text)
        continue

    elif choice == "weston":
        response = perform_update(payload_app2_weston_dev)
        print(response.headers)
        print(response.text)
        continue

print("TODO: use https://app.torizon.io/api/v1/devices/{deviceId}/installation_history to find out about the update status")