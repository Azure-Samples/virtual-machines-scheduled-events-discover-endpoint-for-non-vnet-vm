# Copyright 2014 Microsoft Corporation
#
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
# Requires Python 2.4+ and Openssl 1.0+


# Output of running the script on Windows:
# The cloud control endpoint IP address will be available as part of the system environment variable.
#
# Output of running the script on Linux:
# The cloud control endpoint IP address will be available as part of the environment variable for all users.

import argparse
import os
import socket
import struct
import array
import time
import util
import sys
import _winreg as wreg
from uuid import getnode as get_mac

"""
Defines dhcp exception
"""

class BaseError(Exception):
    """
    Base error class.
    """
    def __init__(self, errno, msg, inner=None):
        msg = u"({0}){1}".format(errno, msg)
        if inner is not None:
            msg = u"{0} \n  inner error: {1}".format(msg, inner)
        super(BaseError, self).__init__(msg)

class DhcpError(BaseError):
    """
    Failed to handle dhcp response
    """
    def __init__(self, msg=None, inner=None):
        super(DhcpError, self).__init__('000006', msg, inner)

class DhcpHandler(object):

    def __init__(self):
        self.osutil = util.DefaultOSUtil()
        self.endpoint = None
        self.gateway = None
        self.routes = None
        self._request_broadcast = False
        self.skip_cache = False

    def run(self, debug, donotaddtoenv, outputregistry):
        """
        Send dhcp request
        """

        self.send_dhcp_req(debug, donotaddtoenv, outputregistry)

    def _send_dhcp_req(self, request, debug):
        __waiting_duration__ = [0, 10, 30, 60, 60]
        for duration in __waiting_duration__:
            try:
                self.osutil.allow_dhcp_broadcast()
                response = socket_send(request, debug)
                validate_dhcp_resp(request, response, debug)
                return response
            except DhcpError as e:
                print("Failed to send DHCP request: {0}", e)
            time.sleep(duration)
        return None

    def send_dhcp_req(self, debug, donotaddtoenv, outputregistry):
        """
        Build dhcp request with mac addr
        Configure route to allow dhcp traffic
        Stop dhcp service if necessary
        """
        if debug == True:
            print("Sending dhcp request")
        mac_addr = self.osutil.get_mac_in_bytes()

        if debug == True:
            print('Mac address', mac_addr)

        req = build_dhcp_request(mac_addr, self._request_broadcast, debug)

        resp = self._send_dhcp_req(req, debug)

        if resp is None:
            raise DhcpError("Failed to receive dhcp response.")
        self.endpoint, self.gateway, self.routes = parse_dhcp_resp(resp, debug)
        print('Cloud Control endpoint IP address:', self.endpoint)

        env_var = "CLOUDCONTROLIP"
        env_val = self.endpoint
        if donotaddtoenv == False:
            print('Adding Cloud Control endpoint IP to the environment')
            if sys.platform == 'win32':
                os.system("SETX {0} {1} /M".format(env_var,env_val))
                
            elif "linux" in sys.platform:
                # Set the cloud control IP address in the environment for the current process
                os.environ['CLOUDCONTROLIP']=self.endpoint

                # Set the cloud control IP address in the environment for all users
                # This is done by reading the file /etc/profile line by line
                # Looking for a match to "export CLOUDCONTROLIP="
                # Writing the same file again excluding that line and appending that line again
                # With the correct value of the IP address
                f = open("/etc/profile", 'r')
                match = "export CLOUDCONTROLIP="
                lines = f.readlines()
                f.close()

                f = open("/etc/profile", 'w')
                for line in lines:
                    if match not in line:
                        f.write(line)
                f.write("export {0}={1}\n".format(env_var, env_val))
                f.close()
            else:
                print('Unknown operating system detected. Cannot add the cloud control IP to the environment')
        if outputregistry == True and sys.platform == 'win32':
            print('Adding Cloud Control endpoint to registry location HKEY_LOCAL_MACHINE\\Software\\CloudControl')
            key = wreg.CreateKey(wreg.HKEY_LOCAL_MACHINE, "Software\\CloudControl")
            # Create new value
            wreg.SetValueEx(key, 'CloudControlIp', 0, wreg.REG_SZ, self.endpoint)
            print(wreg.QueryValueEx(key,'CloudControlIp'))
            key.Close()	

def validate_dhcp_resp(request, response, debug):
    bytes_recv = len(response)
    if bytes_recv < 0xF6:
        print("HandleDhcpResponse: Too few bytes received:{0}",
                     bytes_recv)
        return False

    if debug == True:
        print("BytesReceived:{0}", hex(bytes_recv))
        print("DHCP response:{0}", util.hex_dump(response, bytes_recv))

    # check transactionId, cookie, MAC address cookie should never mismatch
    # transactionId and MAC address may mismatch if we see a response
    # meant from another machine
    if not util.compare_bytes(request, response, 0xEC, 4):
        print("Cookie not match:\nsend={0},\nreceive={1}",
                       util.hex_dump3(request, 0xEC, 4),
                       util.hex_dump3(response, 0xEC, 4))
        raise DhcpError("Cookie in dhcp respones doesn't match the request")

    if not util.compare_bytes(request, response, 4, 4):
        print("TransactionID not match:\nsend={0},\nreceive={1}",
                       util.hex_dump3(request, 4, 4),
                       util.hex_dump3(response, 4, 4))
        raise DhcpError("TransactionID in dhcp respones "
                        "doesn't match the request")

    if not util.compare_bytes(request, response, 0x1C, 6):
        print("Mac Address not match:\nsend={0},\nreceive={1}",
                       util.hex_dump3(request, 0x1C, 6),
                       util.hex_dump3(response, 0x1C, 6))
        raise DhcpError("Mac Addr in dhcp respones "
                        "doesn't match the request")


def parse_route(response, option, i, length, bytes_recv):
    # http://msdn.microsoft.com/en-us/library/cc227282%28PROT.10%29.aspx
    print("Routes at offset: {0} with length:{1}", hex(i),
                   hex(length))
    routes = []
    if length < 5:
        print("Data too small for option:{0}", option)
    j = i + 2
    while j < (i + length + 2):
        mask_len_bits = util.str_to_ord(response[j])
        mask_len_bytes = (((mask_len_bits + 7) & ~7) >> 3)
        mask = 0xFFFFFFFF & (0xFFFFFFFF << (32 - mask_len_bits))
        j += 1
        net = util.unpack_big_endian(response, j, mask_len_bytes)
        net <<= (32 - mask_len_bytes * 8)
        net &= mask
        j += mask_len_bytes
        gateway = util.unpack_big_endian(response, j, 4)
        j += 4
        routes.append((net, mask, gateway))
    if j != (i + length + 2):
        print("Unable to parse routes")
    return routes


def parse_ip_addr(response, option, i, length, bytes_recv):
    if i + 5 < bytes_recv:
        if length != 4:
            print("Endpoint or Default Gateway not 4 bytes")
            return None
        addr = util.unpack_big_endian(response, i + 2, 4)
        ip_addr = util.int_to_ip4_addr(addr)
        return ip_addr
    else:
        print("Data too small for option:{0}", option)
    return None


def parse_dhcp_resp(response, debug):
    """
    Parse DHCP response:
    Returns endpoint server or None on error.
    """
    if debug == True:
        print('Parsing Dhcp response')
    bytes_recv = len(response)
    endpoint = None
    gateway = None
    routes = None

    # Walk all the returned options, parsing out what we need, ignoring the
    # others. We need the custom option 245 to find the the endpoint we talk to
    # options 3 for default gateway and 249 for routes; 255 is end.

    i = 0xF0  # offset to first option
    while i < bytes_recv:
        option = util.str_to_ord(response[i])
        length = 0
        if (i + 1) < bytes_recv:
            length = util.str_to_ord(response[i + 1])
            if debug == True:
                print("DHCP option {0} at offset:{1} with length:{2}", hex(option), hex(i), hex(length))
        if option == 255:
            if debug == True:
                print("DHCP packet ended at offset:{0}", hex(i))
            break
        elif option == 249:
            routes = parse_route(response, option, i, length, bytes_recv)
        elif option == 3:
            gateway = parse_ip_addr(response, option, i, length, bytes_recv)
            if debug == True:
                print("Default gateway:{0}, at {1}", gateway, hex(i))
        elif option == 245:
            endpoint = parse_ip_addr(response, option, i, length, bytes_recv)
            if debug == True:
                print("Azure cloud control endpoint IP:{0}, at {1}", endpoint, hex(i))
        else:
            if debug == True:
                print("Skipping DHCP option:{0} at {1} with length {2}", hex(option), hex(i), hex(length))
        i += length + 2
    return endpoint, gateway, routes


def socket_send(request, debug):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 68))
        sock.sendto(request, ("<broadcast>", 67))
        sock.settimeout(10)
        if debug == True:
            print("Send DHCP request: Setting socket.timeout=10, "
                  "entering recv")
        response = sock.recv(1024)
        return response
    except IOError as e:
        raise DhcpError("{0}".format(e))
    finally:
        if sock is not None:
            sock.close()


def build_dhcp_request(mac_addr, request_broadcast, debug):
    """
    Build DHCP request string.
    """
    #
    # typedef struct _DHCP {
    #  UINT8   Opcode;                    /* op:    BOOTREQUEST or BOOTREPLY */
    #  UINT8   HardwareAddressType;       /* htype: ethernet */
    #  UINT8   HardwareAddressLength;     /* hlen:  6 (48 bit mac address) */
    #  UINT8   Hops;                      /* hops:  0 */
    #  UINT8   TransactionID[4];          /* xid:   random */
    #  UINT8   Seconds[2];                /* secs:  0 */
    #  UINT8   Flags[2];                  /* flags: 0 or 0x8000 for broadcast*/
    #  UINT8   ClientIpAddress[4];        /* ciaddr: 0 */
    #  UINT8   YourIpAddress[4];          /* yiaddr: 0 */
    #  UINT8   ServerIpAddress[4];        /* siaddr: 0 */
    #  UINT8   RelayAgentIpAddress[4];    /* giaddr: 0 */
    #  UINT8   ClientHardwareAddress[16]; /* chaddr: 6 byte eth MAC address */
    #  UINT8   ServerName[64];            /* sname:  0 */
    #  UINT8   BootFileName[128];         /* file:   0  */
    #  UINT8   MagicCookie[4];            /*   99  130   83   99 */
    #                                        /* 0x63 0x82 0x53 0x63 */
    #     /* options -- hard code ours */
    #
    #     UINT8 MessageTypeCode;              /* 53 */
    #     UINT8 MessageTypeLength;            /* 1 */
    #     UINT8 MessageType;                  /* 1 for DISCOVER */
    #     UINT8 End;                          /* 255 */
    # } DHCP;
    #

    # tuple of 244 zeros
    # (struct.pack_into would be good here, but requires Python 2.5)
    request = [0] * 244

    trans_id = gen_trans_id()

    # Opcode = 1
    # HardwareAddressType = 1 (ethernet/MAC)
    # HardwareAddressLength = 6 (ethernet/MAC/48 bits)
    for a in range(0, 3):
        request[a] = [1, 1, 6][a]

    # fill in transaction id (random number to ensure response matches request)
    for a in range(0, 4):
        request[4 + a] = util.str_to_ord(trans_id[a])

    if debug == True:
        print("BuildDhcpRequest: transactionId:%s,%04X" % (
            util.hex_dump2(trans_id),
            util.unpack_big_endian(request, 4, 4)))

    if request_broadcast:
        # set broadcast flag to true to request the dhcp sever
        # to respond to a boradcast address,
        # this is useful when user dhclient fails.
        request[0x0A] = 0x80;

    # fill in ClientHardwareAddress
    for a in range(0, 6):
        request[0x1C + a] = util.str_to_ord(mac_addr[a])

    # DHCP Magic Cookie: 99, 130, 83, 99
    # MessageTypeCode = 53 DHCP Message Type
    # MessageTypeLength = 1
    # MessageType = DHCPDISCOVER
    # End = 255 DHCP_END
    for a in range(0, 8):
        request[0xEC + a] = [99, 130, 83, 99, 53, 1, 1, 255][a]
    return array.array("B", request)

def gen_trans_id():
    return os.urandom(4)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable running the script in debug mode')
parser.add_argument('--donotaddtoenv', action='store_true', help='Do not add the cloud control endpoint to environment variable')
parser.add_argument('--outputregistry', action='store_true', help='Option to store CloudControl IP address as registry value')
args = parser.parse_args()
dhcp = DhcpHandler()
dhcp.run(args.debug, args.donotaddtoenv, args.outputregistry)
