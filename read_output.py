import numpy as np
import math
from odbAccess import DOUBLE_PRECISION

def get_field_data(value):
    if value.precision == DOUBLE_PRECISION:
        return value.dataDouble
    return value.data

def compute_bending(step, region, model_length, rotations):
    UR_FACTOR = rotations / model_length
    frames = step.frames
    n_frames = len(frames)
    time_list = [None] * n_frames
    rm3_list  = [None] * n_frames
    ur3_list  = [None] * n_frames
    for i, frame in enumerate(frames):
        try:
            rm_val = frame.fieldOutputs["RM"].getSubset(region=region).values[0]
            ur_val = frame.fieldOutputs["UR"].getSubset(region=region).values[0]
            time_list[i] = frame.frameValue
            rm3_list[i]  = get_field_data(rm_val)[2]
            ur3_list[i]  = get_field_data(ur_val)[2] * UR_FACTOR
            # rm3_list[i]  = rm_val.data[2]
            # ur3_list[i]  = ur_val.data[2] * UR_FACTOR
        except IndexError:
            continue
    return time_list, ur3_list, rm3_list

def compute_ho(step):    
    # ratios = ['ALLAE', 'ALLKE']
    ratios = []
    exclude = ['CDISP','CFNM','CFN1','CFN2','CFN3','CFSM','CFS1','CFS2','CFS3','CFTM','CFT1','CFT2','CFT3','CICPS','CMNM','CMN1','CMN2','CMN3','CMSM','CMS1','CMS2','CMS3','CMTM','CMT1','CMT2','CMT3','CAREA','CTRQ','XN1','XN2','XN3','XS1','XS2','XS3','XT1','XT2','XT3','PFORCE1','PFORCE2','PFORCE3','PPRESS']
    ho_dict = {}
    for name, _ in step.historyRegions.items():
        hist = step.historyRegions[name]
        for ho_name in hist.historyOutputs.keys():
            if any(name in ho_name for name in exclude):
                continue
            if (ho_name not in ratios) and (ho_name != 'ALLSE'):
                ho_data = hist.historyOutputs[ho_name].data
                time, values  = zip(*ho_data)
                if abs(np.mean(values)) >= 1e-6:
                    ho_dict[ho_name] = values
                    if 'time' not in ho_dict:
                        ho_dict['time'] = time
        for ho_name in hist.historyOutputs.keys():
            if ho_name in ratios:
                ho_data = hist.historyOutputs[ho_name].data
                _, values  = zip(*ho_data)
                values = [a/b if b != 0 else 0 for a, b in zip(values, ho_dict['ALLIE'])]
                ho_dict[ho_name] = values
        
    ho_dict['lim'] = [0.05*a for a in ho_dict.get('ALLIE',[0]*len(ho_dict.get('time')))]
    del_names = []
    for key, valores in list(ho_dict.items()):
        if key.endswith("-EXT") or key.endswith("-INT"):
            instance = key.rsplit("-", 1)[0]
            base = instance.rsplit("-", 1)[0]
            suff = key.rsplit("-", 1)[1]
            new_name = 'CAREA '+base+'-'+suff
            del_names.append(key)
            if new_name not in ho_dict:
                ho_dict[new_name] = valores
            else:
                ho_dict[new_name] = [a+b for a,b in zip(ho_dict[new_name], valores)]
    for key in del_names:
        del ho_dict[key]
    return ho_dict

def compute_displacement(odb, step, frame = None):
    if frame is not None:
        try:
            frame_u = step.frames[frame]
        except Exception as e:
            frame_u = next((frame for frame in reversed(step.frames) if 'U' in frame.fieldOutputs), None)
            print(f"Erro no frame: {e}. Tempo válido: {frame_u.frameValue}s")
        if 'U' not in frame_u.fieldOutputs:
            for i in range(frame, -1, -1):
                frame_u = step.frames[i]
                if 'U' in frame_u.fieldOutputs:
                    print(f'Frame válido encontrado: índice {i}, Tempo: {frame_u.frameValue}s')
                    break
            else:
                print('Nenhum frame válido encontrado.')
        else:
            print(f'Frame válido - Tempo: {frame_u.frameValue}s')

    else:
        frame_u = next((frame for frame in reversed(step.frames) if 'U' in frame.fieldOutputs), None)
        print(f'Tempo: {frame_u.frameValue}s')

    instances = odb.rootAssembly.instances
    last_layer = max(instances.keys(), key=lambda key: max(node.coordinates[0] for node in instances[key].nodes))
    initial_coords = {node.label: node.coordinates for node in instances[last_layer].nodes}
    u_values = [v for v in frame_u.fieldOutputs['U'].getSubset(region=instances[last_layer]).values if v.nodeLabel in initial_coords]
    u_path_1 = {desloc.nodeLabel: get_field_data(desloc) for desloc in u_values if (abs(initial_coords[desloc.nodeLabel][2])<1e-6 and initial_coords[desloc.nodeLabel][0]>0)}
    u_path_2 = {desloc.nodeLabel: get_field_data(desloc) for desloc in u_values if (abs(initial_coords[desloc.nodeLabel][2])<1e-6 and initial_coords[desloc.nodeLabel][0]<0)}

    path_1 = sorted(u_path_1, key=lambda label: initial_coords[label][1])
    y0_1 = [initial_coords[label][1] for label in path_1]
    x0_1 = [initial_coords[label][0] for label in path_1]
    y_1 = [initial_coords[label][1] + u_path_1[label][1] for label in path_1]
    x_1 = [initial_coords[label][0] + u_path_1[label][0] for label in path_1]

    path_2 = sorted(u_path_2, key=lambda label: initial_coords[label][1])
    y0_2 = [initial_coords[label][1] for label in path_2]
    x0_2 = [initial_coords[label][0] for label in path_2]
    y_2 = [initial_coords[label][1] + u_path_2[label][1] for label in path_2]
    x_2 = [initial_coords[label][0] + u_path_2[label][0] for label in path_2]

    path_dict = {'path1': [y0_1, x0_1, y_1, x_1], 'path2': [y0_2, x0_2, y_2, x_2]}
    return path_dict

def get_ovalization(odb, step, frame = None):
    if frame is not None:
        try:
            frame_u = step.frames[frame]
        except Exception as e:
            frame_u = next((frame for frame in reversed(step.frames) if 'U' in frame.fieldOutputs), None)
            print(f"Erro no frame: {e}. Tempo válido: {frame_u.frameValue}s")
        if 'U' not in frame_u.fieldOutputs:
            for i in range(frame, -1, -1):
                frame_u = step.frames[i]
                if 'U' in frame_u.fieldOutputs:
                    print(f'Frame válido encontrado: índice {i}, Tempo: {frame_u.frameValue}s')
                    break
            else:
                print('Nenhum frame válido encontrado.')
        else:
            print(f'Frame válido - Tempo: {frame_u.frameValue}s')
    else:
        frame_u = next((frame for frame in reversed(step.frames) if 'U' in frame.fieldOutputs), None)
        print(f'Tempo: {frame_u.frameValue}s')
        
    instances = odb.rootAssembly.instances
    last_layer = max(instances.keys(), key=lambda key: max(node.coordinates[0] for node in instances[key].nodes))
    initial_coords = {node.label: node.coordinates for node in instances[last_layer].nodes}
    y_mid = (min(coord[1] for coord in initial_coords.values()) + max(coord[1] for coord in initial_coords.values())) / 2
    mid_section = {label: coords for label, coords in initial_coords.items() if abs(coords[1] - y_mid) < 1e-6}
    u_values = {v.nodeLabel: get_field_data(v) for v in frame_u.fieldOutputs['U'].getSubset(region=instances[last_layer]).values if v.nodeLabel in mid_section}

    x_center = sum(coords[0] for coords in mid_section.values()) / len(mid_section)
    z_center = sum(coords[2] for coords in mid_section.values()) / len(mid_section)

    def angle(label):
        x0, z0 = mid_section[label][0], mid_section[label][2]
        return math.atan2(z0 - z_center, x0 - x_center)

    circular_labels = sorted(mid_section.keys(), key=angle)
    ordered_mid_section = [mid_section[label] for label in circular_labels]
    ordered_u = [u_values[label] for label in circular_labels]

    # Seção indeformada, centralizada na origem
    z0 = [coords[2] - z_center for coords in ordered_mid_section]
    x0 = [coords[0] - x_center for coords in ordered_mid_section]

    # Seção deformada, em coordenadas absolutas (ainda não centralizada)
    z1_abs = [coords[2] + u[2] for coords, u in zip(ordered_mid_section, ordered_u)]
    x1_abs = [coords[0] + u[0] for coords, u in zip(ordered_mid_section, ordered_u)]

    # Centroide da seção DEFORMADA (isola a translação de corpo rígido)
    x1_center = sum(x1_abs) / len(x1_abs)
    z1_center = sum(z1_abs) / len(z1_abs)

    # Seção deformada, recentrada no seu próprio centroide
    x1 = [xi - x1_center for xi in x1_abs]
    z1 = [zi - z1_center for zi in z1_abs]

    # Raio nominal (seção inicial é circular)
    r_nominal = sum(math.hypot(xi, zi) for xi, zi in zip(x0, z0)) / len(x0)
    d_nominal = 2 * r_nominal

    # Raio deformado, agora medido a partir do centro próprio da seção deformada
    r_deformed = [math.hypot(xi, zi) for xi, zi in zip(x1, z1)]
    d_max = 2 * max(r_deformed)
    d_min = 2 * min(r_deformed)

    ovalization_index = (d_max - d_min) / d_nominal

    return [z0, x0, z1, x1, ovalization_index]

