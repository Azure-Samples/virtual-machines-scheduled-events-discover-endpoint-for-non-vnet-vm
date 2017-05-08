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
namespace ScheduledEventsEndpointDiscovery
{
    using System;
    using System.Net;
    using System.Net.NetworkInformation;
    using System.Threading;

    public static class ScheduledEventsUtility
    {
        public static readonly int InstanceMetadataServicePort = 8080;
        private static readonly string InstanceMetadataServiceEndpointPath = "/metadata/latest/scheduledevents";
        private const uint ControlSystemDhcpOptionID = 245;

        /// <summary>
        /// Use this method to get the URI for scheduled events
        /// </summary>
        /// <returns></returns>
        public static Uri ObtainScheduledEventsUri()
        {
            IPAddress address = GetDhcpAddress();

            if (address != null)
            {
                Uri endpoint = ConstructScheduledEventsEndpoint(address);
                return endpoint;
            }

            return null;
        }

        // This implementation is copied from the Windows GuestAgent implementation
        private static IPAddress GetDhcpAddress()
        {
            foreach (NetworkInterface nic in DhcpClient.GetDhcpInterfaces())
            {
                if (nic.OperationalStatus != OperationalStatus.Up)
                {
                    continue;
                }

                try
                {
                    IPAddress address = RequestControlSystemEndpointAddress("WindowsAzureGuestAgent", nic);
                    return address;
                }
                catch (DhcpRequestFailedException e)
                {
                    
                }
            }

            return null;
        }

        internal static Uri ConstructScheduledEventsEndpoint(IPAddress address)
        {
            if (address == null)
            {
                throw new ArgumentNullException(nameof(address));
            }

            UriBuilder builder = new UriBuilder();
            builder.Scheme = "http";
            builder.Host = address.ToString();
            builder.Port = InstanceMetadataServicePort;
            builder.Path = InstanceMetadataServiceEndpointPath;
            return builder.Uri;
        }

        private static IPAddress RequestControlSystemEndpointAddress(string appID, NetworkInterface nic)
        {
            IPAddress address = null;
            DhcpRequestFailedException requestException = null;

            var thread = new Thread(() =>
            {
                try
                {
                    using (var client = new DhcpClient() { ApplicationID = appID })
                    {
                        // get DHCP option data
                        byte[] data = client.DhcpRequestParams(nic.Id, ControlSystemDhcpOptionID);

                        if (data == null || data.Length <= 0)
                        {
                            requestException = new DhcpRequestFailedException("Empty DHCP option data returned");
                            return;
                        }

                        if (data.Length != 4)
                        {
                            requestException = new DhcpRequestFailedException("DHCP option data size is not valid");
                            return;
                        }

                        address = new IPAddress(data);
                    }
                }
                catch (Exception e)
                {
                    // We can catch all exceptions here and not re-throw because the caller knows how to handle a null return value.
                    requestException = new DhcpRequestFailedException(e.Message);
                    return;
                }
            });

            thread.Start();

            // wait no more than 3 minutes, to compensate for win7 bug 699003 (timezone issue 
            // causing DHCP service to malfunction, leading to infinite blocking of DHCP API calls)
            if (thread.Join(TimeSpan.FromMinutes(3)) == false)
            {
                // Timed out waiting for DHCP response
                throw new DhcpRequestFailedException("Timed out while waiting for DHCP to respond");
            }

            if (requestException != null)
            {
                throw requestException;
            }

            return address;
        }

    }
}
