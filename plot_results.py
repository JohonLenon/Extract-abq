import numpy as np
import matplotlib.pyplot as plt
from save_files import save_figure
from matplotlib.patches import Circle
from data_utils import load_data, extract_results
from read_files import read_cpress, read_ho, read_rmc, read_curvatures, read_ovalization

t_sample = None
t_sample = np.array([0.1])
t_pressure = 0

def adjust_axis_limits(ax, data, axis='y'):
    get_lim = ax.get_xlim if axis == 'x' else ax.get_ylim
    set_lim = ax.set_xlim if axis == 'x' else ax.set_ylim
    low_key = 'left' if axis == 'x' else 'bottom'
    high_key = 'right' if axis == 'x' else 'top'

    lim_min_atual, lim_max_atual = get_lim()

    novo_max = np.ceil(max(data) * 100) / 100
    novo_min = np.floor(min(data) * 100) / 100

    if novo_max > lim_max_atual:
        valor = novo_max * 1.15 if novo_max > 0 else novo_max * 0.85
        set_lim(**{high_key: valor})
    if novo_min < lim_min_atual:
        valor = novo_min * 1.15 if novo_min < 0 else novo_min * 0.85
        set_lim(**{low_key: valor})

def perclimits(ax, data, axis='y'):
    set_lim = ax.set_xlim if axis == 'x' else ax.set_ylim
    data = np.asarray(data)
    data = data[np.isfinite(data)]
    if len(data) == 0:
        return
    novo_min = np.percentile(data, 5)
    novo_max = np.percentile(data, 95)
    margem = 0.15 * (novo_max - novo_min)
    set_lim(novo_min - margem, novo_max + margem)

def set_section_limits(ax, x_data, z_data, margin=1.15):
    max_range = max(max(abs(v) for v in x_data), max(abs(v) for v in z_data)) * margin
    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_aspect('equal', adjustable='box')

def plot_km(ax, t, k, m, label):
    # k = [abs(a) for a in k]
    # m = [abs(a) for a in m]
    ax.plot(k, m, linewidth=1.5, label=label)
    if t_sample is not None:
        km = np.interp(t_sample, t, k)
        mm = np.interp(t_sample, t, m)
        ax.plot(km, mm, 'o', markersize=5)
    ax.legend()

def plot_tm(ax, tm1, tm2, k1, k2, m1, m2, model):
    # ax.plot(tm1, m1, color=model['color'], linewidth=1.5, label=model['name'])
    # ax.plot(tm2, m2, color=model['color'], linewidth=1.5)
    # ax.plot(tm1, k1, color=model['color'], linewidth=1.5)
    # ax.plot(tm2, k2, color=model['color'], linewidth=1.5)
    def normalize_from_start_scaled(x):
        """Variação relativa desde t=0, escalada pelo range total."""
        x = np.array(x)
        delta = x - x[0]
        amp = x.max() - x.min() #if x.min()>=0 else x.max()
        return delta / amp if amp != 0 else delta

    m1_n = normalize_from_start_scaled(m1)
    m2_n = normalize_from_start_scaled(m2)
    k1_n = normalize_from_start_scaled(k1)
    k2_n = normalize_from_start_scaled(k2)

    ax.plot(tm1, m1_n, color=model['color'], linewidth=1.5, label="Momento")
    ax.plot(tm2, m2_n, color=model['color'], linewidth=1.5)
    ax.plot(tm1, k1_n, color=model['color'], linewidth=1.5, linestyle='--', label = "Curvatura")
    ax.plot(tm2, k2_n, color=model['color'], linewidth=1.5, linestyle='--')

    if t_sample is not None:
        mm1 = np.interp(t_sample, tm1, m1_n)
        mm2 = np.interp(t_sample, tm2, m2_n)
        ax.plot(t_sample, mm1, 'o', markersize=5)
        ax.plot(t_sample, mm2, 'o', markersize=5)

    ax.set_xlim(0, max(max(tm1), max(tm2)))
    # ax.set_ylim(-1.25, 1.25)
    ax.legend()

def plot_stiff(ax, t, k, m, s, label):
    t_fit = []
    k_fit = []
    m_fit = []
    stiff_fit = []
    points = 10

    if len(k)<points:
        return None

    for i in range(0, len(t), points-1):
        k_bloco = k[i:i+points]
        m_bloco = m[i:i+points]
        t_bloco = t[i:i+points]

        if len(k_bloco) < 4:
            continue

        M = np.poly1d(np.polyfit(k_bloco, m_bloco, 1))
        ei = np.polyder(M)
        k_centro = np.mean(k_bloco)

        k_fit.append(k_bloco[0])
        k_fit.append(k_bloco[-1])

        m_fit.append(M(k_bloco[0]))
        m_fit.append(M(k_bloco[-1]))

        t_fit.append(np.mean(t_bloco))
        stiff_fit.append(ei(k_centro))

    stiff_fit = [a/1000 for a in stiff_fit]
    s = [a/1000 for a in s]
    ax.plot(t, s, linewidth=1.5, color='gray', alpha=0.4)
    ax.plot(t_fit, stiff_fit, linewidth=1.5, label=label)

    perclimits(ax, stiff_fit)

    if t_sample is not None:
        sm = np.interp(t_sample, t_fit, stiff_fit)
        ax.plot(t_sample, sm, 'o', markersize=5)
    ax.legend()

def plot_ho(ax, t, r, label):
    adjust_axis_limits(ax, r)
    # perclimits(ax, r)
    if not hasattr(plot_ho, 'color_index'):
        plot_ho.color_index = 0
    colors = plt.cm.get_cmap('tab10', 10)
    color = colors(plot_ho.color_index % 10)
    plot_ho.color_index += 1
    line, = ax.plot(t, r, linewidth=1.5, label=label, color = color)
    if t_sample is not None:
        rm = np.interp(t_sample+t_pressure, t, r)
        ax.plot(t_sample+t_pressure, rm, 'o', markersize=5)
    ax.set_xlim(0, max(t))
    return line

def plot_curvature(ax, y01, x01, y1, x1, y02, x02, y2, x2):
    def normalize(values):
        max_value = max(abs(v) for v in values)
        return [v / max_value for v in values]

    def normalize_u(values):
        max_value = max(abs(v) for v in values)
        return [v / 2 / max_value for v in values]

    x1 = [x - min(x1) for x in x1]
    x2 = [x - min(x2) for x in x2]

    c1 = [v / max(y1) for v in y1]
    c2 = [v / max(y2) for v in y2]

    u1 = normalize_u(x1)
    u2 = normalize_u(x2)
    color = ax._get_lines.get_next_color()
    ax.plot(c1, u1, linewidth=1.5, label=r'Path$_{sup}$', color=color)
    ax.plot(c2, u2, '--', linewidth=1.5, label=r'Path$_{inf}$', color=color)

    circle = Circle((0.5, 0), radius=0.5, fill=True, color='#E6E6E6', zorder=0)
    ax.add_patch(circle)
    ax.set_aspect('equal')
    ax.legend()

def plot_ovalization(ax, z0, x0, z1, x1, ov_index):
    x_all = x0 + x1
    z_all = z0 + z1
    set_section_limits(ax, x_all, z_all)
    color = ax._get_lines.get_next_color()
    ax.plot(z0, x0, linewidth=1.5, label='Indeformada', color=color)
    ax.plot(z1, x1, '--', linewidth=1.5, label=f'Deformada - IOV {ov_index*100:.0f}%', color=color)
    # ax.set_aspect('equal')
    ax.legend()

def plot_cpress(data, ax, fig):
    ax = ax or plt.gca()

    items = sorted(data.items(), key=lambda x: np.median(x[1]))

    filtered = [
        (k, [x for x in v if x > 1e-3])
        for k, v in items
    ]

    filtered = [(k, v) for k, v in filtered if v]

    labels = [k for k, v in filtered]
    values = [v for k, v in filtered]

    ax.boxplot(
        values,
        labels=labels,
        vert=False,
        showfliers=True
    )

    ax.set_xscale('log')

    ax.set_xlabel('CPRESS (MPa)')
    ax.set_ylabel('Instância')

    ax.grid(True, which='both', alpha=0.3)
    fig.tight_layout()

def plot_figure(fig, axes, models, extract, plot, historys):
    for i, model in enumerate(models):
        data = load_data(model)
        if model['extract']:
            extract_results(model, data, extract)

        if plot['RMC']:
            rmc = [r for r in (read_rmc(model['name'], model['path'], end)
                            for end in data['bc_sets']
                            ) if r is not None]
            for ax_name, titles, (t, k, m, _) in zip(['endA', 'endB'], [model['title'] + ' - endA', model['title'] + ' - endB'], rmc):
                plot_km(axes[ax_name], t, k, m, titles)
            for label, (t,k,m,s) in zip(['endA', 'endB'], rmc):
                plot_stiff(axes['stiffness'], t, k, m, s, label)
            if rmc:
                plot_tm(axes['moment_time'], *[r[0] for r in rmc], *[r[1] for r in rmc], *[r[2] for r in rmc], model)

        if plot['History']:
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
            ho = read_ho(model['name'], model['path'])
            for ho_name, ho_values in ho.items():
                if not historys or ho_name in historys:
                    ax_name = ho_name if ho_name in axes else 'balance'
                    if ho_name == 'time':
                        continue
                    else:
                        ho_name = names[ho_name]
                    plot_ho(axes[ax_name], ho['time'], ho_values, ho_name)
                    axes[ax_name].legend()

        if plot['Displacement']:
            coords = read_curvatures(model['name'], model['path'])
            plot_curvature(axes['curvature'], *coords)

        if plot['Ovalization']:
            z0, x0, z1, x1, ovalization_index = read_ovalization(model['name'], model['path'])
            plot_ovalization(axes['ovalization'], z0, x0, z1, x1, ovalization_index)

        save_figure(fig, i, models, data)