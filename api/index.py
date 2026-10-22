import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="Error de Inicialización Vercel")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def fallback(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "estado": "error",
                "mensaje": "Error cargando la aplicación en Vercel",
                "detalle": str(e)
            }
        )
