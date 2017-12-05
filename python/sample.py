'''
Sample python script for Scheduled Events.

Continues to run GET and POST (if approved by user) request to Scheduled Events endpoint.
Press Ctrl + C and then Enter to exit.
'''
# Copyright 2014 Microsoft Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import argparse
import urllib.request
import urllib.parse

def get_address(arg_ip_address, use_registry, headers):

    '''

    Gets the address of the Scheduled Events endpoint.

    '''

    ip_address = None

    address = None

    if arg_ip_address:

        # use IP address provided in parameter.

        ip_address = arg_ip_address

    else:

        # use default IP address for machines in VNET.

        ip_address = '169.254.169.254'



    # Check if the IP address is valid. If not, try getting the IP address from registry

    # or environment. Exits if no IP address is valid.

    address = make_address(ip_address)

    if not check_ip_address(address, headers):

        print("The provided IP address is invalid or VM is not in VNET. " +

              "Trying registry and environment.")

        ip_address = get_ip_address_reg_env(use_registry)

        address = make_address(ip_address)

        if not check_ip_address(address, headers):

            print("Could not find a valid IP address. Please create your VM within a VNET " +

                  "or run discovery.py first")

            exit(1)

    return address

def get_scheduled_events(address, headers):

    '''

    Make a GET request and return the response received.

    '''

    request = urllib.request.Request(address, headers=headers)

    return urllib.request.urlopen(request)



def post_scheduled_events(address, data, headers):

    '''

    Make a POST request.

    '''

    request = urllib.request.Request(address, data=str.encode(data), headers=headers)

    urllib.request.urlopen(request)

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(description="Sample code for getting scheduled events.")
    parser.add_argument('--use_registry', action="store_true",
                        help="Get the IP address from Windows registry.")
    parser.add_argument('--ip_address', type=str,
                        help="The IP address of scheduled events endpoint.")
    return parser.parse_args()

def main():
    '''
    Sample code for getting scheduled events.
    '''
    args = parse_args()
    headers = {'metadata':'true'}

    address = get_address(args.ip_address, args.use_registry, headers)

    print("Scheduled Events endpoint address = " + address)

    # Repeat until user terminates the script.
    while True:
        # Send a GET request for scheduled events and read the response.
        response = get_scheduled_events(address, headers)
        document = json.loads(response.read().decode('utf-8'))
        events = document['Events']
        print('Scheduled Events Document:\n' + str(document))

        # Go through each event in the response and prompt user for approval.
        for event in events:
            print("Current Event:\n" + str(event))
            approved = input("Approve event? (y / n): ")
            if approved.lower() == 'y':
                data = {
                    "DocumentIncarnation": document["DocumentIncarnation"],
                    "StartRequests": [{
                        "EventId": event["EventId"]
                    }]
                }
                print("Approving with the following:\n" + str(data))
                # Send a POST request to expedite.
                post_scheduled_events(address, json.dumps(data), headers)
        input("Press Enter to continue.")

if __name__ == '__main__':
    main()
