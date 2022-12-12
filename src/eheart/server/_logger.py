# Copyright 2022 SHIMAYOSHI, Takao.
#
# This file is part of e-Heart Python Framework.
#
# e-Heart Python Framework is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 3.
#
# e-Heart Python Framework is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import logging

logger = logging.getLogger(__package__)

class ServerLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if 'websocket' in self.extra:
            websocket = self.extra['websocket']
            return f"{websocket.id} {websocket.remote_address} {msg}", kwargs
        else:
            return msg, kwargs
