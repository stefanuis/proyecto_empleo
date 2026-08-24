
from flask_login import current_user, login_required, login_user
from datetime import datetime
from app.extensions import db
from .forms.principal import LoginForm
from flask import Blueprint, session
from ..models.usuarios import Usuario, Permiso, Rol
import pyodbc
import hashlib
import base64
import getpass
import os
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)


class Login:
    def __init__(self):
        server_dinamica = os.getenv('SERVER_DINAMICA')
        base_dinamica = os.getenv('BASE_DINAMICA')
        uid_dinamica = os.getenv('UID_DINAMICA')
        pwd_dinamica = os.getenv('PWD_DINAMICA')

        self.conexion = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server_dinamica};"
            f"DATABASE={base_dinamica};"
            f"UID={uid_dinamica};"
            f"PWD={pwd_dinamica};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        self.usuario = ""
        self.clave = ""

    def consultar(self, usuario, tipo):

        cursor = self.conexion.cursor()

        consulta = f"""
            DECLARE @Documento VARCHAR(50) = '{usuario}'

            select

            N3.USUNOMBRE USUARIO,

            N3.USUCLAVE CLAVE,

            N3.USUDESCRI NOMBRE,

            N2.INFINFORMA as EMAIL

            from "dbo"."NOMEMPLEADO" N0

            inner join "dbo"."COMTERCERO" N1 on (N0."OID" = N1."OID")

            inner join "dbo".COMTERCEROWEB N2 on (N2."COMTERCERO" = N1."OID")

            inner join "dbo".GENUSUARIO N3 on N3.USUNOMBRE = N0."EMPCODIGO"

            where N3.USUESTADO = 1 AND N0.EMPCODIGO = @Documento
        """

        # Consulta anterior : "SELECT @@VERSION"

        cursor.execute(consulta)

        fila = cursor.fetchone()

        self.conexion.close()

        if(tipo == 1):
            return fila[1]
        else:
            return fila
        
    def codificar(self, texto: str) -> str:
        # Antiguo nombre : md5_utf16le_base64
        # 1. Convertir a UTF-16LE
        datos = texto.encode("utf-16le")

        # 2. MD5 binario
        md5_binario = hashlib.md5(datos).digest()

        # 3. Base64
        resultado = base64.b64encode(md5_binario).decode("ascii")

        return resultado
    
    def leer(self):
        print("Ingresa tu usuario")
        self.usuario = input()

        self.clave = getpass.getpass("Ingresa tu clave: ")

    def iniciar(self, usuario, clave):
        codificado = self.codificar(clave)
        consultado = self.consultar(usuario, 0)

        if(consultado == None):
            return 0

        if(codificado == consultado[1]):
            return consultado
        else:
            return 0





principal_bp = Blueprint(
    "principal",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/principal/static"
)


@principal_bp.route("/", methods=["GET", "POST"])
def inicial():

    form = LoginForm()

    misDatos = {
        "anio": 2026,
        "version": "0.01",
        "titulo": "Principal mi Usuario"
    }

    if form.validate_on_submit():

        usuario = form.usuario.data
        password = form.clave.data

        usuario_db = Usuario.query.filter_by(
            usuario=usuario
        ).first()

        if usuario_db:

            obj_login = Login()
            resultado = obj_login.iniciar(usuario, password)

            if resultado != 0:

                login_user(usuario_db)

                session["nombre"] = resultado[2]

                return redirect(url_for('principal.principal_get'))

            else:
                print("\n\nUsuario o contraseña incorrecta\n\n")
                flash(
                    "Usuario o contraseña incorrectos",
                    "warning"
                )

        else:
            print("\n\nNo se encontro el usuario\n\n")
            flash(
                "No se encuentra el usuario",
                "warning"
            )

    elif form.errors:
        print("Formulario no válido")
        print(form.errors)

    return render_template(
        "login.html",
        form=form,
        datos=misDatos
    )


@principal_bp.route("/principal", methods=["GET"])
def principal_get():
    #print("\n\nLlegamos a principal\n\n")
    elForm = LoginForm()

    usuario = current_user

    r_permisos = Permiso.query.filter_by(
        id_usuario=usuario.id
    ).all()


    #print(r_permisos)
    los_permisos = []

    for i in r_permisos:
        permisos = Rol.query.filter_by(
            id_rol=i.id_rol
        ).first()
        los_permisos.append(permisos.codigo)


    print(los_permisos)

    #print(usuario.id)
    #print(usuario.usuario)
    #print(usuario.activo)
    #print(usuario.fecha_creacion)

    misDatos = {
        "permisos": los_permisos,
        "anio": 2026,
        "version": "0.01",
        "titulo": "Principal mi Usuario"
    }
    return render_template("principal.html",form=elForm, datos=misDatos)