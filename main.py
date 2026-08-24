import sys
sys.stdout = sys.__stdout__
from abaqus import *
from abaqusConstants import *
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os
import numpy as np
from matplotlib.widgets import CheckButtons, TextBox

from save_files import save_cpress, save_ho, save_rmc, save_copen, save_curvature, save_ovalization
from read_files import read_cpress, read_ho, read_rmc, find_inp, read_inp, read_sta, read_copen, read_curvatures, read_ovalization
from read_output import compute_bending, compute_tension, compute_ho, compute_copen, compute_displacement, get_ovalization
from plot_results import plot_cpress, plot_ho, plot_km, plot_tm, plot_stiff, plot_copen, plot_copen_heatmap, plot_curvature, plot_ovalization
from part_dimension import get_part_dimensions

models = [
    # {'name': 'Modelo 253', 'path': r'253 - Teste-Witz-NLG', 'color': '#4daf4a', 'extract': False, 'title': 'Polymer'},
    # {'name': 'Modelo 255', 'path': r'255 - Teste-Witz-NLG-NoTension', 'color': '#4daf4a', 'extract': True, 'title': 'NoMetallic'},
    # {'name': 'Modelo 256', 'path': r'256 - Teste-Witz-NLG-ImplicitSolid', 'color': '#4daf4a', 'extract': False, 'title': 'LG'},
    # {'name': 'Modelo 257', 'path': r'257 - Teste-Witz-NLG-ImplicitSolid-PredefinedField', 'color': '#4daf4a', 'extract': True, 'title': 'Predef'},
    # {'name': 'Modelo 259', 'path': r'259 - Teste-Witz-NLG-Implicit-SurfSurf', 'color': '#4daf4a', 'extract': True, 'title': '259'},
    # {'name': 'Modelo 261', 'path': r'261 - Teste-Witz-ImplicitExtPress', 'color': '#4daf4a', 'extract': False, 'title': r'P$_{ext}$ = 1MPa'},
    # {'name': 'Modelo 262', 'path': r'262 - Teste-Witz-ImplicitExtIntPress', 'color': '#4daf4a', 'extract': True, 'title': r'P$_{in}$ = 15MPa'},
    # {'name': 'Modelo 263', 'path': '263 - Teste-Witz-ImplicitExtPress-Parallel', 'color': '#4daf4a', 'extract': True, 'title': r'P$_{ext}$ = 0.5MPa'},
    # {'name': 'Modelo 264', 'path': '264 - Teste-Witz-Explicit-K06', 'color': '#4daf4a', 'extract': True, 'title': r'K = 0.6'},
    # {'name': 'Modelo 265', 'path': '265 - Teste-Witz-NoFabricTape', 'color': '#4daf4a', 'extract': True, 'title': r'NoFabricTape'},
    # {'name': 'Modelo 267', 'path': r'267 - Teste-Witz-NoReducedIntegration', 'color': '#4daf4a', 'extract': True, 'title': 'S4C3D8'},
    # {'name': 'Modelo 268', 'path': r'268 - Teste-Witz-LowerTimeStep', 'color': '#4daf4a', 'extract': True, 'title': 'LowerTS'},
    # {'name': 'Modelo 269', 'path': r'269 - Teste-Witz-ImplicitoNaoLinear', 'color': '#4daf4a', 'extract': True, 'title': 'NLG'},
    # {'name': 'Modelo 270', 'path': r'270 - Teste-Witz-Cruz1996', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996', 'frame': 400},
    # {'name': 'Modelo 271', 'path': r'271 - Teste-Witz-Cruz1996-IntPressure', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996', 'frame': 150},
    # {'name': 'Modelo 272', 'path': r'272 - Teste-Witz-Cruz1996-ExtPressure', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 249', 'path': r'249 - Teste-Witz-Padrao', 'color': '#4daf4a', 'extract': True, 'title': 'Padrao'},
    # {'name': 'Modelo 273', 'path': r'273 - Teste-Witz-Cruz1996-ExtPressureStep', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 274', 'path': r'274 - Teste-Witz-Cruz1996-Linear-K06', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 275', 'path': r'275 - Teste-Witz-Cruz1996-Linear-K04', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 276', 'path': r'276 - Teste-Witz-Cruz1996-K04-IntExt', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 277', 'path': r'277 - Teste-Witz-Cruz1996-K04-IntExt-2Pitch', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 278', 'path': r'278 - Teste-Witz-Cruz1996-K04-IntExt-4xMesh', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 279', 'path': r'279 - Teste-Witz-Cruz1996-K04-IntExt-CilinCoords', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 280', 'path': r'280 - Teste-Witz-Cruz1996-G13', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 281', 'path': r'281 - Teste-Witz-Cruz1996-IntExt', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 282', 'path': r'282 - Teste-Witz-Cruz1996-ShellToSolid', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 283', 'path': r'283 - Teste-Witz-Cruz1996-Coupling', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 284', 'path': r'284 - Teste-Witz-Cruz1996-CouplingExtInt', 'color': '#4daf4a', 'extract': False, 'title': 'Cruz1996'},
    # {'name': 'Modelo 285', 'path': r'285 - Teste-Witz-Cruz1996-CouplingExtInt', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 286', 'path': r'286 - Teste-Witz-Cruz1996-Coupling-2Pitch', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 287', 'path': r'287 - Teste-Witz-Cruz1996-2Pitch', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 288', 'path': r'288 - Teste-Witz-Cruz1996-2Pitch-Linear', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 289', 'path': r'289 - Teste-Witz-Cruz1996-Linear', 'color': '#4daf4a', 'extract': True, 'title': 'Cruz1996'},
    # {'name': 'Modelo 234', 'path': r'234 - Teste-Witz-InternalPressure', 'color': '#4daf4a', 'extract': True, 'title': ''},
    # {'name': 'Modelo 291', 'path': r'291 - Teste-Witz-Cruz1996-CouplingExt', 'color': '#4daf4a', 'extract': True, 'title': ''},
    # {'name': 'Modelo 292', 'path': r'292 - Teste-Witz-Cruz1996-BC', 'color': '#4daf4a', 'extract': True, 'title': ''},
    # {'name': 'Modelo 290', 'path': r'290 - Teste-Witz-SteelTube', 'color': '#4daf4a', 'extract': False, 'title': 'Tube'},
    # {'name': 'Modelo 293', 'path': r'293 - Teste-SteelTube-Implicit', 'color': '#4daf4a', 'extract': False, 'title': 'LG'},
    # {'name': 'Modelo 294', 'path': r'294 - Teste-SteelTube-Implicit-NLG', 'color': '#4daf4a', 'extract': True, 'title': 'NLG'},
    # {'name': 'Modelo 295', 'path': r'295 - Teste-SteelTube-Implicit-Int', 'color': '#4daf4a', 'extract': True, 'title': 'LG', 'frame': 200},
    # {'name': 'Modelo 296', 'path': r'296 - Teste-SteelTube-Implicit-Int-NLG', 'color': '#4daf4a', 'extract': True, 'title': 'NLG', 'frame': 200},
    # {'name': 'Modelo 297', 'path': r'297 - Teste-Witz-Cruz1996-4xMesh', 'color': '#4daf4a', 'extract': False, 'title': '4xMesh'},
    {'name': 'Modelo 298', 'path': r'298 - Teste-Witz-Cruz1996-ExcludeFabricTape', 'color': '#4daf4a', 'extract': True, 'title': 'NoFabricTape'},
    ]

# file_path = r'1 - Cilamce\7 - Skallerud-1Pitch-Pin07MPa\3MPa-NoRecover\DHZL_2013+RK_2015-4.0_skallerud-P07.csv'
# props = [list(), list()]
# file_rmc = open(file_path, 'r')
# line_list = file_rmc.readlines()
# for line in line_list[1:]:
#     line_props = list(map(float, line.split(';')))
#     props[0].append(line_props[0])
#     props[1].append(line_props[1])



def figura():
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    # fig1, axes1 = plt.subplots(figsize=(7, 7))
    x_exp, y_exp, x_exp300, y_exp300, x_lei, y_lei, x_ska07, y_ska07, x_ska07l, y_ska07l, x_ska10, y_ska10 = literatura()

    x = np.linspace(0,0.12,50)
    y = 19309.4*x

    # axes1.plot(x_ska07, y_ska07, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 0.7$MPa", markerfacecolor='#ffffff')
    # # axes1.plot(props[0], props[1], label=r"Analytical estimation")
    # # axes1.plot(x, y, color="#000000", label=r"Analytical estimation")
    # axes1.set_xlim(-0.15, 0.15)
    # axes1.set_ylim(-4000, 4000)
    # axes1.set_xlabel("Curvature (1/m)")
    # axes1.set_ylabel("Moment (Nm)")
    # # axes1.set_title("Relação momento-curvatura")
    # axes1.grid()
    # axes1.set_aspect(aspect=0.3/8000)

    axes[0][0].plot(x_exp, y_exp, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 0$", markerfacecolor='#ffffff')
    # axes[0][0].plot(x_exp300, y_exp300, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 30 MPa$", markerfacecolor='#ffffff')
    # axes[0][0].plot(x_ska10, y_ska10, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 10$MPa", markerfacecolor='#ffffff')
    # axes[0][0].plot(x_ska07, y_ska07, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 0.7$MPa", markerfacecolor='#ffffff')
    # axes[0][0].plot(x_ska07l, y_ska07l, '-', color="#e41a1c", label=r"Wang and Yue (2021)")
    # axes[0][0].plot(x, y, '-', color="green", label=r"19kNm²")
    # axes[0][0].plot(x_lei, y_lei, 'o-', color="#e41a1c", label=r"Lei et al (2024)", markerfacecolor='#e41a1c')
    axes[0][0].set_xlim(-1.5, 1.5)
    axes[0][0].set_ylim(-3000, 3000)
    axes[0][0].set_xlabel("Curvatura (1/m)")
    axes[0][0].set_ylabel("Momento fletor (Nm)")
    axes[0][0].set_title("Relação momento-curvatura")
    axes[0][0].grid()

    # axes[0][1].plot(x_exp, y_exp, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 0$", markerfacecolor='#ffffff')
    # axes[0][1].plot(x_exp300, y_exp300, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 30 MPa$", markerfacecolor='#ffffff')
    # axes[0][1].plot(x_ska07, y_ska07, 's-', color="#4D4D4D", label=r"Experimental P$_{in} = 0.7$MPa", markerfacecolor='#ffffff')
    # axes[0][1].plot(x_ska07l, y_ska07l, '-', color="#e41a1c", label=r"Wang and Yue (2021)")
    # axes[0][1].plot(x, y, '-', color="green", label=r"19kNm²")

    # axes[0][1].plot(x_lei, y_lei, 'o-', color="#e41a1c", label=r"Lei et al (2024)", markerfacecolor='#e41a1c')
    # axes[0][1].set_xlim(-0.15, 0.15)
    # axes[0][1].set_ylim(-4000, 4000)
    axes[0][1].set_xlabel("Tempo de flexão (s)")
    axes[0][1].set_ylabel(r"Rigidez (kNm$^2$)")
    axes[0][1].set_title("Rigidez à flexão")
    axes[0][1].grid()

    axes[0][2].set_xlabel("Tempo de flexão (s)")
    axes[0][2].set_ylabel("Amplitude")
    axes[0][2].set_title("Carregamento vs tempo")
    axes[0][2].grid()

    # axes[1][0].axhline(y=0.05, color='#e41a1c', linestyle='--', linewidth=1, label='Limite 5%')
    # # axes[1][0].set_ylim(0, 0.2)
    # axes[1][0].yaxis.set_major_formatter(PercentFormatter(xmax=1))
    # axes[1][0].set_xlabel("Tempo de simulação (s)")
    # axes[1][0].set_ylabel("Porcentagem da energia interna")
    # axes[1][0].set_title("Parâmetros de controle")
    # axes[1][0].grid()

    # axes[1][1].set_ylim(0, 0.2)
    axes[1][0].set_xlabel("Tempo de simulação (s)")
    axes[1][0].set_ylabel("Energia (J)")
    axes[1][0].set_title(r"Balanço energético")
    axes[1][0].grid()

    axes[1][1].set_xlabel("z (m)")
    axes[1][1].set_ylabel("x (m)")
    axes[1][1].set_title("Deformada da seção central")
    axes[1][1].grid()

    axes[1][2].set_xlabel("Comprimento normalizado")
    axes[1][2].set_ylabel(r"U1/2U1$_{max}$")
    axes[1][2].set_title(r"Deformada")
    axes[1][2].grid()
    axes[1][2].set_xlim(0, 1)
    axes[1][2].set_ylim(0, 1)

    return fig, {
    'endA': axes[0][0],
    'endB': axes[0][0],
    # 'endB': axes1,
    'stiffness': axes[0][1],
    'moment_time': axes[0][2],
    # 'ALLAE': axes[1][0],
    # 'ALLKE': axes[1][0],
    'balance': axes[1][0],
    'ovalization': axes[1][1],
    'curvature': axes[1][2],
    # 'ALLFD': axes[1][2],
}

def literatura():
    exp = [(0, 0),(0.10960960960960953, 394.73435699850825),(0.23873873873873874, 456.00317298430537),(0.355855855855856, 693.5237123916372),(0.45495495495495497, 843.2205790696362),(0.5720720720720722, 1061.8731939486659),(0.6711711711711712, 1085.7838971046522),(0.7882882882882885, 1210.0968893421725),(0.9024024024024024, 1378.472812435077),(1.0075075075075075, 1402.3079683457047),(0.8993993993993996, 913.1017810263099),(0.659159159159159, 457.0041739853068),(0.45495495495495497, 208.00045328347278),(0.355855855856, -17.1681115077331),(0.18168168168168153, -71.58101497724101),(0.052552552552552534, -189.45360454794354),(-0.0015015015015016342, -333.427767390031),(-0.11861861861861867, -382.26906151434423),(-0.23573573573573592, -519.160670104066),(-0.370870870870871, -643.2470206055104),(-0.484984984984985, -786.4657109940126),(-0.602102102102102, -860.4642378227281),(-0.6861861861861864, -1004.0606644380223),(-0.9174174174174174, -1290.4602715923465),(-1.0225225225225227, -1553.2891381947989),(-0.9174174174174174, -680.3973785105859),(-0.8033033033033032, -587.4931535308892),(-0.7042042042042043, -418.9283623245883),(-0.5870870870870872, -326.0619109675713),(-0.484984984984985, -138.66696885564807),(-0.36786786786786774, -14.35397661812749),(-0.13663663663663672, 127.39154248588193),(-0.007507507507507505, 220.1068993521826),(0.04954954954954971, 345.17536404328894)]
    x_exp, y_exp = zip(*exp)

    exp300 = [(0.09655574490985752,631.7606960265471),(0.3373396717194368,1123.5985290160525),(0.42941070948067117,1222.1723921427902),(0.6588483272042336,1358.4626423894488),(0.8741142703381473,1673.1993900798238),(0.9677549556013998,1975.1098753251372),(0.8780159655574489,435.77899363171264),(0.7685891111310428,117.45448022243818),(0.15925195084760957,-717.8222262086301),(0.10252040541752638,-995.5601399228644),(-0.01071845008520933,-1093.4164499058234),(-0.0098215086554847,-1262.93838012378),(-0.12346398780159662,-1284.5098215086573),(-0.25598708404341175,-1237.6446318055441),(-0.3791371423446048,-1462.283612880081),(-0.482016324334021,-1518.118216880439),(-0.5903220019732709,-1548.345143062159),(-0.7116333303435287,-1620.5040810835053),(-0.908556821239573,-1901.9643017310973),(-1.0053816485783478,-2102.0719347026643),(-0.9148802583191318,-706.8346936945027),(-0.8164857834783388,-303.39043860436004),(-0.7067449995515294,-44.39860077137109),(-0.14754686518970317,767.1540048434813),(-0.024127724459592548,940.9364068526302),(0.20544443447842897,1051.798367566595),(0.318638442909678,1158.1307740604511)]
    x_exp300, y_exp300 = zip(*exp300)

    tension = [(0, 0),(0.0010308754761388624, 71.34805363723638),(0.0014778730915735033, 102.78096063918736),(0.001997088972159425, 137.60180855346687),(0.003970084543680903, 310.2629215570903),(0.0060505403982533835, 499.9721284568457)]
    x_tens, y_tens = zip(*tension)

    lei_2024 = [(0.00, 5.95),(0.0240, 83.3),(0.174, 393),(0.257, 524),(0.350, 655),(0.455, 798),(0.587, 946),(0.740, 1.13e+3),(0.829, 1.24e+3),(0.952, 1.38e+3),(1.00, 1.42e+3),(0.937, 1.23e+3),(0.811, 964),(0.737, 810),(0.623, 637),(0.542, 512),(0.437, 357),(0.338, 232),(0.246, 107),(0.186, 23.8),(0.0928, -107),(0.0120, -214),(-0.0898, -333),(-0.171, -435),(-0.281, -577),(-0.377, -690),(-0.449, -786),(-0.545, -905),(-0.668, -1.05e+3),(-0.751, -1.14e+3),(-0.838, -1.25e+3),(-0.946, -1.35e+3),(-0.997, -1.40e+3),(-0.925, -1.21e+3),(-0.805, -923),(-0.722, -792),(-0.644, -679),(-0.536, -512),(-0.440, -363),(-0.320, -214),(-0.237, -77.4),(-0.123, 47.6),(-0.0479, 143),(0.00299, 220)]
    x_lei, y_lei = zip(*lei_2024)

    ska_07 = [(0, 0.6000000000000005),(0.0070775862068965245, 0.7750000000000004),(0.012379310344827588, 0.8375000000000004),(0.02299137931034481, 1),(0.032229885057471264, 1.1875),(0.0409942528735632, 1.3125),(0.050922413793103444, 1.5),(0.05854597701149425, 1.6625),(0.06660632183908047, 1.725),(0.07492528735632181, 1.9125),(0.08278735632183909, 2.1125),(0.0904109195402299, 2.275),(0.09735344827586209, 2.475),(0.1036005747126437, 2.65),(0.10754597701149424, 2.8124999999999996),(0.11171264367816094, 2.9375),(0.1102672413793104, 2.65),(0.10907183908045978, 2.4499999999999997),(0.10765517241379316, 2.2875),(0.10577586206896553, 2.1125),(0.10366379310344823, 1.9250000000000003),(0.10154885057471266, 1.725),(0.09875574712643678, 1.5750000000000002),(0.09572413793103451, 1.3875000000000002),(0.09316091954022987, 1.2374999999999998),(0.08898850574712644, 1.0874999999999995),(0.08480747126436783, 0.8999999999999995),(0.08087356321839084, 0.7875000000000005),(0.07694540229885058, 0.7000000000000002),(0.07393103448275865, 0.5874999999999995),(0.06906609195402297, 0.4250000000000007),(0.0621264367816092, 0.2375000000000007),(0.05150862068965517, 0.05000000000000071),(0.039959770114942506, -0.1875),(0.028181034482758605, -0.4249999999999998),(0.011094827586206862, -0.75),(-0.003908045977011498, -1.0124999999999993),(-0.015913793103448315, -1.2374999999999998),(-0.027229885057471287, -1.4624999999999995),(-0.039913793103448295, -1.6375000000000002),(-0.05261781609195407, -1.8999999999999995),(-0.06508045977011498, -2.1125),(-0.08147413793103452, -2.425),(-0.08839655172413798, -2.5374999999999988),(-0.09370402298850579, -2.624999999999999),(-0.09924425287356325, -2.7249999999999988),(-0.10408620689655176, -2.7874999999999988),(-0.1089252873563219, -2.8374999999999995),(-0.10796551724137936, -2.6625000000000005),(-0.10607471264367821, -2.437499999999999),(-0.10465517241379316, -2.2624999999999993),(-0.1018563218390805, -2.0874999999999995),(-0.10043965517241385, -1.9249999999999998),(-0.09533333333333338, -1.7124999999999995),(-0.08954022988505753, -1.5124999999999993),(-0.08443678160919545, -1.3125),(-0.07702586206896556, -1.0750000000000002),(-0.06938505747126442, -0.8374999999999995),(-0.05897413793103452, -0.5499999999999998),(-0.04995689655172417, -0.3250000000000002),(-0.038859195402298874, -0.04999999999999982),(-0.029393678160919562, 0.125),(-0.01969540229885061, 0.3125),(-0.011155172413793102, 0.46250000000000036),(0, 0.6000000000000005)]
    x_ska07, y_ska07 = zip(*ska_07)
    y_ska07 = [a*1000 for a in y_ska07]

    ska_07l = [(0,0), (0.0032245091200439335, 0.11465086522057), (0.0061627530738652125, 0.18555630026809578), (0.009099336832315008, 0.24923988544967113), (0.012035920590764804, 0.3129234706312447), (0.014972957129770481, 0.37857665123080686), (0.01790878625396053, 0.43897757738240273), (0.020845370012410325, 0.5026611625639772), (0.023781802844008187, 0.5656882159395558), (0.026717631968198235, 0.6260891420911525), (0.029654064799796043, 0.6891161954667311), (0.032590346704541945, 0.7514867170363146), (0.035526326755583953, 0.8125441749939073), (0.038462457733477895, 0.8742581647574941), (0.04139919241877965, 0.9385982817450644), (0.044334719689265806, 0.9976861442846694), (0.047271303447715574, 1.0613697294662439), (0.050207585352461476, 1.1237402510358265), (0.05314311262294763, 1.1828281135754324), (0.056079847308249386, 1.2471682305630019), (0.05901628013984725, 1.3101952839385813), (0.061951505556629455, 1.3679700828661954), (0.0648885420956351, 1.4336232634657566), (0.06782467307352905, 1.4953372532293443), (0.07076004941716324, 1.5537685839629543), (0.07369693502931696, 1.6187652327565196), (0.07663291508035897, 1.679822690714111), (0.07956874420454899, 1.7402236168657073), (0.08250562981670267, 1.805220265659273), (0.08544176079459664, 1.8669342554228612), (0.08837743899193473, 1.9266786497684616), (0.09131432460408845, 1.991675298562027), (0.09425030465513043, 2.0527327565196196), (0.09718613377932048, 2.113133682671216), (0.1001228684646222, 2.177473799658786), (0.10305899944251617, 2.2391877894223735), (0.1059948285667062, 2.29958871557397), (0.10973204908939635, 2.3795542895442354)]
    x_ska07l, y_ska07l = zip(*ska_07l)
    y_ska07l = [a*1000 for a in y_ska07l]

    ska_10 = [(0.1082, 3852.2500),(0.1066, 3595.2900),(0.1044, 3218.4200),(0.0996, 2584.5800),(0.0954, 2053.5300),(0.0890, 1368.3100),(0.0839, 940.0430),(0.0766, 494.6470),(0.0709, 152.0340),(0.0645, -19.2719),(0.0559, -173.4480),(0.0488, -361.8840),(0.0437, -481.7990),(0.0373, -601.7130),(0.0319, -721.6270),(0.0227, -875.8030),(0.0118, -1115.6300),(-0.0003, -1406.8500),(-0.0134, -1629.5500),(-0.0239, -1835.1200),(-0.0341, -2040.6900),(-0.0421, -2194.8600),(-0.0530, -2451.8200),(-0.0664, -2743.0400),(-0.0776, -3000.0000),(-0.0865, -3154.1800),(-0.0951, -3325.4800),(-0.1018, -3445.4000),(-0.1060, -3531.0500),(-0.1034, -3171.3100),(-0.1005, -2862.9600),(-0.0967, -2349.0400),(-0.0916, -1955.0300),(-0.0878, -1680.9400),(-0.0849, -1509.6400),(-0.0811, -1201.2800),(-0.0760, -961.4560),(-0.0702, -635.9740),(-0.0629, -327.6230),(-0.0549, -2.1413),(-0.0453, 289.0790),(-0.0361, 546.0390),(-0.0281, 734.4750),(-0.0188, 974.3040),(-0.0115, 1145.6100),(-0.0003, 1368.3100),(0.0131, 1659.5300),(0.0227, 1882.2300),(0.0319, 2104.9300),(0.0412, 2310.4900),(0.0507, 2533.1900),(0.0635, 2841.5400),(0.0731, 3081.3700),(0.0820, 3286.9400),(0.0929, 3526.7700),(0.1031, 3749.4600)]
    x_ska10, y_ska10 = zip(*ska_10)

    return x_exp, y_exp, x_exp300, y_exp300, x_lei, y_lei, x_ska07, y_ska07, x_ska07l, y_ska07l, x_ska10, y_ska10

def load_data(model):
    p = find_inp(model['path'])
    n_inp = 0 if len(p)==1 else 1
    for file in p:
        inp = read_inp(file)
        if any(step["loads"] for step in inp["steps"]):
            inp_file = inp
        try:
            dims = get_part_dimensions(file)
        except:
            continue
    n_cores, steps_info, progresso_step, progresso_global, wct_total_horas, restante_horas = read_sta(os.path.join(model['path'], f"{inp_file['job_name']}.sta"))
    n_steps_rodando = max(steps_info, key=lambda d: d['step'])['step']
    model_length = max(max(part["length_x"], part["length_y"], part["length_z"]) for part in dims.values())
    idx_step_atual  = n_steps_rodando - n_inp
    # idx_step_atual  = 2
    # model_length = 0.445582178104
    # model_length = 0.5
    rotations = [abs(load['magnitude']) for step in inp_file['steps'] for load in step['loads'] if load['type'] == 'Rotation']

    data = {
        'job_name': inp_file['job_name'],
        'steps': inp_file['steps'],
        'bc_sets': inp_file['bc_sets'],
        'idx_step_atual': idx_step_atual,
        'model_length': model_length,
        'rotations': rotations,
        'n_cores': n_cores,
        'progresso_step': progresso_step,
        'progresso_global': progresso_global,
        'wct_total_horas': wct_total_horas,
        'restante_horas': restante_horas
    }
    # print(data)
    return data

def extract_results(model, data):
    all_ho = {}
    all_copen = {}
    time_offset, n_rotations = 0.0, len(data['rotations'])
    odb = session.openOdb(name=data['job_name'], path=os.path.join(model['path'], f"{data['job_name']}.odb"), readOnly=True)
    for i_step, step in enumerate(data['steps'], 1):
        if i_step <= data['idx_step_atual']:
            abaqus_step = odb.steps[step['name']]
            try: 
                ho = compute_ho(abaqus_step)
                ho['time'] = [t + time_offset for t in ho['time']]
                step_end = ho['time'][-1]
                time_offset = step_end
                for key, values in ho.items():
                    if key not in all_ho:
                        all_ho[key] = []
                    all_ho[key].extend(values)
            except Exception as e:
                print(f"Erro de ho: {e}")
            load_types = {load['type'] for load in step['loads']}

            # copen = compute_copen(abaqus_step)

            # for key, values in copen.items():
            #     if key not in all_copen:
            #         all_copen[key] = []
            #     all_copen[key].extend(values)
            if 'Rotation' in load_types:
                for end in data['bc_sets']:
                    region = odb.rootAssembly.nodeSets[end.upper()]
                    tm, kappa, moment = compute_bending(abaqus_step, region, data['model_length'], n_rotations)
                    save_rmc(model['name'], model['path'], end, tm, kappa, moment)
                    save_cpress(abaqus_step, model['name'], model['path'], data['model_length'])

            if 'Pressure' in load_types:
                save_cpress(abaqus_step, model['name'], model['path'], data['model_length'])
            path_dict = compute_displacement(odb, abaqus_step, model.get('frame'))
            save_curvature(model['name'], model['path'], **path_dict)
            ovalization = get_ovalization(odb, abaqus_step, model.get('frame'))
            save_ovalization(model['name'], model['path'], *ovalization)
    odb.close()
    save_ho(model['name'], model['path'], **all_ho)
    # save_copen(model['name'], model['path'], **all_copen)

def fig_carea():
    fig, axes = plt.subplots(figsize=(15, 10))
    return fig, axes

fig, axes = figura()
# fig2, axes2 = fig_carea()
for i, model in enumerate(models):
    data = load_data(model)

    if model['extract']:
        extract_results(model, data)

    # copen = read_copen(model['name'], model['path'])
    # print(len(copen.keys()))
    # plot_copen(copen, model['path'])
    # plot_copen_heatmap(copen, model['path'])

    rmc = [r for r in (read_rmc(model['name'], model['path'], end)
                    for end in data['bc_sets']
                    ) if r is not None]
    for ax_name, titles, (t, k, m, _) in zip(['endA', 'endB'], [model['title'] + ' - endA', model['title'] + ' - endB'], rmc):
        plot_km(axes[ax_name], t, k, m, titles)

    for label, (t,k,m,s) in zip(['endA', 'endB'], rmc):
        plot_stiff(axes['stiffness'], t, k, m, s, label)

    if rmc:
        plot_tm(axes['moment_time'], *[r[0] for r in rmc], *[r[1] for r in rmc], *[r[2] for r in rmc], model)

    # try:
    #     cpress = read_cpress(model['name'], model['path'])

    #     fig_cp, ax_cp = plt.subplots(figsize=(9,6))
    #     plot_cpress(cpress, ax_cp, fig_cp)

    #     fig_cp.savefig(rf"{model['path']}\Resultado - {model['name']} - CPress.png", dpi=400)
    # except:
    #     print("Sem step de pressão")

    names = {
        'lim': 'Limite - 5% ALLIE',
        'ALLAE': 'Artificial strain energy',
        'ALLCCDW': 'Contact contraint discontinuity work',
        'ALLCCE': 'Contact constraint elastic energy',
        'ALLCCEN': 'Contact constraint elastic normal energy',
        'ALLCCET': 'Contact constraint elastic tangential energy',
        'ALLCCSD': 'Contact constraint stabilization dissipation',
        'ALLCCSDN': 'Contact constraint stabilization normal dissipation',
        'ALLCCSDT': 'Contact constraint stabilization tangential dissipation',
        'ALLCD': 'Creep dissipation energy',
        'ALLDMD': 'Damage dissipation energy',
        'ALLDTI': 'Dynamic time integration energy',
        'ALLEE': 'Electrostatic energy',
        'ALLQB': 'Energy lost to quiet boundaries',
        'ALLMW': 'External work by mass scaling',
        'ALLWK': 'External work',
        'ALLFD': 'Frictional dissipation',
        'ALLIE': 'Internal energy',
        'ALLJD': 'Joule heat dissipation',
        'ALLCW': 'Internal work by constraint penalty',
        'ALLPW': 'Internal work by penalty contact',
        'ALLKE': 'Kinetic energy',
        'ALLKL': 'Loss of kinetic energy at impact',
        'ALLPD': 'Plastic dissipation',
        'ALLSD': 'Static dissipation (stabilization)',
        'ALLSE': 'Strain energy',
        'ETOTAL': 'Total energy',
        'ALLVD': 'Viscous dissipation'
    }
    lines2 = []
    ho = read_ho(model['name'], model['path'])
    for ho_name, ho_values in ho.items():
        if 'CAREA' in ho_name:
            # line = plot_ho(axes2, ho['time'], ho_values, ho_name)
            # lines2.append(line)
            continue
        ax_name = ho_name if ho_name in axes else 'balance'
        if ho_name == 'time':
            continue
        else:
            # pass
            ho_name = names[ho_name]
        plot_ho(axes[ax_name], ho['time'], ho_values, ho_name)
        axes[ax_name].legend()

    coords = read_curvatures(model['name'], model['path'])
    z0, x0, z1, x1, ovalization_index = read_ovalization(model['name'], model['path'])
    plot_curvature(axes['curvature'], *coords)
    plot_ovalization(axes['ovalization'], z0, x0, z1, x1, ovalization_index)

    nome_pasta = os.path.basename(os.getcwd())
    if len(models)==1:
        fig.suptitle(f"Resultado - {model['name']}", fontsize=12, fontweight='bold', y=0.97)
        # if data['restante_horas'] < 1:
        #     fig.text(0.5, 0.05, f"Cores: {data['n_cores']} | Progresso: {data['progresso_global']*100:.1f}% | WCT: {data['wct_total_horas']:.1f} h | Restante: {data['restante_horas']*60:.0f} min", ha='center', fontsize=9, color='black')
        # else:
        #     fig.text(0.5, 0.05, f"Cores: {data['n_cores']} | Progresso: {data['progresso_global']*100:.1f}% | WCT: {data['wct_total_horas']:.1f} h | Restante: {data['restante_horas']:.2f} h", ha='center', fontsize=9, color='black')
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.13, hspace=0.3, wspace=0.3)
        fig.savefig(rf"{model['path']}\Resultado - {model['name']} - Frame {model.get('frame', 'indefinido')}.png", dpi=400)
        # fig.savefig(rf"{model['path']}\Resultado - {model['name']} - {data['progresso_global']*100:.0f}%.png", dpi=400)
    else:
        # fig.text(0.5, 0.06-i*0.02, f"{model['name']} | Cores: {data['n_cores']} | Progresso: {data['progresso_global']*100:.1f}% | WCT: {data['wct_total_horas']:.1f} h | Restante: {data['restante_horas']:.2f} h", ha='center', fontsize=9, color='black')
        save_name = f"Comparação - Modelos { ' e '.join([model['name'].split(' ')[1] for model in models])}"
        # fig.suptitle(save_name, fontsize=12, fontweight='bold', y=0.97)
        # plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.13, hspace=0.3, wspace=0.3)
        plt.savefig(fr"Comparação de resultados\{save_name}.png", dpi=400, bbox_inches='tight')
        # plt.show()
plt.show()