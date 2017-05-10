<# 
# Copyright 2017 Microsoft Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#>

# Whether the VM this script is run in is VNET enabled
param([bool]$isVnet = $true)

# Import endpoint discovery utility for non-vnet VMs
. (Join-Path $PSScriptRoot ScheduledEventsDiscoveryUtility)


# How to get scheduled events 
function GetScheduledEvents($uri)
{
    $scheduledEvents = Invoke-RestMethod -Headers @{"Metadata"="true"} -URI $uri -Method get
    $json = ConvertTo-Json $scheduledEvents
    Write-Host "Received following events: `n" $json
    return $scheduledEvents
}


# How to approve a scheduled event
function ApproveScheduledEvent($eventId, $docIncarnation, $uri)
{    
    # Create the Scheduled Events Approval Document
    $startRequests = [array]@{"EventId" = $eventId}
    $scheduledEventsApproval = @{"StartRequests" = $startRequests; "DocumentIncarnation" = $docIncarnation} 
    
    # Convert to JSON string
    $approvalString = ConvertTo-Json $scheduledEventsApproval

    Write-Host "Approving with the following: `n" $approvalString

    # Post approval string to scheduled events endpoint
    Invoke-RestMethod -Uri $uri -Headers @{"Metadata"="true"} -Method POST -Body $approvalString
}


# Add logic relevant to your service here
function HandleScheduledEvents($scheduledEvents)
{

}

######### Sample Scheduled Events Interaction #########

# Configure the scheduled events Url for the VM
if($isVnet)
{
    # Use common scheduled events uri for VNET enabled VM
    $scheduledEventsUrl = 'http://169.254.169.254/metadata/scheduledevents?api-version=2017-03-01'
}
else
{
    # Use discovery utility to discover the endpoint for Non-Vnet VMs
    $scheduledEventsUrl = GetScheduledEventsURLForNonVnet 
}

# Get the document
$scheduledEvents = GetScheduledEvents $scheduledEventsUrl

# Handle events however is best for your service
HandleScheduledEvents $scheduledEvents

# Approve events when ready (optional)
foreach($event in $scheduledEvents.Events)
{
    Write-Host "Current Event: `n" $event
    $entry = Read-Host "`nApprove event? Y/N"
    if($entry -eq "Y" -or $entry -eq "y")
    {
        ApproveScheduledEvent $event.EventId $scheduledEvents.DocumentIncarnation $scheduledEventsUrl 
    }
}