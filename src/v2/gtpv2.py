#!/usr/bin/env python
# An GTPv2 scapy implementation to provide LTE GTP-C traffic

__VERSION__ = 'v0.1'

from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import IP, UDP
from scapy.layers.sctp import SCTP
from scapy.layers.inet6 import IPv6
from ie import *



import logging
import time
import sys

logging.getLogger("scapy").setLevel(1)      # get warnings for now

# GTPv2 Data Types (see 3GPP TS 29.274 v12.13.0 section 5)


GTPv2MessageTypes = {
    0: "Reserved",
    1: "Echo Request",
    2: "Echo Response",
    3: "Version Not Supported Indication",
    # 4 to 16: "Reserved for S101 interface",
    # 17 to 24: "Reserved for S121 interface",
    # 25 to 31: "Reserved for Sv interface",
    32: "Create Session Request",
    33: "Create Session Response",
    36: "Delete Session Request",
    37: "Delete Session Response",
    34: "Modify Bearer Request",
    35: "Modify Bearer Response",
    38: "Change Notification Request",
    39: "Change Notification Response",
    # 40 to 63: "For future use",
    164: "Resume Notification",
    165: "Resume Acknowledge",
    64: "Modify Bearer Command",
    65: "Modify Bearer Failure Indication",
    66: "Delete Bearer Command",
    67: "Delete Bearer Failure Indication",
    68: "Bearer Resource Command",
    69: "Bearer Resource Failure Indication",
    70: "Downlink Data Notification Failure Indication",
    71: "Trace Session Activation",
    72: "Trace Session Deactivation",
    73: "Stop Paging Indication",
    # 74 to 94: "For future use",
    95: "Create Bearer Request",
    96: "Create Bearer Response",
    97: "Update Bearer Request",
    98: "Update Bearer Response",
    99: "Delete Bearer Request",
    100: "Delete Bearer Response",
    101: "Delete PDN Connection Set Request",
    102: "Delete PDN Connection Set Response",
    103: "PGW Downlink Triggering Notification",
    104: "PGW Downlink Triggering Acknowledge",
    # 105 to 127: "For future use",
    128: "Identification Request",
    129: "Identification Response",
    130: "Context Request",
    131: "Context Response",
    132: "Context Acknowledge",
    133: "Forward Relocation Request",
    134: "Forward Relocation Response",
    135: "Forward Relocation Complete Notification",
    136: "Forward Relocation Complete Acknowledge",
    137: "Forward Access Context Notification",
    138: "Forward Access Context Acknowledge",
    139: "Relocation Cancel Request",
    140: "Relocation Cancel Response",
    141: "Configuration Transfer Tunnel",
    # 142 to 148: "For future use",
    152: "RAN Information Relay",
    149: "Detach Notification",
    150: "Detach Acknowledge",
    151: "CS Paging Indication",
    153: "Alert MME Notification",
    154: "Alert MME Acknowledge",
    155: "UE Activity Notification",
    156: "UE Activity Acknowledge",
    157: "ISR Status Indication",
    # 158 to 159: "For future use",
    162: "Suspend Notification",
    163: "Suspend Acknowledge",
    160: "Create Forwarding Tunnel Request",
    161: "Create Forwarding Tunnel Response",
    166: "Create Indirect Data Forwarding Tunnel Request",
    167: "Create Indirect Data Forwarding Tunnel Response",
    168: "Delete Indirect Data Forwarding Tunnel Request",
    169: "Delete Indirect Data Forwarding Tunnel Response",
    170: "Release Access Bearers Request",
    171: "Release Access Bearers Response",
    # 172 to 175: "For future use",
    176: "Downlink Data Notification",
    177: "Downlink Data Notification Acknowledge",
    179: "PGW Restart Notification",
    180: "PGW Restart Notification Acknowledge",
    178: "Reserved. Allocated in earlier version of the specification.",
    # 181 to 199: "For future use",
    200: "Update PDN Connection Set Request",
    201: "Update PDN Connection Set Response",
    # 202 to 210: "For future use",
    211: "Modify Access Bearers Request",
    212: "Modify Access Bearers Response",
    # 213 to 230: "For future use",
    231: "MBMS Session Start Request",
    232: "MBMS Session Start Response",
    233: "MBMS Session Update Request",
    234: "MBMS Session Update Response",
    235: "MBMS Session Stop Request",
    236: "MBMS Session Stop Response",
    # 237 to 239: "For future use",
    # 240 to 247: "Reserved for Sv interface (see also types 25 to 31)",
    # 248 to 255: "For future use",
}


class GTPv2Header(Packet):
    name = "GTPv2 Header"

    fields_desc = [
        BitField("version", 2, 3),
        BitField("P", 0, 1),
        BitField("T", 1, 1),
        BitField("reserved", 0, 3),
        ByteEnumField("message_type", None, GTPv2MessageTypes),
        ShortField("length", None),
        ConditionalField(IntField("teid", 0), lambda pkt: pkt.T == 1),
        BitField("sequence", 0, 24),
        ByteField("spare", 0)
    ]

    def post_build(self, pkt, pay):

        pkt += pay
        if self.length is None:
            warning("Setting Length")
            l = len(pkt) - 4  # message len of gtpv2 is length of whole minus the mandatory parts of the header (first 4 octets)
            pkt = pkt[:2] + struct.pack("!H", l) + pkt[4:]
        return pkt


class EchoRequest(Packet):
    """
    A GTPv2 echo request -Message Type 1

    Note that T in the header is allowed to be 0 for this message
    """
    name = "GTPv2 Echo Request"

    fields_desc = [
        PacketListField("Information Elements", [IERecovery()], IE_Lookup)
    ]


class EchoResponse(Packet):
    """
    A GTPv2 echo response -Message Type 2

    Note that T in the header is allowed to be 0 for this message
    """
    name = "GTPv2 Echo Response"

    fields_desc = [
        PacketListField("information_elements", [IERecovery()], IE_Lookup)
    ]

bind_layers(UDP, GTPv2Header, {'dport': 2123, 'sport': 2123})

bind_layers(GTPv2Header, EchoRequest, {'message_type': 1})
bind_layers(GTPv2Header, EchoResponse, {'message_type': 2})


if __name__ == "__main__":

    from scapy.all import *
    interact(mydict=globals(), argv=sys.argv, mybanner="GTPv2 Add-on {}".format(__VERSION__))
