from models import crear_tablas_usuario

def init_app(app):
    crear_tablas_usuario()