import re
import os
from pathlib import Path

def read_cpress(name, path):
    data = {}
    with open(fr'{path}\Pressão de contato - {name}.csv') as file_cpress:
        next(file_cpress)

        for line in file_cpress:
            instance, cpress = line.strip().split(',')
            instance = instance.rsplit('-', 1)[0]
            if instance not in data:
                data[instance] = []
            data[instance].append(float(cpress))
    return data

def read_rmc(name, path, end):
    file_path = fr'{path}\Momento-curvatura - {name} - {end}.csv'

    if not os.path.exists(file_path):
        return None

    props = [list(), list(), list(), list()]

    # Lendo Relação Momento-Curvatura
    file_rmc = open(file_path, 'r')
    line_list = file_rmc.readlines()
    for line in line_list[1:]:
        line_props = list(map(float, line.split(', ')))
        props[0].append(line_props[0])
        props[1].append(line_props[1])
        props[2].append(line_props[2])
        props[3].append(line_props[3])

    return props

def read_ho(name, path):
    with open(fr"{path}\History_outputs - {name}.csv") as file_ho:
        header = file_ho.readline().strip().split(', ')
        lines = file_ho.readlines()

    n_props = len(header)
    props = [[] for _ in range(n_props)]

    for line in lines:
        for p, value in zip(props, map(float, line.split(', '))):
            p.append(value)
    
    ho_dict = {h: p for h, p in zip(header, props)}
    return ho_dict

def read_curvatures(name, path):
    with open(fr"{path}\Curvatures - {name}.csv") as file_curv:
        header = file_curv.readline().strip().split(',')
        lines = file_curv.readlines()

    n_props = len(header)
    props = [[] for _ in range(n_props)]

    for line in lines:
        for p, value in zip(props, map(float, line.split(','))):
            p.append(value)
    
    path_dict = {h: p for h, p in zip(header, props)}
    return props

def read_ovalization(name, path):
    with open(fr"{path}\Ovalization - {name}.csv") as file_curv:
        first_line = file_curv.readline().strip().split(',')
        ovalization_index = float(first_line[1])

        header = file_curv.readline().strip().split(',')
        lines = file_curv.readlines()

    n_props = len(header)
    props = [[] for _ in range(n_props)]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for p, value in zip(props, map(float, line.split(','))):
            p.append(value)

    return props + [ovalization_index]

def find_inp(folder_path):
    # return str(next(Path(folder_path).glob("*.inp"), None))
    return [str(p) for p in Path(folder_path).glob("*.inp")]

def read_inp(filepath):
    path = Path(filepath)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
 
    result = {
        "job_name": None,
        "model_name": None,
        "bc_sets": [],
        "steps": [],
    }
 
    for line in lines:
        if line.strip().startswith("** Job name:"):
            m = re.search(r"\*\* Job name:\s*(\S+)\s+Model name:\s*(\S+)", line)
            if m:
                result["job_name"] = m.group(1)
                result["model_name"] = m.group(2)
            break
 
    current_step = None
    in_boundary = False
 
    for i, raw in enumerate(lines):
        line = raw.strip()
        
        # Detecta nome do step e condições de contorno
        if line.upper().startswith("*STEP"):
            m = re.search(r"name\s*=\s*([^,\n]+)", line, re.IGNORECASE)
            step_name = m.group(1).strip() if m else f"Step_{len(result['steps'])+1}"
            current_step = {"name": step_name, "loads": []}
            result["steps"].append(current_step)
            in_boundary = False
        elif line.upper().startswith("*END STEP"):
            current_step = None
            in_boundary = False
        elif line.upper().startswith("*BOUNDARY"):
            in_boundary = True
        elif in_boundary:
            if line.startswith("*") or line.startswith("**"):
                in_boundary = False
            else:
                set_name = line.split(",")[0].strip()
                if set_name and set_name not in result["bc_sets"]:
                    result["bc_sets"].append(set_name)
        if current_step is None:
            continue
 
        # Detecta carregamento
        if re.match(r"\*D[Ss]?load", line, re.IGNORECASE):
            for j in range(i + 1, min(i + 10, len(lines))):
                data = lines[j].strip()
                if data.startswith("**"):
                    continue
                if data.startswith("*"):
                    break
                parts = [p.strip() for p in data.split(",")]
                current_step["loads"].append({
                    "type": "Pressure",
                    "surface": parts[0],
                    "load_type": parts[1],
                    "magnitude": parts[2],
                })
 
        # Rotação / deslocamento: *Boundary com DOF 4-6
        if re.match(r"\*Boundary", line, re.IGNORECASE) and current_step is not None:
            for j in range(i + 1, min(i + 20, len(lines))):
                data = lines[j].strip()
                if data.startswith("**"):
                    continue
                if data.startswith("*"):
                    break
                parts = [p.strip() for p in data.split(",")]
                set_name = parts[0]
                dof_start = int(parts[1])
                dof_end = int(parts[2])
                try:
                    magnitude = float(parts[3])
                except IndexError:
                    continue

                if dof_start is not None:
                    type = _classify_dof(dof_start, dof_end)
                    current_step["loads"].append({
                        "type": type,
                        "set": set_name,
                        "dof_start": dof_start,
                        "dof_end": dof_end,
                        "magnitude": magnitude,
                    })
 
    return result
 
def read_sta(sta_file):
    import re
    with open(sta_file, "r") as f:
        conteudo = f.read()
    # Número de cores
    try:
        n_cores = int(re.search(r'with\s+(\d+)\s+processors', conteudo).group(1))
    except:
        n_cores = 1
    # Encontra todos os steps presentes no arquivo
    step_nums = sorted(set(
        int(m) for m in re.findall(r'STEP\s+(\d+)\s+ORIGIN', conteudo)
    ))
    steps_info = []
    for step_num in step_nums:
        # Início do bloco = a própria linha "STEP X ORIGIN" (não o topo do arquivo)
        pattern_inicio = rf'STEP\s+{step_num}\s+ORIGIN'
        match_inicio = re.search(pattern_inicio, conteudo)
        if not match_inicio:
            continue
        inicio = match_inicio.start()
        # Fim do bloco = início do próximo step ou fim do arquivo
        pattern_proximo = rf'STEP\s+{step_num + 1}\s+ORIGIN'
        match_proximo = re.search(pattern_proximo, conteudo[inicio:])
        fim = inicio + match_proximo.start() if match_proximo else len(conteudo)
        bloco = conteudo[inicio:fim]
        # Output frames do bloco
        frames_bloco = re.findall(
            r'Output Field Frame Number\s+(\d+),\s+of\s+(\d+)', bloco
        )
        if not frames_bloco:
            continue
        total_frames = max(int(t) for _, t in frames_bloco)
        frames_principais = [int(n) for n, t in frames_bloco if int(t) == total_frames]
        frame_atual = max(frames_principais)
        # WCT: todas as linhas de incremento do bloco (cumulativo desde o início do job)
        wcts = re.findall(
            r'^\s+\d+\s+[\d.E+\-]+\s+[\d.E+\-]+\s+(\d+:\d+:\d+)',
            bloco, re.MULTILINE
        )
        if not wcts:
            continue

        def to_horas(hms):
            h, m, s = map(int, hms.split(":"))
            return (h * 3600 + m * 60 + s) / 3600

        wct_inicio_horas = to_horas(wcts[0])   # WCT logo no início deste step
        wct_horas = to_horas(wcts[-1])         # WCT atual (cumulativo)

        steps_info.append({
            "step": step_num,
            "frame_atual": frame_atual,
            "total_frames": total_frames,
            "wct_horas": wct_horas,
            "wct_inicio_horas": wct_inicio_horas,
        })
    if not steps_info:
        raise ValueError("Nenhum step encontrado no arquivo.")

    # Progresso global (só para exibição/log)
    total_frames_global = 0
    frames_concluidos = 0
    for i, s in enumerate(steps_info):
        total_frames_global += s["total_frames"]
        if i < len(steps_info) - 1:
            frames_concluidos += s["total_frames"]
        else:
            frames_concluidos += s["frame_atual"]
    progresso_global = frames_concluidos / total_frames_global

    step_atual = steps_info[-1]
    progresso_step = step_atual["frame_atual"] / step_atual["total_frames"]
    wct_total_horas = step_atual["wct_horas"]

    # Tempo gasto exclusivamente no step atual (isola do resto do job)
    wct_step_atual = step_atual["wct_horas"] - step_atual["wct_inicio_horas"]

    if step_atual["frame_atual"] > 0 and wct_step_atual > 0:
        taxa_horas_por_frame = wct_step_atual / step_atual["frame_atual"]
        restante_horas = taxa_horas_por_frame * (step_atual["total_frames"] - step_atual["frame_atual"])
    else:
        restante_horas = float('inf')

    return n_cores, steps_info, progresso_step, progresso_global, wct_total_horas, restante_horas
 
def _classify_dof(dof_start, dof_end):
    """Classifica o tipo de BC pelo DOF."""
    dofs = set(range(dof_start, dof_end + 1))
    if dofs & {4, 5, 6}:
        return "Rotation"
    if dofs & {1, 2, 3}:
        return "Displacement"
    return "Boundary"
