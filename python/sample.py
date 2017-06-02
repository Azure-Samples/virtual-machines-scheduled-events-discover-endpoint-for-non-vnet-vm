import json
import urllib.request
import urllib.parse
import sys
import os
import argparse
import winreg as wreg

def get_scheduled_events(address, headers):
    '''
    Make a GET request and return the JSON received.
    '''
    request = urllib.request.Request(address, headers=headers)
    response = urllib.request.urlopen(request)
    return json.loads(response.read())

def post_scheduled_events(address, data, headers):
    '''
    Make a POST request.
    '''
    request = urllib.request.Request(address, data=str.encode(data), headers=headers)
    urllib.request.urlopen(request)

def get_ip_address(args):
    '''
    Get the IP address of scheduled event. Returns None if IP address is not provided or stored.
    '''
    ip_address = None
    if args.ip_address:
        # use IP address provided in parameter
        ip_address = args.ip_address
    elif args.use_registry and sys.platform == 'win32':
        # use CloudControlIp in registry if available.
        try:
            key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, "Software\\CloudControl")
            ip_address = wreg.QueryValueEx(key, 'CloudControlIp')[0]
            key.Close()
        except FileNotFoundError:
            return None
    elif sys.platform == 'win32' or "linux" in sys.platform:
        # use CLOUDCONTROLIP in system variables if available.
        ip_address = os.getenv('COUDCONTROLIP')
    return ip_address

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(description="Sample code for getting scheduled events.")
    parser.add_argument('--use_registry', action="store_true",
                        help="Get the IP address from Windows registry")
    parser.add_argument('--ip_address', type=str,
                        help="The IP address of scheduled events endpoint.")
    return parser.parse_args()

def main():
    '''
    Sample code for getting scheduled events.
    '''
    args = parse_args()

    ip_address = get_ip_address(args)
    print(ip_address)
    if ip_address is None:
        # Default IP address for machines in VNET
        ip_address = '169.254.169.254'

    address = 'http://' + ip_address + '/metadata/scheduledevents?api-version=2017-03-01'
    headers = {'metadata':'true'}

    # Repeat until user terminates the script.
    while True:
        # Send a GET request for scheduled events.
        document = get_scheduled_events(address, headers)
        events = document['Events']
        print('Scheduled Events Document:\n' + str(document))

        # Go through each event and prompt user for approval.
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
