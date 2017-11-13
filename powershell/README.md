# Powershell Scheduled Events Sample
To run the powershell sample: 
1. Copy over both powershell scripts in this directory to your VM 
2. Open [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/powershell-scripting?view=powershell-5.1) in your VM
3. Navigate to the scripts directory in your VM within powershell and run:

            .\ScheduledEventsSample.ps1 -isVnet $true

The VNET flag specifies if the VM is VNET enabled. Non-VNET VMs will require the script to use the discovery utility.

If there are no events, the script will simply print currently scheduled events. If there are events, the script will offer to approve all currently scheduled events.

>[!NOTE] If your VM is not VNET enabled, you'll also need the discovery utility library described below. 

# Scheduled Events Endpoint Discovery

The powershell script leverages the discovery utility library written in C#. In order to use this utility for non-VNET enabled VMs, you must include the discovery dll in the same directory that the powershell scripts are being run. To build this DLL, please see details in the [C# Discovery README](../csharp/EndpointDiscoveryLib)

To see how the discovery dll is used in powershell, please look at [ScheduledEventsDiscoveryUtility.ps1](ScheduledEventsDiscoveryUtility.ps1), which contains helper methods for discoverying the endpoint.