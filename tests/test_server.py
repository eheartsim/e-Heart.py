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
import unittest
import math

from eheart import Model, diffvar
from eheart.server import eheart_pb2 as ehpb
from eheart.server._session import Session


class SingleExpModel(Model):
    def initialize_vars(self):
        self.tau = 1
        self.y = diffvar()

    def calc_ode(self, t):
        self.t = t
        self.ydot = -self.tau * self.y
        self.y.der = self.ydot

    def single_valued_method(self, ary, idx, factor):
        return factor * ary[idx]

    def single_array_method(self, ary, factor):
        return [v * factor for v in ary]

    def tuple_method(self, prefix, strary):
        return [f"{prefix}{str}" for str in strary], len(strary)


class TestServer(unittest.TestCase):
    def test_init(self):
        session = Session()
        request = ehpb.Request()
        request.command = ehpb.Command.INIT
        parameter = ehpb.InitParam()
        parameter.model = 'test_server.SingleExpModel'
        parameter.t = 1.2
        parameter.options['init_step'] = 0.1
        parameter.options['min_step'] = 0.001
        parameter.options['max_step'] = 1.0
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertTrue(response.success)

    def test_init_fail(self):
        session = Session()
        request = ehpb.Request()
        request.command = ehpb.Command.INIT
        parameter = ehpb.InitParam()
        parameter.model = 'model.nonexistent.Model'
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertFalse(response.success)
        self.assertIsNotNone(response.message)

    def test_set_diff_val(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        request = ehpb.Request()
        request.command = ehpb.Command.SET_DIFFVAR_VAL
        parameter = ehpb.SetDiffvarValParam()
        parameter.valmap['y'] = 10.0
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertTrue(response.success)

    def test_get_diffvar_name(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        request = ehpb.Request()
        request.command = ehpb.Command.GET_DIFFVAR_NAME
        resmsg = session.process(request.SerializeToString())
        response = ehpb.DiffvarNameResponse()
        response.ParseFromString(resmsg)
        self.assertEqual(response.names, ['y'])

    def test_get_diffvar_val(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        self.assertTrue(self.set_diff_val(session))
        request = ehpb.Request()
        request.command = ehpb.Command.GET_CURRENT_VAL
        resmsg = session.process(request.SerializeToString())
        response = ehpb.CurrentValResponse()
        response.ParseFromString(resmsg)
        self.assertEqual(response.t, 0)
        self.assertEqual(response.y, [10.0])

    def test_set_watching_var(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        self.assertTrue(self.set_diff_val(session))
        request = ehpb.Request()
        request.command = ehpb.Command.SET_WATCHING_VAR
        parameter = ehpb.SetWatchingVarParam()
        parameter.vars[:] = ['ydot']
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertTrue(response.success)

    def test_solve_ivp(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        self.assertTrue(self.set_diff_val(session))
        # Without watching var
        request = ehpb.Request()
        request.command = ehpb.Command.SOLVE_IVP
        parameter = ehpb.SolveIVPParam()
        parameter.tn = 1.0
        parameter.output_interval = 0.1
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.SolutionResponse()
        response.ParseFromString(resmsg)
        for i in range(len(response.t.values)):
            t = i * 0.1
            self.assertAlmostEqual(response.t.values[i], t)
            yexp = 10.0 * math.exp(-t)
            self.assertAlmostEqual(
                response.diffvars[0].values[i], yexp, delta=yexp*1e-5)
        # With a watching var
        self.assertTrue(self.set_watching_var(session))
        request = ehpb.Request()
        request.command = ehpb.Command.SOLVE_IVP
        parameter = ehpb.SolveIVPParam()
        parameter.tn = 2.0
        parameter.output_interval = 0.1
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.SolutionResponse()
        response.ParseFromString(resmsg)
        for i in range(len(response.t.values)):
            t = 1.0 + i * 0.1
            self.assertAlmostEqual(response.t.values[i], t)
            yexp = 10.0 * math.exp(-t)
            self.assertAlmostEqual(
                response.diffvars[0].values[i], yexp, delta=yexp*1e-5)
            self.assertAlmostEqual(
                response.watching_vars[0].values[i], -yexp, delta=yexp*1e-5)

    def test_change_time(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        request = ehpb.Request()
        request.command = ehpb.Command.CHANGE_TIME
        parameter = ehpb.ChangeTimeParam()
        parameter.t = 1.0
        parameter.options['init_step'] = 0.1
        parameter.options['min_step'] = 0.001
        parameter.options['max_step'] = 1.0
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertTrue(response.success)

    def test_set_model_const(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        self.assertTrue(self.set_diff_val(session))
        self.assertTrue(self.set_watching_var(session))
        request = ehpb.Request()
        request.command = ehpb.Command.SET_MODEL_CONST
        parameter = ehpb.SetModelConstParam()
        parameter.valmap['tau'] = 2
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        self.assertTrue(response.success)
        request = ehpb.Request()
        request.command = ehpb.Command.SOLVE_IVP
        parameter = ehpb.SolveIVPParam()
        parameter.tn = 1.0
        parameter.output_interval = 0.1
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.SolutionResponse()
        response.ParseFromString(resmsg)
        for i in range(len(response.t.values)):
            t = i * 0.1
            self.assertEqual(response.t.values[i], t)
            yexp = 10.0 * math.exp(-2 * t)
            self.assertAlmostEqual(
                response.diffvars[0].values[i], yexp, delta=yexp*1e-5)
            self.assertAlmostEqual(
                response.watching_vars[0].values[i],
                -2 * yexp, delta=yexp*1e-5)

    def test_eval_model_var(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        request = ehpb.Request()
        request.command = ehpb.Command.EVAL_MODEL_VAR
        parameter = ehpb.EvalModelVarParam()
        parameter.vars[:] = ['ydot']
        parameter.t = 1.0
        parameter.y[:] = [5]
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.ValueArrayResponse()
        response.ParseFromString(resmsg)
        self.assertEqual(response.values[0], -5)

    def test_call_model_method(self):
        session = Session()
        self.assertTrue(self.init_engine(session))
        request = ehpb.Request()
        request.command = ehpb.Command.CALL_MODEL_METHOD
        ary = [0.5, 1.0, 1.5, 2.0, 2.5]
        # calling single_valued_method
        parameter = ehpb.CallModelMethodParam()
        parameter.method_name = 'single_valued_method'
        parameter.args['ary'].isscalar = False
        for v in ary:
            parameter.args['ary'].value.add().real = v
        parameter.args['idx'].isscalar = True
        parameter.args['idx'].value.add().integer = 2
        parameter.args['factor'].isscalar = True
        parameter.args['factor'].value.add().real = 0.5
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.MethodReturnResponse()
        response.ParseFromString(resmsg)
        rv = response.return_value[0]
        self.assertTrue(rv.isscalar)
        self.assertEqual(rv.value[0].real, 0.75)
        # calling single_array_method
        parameter = ehpb.CallModelMethodParam()
        parameter.method_name = 'single_array_method'
        parameter.args['ary'].isscalar = False
        for v in ary:
            parameter.args['ary'].value.add().real = v
        parameter.args['factor'].isscalar = True
        parameter.args['factor'].value.add().real = 0.5
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.MethodReturnResponse()
        response.ParseFromString(resmsg)
        rv = response.return_value[0]
        self.assertFalse(rv.isscalar)
        for i in range(len(ary)):
            self.assertEqual(rv.value[i].real, ary[i] * 0.5)
        # calling tuple_method
        parameter = ehpb.CallModelMethodParam()
        parameter.method_name = 'tuple_method'
        parameter.args['prefix'].isscalar = True
        parameter.args['prefix'].value.add().string = 'prefix'
        parameter.args['strary'].isscalar = False
        strary = ['one', 'two', 'three']
        for v in strary:
            parameter.args['strary'].value.add().string = v
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.MethodReturnResponse()
        response.ParseFromString(resmsg)
        rstrary = response.return_value[0]
        self.assertFalse(rstrary.isscalar)
        for i in range(len(strary)):
            self.assertEqual(rstrary.value[i].string, f"prefix{strary[i]}")
        self.assertTrue(response.return_value[1].isscalar)
        self.assertEqual(response.return_value[1].value[0].integer, 3)

    def init_engine(self, session):
        request = ehpb.Request()
        request.command = ehpb.Command.INIT
        parameter = ehpb.InitParam()
        parameter.model = 'test_server.SingleExpModel'
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        return response.success

    def set_diff_val(self, session):
        request = ehpb.Request()
        request.command = ehpb.Command.SET_DIFFVAR_VAL
        parameter = ehpb.SetDiffvarValParam()
        parameter.valmap['y'] = 10.0
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        return response.success

    def set_watching_var(self, session):
        request = ehpb.Request()
        request.command = ehpb.Command.SET_WATCHING_VAR
        parameter = ehpb.SetWatchingVarParam()
        parameter.vars[:] = ['ydot']
        request.parameter.Pack(parameter)
        resmsg = session.process(request.SerializeToString())
        response = ehpb.StatusResponse()
        response.ParseFromString(resmsg)
        return response.success


if __name__ == '__main__':
    unittest.main()
