# Discovering the endpoint in C#

The mechanism to discover the Scheduled Events Service IP address is to send a DHCP request. In the centralized DHCP service, the response is customized 
by carrying the IP address inside the DHCP response option 245. The endpoint discovery script uses the same mechanism to determine the Scheduled Events IP address.
 
 The ScheduledEventsEndpointDiscovery library encapsulates all this logic and exposes a single method, ObtainScheduledEventsUri, which can be used to find the full scheduled events endpoint. 

 # Using the Scheduled Events Endpoint Discovery Library

 To use this library, add a reference to the ScheduledEventsEndpointDiscovery library in your C# project. You can then get the scheduled events endpoint as follows: 

        Uri endpoint = ScheduledEventsEndpointDiscovery.ScheduledEventsUtility.ObtainScheduledEventsUri();


**For a sample use of this library, please see the [C# Scheduled Events Sample](../ScheduledEventsSample/Program.cs).** 