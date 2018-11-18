import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

import pyeit.mesh as mesh
from pyeit.eit.utils import eit_scan_lines
import pyeit.eit.greit as greit

class GreitReconstruction(object):

    def __init__(self, f0):
        self._f0 = f0
        self._f1 = []
        self._image = None
        self._ds = None
        self._mesh = self._construct_mesh()
        self._eit_object = self._setup_eit()

    @property
    def image(self):
        return self._image

    @property
    def f0(self):
        return self._f0

    @property
    def f1(self):
        return self._f1

    @f0.setter
    def f0(self, f0):
        self._f0 = f0

    @f1.setter
    def f1(self, f1):
        self._f1 = f1

    def _construct_mesh(self):
        mesh_obj, el_pos = mesh.create(16, h0=0.17)
        return mesh_obj, el_pos

    def _setup_eit(self):
        mesh_t = self._mesh  # ms, el_pos
        el_dist, step = 1, 1
        ex_mat = eit_scan_lines(16, el_dist)
        # Reconstruction step
        eit_obj = greit.GREIT(mesh_t[0], mesh_t[1], ex_mat=ex_mat, step=step, perm=0.8,
                              parser='std')  # prem default value eq = 1.
        eit_obj.setup(p=0.45, lamb=1e-3, n=96, s=10.0, ratio=0.05)  # n - wielkość siatki, domyślna wartość 32
        return eit_obj

    def _plot_fig(self, ds):
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(np.real(ds), interpolation='none', cmap=plt.cm.viridis)
        fig.colorbar(im)
        ax.axis('equal')

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close('all')
        buf.seek(0)
        im = Image.open(buf)
        self._image = im

    def solve_ds(self):
        ds = self._eit_object.solve(self._f1, self._f0)
        x, y, ds = self._eit_object.mask_value(ds, mask_value=np.NAN)
        self._plot_fig(ds=ds)