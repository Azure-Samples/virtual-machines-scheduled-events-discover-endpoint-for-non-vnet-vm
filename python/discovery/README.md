
How does endpoint discovery work?
===
The mechanism to discover the Scheduled Events Service IP address is to send a DHCP request. In the centralized DHCP service, the response is customized by carrying the IP address inside the DHCP response option 245. The endpoint discovery script uses the same mechanism to determine the Scheduled Events IP address. Once the IP address is obtained, it is made available as part of the environment variable both in Windows and Linux worlds.

Running the discovery script
===
### `Pre-requesites`: Install python 2.4+ 

### `Windows:`

Once you have installed python, open an admin cmd window. Run the script by calling “python discovery.py”. 
If you want to include any of the optional switches, you can do so by calling “python discovery.py –debug”.

### `Linux:`

Once you have installed python, run the script by calling “sudo python discovery.py”. You can include any/all of the 
optional switches.

<br>

Discovering the endpoint
===
By default, upon discovering the Scheduled Events Service IP address, the script adds it to the environment variables. The variable name in both Windows and Linux is “SCHEDULEDEVENTSIP”. However, the script has a few additional optional arguments as listed below.

--debug: Enables running the script in debug mode wherein more logging is available for debugging purposes
--donotaddtoenv: Provides the option of not adding the Scheduled Events IP as part of the environment variable
--outputregistry: Provides the option to store scheduled events IP as a registry value in Windows

* python discovery.py -h
usage: discovery.py [-h] [--debug] [--donotaddtoenv]

optional arguments:
  -h, --help       show this help message and exit
  --debug          Enable running the script in debug mode
  --donotaddtoenv  Do not add the scheduled events endpoint to environment variable
  --outputregistry Store scheduled events IP address as registry value in Windows                 


## Example 1: Output to environment variable
* __How to run__: 
```cmd
C:\python> python discovery.py
scheduled events endpoint IP address: 168.63.129.16
Adding scheduled events endpoint IP to the environment

SUCCESS: Specified value was saved.
```
* The host ip is stored in an environment variable %**SCHEDULEDEVENTSIP** by default when running the script with no parameters

## Example 2: Output to registry location
* __How to run__: 
```cmd
C:\python> python discovery.py --outputreg
scheduled events endpoint IP address: 168.63.129.16
Adding scheduled events endpoint IP to the environment

SUCCESS: Specified value was saved.
Adding scheduled events endpoint to registry location HKEY_LOCAL_MACHINE\Software\ScheduledEvents
('168.63.129.16', 1)
```
* For windows VMs, this will set the host IP address for scheduled events in the registry at HKEY_LOCAL_MACHINE\Software\ScheduledEvents

<br>

Creating the Scheduled Events URL with the discovered IP address. 
===
* Once you have the IP address for scheduled events, you can create the scheduled events url with the following format: 

        http://{IPADDRESS}/metadata/scheduledevents?api-version=2017-08-01

## For an example of using the discovery script, please look at the [Python Scheduled Events Sample](../sample/scheduled_events_sample.py)
