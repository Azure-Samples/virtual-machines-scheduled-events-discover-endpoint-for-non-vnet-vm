# Overview

This folder contains sample code for using Scheduled Events and discovering the IP address of Scheduled Events endpoint.


## Sample

### Files

1.  sample.py - This contains the sample script for using Scheduled Events.
2.  util.py – This contains utility functions used by sample script and the discovery script.


### Script usage

If the machine is inside a virtual network, simply run sample.py.

Otherwise, first run discovery.py to find the IP address of the Scheduled Events endpoint. If you used --donotaddtoenv when running
discovery.py, make sure to provide --use_registry when running sample.py. Alternatively, you could provide an IP address using 
--ip_address YOUR_IP_ADDRESS

    $ python sample.py -h
    usage: Sample.py [-h] [--use_registry] [--ip_address IP_ADDRESS]

    Sample code for getting scheduled events.

    optional arguments:
      -h, --help            show this help message and exit
      --use_registry        Get the IP address from Windows registry.
      --ip_address IP_ADDRESS
                            The IP address of scheduled events endpoint.

### Compatibility

**Only runs with Python3.5+**

Runs on both Windows and Linux.


## Discovery

### Files

1.	discovery.py – This contains the core logic and is the entry point.
2.	util.py – This contains utility functions used by main discovery script and the sample script.

### How does endpoint discovery work?

The mechanism to discover the CloudControl IP address is to resend a DHCP request. In the centralized DHCP service, the response is customized 
by carrying the CloudControl IP address inside the DHCP response option 245. The endpoint discovery script uses the same mechanism to determine 
the CloudControl IP address. Once the IP address is obtained, it is made available as part of the environment variable both in Windows and Linux worlds.


### Script usage

By default, upon discovering the CloudControl IP address, the script adds it to the environment variables. The variable name in both Windows and 
Linux is “CLOUDCONTROLIP”. However, the script has two additional modes of operation – “--debug” and “--donotaddtoenv” as listed below.

--debug: Enables running the script in debug mode wherein more logging is available for debugging purposes

--donotaddtoenv: Enables not adding the CloudControl IP as part of the environment variable

    $ python discovery.py -h

    usage: discovery.py [-h] [--debug] [--donotaddtoenv]

    optional arguments:

      -h, --help       show this help message and exit

      --debug          Enable running the script in debug mode

      --donotaddtoenv  Do not add the cloud control endpoint to environment
                      Variable


### Compatibility

python 2.4+ or python 3.5+

**Only runs on Windows**. Once you have installed python, open an admin cmd window. Run the script by calling “python discovery.py”. 
If you want to include any of the optional switches, you can do so by calling “python discovery.py –debug”.
