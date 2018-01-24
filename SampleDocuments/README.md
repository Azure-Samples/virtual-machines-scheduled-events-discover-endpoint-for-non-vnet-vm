# Sample Documents

In this folder you'll find example documents that you may receive in your VM. You can practice interacting with the document locally instead of having to create a VM. Below is a sample of using the samples in windows powershell: 

# Powershell Example
**PS C:\Users\UserName\Desktop>** $events = ConvertFrom-Json (Get-Content .\SampleScheduledEventsDocument.json)

**PS C:\Users\UserName\Desktop>** $events


```
DocumentIncarnation Events
------------------- ------
192                 {@{EventId=28512AF7-C957-4500-9BC4-842D6FB531E4;  
                    EventStatus=Scheduled; EventType=Reboot; ResourceType=VirtualMachine; Resources=System.Object[]; NotBefore=Wed, 24 Jan 2

```

**PS C:\Users\UserName\Desktop>** $events.Events

```
EventId      : 28512AF7-C957-4500-9BC4-842D6FB531E4
EventStatus  : Scheduled
EventType    : Reboot
ResourceType : VirtualMachine
Resources    : {sample_4}
NotBefore    : Wed, 24 Jan 2018 21:20:44 GMT

EventId      : A626E37F-793E-44E1-89B5-99AE0B96044C
EventStatus  : Scheduled
EventType    : Reboot
ResourceType : VirtualMachine
Resources    : {sample_1}
NotBefore    : Wed, 24 Jan 2018 21:20:44 GMT
```

**PS C:\Users\UserName\Desktop>** $events = ConvertFrom-Json (Get-Content .\SampleEmptyEventsDocument.json)

**PS C:\Users\UserName\Desktop>** $events

```
DocumentIncarnation Events
------------------- ------
                190 {}

```

