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
from importlib import import_module

import numpy as np

from .. import Engine
from . import eheart_pb2 as ehpb
from ._logger import logger, ServerLoggerAdapter


class Session:
    """Session class for e-Heart Protocol Buffers interface."""

    def __init__(self):
        self.COMMAND_FUNCS = {
            ehpb.Command.INIT: self._init,
            ehpb.Command.SET_DIFFVAR_VAL: self._set_diffvar_val,
            ehpb.Command.GET_DIFFVAR_NAME: self._get_diffvar_name,
            ehpb.Command.GET_CURRENT_VAL: self._get_current_val,
            ehpb.Command.SET_WATCHING_VAR: self._set_watching_var,
            ehpb.Command.SOLVE_IVP: self._solve_ivp,
            ehpb.Command.CHANGE_TIME: self._change_time,
            ehpb.Command.SET_MODEL_CONST: self._set_model_const,
            ehpb.Command.EVAL_MODEL_VAR: self._eval_model_var,
            ehpb.Command.CALL_MODEL_METHOD: self._call_model_method,
        }
        self.watching = []
        self.logger = logger

    @classmethod
    async def main(cls, websocket):
        """
        Session main loop, receiving commands and \
        sending responses via WebSocket.

        Parameters
        ----------
        websocket : websockets.server.WebSocketServerProtocol
            WebSocket server connection.
        """
        session = cls()
        session.websocket = websocket
        session.logger = ServerLoggerAdapter(logger, {'websocket': websocket})
        async for message in websocket:
            await websocket.send(session.process(message))

    def process(self, message):
        """
        Process a command message.

        Parameters
        ----------
        message : str
            Command message in Protocol Buffers.

        Returns
        -------
        str
            Response message in Protocol Buffers.
        """
        request = ehpb.Request()
        request.ParseFromString(message)
        response = self.COMMAND_FUNCS[request.command](request.parameter)
        return response.SerializeToString()

    def _init(self, req_param):
        parameter = ehpb.InitParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive INIT command')
        self.logger.debug(f"Parameter: {parameter}")
        response = ehpb.StatusResponse()
        try:
            model_package, model_class = parameter.model.rsplit('.', 1)
            package = import_module(model_package)
            self.model = getattr(package, model_class)()
            self.engine = Engine(self.model, parameter.t, **parameter.options)
            self.restart_needed = False
        except Exception as err:
            self.logger.error(f"Error in INIT: {err}")
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Engine initialized')
            response.success = True
        return response

    def _set_diffvar_val(self, req_param):
        parameter = ehpb.SetDiffvarValParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive SET_DIFFVAR_VAL command')
        self.logger.debug(f"Parameter: {parameter}")
        response = ehpb.StatusResponse()
        try:
            self.restart_needed = True
            self.engine.set_diffvar_values(parameter.valmap)
        except Exception as err:
            self.logger.error(f"Error in SET_DIFFVAR_VAL: {err}")
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Diffvar values set')
            response.success = True
        return response

    def _get_diffvar_name(self, _):
        self.logger.info('Receive GET_DIFFVAR_NAME command')
        response = ehpb.DiffvarNameResponse()
        response.names[:] = self.model.diffvars
        return response

    def _get_current_val(self, _):
        self.logger.info('Receive GET_CURRENT_VAL command')
        response = ehpb.CurrentValResponse()
        response.t = self.engine.t
        response.y[:] = self.engine.y.tolist()
        return response

    def _set_watching_var(self, req_param):
        parameter = ehpb.SetWatchingVarParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive SET_WATCHING_VAR command')
        self.logger.debug(f"Parameter: {parameter}")
        self.watching = parameter.vars
        self.logger.info('Watching variables set')
        response = ehpb.StatusResponse()
        response.success = True
        return response

    def _solve_ivp(self, req_param):
        parameter = ehpb.SolveIVPParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive SOLVE_IVP command')
        self.logger.debug(f"Parameter: {parameter}")
        try:
            if self.restart_needed:
                self.engine.restart()
                self.restart_needed = False
            tprev = self.engine.t
            tstep = parameter.output_interval
            sol = self.engine.solve_ivp(parameter.tn)
            tout = np.arange(tprev, parameter.tn + tstep, tstep)
            y = sol(tout)
            if self.watching:
                watching = self.engine.eval(
                    lambda model:
                        np.array([getattr(model, v) for v in self.watching]),
                    tout, y
                )
        except Exception as err:
            self.logger.error(f"Error in SOLVE_IVP: {err}")
            response = ehpb.StatusResponse()
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('IVP solved')
            response = ehpb.SolutionResponse()
            response.t.values[:] = tout.tolist()
            for i in range(len(self.engine.y)):
                response.diffvars.add().values[:] = y[i].tolist()
            for i, _ in enumerate(self.watching):
                response.watching_vars.add().values[:] = watching[i].tolist()
        return response

    def _change_time(self, req_param):
        parameter = ehpb.ChangeTimeParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive CHANGE_TIME command')
        self.logger.debug(f"Parameter: {parameter}")
        response = ehpb.StatusResponse()
        try:
            self.engine.restart(parameter.t, **parameter.options)
            self.restart_needed = False
        except Exception as err:
            self.logger.error(f"Error in CHANGE_TIME: {err}")
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Time changed')
            response.success = True
        return response

    def _set_model_const(self, req_param):
        parameter = ehpb.SetModelConstParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive SET_MODEL_CONST command')
        self.logger.debug(f"Parameter: {parameter}")
        response = ehpb.StatusResponse()
        try:
            for name, value in parameter.valmap.items():
                setattr(self.model, name, value)
        except Exception as err:
            self.logger.error(f"Error in SET_MODEL_CONST: {err}")
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Constant values set')
            response.success = True
        return response

    def _eval_model_var(self, req_param):
        parameter = ehpb.EvalModelVarParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive EVAL_MODEL_VAR command')
        self.logger.debug(f"Parameter: {parameter}")
        try:
            values = self.engine.eval(
                lambda model:
                    [getattr(model, var).item() for var in parameter.vars],
                parameter.t, parameter.y
            )
        except Exception as err:
            self.logger.error(f"Error in EVAL_MODEL_VAR: {err}")
            response = ehpb.StatusResponse()
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Model variables evaluated')
            response = ehpb.ValueArrayResponse()
            response.values[:] = values
        return response

    def _call_model_method(self, req_param):
        parameter = ehpb.CallModelMethodParam()
        req_param.Unpack(parameter)
        self.logger.info('Receive CALL_MODEL_METHOD command')
        self.logger.debug(f"Parameter: {parameter}")
        args = {
            k: self._get_scalar_or_array_value(v)
            for k, v in parameter.args.items()
        }
        try:
            rv = getattr(self.model, parameter.method_name)(**args)
            if isinstance(rv, tuple):
                return_value = [
                    self._build_scalar_or_array_value(v) for v in rv
                ]
            else:
                return_value = [
                    self._build_scalar_or_array_value(rv)
                ]
        except Exception as err:
            self.logger.error(f"Error in CALL_MODEL_METHOD: {err}")
            response = ehpb.StatusResponse()
            response.success = False
            response.message = str(err)
        else:
            self.logger.info('Model method called')
            response = ehpb.MethodReturnResponse()
            response.return_value.extend(return_value)
        return response

    @classmethod
    def _get_scalar_or_array_value(cls, msg):
        values = [getattr(v, v.WhichOneof("value")) for v in msg.value]
        if msg.isscalar:
            return values[0]
        else:
            return values

    @classmethod
    def _build_scalar_or_array_value(cls, value):
        obj = ehpb.GenericScalarOrArray()
        if np.isscalar(value):
            obj.isscalar = True
            obj.value.append(cls._build_generic_value(value))
        else:
            obj.isscalar = False
            obj.value.extend([cls._build_generic_value(v) for v in value])
        return obj

    @classmethod
    def _build_generic_value(cls, value):
        obj = ehpb.GenericValue()
        if isinstance(value, (float, np.double)):
            obj.real = value
        elif isinstance(value, (int, np.int)):
            obj.integer = value
        elif isinstance(value, str):
            obj.string = value
        else:
            raise TypeError(f"Illegal type: {type(value)}")
        return obj
