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
import numpy as np


class Model:
    """
    Base class for e-Heart models.
    Define your model with inheriting this class.
    """

    def __init__(self):
        self.initialize_vars()
        self._diffvars = tuple(
            k for k, v in vars(self).items()
            if isinstance(v, DifferentialVariable)
        )

    def initialize_vars(self):
        """
        Implement this method to define differential variables and
        externally alterable constants as attributes.
        All of the differential variables must be initialized with
        :py:func:`diffvar`.
        """
        raise NotImplementedError()

    def calc_ode(self, t):
        """
        Implement this method to calculate the system of ordinary differential
        equations, that is,
        calculate the derivatives of differential variables using the given
        value of differential variables.
        """
        raise NotImplementedError()

    def eval_ode(self, t, y: np.ndarray):
        """
        Evaluate the ordinary differential equations.

        Parameters
        ----------
        t : number
            The time to be evaluated.
        y : numpy.ndarray
            The array of the values of differential variables.

        Returns
        -------
        numpy.ndarray
            The array of the derivatives of differntial variables.
        """
        for i in range(len(y)):
            setattr(self, self._diffvars[i], diffvar(y[i]))
        self.calc_ode(t)
        return np.array([
            getattr(self, self._diffvars[i]).der for i in range(len(y))
        ])

    @property
    def diffvars(self):
        return self._diffvars


class DifferentialVariable:
    """
    Abstract class for differential variables.

    Attributes
    ----------
    der : float
        The derivative of this differential variable.
    """

    def __init__(self):
        self.der = 0


class _DiffvarScalar(np.double, DifferentialVariable):
    def __init__(self, _):
        super().__init__()


class _DiffvarArray(np.ndarray, DifferentialVariable):
    def __new__(cls, value):
        return super().__new__(cls, value.shape, buffer=value)

    def __init__(self, _):
        super().__init__()


def diffvar(value=None):
    """
    Create a differential variable, an instance of
    :py:class:`eheart._model.DifferentialVariable`.
    """
    if value is None:
        return DifferentialVariable()
    elif np.isscalar(value):
        return _DiffvarScalar(value)
    elif isinstance(value, list):
        return _DiffvarArray(np.array(value, dtype=float))
    elif isinstance(value, np.ndarray):
        return _DiffvarArray(value.copy())
    else:
        raise TypeError('Illegal argument type')
