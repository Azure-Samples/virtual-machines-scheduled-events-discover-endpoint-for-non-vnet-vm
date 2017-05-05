/* Copyright 2014 Microsoft Corporation
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
*/
namespace ScheduledEventsSample
{
    using System;
    using System.Collections.Generic;
    using Newtonsoft.Json;

    public class Program
    {
        private static ScheduledEventsClient client;

        static void Main(string[] args)
        {
            // This is only needed for non-vnet VMs! VNET VMs can use the known endpoint
            Uri scheduledEventsEndpoint =
                ScheduledEventsEndpointDiscovery.ScheduledEventsUtility.ObtainScheduledEventsUri();

            client = new ScheduledEventsClient(scheduledEventsEndpoint);
            while (true)
            {
                Console.WriteLine("Getting the Scheduled Events Document...\n");

                // Get the events json string
                string json = client.GetDocument();
                Console.WriteLine($"Scheduled Events Document: {json}\n");

                // Deserialize using Newtonsoft.Json
                ScheduledEventsDocument scheduledEventsDocument = JsonConvert.DeserializeObject<ScheduledEventsDocument>(json);

                // React to events
                HandleEvents(scheduledEventsDocument.Events);

                // Wait for user response
                Console.WriteLine("Press Enter to approve executing events\n");
                Console.ReadLine();

                // Approve events
                ScheduledEventsApproval scheduledEventsApprovalDocument = new ScheduledEventsApproval();
                foreach (CloudControlEvent ccevent in scheduledEventsDocument.Events)
                {
                    scheduledEventsApprovalDocument.StartRequests.Add(new StartRequest(ccevent.EventId));
                }

                if (scheduledEventsApprovalDocument.StartRequests.Count > 0)
                {
                    // Serialize using Newtonsoft.Json
                    string approveEventsJsonDocument =
                        JsonConvert.SerializeObject(scheduledEventsApprovalDocument);

                    Console.WriteLine($"Approving events with json: {approveEventsJsonDocument}\n");
                    client.PostResponse(approveEventsJsonDocument);
                }

                Console.WriteLine("Complete. Press enter to repeat\n\n");
                Console.ReadLine();
                Console.Clear();
            }
        }

        private static void HandleEvents(List<CloudControlEvent> events)
        {
            // Add logic for handling events here
        }
    }
}
