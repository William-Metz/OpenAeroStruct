from __future__ import print_function, division
import numpy as np

from openmdao.api import ExplicitComponent

class MonotonicConstraint(ExplicitComponent):
    """
    Produce a constraint that is violated if a user-chosen measure on the
    wing does not decrease monotonically from the root to the tip.

    Parameters
    ----------
    var_name : string
        The variable to which the user would like to apply the monotonic constraint.

    Returns
    -------
    monotonic[ny-1] : numpy array
        Values are greater than 0 if the constraint is violated.

    """

    def initialize(self):
        self.metadata.declare('var_name', type_=str)
        self.metadata.declare('surface', type_=dict)

    def initialize_variables(self):

        self.surface = self.metadata['surface']
        self.var_name = self.metadata['var_name']
        self.con_name = 'monotonic_' + var_name

        self.symmetry = surface['symmetry']
        self.ny = surface['num_y']

        self.add_input(self.var_name, val=np.zeros(self.ny))
        self.add_output(self.con_name, val=np.zeros(self.ny-1))

    def compute(self, params, unknowns, resids):
        # Compute the difference between adjacent variable values
        diff = params[self.var_name][:-1] - params[self.var_name][1:]
        if self.symmetry:
            unknowns[self.con_name] = diff
        else:
            ny2 = (self.ny - 1) // 2
            unknowns[self.con_name][:ny2] = diff[:ny2]
            unknowns[self.con_name][ny2:] = -diff[ny2:]

    def linearize(self, params, unknowns, resids):
        jac = self.alloc_jacobian()

        np.fill_diagonal(jac[self.con_name, self.var_name][:, :], 1)
        np.fill_diagonal(jac[self.con_name, self.var_name][:, 1:], -1)

        if not self.symmetry:
            ny2 = (self.ny - 1) // 2
            jac[self.con_name, self.var_name][ny2:, :] *= -1

        return jac