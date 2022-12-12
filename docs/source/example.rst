Getting started
===============

.. py:currentmodule:: eheart

Sample implementation of FHN model

Model implementation
--------------------
.. code-block:: python

    import numpy as np

    from eheart import Model, diffvar

    class FHNmodel(Model):
        def initialize_vars(self):
            self.a = 0.7
            self.b = 0.8
            self.tau = 12.5
            self.i = 0.5
            self.v = diffvar()
            self.w = diffvar()

        def calc_ode(self, t):
            self.vdot = self.v - np.power(self.v, 3) / 3 - self.w + self.i
            self.wdot = (self.v + self.a - self.b * self.w) / self.tau
            self.v.der = self.vdot
            self.w.der = self.wdot

* Define a model with inheriting :py:class:`Model` class.
* Define :py:meth:`Model.initialize_vars` method
  for initialization of differential variables and constants.
* Initialize differential variables with :py:func:`diffvar`.
* Define :py:meth:`Model.calc_ode` method for calculation of the model ODE.
* Use `NumPy routines <https://numpy.org/doc/stable/reference/routines.math.html>`_
  for mathematical functions, because the framework uses NumPy internally.

Vectorization
~~~~~~~~~~~~~
For efficiency and flexibility,
vectorized implementation of :py:meth:`Model.calc_ode` is strongly recommended.
Vectorized is coding :py:meth:`Model.calc_ode`
without control flow statements such as if, while, and for
using model variables in their condition expressions.
Such a implementation enables
processing of each variable as either a scalar or a vector.

A code::

    if x > 0:
        x.der = y
    else:
        x.der = z

can be replaced as::

    x.der = np.where(x > 0, y, z)

which accepts a vector-valued ``x`` and assigns a vector value to ``x.der``.

Simulation
----------
.. code-block:: python
    :caption: Initialization

    import numpy as np

    from eheart import Engine

    model = FHNmodel()        # Instantiate the FHN model
    engine = Engine(model)    # Instantiate the calculation engine

    # Set initial values
    engine.set_diffvar_values({
        'v': 0, 'w': 0
    })

* Create a model instance and an instance of :py:class:`Engine` class.
* Set initial values of differential variables
  using :py:meth:`Engine.set_diffvar_values` method.

.. code-block:: python
    :caption: Simulation at once

    # Simulate the model
    t_end = 50                  # The end of simulation period
    sol = engine.solve_ivp(t_end)

    # Evaluate the result at every 0.5
    output_interval = 0.5       # The time interval of result output
    t_output = np.arange(0, t_end + output_interval, output_interval)
    v, w, vdot, wdot = engine.eval(
        lambda model: (model.v, model.w, model.vdot, model.w.der),
        t_output, sol(t_output)
    )

    # Output the result
    for i in range(len(t_output)):
        print(t_output[i], v[i], w[i], vdot[i], wdot[i])

You can perform simulation of a duration at once and get the solution.
From the solution, you can evaluate model variables at any time
in the duration.

* Use :py:meth:`Engine.solve_ivp` method to simulate the model.
* Call the return value as a function to get the results.
* Use :py:meth:`Engine.eval` method
  to get the values of model variables at a certain time.

.. code-block:: python
    :caption: Model manipulation

    # Change a model parameter value
    model.i = 0.6

    # Restart your engine
    engine.restart()

* Use :py:meth:`Engine.restart` method whenever you manipulate the model.

.. code-block:: python
    :caption: Stepwise simulation

    # Get the current time
    t_base = engine.t

    # Simulate stepwise
    duration = 50               # Simulation duration
    step_size = 0.5             # The size of output time step
    for i in range(int(duration / step_size)):
        t_n = t_base + step_size * (i + 1)
        sol = engine.solve_ivp(t_n)

        v, w, vdot, wdot = engine.eval(
            lambda model: (model.v, model.w, model.v.der, model.wdot)
        )
        print(t_n, v, w, vdot, wdot)

You can separate the simulation period
by calling :py:meth:`Engine.solve_ivp` sequentially.
This manner is slower than the former but allows interactive control.


Offline simulation
------------------
The following code simulates FHN model at once,
then output results to a CSV file using `Pandas <https://pandas.pydata.org>`_.

.. code-block:: python

    import json
    import numpy as np
    import pandas as pd

    from eheart import Engine

    model = FHNmodel()        # Instantiate the FHN model
    engine = Engine(model)    # Instantiate the calculation engine

    # Load initial values of differential variables from a JSON file
    with open('initial_value.json') as f:
        initial_value = json.load(f)
        engine.set_diffvar_values(initial_value)

    # Simulate the model
    duration = 100
    sol = engine.solve_ivp(duration)

    # Obtain results as a dict
    output_interval = 0.5
    t_output = np.arange(0, duration + output_interval, output_interval)
    columns = ('v', 'w', 'vdot', 'wdot')
    result = engine.eval(
        lambda model: {var: getattr(model, var) for var in columns},
        t_output, sol(t_output)
    )

    # Output results using Pandas
    df = pd.DataFrame(result, index=t_output, columns=columns)
    df.to_csv('result.csv', index_label='t')

    # Save final values of differential variables to a JSON file
    with open('final_value.json', 'w') as f:
        final_value = engine.get_diffvar_values()
        json.dump(final_value, f)


Run as a server
---------------

An e-Heart server provides the network API of e-Heart framework
for other programs.

The following command runs a e-Heart server.

.. code-block:: shell

    python -m eheart.server

The server process listen WebSocket connection on localhost:5810.

You can bind all interfaces and the port 12345::

    python -m eheart.server -H 0 -p 12345
