# Scheduled Events Endpoint Discovery for Non-VNET VMs

In the case where your VM is not configured within a VNET, the default scheduled events endpoint will not be accessible. In order to discover the endpoint for scheduled events, you can run the discovery.py script, which will output the ipaddress to be used when creating the scheduled events uri. 

## Example 1: Output to environment variable
* __How to run__: python discovery.py
* The host ip is stored in an environment variable (**CLOUDCONTROLIP**) by default when running the script with no parameters

## Example 2: Output to registry location
* __How to run__: python discovery.py --outputregistry
* For windows VMs, this will set the host IP address for scheduled events in the registry at HKEY_LOCAL_MACHINE\Software\CloudControl

## Creating the Scheduled Events URL with the discovered IP address. 
* Once you have the IP address for scheduled events, you can create the scheduled events url with the following format: **http://{IPADDRESS}/metadata/scheduledevents?api-version=2017-03-01**




#### For more detailed info on script parameters and how endpoint discovery works, please read the **README.md** for the python scripts. 
