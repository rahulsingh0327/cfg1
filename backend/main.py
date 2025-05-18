from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ast

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

@app.post("/parse/")
def parse_code(input: CodeInput):
    code = input.code
    nodes = []
    edges = []
    id_counter = 0

    def new_node(node_type, label, x_offset=0):
        nonlocal id_counter
        node_id = str(id_counter)
        id_counter += 1
        nodes.append({
            "id": node_id,
            "type": node_type,
            "data": {"label": label},
            "position": {"x": x_offset, "y": 150 * id_counter}
        })
        return node_id

    def add_edge(source, target, label='', animated=False, source_handle=None):
        if source and target:
            edge = {
                "id": f"e{source}-{target}",
                "source": source,
                "target": target,
                "label": label,
                "animated": animated,
            }
            if source_handle:
                edge["sourceHandle"] = source_handle
            edges.append(edge)

    def handle_statements(stmts, prev_ids):
        last_ids = prev_ids[:]
        for stmt in stmts:
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                label = ast.unparse(stmt).strip()
                nid = new_node("assignment", label)
                for pid in last_ids:
                    add_edge(pid, nid)
                last_ids = [nid]

            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func = getattr(stmt.value.func, 'id', '')
                if func in ['print', 'input']:
                    label = ast.unparse(stmt).strip()
                    nid = new_node("io", label)
                    for pid in last_ids:
                        add_edge(pid, nid)
                    last_ids = [nid]

            elif isinstance(stmt, ast.If):
                label = f"if {ast.unparse(stmt.test).strip()}:"
                nid = new_node("decision", label)
                for pid in last_ids:
                    add_edge(pid, nid)

                # YES branch (default vertical)
                then_end_ids = handle_statements(stmt.body, [nid])
                for tid in then_end_ids:
                    add_edge(nid, tid, label="Yes", source_handle="yes")

                # NO branch (shifted right)
                if stmt.orelse:
                    original_new_node = new_node
                    def shifted_node(type, label): return original_new_node(type, label, x_offset=250)
                    globals()['new_node'] = shifted_node
                    else_end_ids = handle_statements(stmt.orelse, [nid])
                    globals()['new_node'] = original_new_node
                    for eid in else_end_ids:
                        add_edge(nid, eid, label="No", source_handle="no")
                    last_ids = then_end_ids + else_end_ids
                else:
                    last_ids = then_end_ids + [nid]

            elif isinstance(stmt, ast.For):
                label = f"for {ast.unparse(stmt.target)} in {ast.unparse(stmt.iter)}:"
                nid = new_node("decision", label)
                for pid in last_ids:
                    add_edge(pid, nid)

                body_end_ids = handle_statements(stmt.body, [nid])
                for bid in body_end_ids:
                    add_edge(nid, bid, label="Yes", source_handle="yes")
                    add_edge(bid, nid, label="Repeat", animated=True)
                last_ids = [nid]

            elif isinstance(stmt, ast.While):
                label = f"while {ast.unparse(stmt.test)}:"
                nid = new_node("decision", label)
                for pid in last_ids:
                    add_edge(pid, nid)

                body_end_ids = handle_statements(stmt.body, [nid])
                for bid in body_end_ids:
                    add_edge(nid, bid, label="Yes", source_handle="yes")
                    add_edge(bid, nid, label="Repeat", animated=True)
                last_ids = [nid]

        return last_ids

    tree = ast.parse(code)
    start_id = new_node("assignment", "START")
    handle_statements(tree.body, [start_id])

    return {"nodes": nodes, "edges": edges}