import pytest
from kymatio import Scattering1D
from kymatio.scattering1d.filter_bank import scattering_filter_factory
import os
import sys
import io
import numpy as np

backends = []

from kymatio.scattering1d.backend.numpy_backend import backend
backends.append(backend)
@pytest.mark.parametrize('backend', backends)

class TestScattering1DNumpy:
    def test_Scattering1D(self, backend):
        """
        Applies scattering on a stored signal to make sure its output agrees with
        a previously calculated version.
        """
        test_data_dir = os.path.dirname(__file__)
        with open(os.path.join(test_data_dir, 'test_data_1d.npz'), 'rb') as f:
            buffer = io.BytesIO(f.read())
            data = np.load(buffer)
        x = data['x']
        J = data['J']
        Q = data['Q']
        Sx0 = data['Sx']
        N = x.shape[-1]
        scattering = Scattering1D(J, N, Q, backend=backend, frontend='numpy')
        Sx = scattering(x)
        assert np.allclose(Sx, Sx0)

    def test_Scattering1D_T(self, backend):
        """
        Applies scattering on a stored signal to make sure its output agrees with
        a previously calculated version.
        """
        test_data_dir = os.path.dirname(__file__)
        with open(os.path.join(test_data_dir, 'test_data_1d.npz'), 'rb') as f:
            buffer = io.BytesIO(f.read())
            data = np.load(buffer)
        x = data['x']
        J = data['J']
        Q = data['Q']
        Sx0 = data['Sx']
        N = x.shape[-1]
        # default
        scattering1 = Scattering1D(J, N, Q, backend=backend, frontend='numpy')
        Sx1 = scattering1(x)
        meta1 = scattering1.meta()
        order0_1 = np.where(meta1['order'] == 0)
        order1_1 = np.where(meta1['order'] == 1)
        order2_1 = np.where(meta1['order'] == 2)
        # adjust T
        sigma_low_scale_factor = 2
        T=2**(J-sigma_low_scale_factor)
        scattering2 = Scattering1D(J, N, Q, T=T, backend=backend, frontend='numpy')
        Sx2 = scattering2(x)
        assert Sx2.shape == (Sx1.shape[0], Sx1.shape[1], Sx1.shape[2]*2**(sigma_low_scale_factor))        
        # adjust J
        sigma_low_scale_factor = 1
        T=2**J
        scattering2 = Scattering1D(J-sigma_low_scale_factor, N, Q, T=T, backend=backend, frontend='numpy')
        Sx2 = scattering2(x)
        meta2 = scattering2.meta()             
        # find comparable paths
        indices1 = np.array([], dtype=int)
        indices2 = np.array([], dtype=int)        
        meta1['sigma'][np.isnan(meta1['sigma'])] = -1
        meta2['sigma'][np.isnan(meta2['sigma'])] = -1
        i = 0
        for key2 in meta2['sigma']:
          index1 = np.where((meta1['sigma'] == key2).all(axis=1))
          if len(index1[0]) != 0:
            indices1 = np.append(indices1, index1[0])
            indices2 = np.append(indices2, i)
          i += 1         
        assert np.allclose(Sx1[:,indices1, :],Sx2[:,indices2, :])
        
    def test_Scattering1D_filter_factory_T(self, backend):
        """
        Constructs the scattering filters for the T parameter which controls the
        temporal extent of the low-pass sigma_log filter
        """
        N = 2**13
        Q = 1
        sigma_low_scale_factor = [0, 5]
        Js = [5]

        for j in Js:
            J = j
            for i in sigma_low_scale_factor:
                T=2**(J-i)
                if i == 0:
                    default_str = ' (default)'
                else:
                    default_str = ''
                phi_f, psi1_f, psi2_f = scattering_filter_factory(np.log2(N), J, Q, T)
                assert(phi_f['sigma']==0.1/T)
