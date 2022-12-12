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
import asyncio
import signal

import websockets

from ._session import Session


async def _server(host, port):
    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    try:
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, stop.set_result, None)
    except NotImplementedError:
        pass

    async with websockets.serve(Session.main, host, port):
        await stop

def run(host='localhost', port=5810):
    """
    Run e-Heart WebSocket server.

    Parameters
    ----------
    host : string, optional
        The bind hostname (the default is localhost).
    port : int, optional
        The listen port (the default is 5810).
    """
    asyncio.run(_server(host, port))
