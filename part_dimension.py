import re

def get_part_dimensions(filepath):
    parts = {}
    current_part = None
    in_nodes = False

    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line_stripped = line.strip()

            m = re.match(r"\*Part,\s*name=(\S+)", line_stripped, re.IGNORECASE)
            if m:
                current_part = m.group(1).rstrip(",")
                parts[current_part] = {"x": [], "y": [], "z": []}
                in_nodes = False
                continue

            if re.match(r"\*End Part", line_stripped, re.IGNORECASE):
                current_part = None
                in_nodes = False
                continue

            if re.match(r"\*Node", line_stripped, re.IGNORECASE):
                in_nodes = True
                continue

            if line_stripped.startswith("*"):
                in_nodes = False
                continue

            if in_nodes and current_part:
                vals = [v.strip() for v in line_stripped.split(",")]
                if len(vals) >= 4:
                    try:
                        parts[current_part]["x"].append(float(vals[1]))
                        parts[current_part]["y"].append(float(vals[2]))
                        parts[current_part]["z"].append(float(vals[3]))
                    except ValueError:
                        pass

    results = {}
    for name, coords in parts.items():
        if coords["x"]:
            results[name] = {
                "x": (min(coords["x"]), max(coords["x"])),
                "y": (min(coords["y"]), max(coords["y"])),
                "z": (min(coords["z"]), max(coords["z"])),
                "length_x": max(coords["x"]) - min(coords["x"]),
                "length_y": max(coords["y"]) - min(coords["y"]),
                "length_z": max(coords["z"]) - min(coords["z"]),
            }
    return results