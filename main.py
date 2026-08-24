import sys
sys.stdout = sys.__stdout__
from abaqus import *
from abaqusConstants import *
from data_utils import figura
import matplotlib.pyplot as plt
from plot_results import plot_figure


models = [
    {'name': 'Modelo 299', 'path': r'299 - Teste-Witz-iso', 'color': '#4daf4a', 'extract': False, 'title': 'Iso'},
    {'name': 'Modelo 300', 'path': r'300 - Teste-Witz-iso-thick', 'color': '#4daf4a', 'extract': False, 'title': 'Thick'},
    ]

extract = {
    'RMC':          True,
    'History':      True,
    'ContactPress': False,
    'Ovalization':  True,
    'Displacement': True
}

plot = {
    'RMC':          True,
    'History':      True,
    'ContactPress': False,
    'Ovalization':  True,
    'Displacement': True
}

fig, axes = figura()
plot_figure(fig, axes, models, extract, plot)

plt.show()