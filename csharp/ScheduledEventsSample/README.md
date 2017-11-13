# C# Scheduled Events Sample

The C# Scheduled Events sample is an interactive application that will query for the current scheduled events, then offer to approve any availailable scheduled events.

# How to build the scheduled events sample application

To build the application:

1. Download and install the [Visual Studio IDE](https://www.visualstudio.com)
2. [Clone this repository](https://help.github.com/articles/cloning-a-repository/) to your local machine
3. Open [ScheduledEventsSample.sln](../ScheduledEventsSample.sln) in Visual Studio.
4. Under the `Build` tab in Visual Studio, click `Build Solution`.
    * See here for more info on [Building in Visual Studio](https://msdn.microsoft.com/en-us/library/cyz1h6zd.aspx)

# Running the C# Scheduled Events Sample
After you've built the application in Visual Studio, you should have the assemblies available in your local bin directory within the Scheduled Events Sample directory. To run the application:

1. Copy over the entire folder that contains the assemblies that were created when you built the sample to you Windows virtual machine.
2. Double click the ScheduledEventsSample.exe file in the folder just coped to your virtual machine.
3. The sample will ask if the current VM is VNET enabled. Type `Y` if it is and `N` if the VM is not VNET enabled.

# Endpoint Discovery for Non-VNET VMs
For more information on endpoint discovery for non-VNET VMs, please see the [Endpoint Discovery in C# README](../EndpointDiscoveryLib).