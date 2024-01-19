import os
import sys
from dataclasses import dataclass, field
from typing import List
from code_to_mermaid import write_mermaid_file


@dataclass
class Node:
    path: str
    imports: List["str"] = field(default_factory=list)
    subnodes: List["Node"] = field(default_factory=list)
    external_libraries: List["str"] = field(default_factory=list)


def find_main_files(directory):
    main_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                with open(file_path, "r") as f:
                    for line in f:
                        if 'if __name__ == "__main__":' in line:
                            main_files.append(file_path)
                            break
    return main_files


def find_import(node, directory, import_str):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                with open(file_path, "r") as f:
                    for line in f:
                        if (
                            line.startswith(f"def {import_str}")
                            or line.startswith(f"class {import_str}")
                            or line.startswith(import_str)
                        ):
                            node.subnodes.append(Node(file_path))
                            break


def find_subnodes(node, project):
    with open(node.path, "r") as f:
        found = 0
        import_path = ""
        target_import = ""
        for line in f:
            if found == 2:
                if line.find(")") != -1:
                    found = 0
                    continue
                target_import = line.lstrip().split(",")[0]
                node.imports.append(target_import)
                find_import(node, import_path, target_import)
            if line.startswith(f"from {project}") or line.startswith("from ."):
                found = 1
                import_path = line.split(" ")[1].replace(".", "/")
                target_import = line.split(" ")[3].removesuffix("\n")
                if target_import == "(":
                    found = 2
            elif line.startswith("from "):
                node.external_libraries.append(line.split(" ")[1].split(".")[0])
            if found == 1:
                words = line.split(" ")
                if len(words) > 4:
                    for i in range(len(words)):
                        node.imports.append(target_import)
                        find_import(node, import_path, target_import)
                else:
                    node.imports.append(target_import)
                    find_import(node, import_path, target_import)
                found = 0
    if len(node.subnodes) > 0:
        for n in node.subnodes:
            find_subnodes(n, project)


if __name__ == "__main__":
    root_dir = sys.argv[1]
    entry_nodes = [Node(node) for node in find_main_files(root_dir)]
    for node in entry_nodes:
        find_subnodes(node, root_dir)
        write_mermaid_file([node], root_dir)
