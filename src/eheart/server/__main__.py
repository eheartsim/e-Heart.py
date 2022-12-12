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
import argparse

import pyximport

from ._run import run

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str,
                    help='bind hostname or address')
parser.add_argument('-p', '--port', type=int,
                    help='port number')

pyximport.install(pyimport=True)

run(**{k: v for k, v in vars(parser.parse_args()).items() if v is not None})
