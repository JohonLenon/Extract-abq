from numpy import mean
from odbAccess import DOUBLE_PRECISION

def get_field_data(value):
    if value.precision == DOUBLE_PRECISION:
        return value.dataDouble
    return value.data

def save_cpress(step, name, path, length):
    file_cpress = open(fr'{path}\Pressão de contato - {name}.csv', 'w')
    
    file_cpress.write('Instance, Cpress (MPa)\n')

    frame = step.frames[-1]

    layer_dict = {}
    mean_dict = {step.name: {}}

    if 'CPRESS' in frame.fieldOutputs:
        for v in frame.fieldOutputs['CPRESS'].values:
            if get_field_data(v) is not None:
                inst = v.instance
                node = inst.getNodeFromLabel(v.nodeLabel)
                coords = node.coordinates   # (x, y, z) na configuração indeformada
                if 0.2 * length <= coords[1] <= 0.8 * length:
                    key = inst.name.split("-", 1)[0]
                    layer_dict.setdefault(key, []).append(get_field_data(v))
                    # print('Instancia: %s  No: %d  CPRESS: %.3f  Pos: %s' %
                    #     (inst.name, v.nodeLabel, v.data, coords))
                file_cpress.write(f'{v.instance.name},{(get_field_data(v)/1E6):.6f}\n')
    for key, values in layer_dict.items():
        mean_dict[step.name][key] = mean(values)/1E6

    print(mean_dict)
    file_cpress.close()

def save_rmc(name, path, end, time, kappa, moment):
    # Salvando Relação Momento-Curvatura
    file_rmc = open(fr'{path}\Momento-curvatura - {name} - {end}.csv', 'w')
    file_rmc.write('time, kappa (1/m), moment (Nm), stiffness (Nm^2)\n')
    stiffness = [(moment[i] - moment[i-1]) / dk if (dk := kappa[i] - kappa[i-1]) != 0 else 0 for i in range(1, len(moment))]
    for t, ki, mi, ei in zip(time, kappa, moment, stiffness):
        file_rmc.write(f'{t:.4f}, {ki:.6e}, {mi:.6e}, {ei:.6e}\n')
    file_rmc.close()

def save_ho(name, path, **ho):
    file_ho = open(fr"{path}\History_outputs - {name}.csv", 'w')
    file_ho.write(', '.join(ho.keys()) + '\n')
    for values in zip(*list(ho.values())):
        file_ho.write(', '.join([
            f'{v:.6e}'
            for v in values
        ]) + '\n')
    file_ho.close()

def save_copen(name, path, **ho):
    file_ho = open(fr"{path}\Copen - {name}.csv", 'w')
    file_ho.write(', '.join(ho.keys()) + '\n')
    for values in zip(*list(ho.values())):
        file_ho.write(', '.join([
            f'{v:.6e}'
            for v in values
        ]) + '\n')
    file_ho.close()

def save_curvature(name, path, **path_dict):
    file_path = open(fr"{path}\Curvatures - {name}.csv", 'w')
    file_path.write('y0_1,x0_1,y_1,x_1,y0_2,x0_2,y_2,x_2\n')
    path1 = path_dict['path1']
    path2 = path_dict['path2']
    for values in zip(*path1, *path2):
        file_path.write(', '.join(f'{v:.6e}' for v in values) + '\n')
    file_path.close()

def save_ovalization(name, path, z0, x0, z1, x1, ovalization_index):
    file_path = fr"{path}\Ovalization - {name}.csv"
    with open(file_path, 'w') as f:
        f.write(f'ovalization_index,{ovalization_index:.6e}\n')
        f.write('z0,x0,z1,x1\n')
        for zi0, xi0, zi1, xi1 in zip(z0, x0, z1, x1):
            f.write(f'{zi0:.6e},{xi0:.6e},{zi1:.6e},{xi1:.6e}\n')