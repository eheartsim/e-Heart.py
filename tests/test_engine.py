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

import numpy as np

from eheart import diffvar, Model, Engine


class TestEngine(unittest.TestCase):
    class SingleExpModel(Model):
        def initialize_vars(self):
            self.tau = 1
            self.y = diffvar()

        def calc_ode(self, t):
            self.t = t
            self.y.der = -self.tau * self.y

    def test_instance(self):
        model = self.SingleExpModel()
        # Default initialization
        engine = Engine(model)
        self.assertEqual(engine.model, model)
        self.assertEqual(engine.t, 0)
        self.assertEqual(engine.y, [0])
        # Fully specified initialization
        engine = Engine(
            model, 1.0, init_step=0.1, min_step=1.0E-10, max_step=1.0
        )
        self.assertEqual(engine.model, model)
        self.assertEqual(engine.t, 1.0)
        self.assertEqual(engine.y, [0])

    def test_set_diffvar_values(self):
        engine = Engine(self.SingleExpModel())
        engine.set_diffvar_values(dict(y=10.0))
        self.assertEqual(engine.y, [10.0])

    def test_solve_ivp(self):
        engine = Engine(self.SingleExpModel())
        engine.set_diffvar_values(dict(y=10.0))
        # Solve until 1
        sol = engine.solve_ivp(1)
        self.assertEqual(engine.t, 1)
        yexp1 = 10.0 * np.exp(-1)
        self.assertAlmostEqual(engine.y[0], yexp1, delta=yexp1*1e-5)
        yexp0_5 = 10.0 * np.exp(-0.5)
        self.assertAlmostEqual(sol(0.5), yexp0_5, delta=yexp0_5*1e-5)
        # Solve until 2
        sol = engine.solve_ivp(2)
        self.assertEqual(engine.t, 2)
        yexp2 = 10.0 * np.exp(-2)
        self.assertAlmostEqual(engine.y[0], yexp2, delta=yexp2*1e-5)
        yexp1_5 = 10.0 * np.exp(-1.5)
        self.assertAlmostEqual(sol(1.5), yexp1_5, delta=yexp1_5*1e-5)

    def test_restart(self):
        engine = Engine(self.SingleExpModel())
        engine.set_diffvar_values(dict(y=10.0))
        sol = engine.solve_ivp(1)
        # Restart
        engine.restart()
        self.assertEqual(engine.t, 1)
        self.assertEqual(engine.y, sol(1))
        sol = engine.solve_ivp(2)
        yexp2 = 10.0 * np.exp(-2)
        self.assertAlmostEqual(engine.y[0], yexp2, delta=yexp2*1e-5)
        # Restart after altering the differential variable
        engine.set_diffvar_values(dict(y=5.0))
        engine.restart()
        self.assertEqual(engine.t, 2)
        self.assertEqual(engine.y, [5.0])
        sol = engine.solve_ivp(3)
        yexp3 = 5.0 * np.exp(-1)
        self.assertAlmostEqual(engine.y[0], yexp3, delta=yexp3*1e-5)
        # Restart with fully specified arguments
        engine.restart(
            1.0, [10.0], init_step=0.1, min_step=1.0E-10, max_step=1.0
        )
        self.assertEqual(engine.t, 1.0)
        self.assertEqual(engine.y, [10.0])
        sol = engine.solve_ivp(2)
        yexp2 = 10.0 * np.exp(-1)
        self.assertAlmostEqual(engine.y[0], yexp2, delta=yexp2*1e-5)

    def test_eval(self):
        engine = Engine(self.SingleExpModel())
        engine.set_diffvar_values(dict(y=10.0))
        sol = engine.solve_ivp(1)
        # Eval using the current value
        t, yder = engine.eval(lambda model: (model.t, model.y.der))
        self.assertEqual(t, 1.0)
        self.assertEqual(yder, -1.0 * engine.y[0])
        # Eval using the specified value
        y = sol(0.5)
        t, yder = engine.eval(
            lambda model: (model.t, model.y.der), 0.5, y
        )
        self.assertEqual(t, 0.5)
        self.assertEqual(yder, -1.0 * y[0])


if __name__ == '__main__':
    unittest.main()
