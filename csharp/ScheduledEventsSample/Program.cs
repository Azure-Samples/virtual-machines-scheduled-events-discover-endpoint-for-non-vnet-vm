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
            Uri scheduledEventsEndpoint;

            Console.WriteLine("Is this virtual machine VNET Enabled? Y/N");
            string response = Console.ReadLine();
            bool vNet = string.Equals("Y", response, StringComparison.OrdinalIgnoreCase);

            if (vNet)
            {
                // Use the known endpoint available for VNET VMs
                scheduledEventsEndpoint = new Uri("http://169.254.169.254/metadata/scheduledevents?api-version=2017-08-01");
            }
            else
            {
                // Use discovery utility to discover the endpoint
                scheduledEventsEndpoint = ScheduledEventsEndpointDiscovery.ScheduledEventsUtility.ObtainScheduledEventsUri();
            }

            Console.WriteLine("Scheduled Events URI: {0}", scheduledEventsEndpoint);

            client = new ScheduledEventsClient(scheduledEventsEndpoint);

            while (true)
            {
                Console.WriteLine("Getting the Scheduled Events Document...\n");

                // Get the events json string
                string json = client.GetScheduledEvents();
                Console.WriteLine($"Scheduled Events Document: {json}\n");

                // Deserialize using Newtonsoft.Json
                ScheduledEventsDocument scheduledEventsDocument = JsonConvert.DeserializeObject<ScheduledEventsDocument>(json);

                // React to events
                HandleEvents(scheduledEventsDocument.Events);

                // Wait for user response
                Console.WriteLine("Press Enter to approve all scheduled events\n");
                Console.ReadLine();

                // Create approval document and approve events
                ScheduledEventsApproval scheduledEventsApprovalDocument = new ScheduledEventsApproval()
                {
                    DocumentIncarnation = scheduledEventsDocument.DocumentIncarnation
                };

                foreach (ScheduledEvent e in scheduledEventsDocument.Events)
                {
                    scheduledEventsApprovalDocument.StartRequests.Add(new StartRequest(e.EventId));
                }

                if (scheduledEventsApprovalDocument.StartRequests.Count > 0)
                {
                    // Serialize using Newtonsoft.Json
                    string approveEventsJsonDocument =
                        JsonConvert.SerializeObject(scheduledEventsApprovalDocument);

                    Console.WriteLine($"Approving events with json: {approveEventsJsonDocument}\n");
                    client.ExpediteScheduledEvents(approveEventsJsonDocument);
                }

                Console.WriteLine("Complete. Press enter to repeat\n\n");
                Console.ReadLine();
                Console.Clear();
            }
        }

        private static void HandleEvents(List<ScheduledEvent> events)
        {
            // Add logic for handling events here
        }
    }
}
