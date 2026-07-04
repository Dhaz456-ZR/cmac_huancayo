from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

from decimal import Decimal
import os

from sqlalchemy.orm import joinedload

from src.database import Base, engine, SessionLocal
from src.models import Usuario, Cuenta, Credito, Movimiento, Transferencia, Pago
from src.security import hash_password, verify_password


load_dotenv()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Middleware de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "clave_secreta_temporal_para_desarrollo")
)

# Archivos estáticos
app.mount("/css", StaticFiles(directory="src/css"), name="css")
app.mount("/js", StaticFiles(directory="src/js"), name="js")
app.mount("/img", StaticFiles(directory="src/img"), name="img")
app.mount("/videos", StaticFiles(directory="src/videos"), name="videos")

templates = Jinja2Templates(directory="src/html")


def get_usuario_logueado(request: Request):
    """Obtiene el usuario actual de la sesión"""
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return None

    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    db.close()

    return usuario


def get_dashboard_data(usuario):
    """Obtiene todos los datos del dashboard para un usuario"""
    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    credito = db.query(Credito).filter(
        Credito.usuario_id == usuario.id
    ).order_by(Credito.fecha_creacion.desc()).first()

    creditos = db.query(Credito).filter(
        Credito.usuario_id == usuario.id
    ).order_by(Credito.fecha_creacion.desc()).limit(5).all()

    movimientos = db.query(Movimiento).filter(
        Movimiento.usuario_id == usuario.id
    ).order_by(Movimiento.fecha.desc()).limit(5).all()

    transferencias = db.query(Transferencia).filter(
        Transferencia.usuario_id == usuario.id
    ).order_by(Transferencia.fecha.desc()).limit(5).all()

    pagos = db.query(Pago).filter(
        Pago.usuario_id == usuario.id
    ).order_by(Pago.fecha.desc()).limit(5).all()

    context = {
        "nombre": usuario.nombre,
        "dni": usuario.dni,
        "tarjeta": usuario.tarjeta,
        "estado": usuario.estado,
        "cuenta": cuenta,
        "credito": credito,
        "creditos": creditos,
        "movimientos": movimientos,
        "transferencias": transferencias,
        "pagos": pagos,
        "error": None,
        "success": None
    }

    db.close()
    return context


# ==========================================
# PÁGINAS
# ==========================================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/index", response_class=HTMLResponse)
def index_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=get_dashboard_data(usuario)
    )


@app.get("/mis-cuentas", response_class=HTMLResponse)
def mis_cuentas_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="mis_cuentas.html",
        context=get_dashboard_data(usuario)
    )


@app.get("/transferencias", response_class=HTMLResponse)
def transferencias_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="transferencias.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/transferencias", response_class=HTMLResponse)
def realizar_transferencia(
    request: Request,
    cuenta_destino: str = Form(...),
    destinatario: str = Form(...),
    monto: str = Form(...),
    motivo: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    try:
        monto_decimal = Decimal(monto)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto ingresado no es válido."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if not cuenta:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "No tienes una cuenta registrada."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if cuenta.saldo < monto_decimal:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "Saldo insuficiente para realizar la transferencia."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    nueva_transferencia = Transferencia(
        usuario_id=usuario.id,
        cuenta_destino=cuenta_destino,
        destinatario=destinatario,
        monto=monto_decimal,
        motivo=motivo
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Transferencia enviada a " + destinatario,
        monto=monto_decimal,
        tipo="salida"
    )

    cuenta.saldo = cuenta.saldo - monto_decimal

    db.add(nueva_transferencia)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/transferencias", status_code=303)


@app.get("/creditos", response_class=HTMLResponse)
def creditos_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="creditos.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/creditos", response_class=HTMLResponse)
def solicitar_credito(
    request: Request,
    tipo_credito: str = Form(...),
    monto_total: str = Form(...),
    cuotas_totales: int = Form(...),
    cuota_mensual: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    db = SessionLocal()

    try:
        monto_decimal = Decimal(monto_total)
        cuota_decimal = Decimal(cuota_mensual)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto o la cuota ingresada no es válida."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto solicitado debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    if cuotas_totales <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El número de meses debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    nuevo_credito = Credito(
        usuario_id=usuario.id,
        tipo_credito=tipo_credito,
        monto_total=monto_decimal,
        cuota_mensual=cuota_decimal,
        cuotas_totales=cuotas_totales,
        cuotas_pagadas=0,
        estado="Pendiente"
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Solicitud de crédito: " + tipo_credito,
        monto=monto_decimal,
        tipo="entrada"
    )

    db.add(nuevo_credito)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/creditos", status_code=303)


@app.get("/pagos", response_class=HTMLResponse)
def pagos_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="pagos.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/pagos", response_class=HTMLResponse)
def realizar_pago(
    request: Request,
    servicio: str = Form(...),
    codigo_cliente: str = Form(...),
    monto: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    try:
        monto_decimal = Decimal(monto)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto ingresado no es válido."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if not cuenta:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "No tienes una cuenta registrada."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if cuenta.saldo < monto_decimal:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "Saldo insuficiente para realizar el pago."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    nuevo_pago = Pago(
        usuario_id=usuario.id,
        servicio=servicio,
        codigo_cliente=codigo_cliente,
        monto=monto_decimal
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Pago de servicio: " + servicio,
        monto=monto_decimal,
        tipo="salida"
    )

    cuenta.saldo = cuenta.saldo - monto_decimal

    db.add(nuevo_pago)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/pagos", status_code=303)


@app.get("/core-creditos", response_class=HTMLResponse)
def core_creditos_page(request: Request):
    db = SessionLocal()

    creditos = db.query(Credito).options(
        joinedload(Credito.usuario)
    ).order_by(Credito.fecha_creacion.desc()).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="core_creditos.html",
        context={"creditos": creditos}
    )


@app.post("/core-creditos/{credito_id}/aprobar")
def aprobar_credito(credito_id: int):
    db = SessionLocal()
    credito = db.query(Credito).filter(Credito.id == credito_id).first()
    if credito:
        credito.estado = "Aprobado"
        db.commit()
    db.close()
    return RedirectResponse(url="/core-creditos", status_code=303)


@app.post("/core-creditos/{credito_id}/rechazar")
def rechazar_credito(credito_id: int):
    db = SessionLocal()
    credito = db.query(Credito).filter(Credito.id == credito_id).first()
    if credito:
        credito.estado = "Rechazado"
        db.commit()
    db.close()
    return RedirectResponse(url="/core-creditos", status_code=303)


@app.post("/core-creditos/{credito_id}/desembolsar")
def desembolsar_credito(credito_id: int):
    db = SessionLocal()

    credito = db.query(Credito).filter(Credito.id == credito_id).first()

    if credito and credito.estado == "Aprobado":
        cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == credito.usuario_id).first()

        if cuenta:
            cuenta.saldo = cuenta.saldo + credito.monto_total
            credito.estado = "Desembolsado"

            movimiento = Movimiento(
                usuario_id=credito.usuario_id,
                descripcion="Desembolso de crédito: " + credito.tipo_credito,
                monto=credito.monto_total,
                tipo="entrada"
            )

            db.add(movimiento)
            db.commit()

    db.close()
    return RedirectResponse(url="/core-creditos", status_code=303)


@app.get("/perfil", response_class=HTMLResponse)
def perfil_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=get_dashboard_data(usuario)
    )


# ==========================================
# REGISTRO (SIN CORREO)
# ==========================================

@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    tarjeta: str = Form(...),
    password: str = Form(...),
    pin1: str = Form(...),
    pin2: str = Form(...),
    pin3: str = Form(...),
    pin4: str = Form(...)
):
    db = SessionLocal()

    # Verificar si el DNI ya existe
    existing_user_dni = db.query(Usuario).filter(Usuario.dni == dni).first()
    if existing_user_dni:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "El DNI ya está registrado"}
        )

    # Verificar si la tarjeta ya existe
    existing_user_tarjeta = db.query(Usuario).filter(Usuario.tarjeta == tarjeta).first()
    if existing_user_tarjeta:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "El número de tarjeta ya está registrado"}
        )

    codigo_seguridad = pin1 + pin2 + pin3 + pin4

    try:
        nuevo_usuario = Usuario(
            nombre=nombre,
            dni=dni,
            tarjeta=tarjeta,
            password=hash_password(password),
            codigo_seguridad=codigo_seguridad,
            estado="Verificado"
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        # Crear cuenta asociada
        nueva_cuenta = Cuenta(
            usuario_id=nuevo_usuario.id,
            numero_cuenta="001-" + tarjeta[-4:] + "-" + dni,
            tipo_cuenta="Cuenta de Ahorros",
            saldo=Decimal("12450.90")
        )
        db.add(nueva_cuenta)

        # Crear crédito inicial
        nuevo_credito = Credito(
            usuario_id=nuevo_usuario.id,
            tipo_credito="Préstamo Personal",
            monto_total=Decimal("4800.00"),
            cuota_mensual=Decimal("420.00"),
            cuotas_totales=12,
            cuotas_pagadas=8,
            estado="Al día"
        )
        db.add(nuevo_credito)

        # Crear movimientos iniciales
        movimientos = [
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Depósito recibido",
                monto=Decimal("850.00"),
                tipo="entrada"
            ),
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Pago de servicio",
                monto=Decimal("120.00"),
                tipo="salida"
            ),
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Transferencia enviada",
                monto=Decimal("300.00"),
                tipo="salida"
            )
        ]
        for m in movimientos:
            db.add(m)

        db.commit()
        db.close()

        # Redirigir al login
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        db.rollback()
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": f"Error al registrar: {str(e)}"}
        )


# ==========================================
# LOGIN (SIN CORREO)
# ==========================================

@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    dni: str = Form(...),
    tarjeta: str = Form(...),
    password: str = Form(...),
    codigo_seguridad: str = Form(...)
):
    db = SessionLocal()

    usuario = db.query(Usuario).filter(
        Usuario.dni == dni,
        Usuario.tarjeta == tarjeta
    ).first()

    if not usuario:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "DNI o tarjeta incorrectos"}
        )

    if not verify_password(password, usuario.password):
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Contraseña incorrecta"}
        )

    if usuario.codigo_seguridad != codigo_seguridad:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "PIN incorrecto"}
        )

    request.session["usuario_id"] = usuario.id
    request.session["nombre"] = usuario.nombre

    db.close()

    return RedirectResponse(url="/index", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete-user")
def delete_user(dni: str = Form(...)):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.dni == dni).first()

    if not usuario:
        db.close()
        return {"mensaje": "Usuario no encontrado"}

    db.delete(usuario)
    db.commit()
    db.close()

    return {"mensaje": f"Usuario con DNI {dni} eliminado"}


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    db = SessionLocal()

    usuarios = db.query(Usuario).all()
    creditos = db.query(Credito).all()
    transferencias = db.query(Transferencia).all()
    pagos = db.query(Pago).all()
    movimientos = db.query(Movimiento).order_by(Movimiento.fecha.desc()).limit(10).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "usuarios": usuarios,
            "creditos": creditos,
            "transferencias": transferencias,
            "pagos": pagos,
            "movimientos": movimientos
        }
    )
