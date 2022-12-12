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
from typing import Union, Callable, TypeVar

import numpy as np
from scipy.integrate import LSODA, OdeSolution

from eheart import Model


class Engine:
    """
    Simulation engine.

    Parameters
    ----------
    model : eheart.Model
        The model to be calculated.
    t : float, optional
        The initial time (the default is zero).
    init_step : float, optional
        The initial value of internal adaptive step sizes.
        Automatically calculated without specified.
    min_step : float, optional
        The lower limit of the internal time step size
        (the default is zero).
    max_step : float, optional
        The upper limit of the internal time step size
        (the default is infinity).
    """

    def __init__(self, model: Model,
                 t: float = 0, init_step: float = None,
                 min_step: float = 0, max_step: float = np.inf):
        self.model = model
        self._t = t
        self._y = np.zeros(len(model.diffvars))
        self._init_step = init_step
        self._min_step = min_step
        self._max_step = max_step
        self._solver = None

    @property
    def t(self):
        """
        The current time (read-only).
        """
        return self._t

    @property
    def y(self):
        """
        The current values of the differential variable (read-only).
        """
        return self._y

    def set_diffvar_values(self, vdict: dict[str, float]) -> None:
        """
        Set the values of differential variables.
        When the solver is already started, you need to call
        :py:meth:`restart` method followed to this method.

        Parameters
        ----------
        vdict : dict
            A dictionary of values to be set indexed by variable names.
        """
        for i, var in enumerate(self.model.diffvars):
            if var in vdict:
                self._y[i] = vdict[var]

    def get_diffvar_values(self) -> dict[str, float]:
        """
        Get the current values of differential variables.

        Returns
        -------
        dict
            A dictionary of all of the variable values indexed by their name.
        """
        return {
            var: self._y[i]
            for i, var in enumerate(self.model.diffvars)
        }

    def solve_ivp(self, tn: float) -> OdeSolution:
        """
        Solve an initial value problem of the model
        from the current `t` to the specified `tn`.
        After execution, `t` and `y` are updated
        to `tn` and the differential variable values at `tn`, respectively.

        Internal time steps are adaptively controlled.

        Parameters
        ----------
        tn : float
            *t* at the next step.

        Returns
        -------
        scipy.integrate.OdeSolution
            The solution as a callable.
            Calling it with a certain time as the argument returns
            the array of the differential variable values
            interpolated using calculated values at internal timesteps.
            Note that the valid argument time is
            between the previous `t` and `tn`.

        Examples
        --------
        >>> # Solve a model until t = 1.0
        >>> sol = engine.solve_ivp(1.0)
        >>> # Obtain the array of the differential variable values at t = 0.5
        >>> y = sol(0.5)
        """
        if self._solver is None:
            self._solver = LSODA(
                self.model.eval_ode, self._t, self._y, np.inf,
                self._init_step, self._min_step, self._max_step,
                rtol=1e-6, atol=1e-10
            )
            self._ts = [self._t]
            self._interpolants = []
        else:
            self._ts = self._ts[-2:]
            self._interpolants = self._interpolants[-1:]

        while self._ts[-1] < tn:
            message = self._solver.step()
            if message is not None:
                raise SolverError(message)
            self._ts.append(self._solver.t)
            sol = self._solver.dense_output()
            self._interpolants.append(sol)

        self._t = tn
        self._y = self._interpolants[-1](tn)

        return OdeSolution(self._ts, self._interpolants)

    def restart(self, t: float = None, y: np.ndarray = None,
                init_step: float = None,
                min_step: float = None, max_step: float = None) -> None:
        """
        Restart the ODE solver with clearing internal states.
        You need to call this method after externally altering any
        differential variable or constant.

        Parameters
        ----------
        t : float, optional
            The restarting time (the default is the current value).
        y : np.ndarray, optional
            The array of differential variable values set on restart
            (the default is the current values).
        init_step : float, optional
            The initial value of internal adaptive step sizes.
            Keep the current setting specified.
        min_step : float, optional
            The lower limit of the internal time step size
            Keep the current setting specified.
        max_step : float, optional
            The upper limit of the internal time step size
            Keep the current setting specified.
        """
        if t is not None:
            self._t = t
        if y is not None:
            self._y = y
        if init_step is not None:
            self._init_step = init_step
        if min_step is not None:
            self._min_step = min_step
        if max_step is not None:
            self._max_step = max_step
        self._solver = None

    EvalFuncReturn = TypeVar('EvalFuncReturn')

    def eval(
        self, func: Callable[[Model], EvalFuncReturn],
        t: Union[float, np.ndarray] = None, y: np.ndarray = None
    ) -> EvalFuncReturn:
        """
        Evaluate a function at *t* with the values of differential variables.

        Parameters
        ----------
        func: callable
            A function to be evaluated. The calling signature is func(model).
        t : float
            The time to be evaluated (the default is the current value).
        y : numpy.ndarray
            The array of the differential variable values used in evaluation
            (the default is the current values).

        Returns
        -------
        any
            The evaluate of the argument function.
        """
        if t is None:
            t = self._t
        if y is None:
            y = self._y
        self.model.eval_ode(t, y)

        return func(self.model)


class SolverError(Exception):
    """
    Exception raised when a solver failed.
    """
