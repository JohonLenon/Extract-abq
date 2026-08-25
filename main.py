import sys
from abaqus import *
sys.stdout = sys.__stdout__
from abaqusConstants import *
from data_utils import figura
import matplotlib.pyplot as plt
from plot_results import plot_figure


models = [
   # {'name': 'Modelo 299', 'path': r'299 - Teste-Witz-iso', 'color': '#4daf4a', 'extract': False, 'title': 'Iso'},
    # {'name': 'Modelo 300', 'path': r'300 - Teste-Witz-iso-thick', 'color': '#4daf4a', 'extract': False, 'title': 'IsoThick'},
    {'name': 'Modelo 270', 'path': r'270 - Teste-Witz-Cruz1996', 'color': '#4daf4a', 'extract': False, 'title': 'Ortho'},
    {'name': 'Modelo 301', 'path': r'301 - Teste-Witz-Cruz-Thick', 'color': '#4daf4a', 'extract': False, 'title': 'OrthoThick'},
    ]

extract = {
    'RMC':          True,
    'History':      False,
    'ContactPress': False,
    'Ovalization':  False,
    'Displacement': False
}

plot = {
    'RMC':          True,
    'History':      True,
    'ContactPress': False,
    'Ovalization':  True,
    'Displacement': True
}

historys = [
    'ALLIE',
    # 'ALLKE',
    # 'ALLAE',
    # 'ETOTAL'
]

fig, axes = figura()
plot_figure(fig, axes, models, extract, plot, historys)

plt.show()