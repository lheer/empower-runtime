#!/usr/bin/env python3
#
# Copyright (c) 2016 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""Virtual port."""


from empower.datatypes.etheraddress import EtherAddress
from empower.intentserver.intentserver import IntentServer

from empower.main import RUNTIME


def ofmatch_d2s(key):
    """Convert an OFMatch from dictionary to string."""

    match = ";".join(["%s=%s" % x for x in sorted(key.items())])
    return match


def ofmatch_s2d(match):
    """Convert an OFMatch from string to dictionary."""

    key = {}

    for token in match.split(";"):
        key_t, value_t = token.split("=")
        key[key_t] = value_t

    return key


class VirtualPort(object):
    """Virtual port."""

    def __init__(self, dpid, ovs_port_id, virtual_port_id, hwaddr, iface):

        self.dpid = dpid
        self.ovs_port_id = ovs_port_id
        self.virtual_port_id = virtual_port_id
        self.hwaddr = hwaddr
        self.iface = iface

    def to_dict(self):
        """ Return a JSON-serializable dictionary representing the Port """

        return {'dpid': self.dpid,
                'ovs_port_id': self.ovs_port_id,
                'virtual_port_id': self.virtual_port_id,
                'hwaddr': self.hwaddr,
                'iface': self.iface}

    def __hash__(self):

        return hash(self.dpid) + hash(self.ovs_port_id) + \
            hash(self.virtual_port_id)

    def __eq__(self, other):

        return (other.dpid == self.dpid and
                other.ovs_port_id == self.ovs_port_id and
                other.virtual_port_id == self.virtual_port_id)

    def __repr__(self):

        out_string = "%s ovs_port %s virtual_port %s hwaddr %s iface %s"

        out = out_string % (self.dpid, self.ovs_port_id, self.virtual_port_id,
                            self.hwaddr, self.iface)

        return out


class VirtualPortLvap(VirtualPort):
    """ Virtual port associated to an LVAP."""

    def __init__(self, dpid, ovs_port_id, virtual_port_id, hwaddr, iface):

        self.dpid = dpid
        self.ovs_port_id = ovs_port_id
        self.virtual_port_id = virtual_port_id
        self.hwaddr = hwaddr
        self.iface = iface
        self.next = VirtualPortPropLvap()


class VirtualPortLvnf(VirtualPort):
    """ Virtual port associated to an LVAP."""

    def __init__(self, dpid, ovs_port_id, virtual_port_id, hwaddr, iface):

        self.dpid = dpid
        self.ovs_port_id = ovs_port_id
        self.virtual_port_id = virtual_port_id
        self.hwaddr = hwaddr
        self.iface = iface
        self.next = VirtualPortPropLvnf()


class VirtualPortProp(dict):
    """Maps Flows to VirtualPorts.

    Flows are dictionary keys in the following format:
        dl_src=11:22:33:44:55:66,tp_dst=80
    """

    def __init__(self):
        super(VirtualPortProp, self).__init__()
        self.__uuids__ = {}

    def __delitem__(self, key):
        """Clear virtual port configuration.

        Remove entry from dictionary and remove flows.
        """

        intent_server = RUNTIME.components[IntentServer.__module__]

        # remove virtual links
        if key in self.__uuids__:
            for uuid in self.__uuids__[key]:
                intent_server.remove_intent(uuid)
            del self.__uuids__[key]

        # remove old entry
        dict.__delitem__(self, key)


class VirtualPortPropLvap(VirtualPortProp):
    """VirtualPortProp class for LVAPs."""

    def __init__(self):
        super(VirtualPortPropLvap, self).__init__()
        self.lvap = None

    def __setitem__(self, key, value):
        """Set virtual port configuration."""

        if value and not isinstance(value, VirtualPort):
            raise KeyError("Expected VirtualPort, got %s" % type(key))

        # if encap is set, then all outgoing traffic must go to THE SAME
        # LVNF. This is because the outgoing traffic will be LWAPP
        # encapsulated and as such cannot be handled anyway by OF
        # switches. Ignore totally the specified key and silently use as
        # key the LWAPP src and dst addresses. Notice that this will send
        # as many intents as the number of blocks.
        if self.lvap.encap != EtherAddress("00:00:00:00:00:00"):

            key = {'dl_src': self.lvap.addr, 'dl_dst': self.lvap.encap}

            # remove virtual link
            if self.__contains__(ofmatch_d2s(key)):
                self.__delitem__(ofmatch_d2s(key))

            self.__uuids__[ofmatch_d2s(key)] = []

            intent_server = RUNTIME.components[IntentServer.__module__]

            # Set downlink and uplink virtual link(s)
            dl_blocks = list(self.lvap.downlink.values())
            ul_blocks = list(self.lvap.uplink.values())
            blocks = dl_blocks + ul_blocks

            # r_port is a RadioPort object
            for r_port in blocks:

                n_port = r_port.block.radio.port()

                # set/update intent
                intent = {'version': '1.0',
                          'ttp_dpid': value.dpid,
                          'ttp_port': value.ovs_port_id,
                          'stp_dpid': n_port.dpid,
                          'stp_port': n_port.port_id,
                          'match': key}

                # add new virtual link
                uuid = intent_server.send_intent(intent)
                self.__uuids__[ofmatch_d2s(key)].append(uuid)

                # add entry
                dict.__setitem__(self, ofmatch_d2s(key), value)


class VirtualPortPropLvnf(VirtualPortProp):
    """VirtualPortProp class for LVAPs."""

    def __init__(self):
        super().__init__()
        self.lvnf = None
