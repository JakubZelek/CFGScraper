import os
import json
import subprocess
import shlex
import argparse

parser = argparse.ArgumentParser(description="CppApp")
parser.add_argument("--filepath", type=str, help="Path to the file will be processed")
parser.add_argument(
    "--compile-commands",
    type=str,
    required=True,
    help="Path to compile_commands.json",
)

args = parser.parse_args()
FILEPATH = args.filepath
COMPILE_COMMANDS_PATH = args.compile_commands

def find_compile_command(compile_commands, filepath):
    for entry in compile_commands:
        if os.path.normpath(entry["file"]) == os.path.normpath(filepath):
            return entry["command"]
    return None


def get_raw_cfg(filepath: str, compile_commands: list[dict]) -> list[str]:
    command_line = find_compile_command(compile_commands, filepath)

    if not command_line:
        return []

    original_cmd_args = shlex.split(command_line)
    cmd = [
        "clang++",
        "-Xclang",
        "-analyze",
        "-Xclang",
        "-analyzer-checker=debug.DumpCFG",
        "-fsyntax-only",
    ] + original_cmd_args[1:]

    lines = []

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        lines.append(line)
    process.wait()

    return lines


def replace_keys(current_graph: dict, current_key: str, value: str) -> str:
    current_key = current_key.upper()
    if f"({value})" in current_key:
        current_key = current_key.replace(f"({value})", "")
        current_key = current_key.strip()

        if current_key not in current_graph.get(value, {}):
            current_graph.setdefault(value, []).append(current_key)
    return current_key

def migrate_other_info_to_separate_field(current_graph: dict) -> dict:
    other_info = {}
    for key, value in current_graph.items():
        if key not in ["name", "graph_dict"]:
            other_info[key] = value
    current_graph["other_graph_info"] = other_info
    return current_graph

def parse_cfg_to_graphs(lines: list[str]):
    graphs = {
        "filepath": FILEPATH,
        "graphs": [],
    }
    header = None
    current_graph = {}

    for line in lines:
        if line and line[0].isalpha():
            if header and current_graph:
                current_graph = migrate_other_info_to_separate_field(current_graph)
                graphs["graphs"].append(current_graph)
            
            header = line.replace("\n", "")
            current_graph = {}
            continue

        if line.startswith(" [B"):
            current_graph["name"] = header
            current_graph.setdefault("graph_dict", {})

            current_key = line.split("[")[1].split("]")[0]
            current_key = replace_keys(current_graph, current_key, value="NORETURN")
            current_key = replace_keys(current_graph, current_key, value="ENTRY")
            current_key = replace_keys(current_graph, current_key, value="EXIT")

            current_graph["graph_dict"].setdefault(current_key, [])
            continue

        if line.strip().startswith("Succs"):
            succ = line.split(":")[1].split()
            nodes = []
            for node in succ:
                node = node.upper().strip()

                if "(UNREACHABLE)" in node:
                    node = node.replace("(UNREACHABLE)", "")
                    current_graph.setdefault("UNREACHABLE", []).append(
                        {current_key: node}
                    )
                if "NULL" in node:
                    node = node.replace("NULL", "")
                    current_graph.setdefault("NULL", []).append(current_key)

                if node not in current_graph["graph_dict"][current_key] and node != "":
                    nodes.append(node)

            current_graph["graph_dict"][current_key].extend(nodes)
            continue

    if current_graph:
        current_graph = migrate_other_info_to_separate_field(current_graph)
        graphs["graphs"].append(current_graph)

    return graphs


with open(COMPILE_COMMANDS_PATH, "r", encoding="utf-8") as f:
    compile_commands = json.load(f)

lines = get_raw_cfg(FILEPATH, compile_commands)
result = parse_cfg_to_graphs(lines)
print(json.dumps(result))
