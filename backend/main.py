from fastapi import FastAPI
from pydantic import BaseModel
import ast
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

class CodeModel(BaseModel):
    code: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FlowchartParser:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.id_counter = 0
        self.next_y = 0
        # Spacing for node placement
        self.X_SPACING = 100
        self.Y_SPACING = 100
        self.X_OFFSET = 0  # Additional offset for nested if-else

    def new_node(self, node_type: str, label: str, indent: int):
        """Create a new node with a unique ID and set its position."""
        self.id_counter += 1
        node_id = self.id_counter
        x = indent * self.X_SPACING + self.X_OFFSET
        y = self.next_y
        self.next_y += self.Y_SPACING
        node = {"id": node_id, "type": node_type, "label": label, "x": x, "y": y}
        node['data'] = {"label": label}
        node['position'] = {"x": x, "y": y}
        node['data']['x'] = x
        node['data']['y'] = y
        self.nodes.append(node)
        return node

    def add_edge(self, source: int, target: int, label: str = "", animated: bool = False):
        """Add an edge between source and target node IDs."""
        edge = {"source": source, "target": target}
        if label:
            edge["label"] = label
        else:
            edge["label"] = ""
        edge["animated"] = animated
        edge['id'] = f"e{source}-{target}"
        # if the label is "False", then put the target node into 
        self.edges.append(edge)

    def parse(self, code: str):
        self.nodes = []
        self.edges = []
        self.id_counter = 0
        self.next_y = 0
        self.X_OFFSET = 0
        tree = ast.parse(code)
        self._parse_statements(tree.body, indent=0, prev_tails=[])
        for edge in self.edges:
            if "label" not in edge:
                src_node = next((n for n in self.nodes if n["id"] == edge["source"]), None)
                if src_node and src_node["type"] == "decision":
                    edge["label"] = "False"
        return {"nodes": self.nodes, "edges": self.edges}

    def _parse_statements(self, stmts, indent: int, prev_tails):
        tails = prev_tails
        for stmt in stmts:
            tails = self._parse_statement(stmt, indent, tails)
        return tails

    def _parse_statement(self, stmt, indent: int, prev_tails):
        if isinstance(stmt, (ast.Assign, ast.AugAssign)):
            label = ast.unparse(stmt)
            node = self.new_node("assignment", label, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])
            return [node["id"]]

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id in ("print", "input"):
                label = ast.unparse(stmt)
                node = self.new_node("io", label, indent)
            else:
                label = ast.unparse(stmt)
                node = self.new_node("assignment", label, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])
            return [node["id"]]

        if isinstance(stmt, ast.If):
            label = f"if {ast.unparse(stmt.test)}"
            node = self.new_node("decision", label, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])

            self.X_OFFSET += 100  # Increase horizontal offset for nested blocks

            # True branch
            body_tails = []
            if stmt.body:
                first_body = stmt.body[0]
                body_tails = self._parse_statement(first_body, indent+1, [node["id"]])
                for s in stmt.body[1:]:
                    body_tails = self._parse_statement(s, indent+1, body_tails)

            # False branch
            else_tails = []
            if stmt.orelse:
                first_else = stmt.orelse[0]
                else_tails = self._parse_statement(first_else, indent+1, [node["id"]])
                for s in stmt.orelse[1:]:
                    else_tails = self._parse_statement(s, indent+1, else_tails)
            else:
                else_tails = [node["id"]]

            # Label edges properly now that they exist
            for edge in self.edges:
                if edge["source"] == node["id"]:
                    if edge["target"] in body_tails:
                        edge["label"] = "True"
                    elif edge["target"] in else_tails:
                        edge["label"] = "False"

            self.X_OFFSET -= 100  # Restore offset

            return list(dict.fromkeys(body_tails + else_tails))


        if isinstance(stmt, ast.For):
            label = f"for {ast.unparse(stmt.target)} in {ast.unparse(stmt.iter)}"
            node = self.new_node("decision", label, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])
            body_tails = []
            if stmt.body:
                first_body = stmt.body[0]
                body_tails = self._parse_statement(first_body, indent+1, [node["id"]])
                for edge in self.edges:
                    if edge["source"] == node["id"] and edge["target"] == body_tails[0]:
                        edge["label"] = "True"
                for s in stmt.body[1:]:
                    body_tails = self._parse_statement(s, indent+1, body_tails)
                for t in body_tails:
                    self.add_edge(t, node["id"])
            else:
                body_tails = []
            else_tails = []
            if stmt.orelse:
                first_else = stmt.orelse[0]
                else_tails = self._parse_statement(first_else, indent+1, [node["id"]])
                for edge in self.edges:
                    if edge["source"] == node["id"] and edge["target"] == else_tails[0]:
                        edge["label"] = "False"
                for s in stmt.orelse[1:]:
                    else_tails = self._parse_statement(s, indent+1, else_tails)
            else:
                else_tails = [node["id"]]
            return list(dict.fromkeys(body_tails + else_tails))

        if isinstance(stmt, ast.While):
            label = f"while {ast.unparse(stmt.test)}"
            node = self.new_node("decision", label, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])
            body_tails = []
            if stmt.body:
                first_body = stmt.body[0]
                body_tails = self._parse_statement(first_body, indent+1, [node["id"]])
                for edge in self.edges:
                    if edge["source"] == node["id"] and edge["target"] == body_tails[0]:
                        edge["label"] = "True"
                for s in stmt.body[1:]:
                    body_tails = self._parse_statement(s, indent+1, body_tails)
                for t in body_tails:
                    self.add_edge(t, node["id"])
            else:
                body_tails = []
            else_tails = []
            if stmt.orelse:
                first_else = stmt.orelse[0]
                else_tails = self._parse_statement(first_else, indent+1, [node["id"]])
                for edge in self.edges:
                    if edge["source"] == node["id"] and edge["target"] == else_tails[0]:
                        edge["label"] = "False"
                for s in stmt.orelse[1:]:
                    else_tails = self._parse_statement(s, indent+1, else_tails)
            else:
                else_tails = [node["id"]]
            return list(dict.fromkeys(body_tails + else_tails))

        if isinstance(stmt, ast.FunctionDef):
            node = self.new_node("connector", stmt.name, indent)
            for tail in prev_tails:
                self.add_edge(tail, node["id"])
            if stmt.body:
                first_stmt = stmt.body[0]
                body_tails = self._parse_statement(first_stmt, indent+1, [node["id"]])
                for s in stmt.body[1:]:
                    body_tails = self._parse_statement(s, indent+1, body_tails)
            return [node["id"]]

        try:
            label = ast.unparse(stmt)
        except Exception:
            label = ""
        node = self.new_node("assignment", label, indent)
        for tail in prev_tails:
            self.add_edge(tail, node["id"])
        return [node["id"]]

@app.post("/parse/")
def parse_endpoint(data: CodeModel):
    parser = FlowchartParser()
    result = parser.parse(data.code)
    for node in result['nodes']:
        node['id'] = str(node['id'])
    for edge in result['edges']:
        edge['source'] = str(edge['source'])
        edge['target'] = str(edge['target'])
    # if the edge have label of "false" then put the node into negative x
    for edge in result['edges']:
        if edge.get('label') == "False":
            print(f"Reversing edge {edge['id']} with label 'False'")
            for n in range(len(result['nodes'])):
                if result['nodes'][n]['id'] == edge['target']:
                    result['nodes'][n]['position']['x'] *= -1
                    result['nodes'][n]['data']['x'] *= -1
                    result['nodes'][n]['x'] *= -1
                    print(f"Node {result['nodes'][n]['id']} moved to negative x position")

    ast_tree = ast.parse(data.code)
    ast_string = ast.dump(ast_tree, indent=2)

    return {
        **result,
        "ast": ast_string,
    }