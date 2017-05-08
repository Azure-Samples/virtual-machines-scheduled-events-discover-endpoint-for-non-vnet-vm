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
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Net.NetworkInformation;
    using System.Runtime.InteropServices;

    /// <summary>
    /// A simple DHCP client for retrieving the Instance Metadata Service endpoint
    /// </summary>
    /// <remarks>
    /// This implementation is copied from the Windows GuestAgent implementation 
    /// </remarks>
    public class DhcpClient : IDisposable
    {
        /// <summary>
        /// Gets or sets the application identifier to use for persistent requests.
        /// </summary>
        public string ApplicationID { get; set; }

        public DhcpClient()
        {
            uint version;
            int err = NativeMethods.DhcpCApiInitialize(out version);
            if (err != 0)
            {
                throw new Win32Exception(err);
            }
        }

        public void Dispose()
        {
            NativeMethods.DhcpCApiCleanup();
        }

        /// <summary>
        /// Gets the available interfaces that are enabled for DHCP.
        /// </summary>
        /// <remarks>
        /// The operational status of the interface is not assessed.
        /// </remarks>
        /// <returns></returns>
        public static IEnumerable<NetworkInterface> GetDhcpInterfaces()
        {
            foreach (var nic in NetworkInterface.GetAllNetworkInterfaces())
            {
                if (nic.NetworkInterfaceType != NetworkInterfaceType.Ethernet ||
                    !nic.Supports(NetworkInterfaceComponent.IPv4))
                {
                    continue;
                }

                IPv4InterfaceProperties v4props = nic.GetIPProperties()?.GetIPv4Properties();
                if (v4props == null || !v4props.IsDhcpEnabled)
                {
                    continue;
                }

                yield return nic;
            }
        }

        /// <summary>
        /// Requests DHCP parameter data.
        /// </summary>
        /// <remarks>
        /// Windows serves the data from a cache when possible.  
        /// With persistent requests, the option is obtained during boot-time DHCP negotiation.
        /// </remarks>
        /// <param name="adapterName">Name of the adapter on which the request is being made.</param>
        /// <param name="optionId">the option to obtain.</param>
        /// <returns></returns>
        public byte[] DhcpRequestParams(string adapterName, uint optionId)
        {
            uint bufferSize = 1024;
            Retry:
            IntPtr buffer = Marshal.AllocHGlobal((int)bufferSize);
            try
            {
                var sendParams = new NativeMethods.DHCPCAPI_PARAMS_ARRAY();
                sendParams.nParams = 0;
                sendParams.Params = IntPtr.Zero;

                var recv = new NativeMethods.DHCPCAPI_PARAMS();
                recv.Flags = 0x0;
                recv.OptionId = optionId;
                recv.IsVendor = false;
                recv.Data = IntPtr.Zero;
                recv.nBytesData = 0;

                var recdParamsPtr = Marshal.AllocHGlobal(Marshal.SizeOf(recv));
                try
                {
                    Marshal.StructureToPtr(recv, recdParamsPtr, false);

                    var recdParams = new NativeMethods.DHCPCAPI_PARAMS_ARRAY();
                    recdParams.nParams = 1;
                    recdParams.Params = recdParamsPtr;

                    var flags = NativeMethods.DhcpRequestFlags.DHCPCAPI_REQUEST_SYNCHRONOUS;

                    int err = NativeMethods.DhcpRequestParams(
                        flags,
                        IntPtr.Zero,
                        adapterName,
                        IntPtr.Zero,
                        sendParams,
                        recdParams,
                        buffer,
                        ref bufferSize,
                        this.ApplicationID);

                    if (err == NativeMethods.ERROR_MORE_DATA)
                    {
                        bufferSize *= 2;
                        goto Retry;
                    }

                    if (err != 0)
                    {
                        throw new Win32Exception(err);
                    }

                    recv = (NativeMethods.DHCPCAPI_PARAMS)
                        Marshal.PtrToStructure(recdParamsPtr, typeof(NativeMethods.DHCPCAPI_PARAMS));

                    if (recv.Data == IntPtr.Zero)
                    {
                        return null;
                    }

                    byte[] data = new byte[recv.nBytesData];
                    Marshal.Copy(recv.Data, data, 0, (int)recv.nBytesData);
                    return data;
                }
                finally
                {
                    Marshal.FreeHGlobal(recdParamsPtr);
                }
            }
            finally
            {
                Marshal.FreeHGlobal(buffer);
            }
        }
    }

    #region Native Methods
    internal static partial class NativeMethods
    {
        public const uint ERROR_MORE_DATA = 124;

        [DllImport("dhcpcsvc.dll", EntryPoint = "DhcpRequestParams", CharSet = CharSet.Unicode, SetLastError = false)]
        public static extern int DhcpRequestParams(
            DhcpRequestFlags Flags,
            IntPtr Reserved,
            string AdapterName,
            IntPtr ClassId,
            DHCPCAPI_PARAMS_ARRAY SendParams,
            DHCPCAPI_PARAMS_ARRAY RecdParams,
            IntPtr Buffer,
            ref UInt32 pSize,
            string RequestIdStr
        );

        [DllImport("dhcpcsvc.dll", EntryPoint = "DhcpUndoRequestParams", CharSet = CharSet.Unicode, SetLastError = false)]
        public static extern int DhcpUndoRequestParams(
            uint Flags,
            IntPtr Reserved,
            string AdapterName,
            string RequestIdStr
        );

        [DllImport("dhcpcsvc.dll", EntryPoint = "DhcpCApiInitialize", CharSet = CharSet.Unicode, SetLastError = false)]
        public static extern int DhcpCApiInitialize(out uint Version);

        [DllImport("dhcpcsvc.dll", EntryPoint = "DhcpCApiCleanup", CharSet = CharSet.Unicode, SetLastError = false)]
        public static extern int DhcpCApiCleanup();

        [Flags]
        public enum DhcpRequestFlags : uint
        {
            DHCPCAPI_REQUEST_PERSISTENT = 0x01,
            DHCPCAPI_REQUEST_SYNCHRONOUS = 0x02,
            DHCPCAPI_REQUEST_ASYNCHRONOUS = 0x04,
            DHCPCAPI_REQUEST_CANCEL = 0x08,
            DHCPCAPI_REQUEST_MASK = 0x0F
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct DHCPCAPI_PARAMS_ARRAY
        {
            public UInt32 nParams;
            public IntPtr Params;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct DHCPCAPI_PARAMS
        {
            public UInt32 Flags;
            public UInt32 OptionId;
            [MarshalAs(UnmanagedType.Bool)]
            public bool IsVendor;
            public IntPtr Data;
            public UInt32 nBytesData;
        }
    }
    #endregion
}
