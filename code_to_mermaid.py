import os
import distutils.sysconfig as sysconfig
from pathlib import Path

python_version = float(sysconfig.get_python_version())

std_lib_path = Path(sysconfig.get_python_lib(standard_lib=True))
std_lib_glob = std_lib_path.glob("*")
std_lib = set()

for mod in std_lib_glob:
    if mod.stem.startswith("_") or mod.stem == "LICENSE":
        continue
    if mod.suffix == ".py" and mod.parent == std_lib_path:
        std_lib.add(mod.stem)
    elif mod.is_dir() and mod.parent == std_lib_path:
        std_lib.add(mod.stem)


def remove_substr(string, str_list=[" ", "(", ")", "[", "]"]):
    result = string
    for substr in str_list:
        result = result.replace(substr, "")
    return result


def write_mermaid_file(nodes, root_dir):
    diagram_text = '::: mermaid\n%%{\n\tinit: {\n\t\t"flowchart":{\n\t\t\t"useMaxWidth": 0\n\t\t}\n\t}\n}%%\nflowchart TD;\n'
    diagram_text += "\tclassDef ep fill:#733,color:#fff,stroke:#fff,stroke-width:4px\n"
    diagram_text += "\tclassDef im fill:#373,color:#fff,stroke:#fff\n"
    diagram_text += (
        "\tclassDef lib fill:#337,color:#fff,stroke:#fff,stroke-dasharray: 5 5\n"
    )
    for node in nodes:
        diagram_text += f"\t{remove_substr(node.path.split(root_dir)[1])}([{remove_substr(node.path.split(root_dir)[1])}]):::ep\n"
        diagram_text = write_diagram(diagram_text, node, root_dir, len(node.subnodes))
    if os.path.exists(
        ("diagram_" + nodes[0].path.split("/")[-1]).split(".")[0] + ".md"
    ):
        os.remove(("diagram_" + nodes[0].path.split("/")[-1]).split(".")[0] + ".md")
    with open(
        ("diagram_" + nodes[0].path.split("/")[-1]).split(".")[0] + ".md", "w"
    ) as f:
        f.write(diagram_text + ":::")


def write_diagram(text: str, node, root, arr_len):
    consts = ""
    imports = ""
    libs = ""
    if arr_len > 2:
        for i in range(arr_len - 2):
            consts += "."
            imports += "="
            libs += "-"
    t = ""
    for i in range(len(node.subnodes)):
        if node.imports[i].isupper():
            t += node.imports[i].replace(" ", "") + "<br>"
        else:
            if t != "":
                import_text = f' -. <p style="font-size:10px">{t[:-4]}</p> {consts}..- '
                t = f"\t{remove_substr(node.path.split(root)[1])}{import_text}{remove_substr(node.subnodes[i].path.split(root)[1])}:::im\n"
                if text.find(t) == -1:
                    text += t
                    text = write_diagram(text, node.subnodes[i], root, arr_len)
                t = ""
            import_text = f' == {node.imports[i].replace(" ", "")} {imports}==> '
            tmp_txt = f"\t{remove_substr(node.path.split(root)[1])}{import_text}{remove_substr(node.subnodes[i].path.split(root)[1])}:::im\n"
            if text.find(tmp_txt) == -1:
                text += tmp_txt
                text = write_diagram(text, node.subnodes[i], root, arr_len)

    # for lib in node.external_libraries:
    #     if lib in std_lib:
    #         continue
    #     t = f'\t{lib}(({lib})):::lib\n'
    #     if text.find(t) == -1:
    #         text += t
    #     t = f'\t{remove_substr(node.path.split(root)[1])} {libs}--o {lib}\n'
    #     if text.find(t) == -1:
    #         text += t

    return text
