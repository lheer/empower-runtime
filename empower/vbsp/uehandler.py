#!/usr/bin/env python3
#
# Copyright (c) 2016 Supreeth Herle
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

"""UEs Handerler."""

import tornado.web
import tornado.httpserver

from empower.datatypes.etheraddress import EtherAddress
from empower.restserver.apihandlers import EmpowerAPIHandlerAdminUsers
from empower.main import RUNTIME


class UEHandler(EmpowerAPIHandlerAdminUsers):
    """UE handler. Used to view UEs (controller-wide)."""

    HANDLERS = [r"/api/v1/ues/?",
                r"/api/v1/ues/([0-9:]*)/?"]

    def get(self, *args, **kwargs):
        """ Get all UEs or just the specified one.

        Args:
            imsi: the lvap address

        Example URLs:
            GET /api/v1/ues
            GET /api/v1/ues/123345
        """

        try:
            if len(args) > 1:
                raise ValueError("Invalid URL")
            if len(args) == 0:
                self.write_as_json(RUNTIME.ues.values())
            else:
                ue = int(args[0])
                self.write_as_json(RUNTIME.ues[ue])
        except KeyError as ex:
            self.send_error(404, message=ex)
        except ValueError as ex:
            self.send_error(400, message=ex)
        self.set_status(200, None)

    def put(self, *args, **kwargs):
        """ Set the cell for a given UE.

        Args:
            imsi: the ue IMSI

        Request:
            version: the protocol version (1.0)

        Example URLs:
            PUT /api/v1/ues/111
        """

        try:

            if len(args) != 1:
                raise ValueError("Invalid URL")

            request = tornado.escape.json_decode(self.request.body)

            if "version" not in request:
                raise ValueError("missing version element")

            if "vbs" not in request:
                raise ValueError("missing vbs element")

            if "pci" not in request:
                raise ValueError("missing pci element")

            imsi = int(args[0])
            ue = RUNTIME.ues[imsi]

            vbs_addr = EtherAddress(request['vbs'])
            pci = int(request['pci'])

            vbs = RUNTIME.vbses[vbs_addr]

            target = None
            for cell in vbs.cells:
                if cell.pci == pci:
                    target = cell

            if not target:
                raise KeyError("Cell %s/%u not found", vbs_addr, pci)

            ue.cell = target

        except KeyError as ex:
            self.send_error(404, message=ex)
        except ValueError as ex:
            self.send_error(400, message=ex)

        self.set_status(204, None)
