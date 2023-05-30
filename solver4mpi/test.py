import pysm3
import pysm3.units as u
from pysm3 import utils
import healpy as hp
import matplotlib.pyplot as plt
from minimizer_multiprocess import *
import sys
import time
import pickle
from functools import partial
import os
sys.path.append('/Users/mregnier/Desktop/Libs/qubic/qubic/scripts/MapMaking')

import component_model as c
import mixing_matrix as mm

comm = MPI.COMM_WORLD

def _scale_components_1pix(beta, ipix, mref, allnus):

    components = c.Dust(nu0=nu0, temp=20)
    A_ev = mm.MixingMatrix(components).evaluator(allnus)
    Aev = A_ev(beta)
    nf, nc = Aev.shape
    m_nu = np.zeros((nf, 3))
    for i in range(3): #Nstk
        m_nu[:, i] = Aev @ np.array([mref[ipix, i]])

    return m_nu

nside = 4
sky=pysm3.Sky(nside=nside, preset_strings=['d0'], output_unit="uK_CMB")
nu0 = 150
mref = np.array(sky.get_emission(nu0 * u.GHz, None).T * utils.bandpass_unit_conversion(nu0*u.GHz, None, u.uK_CMB))


allnus = np.array([140, 150, 160])
m_nu = np.zeros((len(allnus), 12*nside**2, 3))

for j in range(12*nside**2):
    m_nu[:, j, :] = _scale_components_1pix(np.array([1.54]), j, mref, allnus)

def chi2(x, ipix, mref, m_nu, allnus):

    #map_beta[ipix] = x
    m_nu_fake = _scale_components_1pix(x, ipix, mref, allnus)
    
    return np.sum((m_nu_fake - m_nu[:, ipix, :])**2)

index_beta = np.arange(0, 10, 1)

chi2_partial = partial(chi2, mref=mref, m_nu=m_nu, allnus=allnus)

start = time.time()

beta_est = WrapperMPI(comm, chi2_partial, x0=np.ones(10), verbose=True).perform(index_beta)

end = time.time()

if comm.Get_rank() == 0:
    print(f'Execution time : {end - start} s')
    print(f'Residuals :', beta_est - 1.54)



