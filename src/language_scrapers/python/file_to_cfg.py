import json
import types
import argparse
from typing import Any
from bytecode import Bytecode, ControlFlowGraph, BasicBlock

parser = argparse.ArgumentParser(description="CppApp")
parser.add_argument("--filepath", type=str, help="Path to the file will be processed")

args = parser.parse_args()
FILEPATH = args.filepath

def get_cfg_dict(blocks: ControlFlowGraph) -> dict[str, list[str]]:
    cfg_graph: dict[str, list[str]] = {}

    for block in blocks:
        block_index = blocks.get_block_index(block)
        block_id = f"B{block_index}"
        cfg_graph[block_id] = []

        for instr in block:
            outgoing_blocks = []

            if hasattr(instr, "arg") and isinstance(instr.arg, BasicBlock):
                outgoing_blocks.append(instr.arg)

            if hasattr(instr, "target") and isinstance(instr.target, BasicBlock):
                outgoing_blocks.append(instr.target)

            if hasattr(instr, "handlers") and isinstance(instr.handlers, list):
                for handler_block in instr.handlers:
                    if isinstance(handler_block, BasicBlock):
                        outgoing_blocks.append(handler_block)

            for out_block in outgoing_blocks:
                out_block_index = blocks.get_block_index(out_block)
                outgoing_block_id = f"B{out_block_index}"
                if outgoing_block_id not in cfg_graph[block_id]:
                    cfg_graph[block_id].append(outgoing_block_id)

        if block.next_block is not None:
            next_block_index = blocks.get_block_index(block.next_block)
            next_block_id = f"B{next_block_index}"
            if next_block_id not in cfg_graph[block_id]:
                cfg_graph[block_id].append(next_block_id)

    return cfg_graph

def extract_code_objects_with_context(code_obj: types.CodeType, parent_name: str = "") -> list[dict[str, Any]]:
    objects = []
    qualified_name = f"{parent_name}.{code_obj.co_name}" if parent_name else code_obj.co_name
    objects.append({"name": qualified_name, "code": code_obj})

    for const in code_obj.co_consts:
        if isinstance(const, types.CodeType):
            objects.extend(extract_code_objects_with_context(const, parent_name=qualified_name))
    return objects

def parse_cfg_to_graphs(
    module_code: types.CodeType,
):
    graphs = {
        "filepath": FILEPATH,
        "graphs": [],
    }

    all_code_objects = extract_code_objects_with_context(module_code)
    for obj in all_code_objects:
        code_obj = obj["code"]

        if code_obj.co_name != "<module>":
            name = obj["name"].replace("<module>.", "")
            bytecode = Bytecode.from_code(code_obj)
            cfg = ControlFlowGraph.from_bytecode(bytecode)
            graph = get_cfg_dict(cfg)
            if len(graph) > 1:
                current_graph = {"name": name,
                                 "graph_dict": graph}
                
                graphs["graphs"].append(current_graph)

    return graphs

with open(FILEPATH, "r", encoding="utf-8") as f:
    source = f.read()

module_code = compile(source, FILEPATH, "exec")
print(json.dumps(parse_cfg_to_graphs(module_code)))
