import json
from pathlib import Path


class GestorJSON:
    def __init__(self, archivo):
        # Las rutas se calculan desde la carpeta del proyecto.
        self.ruta = Path(__file__).resolve().parent.parent / 'data' / archivo
        self.ruta.parent.mkdir(exist_ok=True)

    def leer(self):
        if not self.ruta.exists():
            return []
        try:
            with self.ruta.open('r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def guardar(self, datos):
        try:
            with self.ruta.open('w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (OSError, TypeError):
            return False
