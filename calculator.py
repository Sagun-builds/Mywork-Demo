from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import ast
import math

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class CalcRequest(BaseModel):
    expression: str

class CalcResponse(BaseModel):
    result: float

@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as html_file:
        return html_file.read()

@app.post("/api/calc", response_model=CalcResponse)
def calculate(request: CalcRequest):
    try:
        node = ast.parse(request.expression, mode="eval")
    except SyntaxError:
        raise HTTPException(status_code=400, detail="Invalid expression")

    allowed_nodes = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.FloorDiv,
        ast.LShift,
        ast.RShift,
        ast.BitAnd,
        ast.BitOr,
        ast.BitXor,
        ast.MatMult,
    }

    for node_item in ast.walk(node):
        if isinstance(node_item, ast.Call):
            raise HTTPException(status_code=400, detail="Function calls are not allowed")
        if type(node_item) not in allowed_nodes:
            raise HTTPException(status_code=400, detail="Unsupported operation")

    try:
        result = eval(compile(node, filename="<ast>", mode="eval"), {"__builtins__": {}}, {})
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to evaluate expression")

    try:
        result = float(result)
    except (OverflowError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Result is too large to represent")

    if not math.isfinite(result):
        raise HTTPException(status_code=400, detail="Result is infinity or NaN")

    return {"result": result}