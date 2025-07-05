def format_config_dict(name: str, config: dict) -> str:
    lines = [f"{name} = {{"]
    for k, v in config.items():
        if isinstance(v, (int, float)) and v != 0:
            lines.append(f"    {k!r}: {v},")
    lines.append("}")
    return "\n".join(lines)

def format_config_diff(s1: dict, s2: dict) -> str:
    diff = {}
    for k in s1:
        if s1.get(k, 0) != s2.get(k, 0):
            if s1.get(k, 0) != 0 or s2.get(k, 0) != 0:
                diff[k] = (s1.get(k, 0), s2.get(k, 0))
    lines = ["DIFF = {"]
    for k, (v1, v2) in diff.items():
        lines.append(f"    {k!r}: ({v1}, {v2}),")
    lines.append("}")
    return "\n".join(lines)

def copy_s1_to_s2(*values):
    mid = len(values) // 2
    s1_values = values[:mid]
    return s1_values
