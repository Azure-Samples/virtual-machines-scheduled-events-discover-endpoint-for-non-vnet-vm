# Azure Metadata Service: Scheduled Events Samples

Scheduled Events is one of the subservices under the Azure Metadata Service. It is responsible for surfacing information regarding upcoming events (for example, reboot) so your application can prepare for them and limit disruption. It is available for all Azure Virtual Machine types including PaaS and IaaS. Scheduled Events gives your Virtual Machine time to perform preventive tasks to minimize the effect of an event.

Scheduled Events is available for both Linux and Windows VMs. 
* For information about Scheduled Events on Linux, see [Scheduled Events for Linux VMs](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/scheduled-events).
* For information about Scheduled Events on Windows, see [Scheduled Events for Windows VMs](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/scheduled-events).


# Currently Available Samples
Samples have been created for the following programming languages. Please follow the links for more details on how to build and run the samples: 
- [Powershell](powershell)
- [Python](python)
- [C#](csharp)

# Scheduled Events Endpoint Discovery for Non-VNET VMs

In the case where your VM is not configured within a VNET, the default scheduled events endpoint will not be accessible and will need to be discovered. Each of the above language samples provide utilities that can be used to discover the endpoint. 

#### For more detailed info on script parameters and how endpoint discovery works, please read the [README.md](https://github.com/Azure-Samples/virtual-machines-python-scheduled-events-discover-endpoint-for-non-vnet-vm/blob/master/python/README.md) for any of the languages above. 
