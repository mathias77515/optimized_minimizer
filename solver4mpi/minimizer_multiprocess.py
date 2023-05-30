import numpy as np
from pyoperators import *
from scipy.optimize import minimize


class WrapperMPI:

    def __init__(self, comm, chi2, x0, method='TNC', tol=1e-3, options={}, verbose=False):

        ### Do some prints
        self.verbose = verbose
        
        ### MPI distribution
        self.comm = comm
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        ### Minimizer
        self.chi2 = chi2
        self.x0 = x0
        self.method = method
        self.tol = tol
        self.options = options

        if verbose:
            print(f'size = {self.size} and rank = {self.rank}')

    def _split_params(self, index_theta):

        '''
        
        Distribute the parameters across all available processes

        '''
        return np.where(index_theta % self.size == self.rank)[0]
    
    def _apply_minimize(self, fun, args):

        '''
        
        Apply the scipy.optimize.minimize method on the fun cost function.

            Warning : fun is the cost function and should take as free parameter theta and the id of the targeted pixel

        '''

        r = minimize(fun, x0=self.x0, args=args, method=self.method, tol=self.tol, options=self.options)
        return r.x
    
    def _joint_process(self, theta):

        '''
        
        Joint the results of all processes. After that command, all processes knows the result of the minimization.

        '''
        return self.comm.allreduce(theta, op=MPI.SUM)
        
    def perform(self, index_theta):

        '''
        
        Main function to be called. Perform the minimization on the pixel indexed by index_theta array.
        
        '''
        res = np.zeros(len(index_theta))
        index_per_process = self._split_params(index_theta)
        if self.verbose:
            print(f'Doing minimization on pixel {index_per_process}')
        
        for _, index in enumerate(index_per_process):
            res[index] = self._apply_minimize(self.chi2, args=(index)) 
        
        ### Wait for all processes
        self.comm.Barrier()
 
        return self._joint_process(res)