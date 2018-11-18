"""
   Real time plotting of DeviceHive device' data using kivy
   2018 Tomasz Cieplak

   DeviceHiveDataFilters
"""

import numpy as np


class Filters():
    def __init__(self):
        pass

    def running_mean_fast(self, x, N):
        return np.convolve(x, np.ones((N,)) / N)[(N - 1):]
