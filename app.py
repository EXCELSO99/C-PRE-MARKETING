import os
import json
import re
import math
import hashlib
from datetime import datetime
from urllib.parse import quote_plus
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# ==============================================================================
# 01. CONFIGURACION DE SERVIDOR Y PERSISTENCIA (PARTE 1)
# ==============================================================================
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
ARCHIVO_DB = os.environ.get("CPRE_MKT_PART1_DB", "cpre_marketing_parte1_db.json")
NOMBRE_APP = "C-Pre Marketing"
CREADOR_APP = "Creaciones Celso"
VERSION_APP = "10.1-P1"

PALETA_VISUAL = {
    "negro_fondo": "#090a0d",
    "negro_panel": "#12141a",
    "negro_tarjeta": "#181b23",
    "negro_campo": "#0d0f14",
    "dorado": "#d4af37",
    "dorado_brillo": "#f2d379",
    "plateado": "#cbd5e1",
    "plateado_borde": "#64748b",
    "texto_claro": "#f8fafc",
}

AJUSTES_PRIVACIDAD_BASE = [
    {
        "clave": "acceso_gratuito_abierto",
        "titulo": "01. Acceso gratuito sin cobros",
        "descripcion": "Uso libre de la aplicacion sin tarifas ocultas ni bloqueos externos.",
        "activo": True,
    },
    {
        "clave": "proteccion_clave_cuenta",
        "titulo": "02. Clave personal por cuenta",
        "descripcion": "Cada cuenta se asocia a correo, usuario y clave personal para resguardar su espacio.",
        "activo": True,
    },
    {
        "clave": "separacion_datos_perfil",
        "titulo": "03. Separacion de datos por usuario",
        "descripcion": "Mantiene separadas las notas, lanzamientos y registros de cada cuenta.",
        "activo": True,
    },
    {
        "clave": "guardado_en_servidor",
        "titulo": "04. Guardado persistente del progreso",
        "descripcion": "Guarda tus cambios en el archivo de datos del servidor para recuperarlos luego.",
        "activo": True,
    },
    {
        "clave": "sin_rastreo_terceros",
        "titulo": "05. Sin rastreadores publicitarios externos",
        "descripcion": "No incluye scripts de seguimiento publicitario de terceros en la pagina.",
        "activo": True,
    },
    {
        "clave": "correo_en_cabecera",
        "titulo": "06. Correo visible en la barra superior",
        "descripcion": "Muestra el correo de la cuenta activa en la cabecera de la aplicacion.",
        "activo": True,
    },
    {
        "clave": "copia_rapida_enlaces_copy",
        "titulo": "07. Copia directa de textos y enlaces",
        "descripcion": "Permite copiar guiones, ofertas y enlaces de grupos con un toque.",
        "activo": True,
    },
    {
        "clave": "figuras_geometricas_activas",
        "titulo": "08. Figuras geometricas con cambio de color",
        "descripcion": "Activa figuras geometricas en movimiento cambiando entre tonos dorados y plateados.",
        "activo": True,
    },
    {
        "clave": "confirmacion_lanzamientos",
        "titulo": "09. Validacion al lanzar productos",
        "descripcion": "Verifica datos obligatorios antes de publicar un producto en el catalogo.",
        "activo": True,
    },
    {
        "clave": "mensajes_estado_claros",
        "titulo": "10. Notificaciones de estado",
        "descripcion": "Informa claramente cuando se guarda, carga, busca o lanza un registro.",
        "activo": True,
    },
]

INFO_APLICACION = {
    "para_que_sirve": (
        "Sirve para buscar productos o servicios, lanzar tus propios productos al catalogo de la app, "
        "adaptar precios y pagos por pais, preparar anuncios y guiones, conectar con enlaces de grupos de "
        "WhatsApp y comunidades de Google, y calcular retornos y embudos de marketing."
    ),
    "como_funciona": (
        "Entras con tu correo, nombre de usuario y clave personal (o revisas Ajustes y Privacidad). "
        "Desde el Menu Principal accedes a cada modulo y regresas cuando quieras con la flecha arriba "
        "a la izquierda o el boton de volver al menu."
    ),
    "diferencia_clave": (
        "Reune catalogo buscable, lanzamiento directo de productos del usuario, localizacion por pais, "
        "accesos a grupos de WhatsApp y Google, y herramientas financieras en un solo flujo con cuenta."
    ),
}


# ==============================================================================
# 02. PAISES, MONEDAS, MEDIOS DE PAGO Y DIRECTORIO DE GRUPOS (WHATSAPP / GOOGLE)
# ==============================================================================
PAISES_DISPONIBLES = [
    {
        "codigo": "VE",
        "nombre": "Venezuela",
        "moneda": "USD / VES",
        "simbolo": "$",
        "tasa_usd": 1.0,
        "envio_usd": 3.5,
        "pagos": "Pago Movil, Zelle, Binance USDT, Efectivo",
        "horario": "12:30 - 14:30 y 19:30 - 22:30 VET",
        "cta": "Escribenos por WhatsApp y coordina tu pedido",
    },
    {
        "codigo": "US",
        "nombre": "Estados Unidos",
        "moneda": "USD",
        "simbolo": "$",
        "tasa_usd": 1.0,
        "envio_usd": 6.5,
        "pagos": "Tarjeta Credito/Debito, Apple Pay, Google Pay, PayPal",
        "horario": "18:00 - 22:30 EST",
        "cta": "Order today with tracked shipping",
    },
    {
        "codigo": "MX",
        "nombre": "Mexico",
        "moneda": "MXN",
        "simbolo": "MX$",
        "tasa_usd": 17.2,
        "envio_usd": 4.8,
        "pagos": "Tarjeta, OXXO Pay, Mercado Pago, SPEI",
        "horario": "13:00 - 15:00 y 20:00 - 23:00 CST",
        "cta": "Pide hoy con envio disponible",
    },
    {
        "codigo": "CO",
        "nombre": "Colombia",
        "moneda": "COP",
        "simbolo": "COL$",
        "tasa_usd": 4150.0,
        "envio_usd": 3.8,
        "pagos": "Pago Contra Entrega, Nequi, Daviplata, PSE",
        "horario": "12:00 - 14:00 y 19:00 - 22:00 COT",
        "cta": "Solicitalo hoy y coordina tu entrega",
    },
    {
        "codigo": "ES",
        "nombre": "Espana",
        "moneda": "EUR",
        "simbolo": "EUR ",
        "tasa_usd": 0.92,
        "envio_usd": 5.2,
        "pagos": "Tarjeta, Bizum, PayPal, Apple Pay",
        "horario": "14:00 - 16:00 y 20:30 - 23:00 CET",
        "cta": "Consiguelo ahora con envio rapido",
    },
    {
        "codigo": "AR",
        "nombre": "Argentina",
        "moneda": "ARS",
        "simbolo": "AR$",
        "tasa_usd": 1050.0,
        "envio_usd": 4.2,
        "pagos": "Mercado Pago, Transferencia Bancaria, Tarjeta",
        "horario": "13:00 - 15:00 y 20:00 - 23:30 ART",
        "cta": "Consultanos y pedilo hoy",
    },
    {
        "codigo": "CL",
        "nombre": "Chile",
        "moneda": "CLP",
        "simbolo": "CLP$",
        "tasa_usd": 950.0,
        "envio_usd": 4.5,
        "pagos": "Webpay, Debito/Credito, Mercado Pago, Transferencia",
        "horario": "13:00 - 14:30 y 20:00 - 22:30 CLT",
        "cta": "Pide online con despacho",
    },
    {
        "codigo": "PE",
        "nombre": "Peru",
        "moneda": "PEN",
        "simbolo": "S/",
        "tasa_usd": 3.75,
        "envio_usd": 3.2,
        "pagos": "Yape, Plin, Pago Contra Entrega, Tarjeta",
        "horario": "12:30 - 14:30 y 19:30 - 22:30 PET",
        "cta": "Escribenos y paga facil con Yape o Plin",
    },
]

GRUPOS_Y_COMUNIDADES_BASE = [
    {
        "id": "GRP-WA-01",
        "canal": "WhatsApp",
        "nombre": "Red de Emprendedores y Ventas WhatsApp",
        "categoria": "Negocios y Ventas",
        "descripcion": "Espacio para compartir ofertas, intercambiar ideas de marketing y contactar compradores.",
        "url": "https://chat.whatsapp.com/",
    },
    {
        "id": "GRP-WA-02",
        "canal": "WhatsApp",
        "nombre": "Creadores de Contenido y Video Corto",
        "categoria": "Contenido y Redes",
        "descripcion": "Grupo enfocado en ganchos, guiones para Reels/TikTok/Shorts y pruebas de anuncios.",
        "url": "https://chat.whatsapp.com/",
    },
    {
        "id": "GRP-GG-01",
        "canal": "Grupos de Google",
        "nombre": "Google Groups · Marketing Digital y Comercio",
        "categoria": "Marketing y Estrategia",
        "descripcion": "Hilos y debates sobre campanas, segmentacion, precios locales y crecimiento de ventas.",
        "url": "https://groups.google.com/",
    },
    {
        "id": "GRP-GG-02",
        "canal": "Grupos de Google",
        "nombre": "Google Groups · Lanzamiento de Productos y Nichos",
        "categoria": "Productos y Nichos",
        "descripcion": "Comunidad para validar ideas de productos, resolver dudas y organizar lanzamientos.",
        "url": "https://groups.google.com/",
    },
]


# ==============================================================================
# 03. CATALOGO INICIAL Y FUNCIONES DE LANZAMIENTO DE PRODUCTOS
# ==============================================================================
def armar_producto(
    item_id,
    nombre,
    categoria,
    precio_usd,
    costo_usd,
    problema,
    beneficio,
    publico="Publico general",
    autor="Catalogo Base",
    es_lanzamiento_usuario=False,
    enlace_contacto="",
):
    p = round(float(precio_usd), 2)
    c = round(float(costo_usd), 2)
    margen_usd = round(p - c, 2)
    margen_pct = round((margen_usd / p) * 100, 1) if p > 0 else 0.0
    return {
        "id": item_id,
        "nombre": nombre.strip(),
        "categoria": categoria.strip(),
        "precio_base_usd": p,
        "costo_base_usd": c,
        "margen_usd": margen_usd,
        "margen_pct": margen_pct,
        "problema": problema.strip(),
        "beneficio": beneficio.strip(),
        "publico": publico.strip(),
        "autor": autor.strip(),
        "es_lanzamiento_usuario": bool(es_lanzamiento_usuario),
        "enlace_contacto": (enlace_contacto or "").strip(),
    }


CATALOGO_BASE = [
    armar_producto(
        "PRD-01",
        "Audifonos Inalambricos ANC Pro",
        "Tecnologia y Gadgets",
        49.90,
        14.50,
        "Ruido externo y cables incomodos al moverte",
        "Audio inalambrico nitido con reduccion de ruido y buena bateria",
        "Estudiantes, trabajadores remotos y viajeros",
        "Creaciones Celso",
        False,
    ),
    armar_producto(
        "PRD-02",
        "Reloj Deportivo Pantalla Clara",
        "Tecnologia y Gadgets",
        59.00,
        18.00,
        "Perder avisos o no llevar control practico de rutinas",
        "Lectura clara en muneca y seguimiento diario sencillo",
        "Personas activas y de rutina diaria",
        "Creaciones Celso",
        False,
    ),
    armar_producto(
        "PRD-03",
        "Termo Acero Termico 1L",
        "Hogar y Estilo de Vida",
        24.90,
        6.20,
        "Bebidas que pierden temperatura durante el dia",
        "Conserva temperatura por horas con cierre seguro",
        "Estudiantes, conductores y oficina",
        "Creaciones Celso",
        False,
    ),
    armar_producto(
        "PRD-04",
        "Serum Hidratante Rutina Diaria",
        "Cuidado Personal",
        32.00,
        7.50,
        "Sensacion de resequedad por clima o jornadas largas",
        "Textura ligera de rapida absorcion para uso diario",
        "Personas con rutina de cuidado personal",
        "Creaciones Celso",
        False,
    ),
    armar_producto(
        "PRD-05",
        "Set Bandas de Entrenamiento",
        "Deporte y Bienestar",
        29.90,
        8.40,
        "Falta de espacio o equipo al entrenar en casa",
        "Niveles variados de resistencia en estuche compacto",
        "Quienes entrenan en casa o viajan",
        "Creaciones Celso",
        False,
    ),
]


# ==============================================================================
# 04. PERSISTENCIA, CUENTAS, LANZAMIENTOS Y GRUPOS
# ==============================================================================
def normalizar_texto(val):
    s = (val or "").strip().lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


def validar_correo_limpio(correo):
    c = (correo or "").strip().lower()
    if not c or "@" not in c:
        return ""
    partes = c.split("@")
    if len(partes) != 2 or not partes[0] or "." not in partes[1]:
        return ""
    return c


def hash_clave(clave, correo):
    raw = f"{validar_correo_limpio(correo)}::{(clave or '').strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {
            "cuentas": {},
            "productos_lanzados": [],
            "grupos_personalizados": [],
        }
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("cuentas", {})
                data.setdefault("productos_lanzados", [])
                data.setdefault("grupos_personalizados", [])
                return data
    except Exception:
        pass
    return {
        "cuentas": {},
        "productos_lanzados": [],
        "grupos_personalizados": [],
    }


def guardar_db(data):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def obtener_catalogo_completo():
    db = cargar_db()
    lista = list(CATALOGO_BASE)
    for item in db.get("productos_lanzados", []):
        if isinstance(item, dict) and item.get("nombre"):
            lista.append(item)
    return lista


def obtener_grupos_completos():
    db = cargar_db()
    lista = list(GRUPOS_Y_COMUNIDADES_BASE)
    for g in db.get("grupos_personalizados", []):
        if isinstance(g, dict) and g.get("nombre"):
            lista.append(g)
    return lista


# ==============================================================================
# 05. INTERFAZ WEB (PARTE 1: NEGRO, DORADO, PLATEADO + FIGURAS GEOMETRICAS)
# ==============================================================================
HTML_PARTE_1 = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-Pre Marketing · Creaciones Celso</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --negro: #090a0d;
  --panel: #12141a;
  --tarjeta: #181b23;
  --campo: #0d0f14;
  --dorado: #d4af37;
  --dorado-claro: #f2d379;
  --plateado: #cbd5e1;
  --borde: #64748b;
  --blanco: #f8fafc;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background-color: var(--negro);
  color: var(--blanco);
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
}

body {
  padding-bottom: 64px;
}

#canvasFiguras {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.header-app {
  position: sticky;
  top: 0;
  z-index: 25;
  background-color: rgba(18, 20, 26, 0.96);
  border-bottom: 1px solid var(--dorado);
  padding: 12px 14px 10px;
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.left-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-atras {
  width: auto;
  margin: 0;
  padding: 7px 12px;
  font-size: 14px;
  font-weight: 700;
  border-radius: 8px;
  background-color: var(--campo);
  color: var(--dorado);
  border: 1px solid var(--borde);
  cursor: pointer;
}

.btn-atras:hover {
  border-color: var(--dorado);
  color: var(--dorado-claro);
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--dorado);
}

.app-sub {
  font-size: 12px;
  color: var(--plateado);
}

.badge-cuenta {
  background-color: var(--campo);
  border: 1px solid var(--dorado);
  color: var(--dorado-claro);
  padding: 6px 11px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  max-width: 46%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 10px 0 3px;
}

.nav-item {
  flex: 0 0 auto;
  width: auto;
  margin: 0;
  padding: 8px 13px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  background-color: var(--campo);
  color: var(--plateado);
  border: 1px solid var(--borde);
  cursor: pointer;
}

.nav-item.activa {
  background-color: var(--dorado);
  color: var(--negro);
  border-color: var(--dorado-claro);
  font-weight: 700;
}

.wrap-app {
  position: relative;
  z-index: 10;
  max-width: 1020px;
  margin: 0 auto;
  padding: 14px;
}

.inicio-centro {
  min-height: calc(100vh - 96px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 0;
}

.card-box {
  background-color: rgba(24, 27, 35, 0.96);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}

.card-oro {
  border-color: var(--dorado);
}

.sub-header-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

h2 {
  margin: 0 0 6px;
  font-size: 18px;
  color: var(--dorado);
}

h3 {
  margin: 12px 0 6px;
  font-size: 15px;
  color: var(--plateado);
}

.desc-texto {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--plateado);
  line-height: 1.45;
}

label {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--plateado);
  margin-top: 10px;
}

input[type="text"],
input[type="password"],
input[type="email"],
input[type="number"],
textarea,
select {
  width: 100%;
  padding: 11px 13px;
  font-size: 15px;
  font-family: 'Space Grotesk', sans-serif;
  border-radius: 8px;
  border: 1px solid var(--borde);
  background-color: var(--campo);
  color: var(--blanco);
  margin-top: 6px;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: var(--dorado);
}

textarea {
  min-height: 96px;
  line-height: 1.45;
}

.btn-oro {
  width: 100%;
  padding: 12px 14px;
  font-size: 14.5px;
  font-weight: 700;
  border-radius: 8px;
  border: 1px solid var(--dorado-claro);
  background-color: var(--dorado);
  color: var(--negro);
  cursor: pointer;
  margin-top: 12px;
}

.btn-plata {
  width: 100%;
  padding: 11px 13px;
  font-size: 13.5px;
  font-weight: 600;
  border-radius: 8px;
  border: 1px solid var(--borde);
  background-color: var(--campo);
  color: var(--plateado);
  cursor: pointer;
  margin-top: 8px;
}

.btn-plata:hover {
  border-color: var(--dorado);
  color: var(--blanco);
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

@media (max-width: 640px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr 1fr;
  }
}

.kpi-card {
  background-color: var(--campo);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.kpi-card span {
  display: block;
  font-size: 11.5px;
  color: var(--plateado);
}

.kpi-card strong {
  display: block;
  font-size: 16px;
  color: var(--dorado);
  margin-top: 4px;
}

.caja-salida {
  background-color: var(--campo);
  border-left: 3px solid var(--dorado);
  border-top: 1px solid rgba(203, 213, 225, 0.2);
  border-right: 1px solid rgba(203, 213, 225, 0.2);
  border-bottom: 1px solid rgba(203, 213, 225, 0.2);
  border-radius: 0 8px 8px 0;
  padding: 12px 14px;
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-line;
}

.item-tarjeta {
  background-color: var(--campo);
  border: 1px solid rgba(203, 213, 225, 0.28);
  border-radius: 8px;
  padding: 12px;
  margin-top: 10px;
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.chip {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  background-color: var(--tarjeta);
  color: var(--plateado);
  border: 1px solid var(--borde);
  margin: 3px 4px 3px 0;
}

.chip-oro {
  color: var(--dorado-claro);
  border-color: var(--dorado);
}

.fila-ajuste {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  background-color: var(--campo);
  border: 1px solid rgba(203, 213, 225, 0.24);
  border-radius: 8px;
  padding: 11px 12px;
  margin-top: 8px;
}

.fila-ajuste input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--dorado);
  cursor: pointer;
}

.enlace-grupo {
  display: inline-block;
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: var(--dorado);
  color: var(--negro);
  font-weight: 700;
  font-size: 13px;
  text-decoration: none;
}

.estado-txt {
  font-size: 13.5px;
  color: var(--dorado-claro);
  margin-top: 8px;
  line-height: 1.4;
}

.firma-fija {
  position: fixed;
  right: 12px;
  bottom: 10px;
  z-index: 30;
  background-color: var(--panel);
  border: 1px solid var(--dorado);
  color: var(--dorado);
  font-size: 11px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 6px;
}

.oculto {
  display: none !important;
}
</style>
</head>
<body>

<canvas id="canvasFiguras" aria-hidden="true"></canvas>

<!-- INICIO: CORREO, NOMBRE DE USUARIO, CLAVE PERSONAL Y AJUSTES/PRIVACIDAD -->
<section id="vistaInicio" class="inicio-centro">
  <div class="wrap-app" style="width:100%;max-width:560px;">
    <div class="card-box card-oro">
      <h2>C-Pre Marketing</h2>
      <div style="font-size:13px;font-weight:700;color:var(--plateado);margin-bottom:8px;">Creaciones Celso · Parte 1</div>
      <p class="desc-texto">
        Ingresa tu correo, nombre de usuario y tu clave personal para guardar tu progreso en tu cuenta.
        Acceso gratuito sin clave externa de pago.
      </p>

      <label for="inCorreo">Correo electronico:</label>
      <input type="email" id="inCorreo" placeholder="tu_correo@ejemplo.com">

      <label for="inUsuario">Nombre de usuario:</label>
      <input type="text" id="inUsuario" placeholder="Ej. Celso">

      <label for="inClave">Clave personal de cuenta:</label>
      <input type="password" id="inClave" placeholder="Tu clave personal">

      <button type="button" class="btn-oro" onclick="entrarCuenta()">ENTRAR A LA APLICACION</button>
      <button type="button" class="btn-plata" onclick="verAjustesPrivacidad()">AJUSTES Y PRIVACIDAD</button>
      <div id="msgInicio" class="estado-txt"></div>
    </div>
  </div>
</section>

<!-- AJUSTES Y PRIVACIDAD -->
<section id="vistaAjustes" class="wrap-app oculto">
  <div class="sub-header-bar">
    <button type="button" class="btn-atras" onclick="volverDesdeAjustes()">&#8592; Regresar</button>
    <h2 style="margin:0;">Ajustes y Privacidad</h2>
  </div>
  <div class="card-box card-oro">
    <p class="desc-texto">Ajustes de cuenta gratuita, privacidad, enlaces y figuras geometricas.</p>
    <div id="listaAjustes"></div>
    <button type="button" class="btn-oro" onclick="guardarAjustes()">GUARDAR AJUSTES</button>
    <div id="msgAjustes" class="estado-txt"></div>
  </div>
</section>

<!-- CABECERA Y NAVEGACION -->
<header id="headerPrincipal" class="header-app oculto">
  <div class="top-row">
    <div class="left-brand">
      <button type="button" class="btn-atras" onclick="accionFlechaArriba()" title="Regresar al menu principal">&#8592;</button>
      <div>
        <div class="app-title">C-Pre Marketing</div>
        <div class="app-sub">Creaciones Celso · Parte 1</div>
      </div>
    </div>
    <div class="badge-cuenta" id="badgeCuenta">Cuenta</div>
  </div>

  <nav class="nav-scroll" aria-label="Modulos Parte 1">
    <button type="button" class="nav-item activa" data-sec="secMenu" onclick="abrirSeccion('secMenu', this)">Menu Principal</button>
    <button type="button" class="nav-item" data-sec="secBuscar" onclick="abrirSeccion('secBuscar', this)">Buscar Productos</button>
    <button type="button" class="nav-item" data-sec="secLanzar" onclick="abrirSeccion('secLanzar', this)">Lanzar Mis Productos</button>
    <button type="button" class="nav-item" data-sec="secGrupos" onclick="abrirSeccion('secGrupos', this)">WhatsApp y Google Groups</button>
    <button type="button" class="nav-item" data-sec="secPaises" onclick="abrirSeccion('secPaises', this)">Paises y Monedas</button>
    <button type="button" class="nav-item" data-sec="secGuia" onclick="abrirSeccion('secGuia', this)">Uso y Diferencias</button>
  </nav>
</header>

<main id="mainApp" class="wrap-app oculto">

  <!-- MENU PRINCIPAL -->
  <section id="secMenu" class="sec-panel card-box card-oro">
    <h2>Menu Principal</h2>
    <p class="desc-texto">Busca productos, lanza tus propios productos a la aplicacion, entra a enlaces de grupos de WhatsApp y Google, y revisa precios por pais.</p>

    <div class="grid-3">
      <div class="kpi-card"><span>Productos</span><strong id="kpiMenuProds">0</strong></div>
      <div class="kpi-card"><span>Grupos / Enlaces</span><strong id="kpiMenuGrupos">0</strong></div>
      <div class="kpi-card"><span>Paises</span><strong id="kpiMenuPaises">8</strong></div>
    </div>

    <div class="grid-2" style="margin-top:12px;">
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secBuscar')">1. Buscar Productos</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secLanzar')">2. Lanzar Mis Productos</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secGrupos')">3. Links WhatsApp y Google Groups</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secPaises')">4. Paises, Monedas y Pagos</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secGuia')">5. Para Que Sirve y Diferencias</button>
      <button type="button" class="btn-plata" onclick="verAjustesPrivacidad()">6. Ajustes y Privacidad</button>
    </div>
  </section>

  <!-- BUSCAR PRODUCTOS -->
  <section id="secBuscar" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Buscar Productos</h2>
    </div>
    <p class="desc-texto">Busca por nombre, categoria, problema, beneficio o creador.</p>

    <div class="grid-2">
      <div>
        <label for="txtBuscarProd">Palabra clave o producto:</label>
        <input type="text" id="txtBuscarProd" placeholder="Ej. audifonos, termo, lanzamiento..." oninput="pintarCatalogo()">
      </div>
      <div>
        <label for="selCatBuscar">Categoria:</label>
        <select id="selCatBuscar" onchange="pintarCatalogo()">
          <option value="TODAS">Todas las categorias</option>
        </select>
      </div>
    </div>

    <div id="listaCatalogo"></div>
  </section>

  <!-- LANZAR MIS PRODUCTOS A LA APLICACION -->
  <section id="secLanzar" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Lanzar Mis Productos a la Aplicacion</h2>
    </div>
    <p class="desc-texto">Como usuario con cuenta, publica tus productos o servicios para que queden disponibles en el catalogo de la aplicacion.</p>

    <div class="grid-2">
      <div>
        <label for="lanNombre">Nombre de tu producto o servicio:</label>
        <input type="text" id="lanNombre" placeholder="Ej. Curso de Ventas por WhatsApp">
      </div>
      <div>
        <label for="lanCategoria">Categoria:</label>
        <input type="text" id="lanCategoria" value="Productos y Servicios">
      </div>
    </div>

    <div class="grid-2">
      <div>
        <label for="lanPrecio">Precio de venta (USD):</label>
        <input type="number" id="lanPrecio" value="25" step="0.1">
      </div>
      <div>
        <label for="lanCosto">Costo base (USD):</label>
        <input type="number" id="lanCosto" value="5" step="0.1">
      </div>
    </div>

    <label for="lanProblema">Problema que resuelve:</label>
    <input type="text" id="lanProblema" placeholder="Ej. Dificultad para organizar mensajes y cierres">

    <label for="lanBeneficio">Beneficio principal:</label>
    <input type="text" id="lanBeneficio" placeholder="Ej. Respuestas claras y seguimiento ordenado">

    <label for="lanEnlace">Enlace de contacto, WhatsApp o pagina (opcional):</label>
    <input type="text" id="lanEnlace" placeholder="https://wa.me/... o enlace de tu oferta">

    <button type="button" class="btn-oro" onclick="lanzarProductoUsuario()">LANZAR PRODUCTO A LA APLICACION</button>
    <div id="msgLanzar" class="estado-txt"></div>

    <h3>Productos Lanzados Recientemente</h3>
    <div id="listaLanzados"></div>
  </section>

  <!-- LINKS A GRUPOS DE WHATSAPP Y GOOGLE GROUPS -->
  <section id="secGrupos" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Links de Grupos de WhatsApp y Google Groups</h2>
    </div>
    <p class="desc-texto">Abre enlaces a grupos de WhatsApp o Google Groups, genera un enlace directo de WhatsApp con mensaje listo y guarda tus propios enlaces de grupos.</p>

    <div class="card-box" style="background-color:var(--panel);">
      <h3>Generador Rapido de Link de WhatsApp</h3>
      <div class="grid-2">
        <div>
          <label for="waNumero">Numero con codigo de pais (sin + ni espacios):</label>
          <input type="text" id="waNumero" placeholder="Ej. 584120000000" oninput="actualizarLinkWa()">
        </div>
        <div>
          <label for="waTexto">Mensaje inicial:</label>
          <input type="text" id="waTexto" value="Hola, quiero informacion sobre este producto" oninput="actualizarLinkWa()">
        </div>
      </div>
      <div id="waUrlPreview" class="caja-salida">https://wa.me/</div>
      <div class="grid-2">
        <a id="waAbrirLink" class="enlace-grupo" href="https://wa.me/" target="_blank" rel="noopener noreferrer" style="text-align:center;">ABRIR ENLACE WHATSAPP</a>
        <button type="button" class="btn-plata" onclick="copiarTexto('waUrlPreview')">COPIAR ENLACE</button>
      </div>
    </div>

    <h3>Grupos y Comunidades Disponibles</h3>
    <div id="listaGrupos"></div>

    <div class="card-box card-oro" style="margin-top:14px;background-color:var(--panel);">
      <h3>Agregar Link de Grupo (WhatsApp o Google Groups)</h3>
      <div class="grid-2">
        <div>
          <label for="grpCanal">Plataforma:</label>
          <select id="grpCanal">
            <option value="WhatsApp">WhatsApp</option>
            <option value="Grupos de Google">Grupos de Google</option>
          </select>
        </div>
        <div>
          <label for="grpNombre">Nombre del grupo:</label>
          <input type="text" id="grpNombre" placeholder="Ej. Grupo Marketing Local">
        </div>
      </div>
      <label for="grpUrl">URL del grupo (https://...):</label>
      <input type="text" id="grpUrl" placeholder="https://chat.whatsapp.com/... o https://groups.google.com/...">
      <label for="grpDesc">Descripcion breve:</label>
      <input type="text" id="grpDesc" placeholder="Tema principal o reglas del grupo">
      <button type="button" class="btn-oro" onclick="agregarGrupoEnlace()">GUARDAR ENLACE DE GRUPO</button>
      <div id="msgGrupo" class="estado-txt"></div>
    </div>
  </section>

  <!-- PAISES Y MONEDAS -->
  <section id="secPaises" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Paises, Monedas y Medios de Pago</h2>
    </div>
    <p class="desc-texto">Revisa conversion estimada, envio, margen y medios de pago por pais.</p>

    <div class="grid-2">
      <div>
        <label for="selPais">Pais:</label>
        <select id="selPais" onchange="actualizarPais()"></select>
      </div>
      <div>
        <label for="selProdPais">Producto:</label>
        <select id="selProdPais" onchange="cargarProductoPais()"></select>
      </div>
    </div>

    <div class="grid-2">
      <div>
        <label for="paisPrecioUsd">Precio base (USD):</label>
        <input type="number" id="paisPrecioUsd" value="49.90" step="0.1" oninput="actualizarPais()">
      </div>
      <div>
        <label for="paisCostoUsd">Costo base (USD):</label>
        <input type="number" id="paisCostoUsd" value="14.50" step="0.1" oninput="actualizarPais()">
      </div>
    </div>

    <div class="grid-4" style="margin-top:10px;">
      <div class="kpi-card"><span>Precio Local</span><strong id="pLocal">$0</strong></div>
      <div class="kpi-card"><span>Envio Est.</span><strong id="pEnvio">$0</strong></div>
      <div class="kpi-card"><span>Margen USD</span><strong id="pMargenUsd">$0</strong></div>
      <div class="kpi-card"><span>Margen %</span><strong id="pMargenPct">0%</strong></div>
    </div>

    <div id="detallePais" class="caja-salida"></div>
  </section>

  <!-- PARA QUE SIRVE, COMO FUNCIONA Y DIFERENCIAS -->
  <section id="secGuia" class="sec-panel card-box card-oro oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Para Que Sirve, Como Funciona y Diferencias</h2>
    </div>

    <h3>Para que sirve esta aplicacion</h3>
    <div id="txtParaQueSirve" class="caja-salida"></div>

    <h3>Como funciona</h3>
    <div id="txtComoFunciona" class="caja-salida"></div>

    <h3>En que se diferencia de otras aplicaciones</h3>
    <div id="txtDiferencias" class="caja-salida"></div>
  </section>

</main>

<div class="firma-fija">Creaciones Celso</div>

<script id="jsonPaises" type="application/json">__PAISES_JSON__</script>
<script id="jsonCatalogo" type="application/json">__CATALOGO_JSON__</script>
<script id="jsonGrupos" type="application/json">__GRUPOS_JSON__</script>
<script id="jsonAjustes" type="application/json">__AJUSTES_JSON__</script>
<script id="jsonInfo" type="application/json">__INFO_JSON__</script>

<script>
const PAISES = JSON.parse(document.getElementById("jsonPaises").textContent);
let CATALOGO = JSON.parse(document.getElementById("jsonCatalogo").textContent);
let GRUPOS = JSON.parse(document.getElementById("jsonGrupos").textContent);
const AJUSTES_DEF = JSON.parse(document.getElementById("jsonAjustes").textContent);
const INFO_APP = JSON.parse(document.getElementById("jsonInfo").textContent);

let sesion = {
  correo: "",
  usuario: "",
  clave: "",
  ajustes: {}
};

AJUSTES_DEF.forEach(a => {
  sesion.ajustes[a.clave] = Boolean(a.activo);
});

let vistaActiva = "secMenu";
let origenAjustes = "inicio";

function norm(t) {
  return String(t || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "");
}

function esc(t) {
  return String(t || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function iniciarFigurasGeometricas() {
  const canvas = document.getElementById("canvasFiguras");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const colores = [
    "rgba(212, 175, 55, 0.25)",
    "rgba(242, 211, 121, 0.20)",
    "rgba(203, 213, 225, 0.18)",
    "rgba(148, 163, 184, 0.16)",
  ];
  const formas = ["triangulo", "cuadrado", "hexagono", "rombo"];
  const piezas = [];

  function redimensionar() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  redimensionar();
  window.addEventListener("resize", redimensionar);

  for (let i = 0; i < 16; i++) {
    piezas.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      tam: 18 + Math.random() * 26,
      vx: (Math.random() - 0.5) * 0.45,
      vy: (Math.random() - 0.5) * 0.45,
      rot: Math.random() * Math.PI * 2,
      vrot: (Math.random() - 0.5) * 0.008,
      forma: formas[i % formas.length],
      cIdx: i % colores.length,
      paso: Math.random() * 180,
    });
  }

  function poligono(x, y, r, lados, rot) {
    ctx.beginPath();
    for (let k = 0; k < lados; k++) {
      const ang = rot + (k * Math.PI * 2) / lados;
      const px = x + Math.cos(ang) * r;
      const py = y + Math.sin(ang) * r;
      if (k === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
  }

  function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (sesion.ajustes["figuras_geometricas_activas"] !== false) {
      piezas.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.rot += p.vrot;
        p.paso += 1;
        if (p.paso % 180 === 0) {
          p.cIdx = (p.cIdx + 1) % colores.length;
        }
        if (p.x < -60) p.x = canvas.width + 60;
        if (p.x > canvas.width + 60) p.x = -60;
        if (p.y < -60) p.y = canvas.height + 60;
        if (p.y > canvas.height + 60) p.y = -60;

        ctx.save();
        ctx.strokeStyle = colores[p.cIdx];
        ctx.lineWidth = 1.5;
        if (p.forma === "triangulo") {
          poligono(p.x, p.y, p.tam, 3, p.rot);
          ctx.stroke();
        } else if (p.forma === "cuadrado") {
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rot);
          ctx.strokeRect(-p.tam * 0.65, -p.tam * 0.65, p.tam * 1.3, p.tam * 1.3);
        } else if (p.forma === "hexagono") {
          poligono(p.x, p.y, p.tam * 0.75, 6, p.rot);
          ctx.stroke();
        } else {
          poligono(p.x, p.y, p.tam * 0.8, 4, p.rot);
          ctx.stroke();
        }
        ctx.restore();
      });
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}

function pintarAjustes() {
  const cont = document.getElementById("listaAjustes");
  cont.innerHTML = "";
  AJUSTES_DEF.forEach(a => {
    const chk = sesion.ajustes[a.clave] !== false;
    const div = document.createElement("div");
    div.className = "fila-ajuste";
    div.innerHTML =
      `<div><div style="font-weight:700;font-size:14.5px;color:#f8fafc;">${esc(a.titulo)}</div>` +
      `<div style="font-size:13px;color:#cbd5e1;margin-top:3px;">${esc(a.descripcion)}</div></div>` +
      `<input type="checkbox" data-k="${esc(a.clave)}" ${chk ? "checked" : ""}>`;
    cont.appendChild(div);
  });
}

function verAjustesPrivacidad() {
  const appVisible = !document.getElementById("mainApp").classList.contains("oculto");
  origenAjustes = appVisible ? "app" : "inicio";
  pintarAjustes();
  document.getElementById("vistaInicio").classList.add("oculto");
  document.getElementById("headerPrincipal").classList.add("oculto");
  document.getElementById("mainApp").classList.add("oculto");
  document.getElementById("vistaAjustes").classList.remove("oculto");
  window.scrollTo(0, 0);
}

function volverDesdeAjustes() {
  document.getElementById("vistaAjustes").classList.add("oculto");
  if (origenAjustes === "app") {
    document.getElementById("headerPrincipal").classList.remove("oculto");
    document.getElementById("mainApp").classList.remove("oculto");
  } else {
    document.getElementById("vistaInicio").classList.remove("oculto");
  }
  window.scrollTo(0, 0);
}

function guardarAjustes() {
  document.querySelectorAll('#listaAjustes input[type="checkbox"]').forEach(cb => {
    sesion.ajustes[cb.getAttribute("data-k")] = cb.checked;
  });
  aplicarCabeceraCuenta();
  document.getElementById("msgAjustes").textContent = "Ajustes guardados.";
}

function aplicarCabeceraCuenta() {
  const badge = document.getElementById("badgeCuenta");
  if (sesion.ajustes["correo_en_cabecera"] === false) {
    badge.textContent = sesion.usuario || "Cuenta";
  } else {
    badge.textContent = sesion.correo || sesion.usuario || "Cuenta";
  }
}

async function entrarCuenta() {
  const correo = document.getElementById("inCorreo").value.trim().toLowerCase();
  const usuario = document.getElementById("inUsuario").value.trim();
  const clave = document.getElementById("inClave").value.trim();
  const msg = document.getElementById("msgInicio");

  if (!correo || !correo.includes("@")) {
    msg.textContent = "Ingresa un correo electronico valido.";
    return;
  }
  if (!usuario) {
    msg.textContent = "Ingresa tu nombre de usuario.";
    return;
  }
  if (!clave || clave.length < 3) {
    msg.textContent = "Ingresa tu clave personal (minimo 3 caracteres).";
    return;
  }

  try {
    const r = await fetch("/api/p1/cuenta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo: correo, usuario: usuario, clave: clave })
    });
    const d = await r.json();
    if (!d.ok) {
      msg.textContent = d.mensaje || "No se pudo iniciar la cuenta.";
      return;
    }

    sesion.correo = correo;
    sesion.usuario = d.cuenta.usuario || usuario;
    sesion.clave = clave;
    if (d.cuenta.ajustes && typeof d.cuenta.ajustes === "object") {
      sesion.ajustes = Object.assign({}, sesion.ajustes, d.cuenta.ajustes);
    }
    aplicarCabeceraCuenta();

    document.getElementById("vistaInicio").classList.add("oculto");
    document.getElementById("vistaAjustes").classList.add("oculto");
    document.getElementById("headerPrincipal").classList.remove("oculto");
    document.getElementById("mainApp").classList.remove("oculto");
    abrirSeccion("secMenu");
    window.scrollTo(0, 0);
  } catch (e) {
    msg.textContent = "Error al conectar con el servidor.";
  }
}

function abrirSeccion(idSec, btnRef) {
  vistaActiva = idSec;
  document.querySelectorAll(".sec-panel").forEach(s => s.classList.add("oculto"));
  const target = document.getElementById(idSec);
  if (target) target.classList.remove("oculto");

  document.querySelectorAll(".nav-item").forEach(b => {
    b.classList.toggle("activa", b.getAttribute("data-sec") === idSec);
    if (btnRef && b === btnRef) b.classList.add("activa");
  });
  window.scrollTo(0, 0);
}

function irDesdeMenu(idSec) {
  const b = document.querySelector(`.nav-item[data-sec="${idSec}"]`);
  abrirSeccion(idSec, b);
}

function accionFlechaArriba() {
  if (vistaActiva !== "secMenu") {
    irDesdeMenu("secMenu");
  } else {
    document.getElementById("headerPrincipal").classList.add("oculto");
    document.getElementById("mainApp").classList.add("oculto");
    document.getElementById("vistaInicio").classList.remove("oculto");
    window.scrollTo(0, 0);
  }
}

function actualizarKpisMenu() {
  document.getElementById("kpiMenuProds").textContent = String(CATALOGO.length);
  document.getElementById("kpiMenuGrupos").textContent = String(GRUPOS.length);
  document.getElementById("kpiMenuPaises").textContent = String(PAISES.length);
}

function cargarSelectores() {
  const selCat = document.getElementById("selCatBuscar");
  const catPrev = selCat.value || "TODAS";
  const cats = new Set(["TODAS"]);
  CATALOGO.forEach(p => cats.add(p.categoria));
  selCat.innerHTML = "";
  cats.forEach(c => {
    const op = document.createElement("option");
    op.value = c;
    op.textContent = c === "TODAS" ? "Todas las categorias" : c;
    if (c === catPrev) op.selected = true;
    selCat.appendChild(op);
  });

  const selProdPais = document.getElementById("selProdPais");
  selProdPais.innerHTML = "";
  CATALOGO.forEach((p, idx) => {
    const op = document.createElement("option");
    op.value = idx;
    op.textContent = `${p.nombre} ($${p.precio_base_usd})`;
    selProdPais.appendChild(op);
  });

  const selPais = document.getElementById("selPais");
  selPais.innerHTML = "";
  PAISES.forEach(m => {
    const op = document.createElement("option");
    op.value = m.codigo;
    op.textContent = `${m.nombre} (${m.moneda})`;
    selPais.appendChild(op);
  });

  actualizarKpisMenu();
}

function pintarCatalogo() {
  const q = norm(document.getElementById("txtBuscarProd").value);
  const cat = document.getElementById("selCatBuscar").value;
  const cont = document.getElementById("listaCatalogo");
  cont.innerHTML = "";

  const items = CATALOGO.filter(p => {
    if (cat !== "TODAS" && p.categoria !== cat) return false;
    if (!q) return true;
    const blob = norm([p.nombre, p.categoria, p.problema, p.beneficio, p.publico, p.autor].join(" "));
    return blob.includes(q);
  });

  if (!items.length) {
    cont.innerHTML = `<div class="caja-salida">No se encontraron productos con ese criterio.</div>`;
    return;
  }

  items.forEach(p => {
    const idx = CATALOGO.indexOf(p);
    const card = document.createElement("div");
    card.className = "item-tarjeta";
    let enlaceHtml = "";
    if (p.enlace_contacto && (p.enlace_contacto.startsWith("http://") || p.enlace_contacto.startsWith("https://"))) {
      enlaceHtml = `<a class="enlace-grupo" href="${esc(p.enlace_contacto)}" target="_blank" rel="noopener noreferrer">ABRIR ENLACE DEL PRODUCTO</a>`;
    }
    card.innerHTML =
      `<div class="item-top">` +
      `<div><strong style="font-size:15.5px;">${esc(p.nombre)}</strong>` +
      `<div style="margin-top:4px;">` +
      `<span class="chip">${esc(p.categoria)}</span>` +
      `<span class="chip chip-oro">Margen ${p.margen_pct}%</span>` +
      `<span class="chip">${p.es_lanzamiento_usuario ? "Lanzado por usuario" : "Catalogo"}</span>` +
      `</div></div>` +
      `<div style="text-align:right;"><strong style="color:#d4af37;font-size:16px;">$${p.precio_base_usd}</strong>` +
      `<div style="font-size:12px;color:#cbd5e1;">Por: ${esc(p.autor || "Base")}</div></div></div>` +
      `<div style="margin-top:8px;font-size:13.5px;"><strong>Beneficio:</strong> ${esc(p.beneficio)}</div>` +
      `<div style="margin-top:3px;font-size:13px;color:#cbd5e1;"><strong>Resuelve:</strong> ${esc(p.problema)}</div>` +
      `<div style="margin-top:8px;"><button type="button" class="btn-plata" onclick="enviarItemAPais(${idx})">CALCULAR EN PAISES</button>${enlaceHtml}</div>`;
    cont.appendChild(card);
  });
}

function pintarLanzados() {
  const cont = document.getElementById("listaLanzados");
  const lanzados = CATALOGO.filter(p => p.es_lanzamiento_usuario);
  cont.innerHTML = "";
  if (!lanzados.length) {
    cont.innerHTML = `<div class="caja-salida">Aun no has lanzado productos propios. Completa el formulario de arriba para publicar el primero.</div>`;
    return;
  }
  lanzados.forEach(p => {
    const div = document.createElement("div");
    div.className = "item-tarjeta";
    div.innerHTML =
      `<strong>${esc(p.nombre)}</strong> <span class="chip chip-oro">$${p.precio_base_usd}</span>` +
      `<div style="font-size:13px;color:#cbd5e1;margin-top:4px;">${esc(p.beneficio)} · Autor: ${esc(p.autor)}</div>`;
    cont.appendChild(div);
  });
}

async function lanzarProductoUsuario() {
  const nombre = document.getElementById("lanNombre").value.trim();
  const categoria = document.getElementById("lanCategoria").value.trim() || "Productos y Servicios";
  const precio = parseFloat(document.getElementById("lanPrecio").value) || 0;
  const costo = parseFloat(document.getElementById("lanCosto").value) || 0;
  const problema = document.getElementById("lanProblema").value.trim() || "Necesidad de clientes";
  const beneficio = document.getElementById("lanBeneficio").value.trim() || "Solucion directa";
  const enlace = document.getElementById("lanEnlace").value.trim();
  const msg = document.getElementById("msgLanzar");

  if (!nombre || precio <= 0) {
    msg.textContent = "Escribe el nombre del producto y un precio mayor a cero.";
    return;
  }

  try {
    const r = await fetch("/api/p1/lanzar_producto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nombre: nombre,
        categoria: categoria,
        precio_base_usd: precio,
        costo_base_usd: costo,
        problema: problema,
        beneficio: beneficio,
        enlace_contacto: enlace,
        autor: sesion.usuario || sesion.correo || "Usuario"
      })
    });
    const d = await r.json();
    if (d.ok && d.producto) {
      CATALOGO.push(d.producto);
      cargarSelectores();
      pintarCatalogo();
      pintarLanzados();
      document.getElementById("lanNombre").value = "";
      document.getElementById("lanEnlace").value = "";
      msg.textContent = `Producto "${nombre}" lanzado al catalogo.`;
    }
  } catch (e) {
    msg.textContent = "Error al lanzar el producto.";
  }
}

function actualizarLinkWa() {
  const numRaw = (document.getElementById("waNumero").value || "").replace(/[^0-9]/g, "");
  const txt = (document.getElementById("waTexto").value || "").trim();
  const url = numRaw
    ? `https://wa.me/${numRaw}?text=${encodeURIComponent(txt)}`
    : "https://wa.me/";
  document.getElementById("waUrlPreview").textContent = url;
  document.getElementById("waAbrirLink").href = url;
}

function pintarGrupos() {
  const cont = document.getElementById("listaGrupos");
  cont.innerHTML = "";
  GRUPOS.forEach(g => {
    const safeUrl = (g.url && (g.url.startsWith("https://") || g.url.startsWith("http://"))) ? g.url : "https://chat.whatsapp.com/";
    const div = document.createElement("div");
    div.className = "item-tarjeta";
    div.innerHTML =
      `<div class="item-top"><strong style="color:#d4af37;">${esc(g.nombre)}</strong><span class="chip chip-oro">${esc(g.canal)}</span></div>` +
      `<div style="font-size:13px;color:#cbd5e1;margin-top:4px;">${esc(g.descripcion)}</div>` +
      `<a class="enlace-grupo" href="${esc(safeUrl)}" target="_blank" rel="noopener noreferrer">ENTRAR AL GRUPO (${esc(g.canal)})</a>`;
    cont.appendChild(div);
  });
}

async function agregarGrupoEnlace() {
  const canal = document.getElementById("grpCanal").value;
  const nombre = document.getElementById("grpNombre").value.trim();
  const url = document.getElementById("grpUrl").value.trim();
  const descripcion = document.getElementById("grpDesc").value.trim() || "Comunidad de marketing y contactos";
  const msg = document.getElementById("msgGrupo");

  if (!nombre || (!url.startsWith("https://") && !url.startsWith("http://"))) {
    msg.textContent = "Ingresa un nombre y una URL valida que comience con https://";
    return;
  }

  try {
    const r = await fetch("/api/p1/grupos/agregar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ canal: canal, nombre: nombre, url: url, descripcion: descripcion })
    });
    const d = await r.json();
    if (d.ok && d.grupo) {
      GRUPOS.push(d.grupo);
      pintarGrupos();
      actualizarKpisMenu();
      document.getElementById("grpNombre").value = "";
      document.getElementById("grpUrl").value = "";
      msg.textContent = `Enlace "${nombre}" agregado.`;
    }
  } catch (e) {
    msg.textContent = "Error al guardar el enlace.";
  }
}

function cargarProductoPais() {
  const idx = parseInt(document.getElementById("selProdPais").value || "0", 10);
  const p = CATALOGO[idx];
  if (p) {
    document.getElementById("paisPrecioUsd").value = p.precio_base_usd;
    document.getElementById("paisCostoUsd").value = p.costo_base_usd;
  }
  actualizarPais();
}

function enviarItemAPais(idx) {
  const p = CATALOGO[idx];
  if (!p) return;
  document.getElementById("selProdPais").value = idx;
  document.getElementById("paisPrecioUsd").value = p.precio_base_usd;
  document.getElementById("paisCostoUsd").value = p.costo_base_usd;
  actualizarPais();
  irDesdeMenu("secPaises");
}

function actualizarPais() {
  const cod = document.getElementById("selPais").value;
  const m = PAISES.find(x => x.codigo === cod) || PAISES[0];
  const precio = parseFloat(document.getElementById("paisPrecioUsd").value) || 0;
  const costo = parseFloat(document.getElementById("paisCostoUsd").value) || 0;

  const pLoc = (precio * m.tasa_usd).toFixed(2);
  const eLoc = (m.envio_usd * m.tasa_usd).toFixed(2);
  const ganUsd = (precio - costo - m.envio_usd).toFixed(2);
  const marPct = precio > 0 ? ((parseFloat(ganUsd) / precio) * 100).toFixed(1) : "0.0";

  document.getElementById("pLocal").textContent = `${m.simbolo}${pLoc}`;
  document.getElementById("pEnvio").textContent = `${m.simbolo}${eLoc}`;
  document.getElementById("pMargenUsd").textContent = `$${ganUsd}`;
  document.getElementById("pMargenPct").textContent = `${marPct}%`;

  document.getElementById("detallePais").textContent =
    `Pais: ${m.nombre} (${m.moneda})\n` +
    `Medios de pago: ${m.pagos}\n` +
    `Horario sugerido: ${m.horario}\n` +
    `Llamado a la accion: ${m.cta}`;
}

function copiarTexto(idElem) {
  const el = document.getElementById(idElem);
  if (el && navigator.clipboard && el.textContent) {
    navigator.clipboard.writeText(el.textContent).catch(() => {});
  }
}

function pintarInfo() {
  document.getElementById("txtParaQueSirve").textContent = INFO_APP.para_que_sirve || "";
  document.getElementById("txtComoFunciona").textContent = INFO_APP.como_funciona || "";
  document.getElementById("txtDiferencias").textContent = INFO_APP.diferencia_clave || "";
}

iniciarFigurasGeometricas();
cargarSelectores();
pintarCatalogo();
pintarLanzados();
pintarGrupos();
actualizarLinkWa();
actualizarPais();
pintarInfo();
</script>
</body>
</html>
"""


# ==============================================================================
# 06. RUTAS DE LA PARTE 1 Y FUNCIONES AUXILIARES DE CALCULO
# ==============================================================================
@app.route("/")
def ruta_principal():
    catalogo = obtener_catalogo_completo()
    grupos = obtener_grupos_completos()
    html = (
        HTML_PARTE_1
        .replace("__PAISES_JSON__", json.dumps(PAISES_DISPONIBLES, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__CATALOGO_JSON__", json.dumps(catalogo, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__GRUPOS_JSON__", json.dumps(grupos, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__AJUSTES_JSON__", json.dumps(AJUSTES_PRIVACIDAD_BASE, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__INFO_JSON__", json.dumps(INFO_APLICACION, ensure_ascii=True).replace("</", "<\\/"))
    )
    resp = make_response(html)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.route("/api/p1/cuenta", methods=["POST"])
def ruta_p1_cuenta():
    datos = request.get_json(silent=True) or {}
    correo = validar_correo_limpio(datos.get("correo"))
    usuario = (datos.get("usuario") or "").strip()
    clave = (datos.get("clave") or "").strip()

    if not correo:
        return jsonify({"ok": False, "mensaje": "Correo electronico invalido."}), 400
    if not usuario:
        return jsonify({"ok": False, "mensaje": "Nombre de usuario requerido."}), 400
    if len(clave) < 3:
        return jsonify({"ok": False, "mensaje": "Clave personal minima de 3 caracteres."}), 400

    h = hash_clave(clave, correo)
    db = cargar_db()
    cuentas = db.setdefault("cuentas", {})

    if correo in cuentas:
        reg = cuentas[correo]
        if reg.get("clave_hash") and reg["clave_hash"] != h:
            return jsonify({"ok": False, "mensaje": "Clave personal incorrecta para este correo."}), 403
        reg["usuario"] = usuario
        reg["ultimo_acceso"] = datetime.utcnow().isoformat()
        guardar_db(db)
        return jsonify({
            "ok": True,
            "cuenta": {
                "correo": correo,
                "usuario": reg.get("usuario", usuario),
                "ajustes": reg.get("ajustes", {}),
            },
        })

    ajustes_ini = {a["clave"]: bool(a["activo"]) for a in AJUSTES_PRIVACIDAD_BASE}
    cuentas[correo] = {
        "correo": correo,
        "usuario": usuario,
        "clave_hash": h,
        "creado": datetime.utcnow().isoformat(),
        "ultimo_acceso": datetime.utcnow().isoformat(),
        "ajustes": ajustes_ini,
    }
    guardar_db(db)
    return jsonify({
        "ok": True,
        "cuenta": {
            "correo": correo,
            "usuario": usuario,
            "ajustes": ajustes_ini,
        },
    })


@app.route("/api/p1/lanzar_producto", methods=["POST"])
def ruta_p1_lanzar_producto():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    categoria = (datos.get("categoria") or "Productos y Servicios").strip()
    try:
        precio = float(datos.get("precio_base_usd") or 0)
    except Exception:
        precio = 0.0
    try:
        costo = float(datos.get("costo_base_usd") or 0)
    except Exception:
        costo = 0.0
    problema = (datos.get("problema") or "Necesidad de clientes").strip()
    beneficio = (datos.get("beneficio") or "Solucion directa").strip()
    enlace = (datos.get("enlace_contacto") or "").strip()
    autor = (datos.get("autor") or "Usuario").strip()

    if not nombre or precio <= 0:
        return jsonify({"ok": False, "mensaje": "Nombre y precio validos son obligatorios."}), 400

    db = cargar_db()
    lanzados = db.setdefault("productos_lanzados", [])
    nuevo_id = f"PRD-LANZ-{len(lanzados) + 101}"
    nuevo = armar_producto(
        nuevo_id,
        nombre,
        categoria,
        precio,
        costo,
        problema,
        beneficio,
        autor=autor,
        es_lanzamiento_usuario=True,
        enlace_contacto=enlace,
    )
    lanzados.append(nuevo)
    guardar_db(db)
    return jsonify({"ok": True, "producto": nuevo})


@app.route("/api/p1/grupos/agregar", methods=["POST"])
def ruta_p1_grupos_agregar():
    datos = request.get_json(silent=True) or {}
    canal = (datos.get("canal") or "WhatsApp").strip()
    nombre = (datos.get("nombre") or "").strip()
    url = (datos.get("url") or "").strip()
    descripcion = (datos.get("descripcion") or "Grupo de marketing").strip()

    if not nombre or not (url.startswith("https://") or url.startswith("http://")):
        return jsonify({"ok": False, "mensaje": "Nombre y URL https:// validos requeridos."}), 400

    db = cargar_db()
    grupos = db.setdefault("grupos_personalizados", [])
    nuevo = {
        "id": f"GRP-USR-{len(grupos) + 101}",
        "canal": canal,
        "nombre": nombre,
        "descripcion": descripcion,
        "url": url,
    }
    grupos.append(nuevo)
    guardar_db(db)
    return jsonify({"ok": True, "grupo": nuevo})


def calcular_metricas_campana(presupuesto_usd, cpm_usd, ctr_pct, conv_pct, ticket_usd):
    pres = max(0.0, float(presupuesto_usd))
    cpm = max(0.01, float(cpm_usd))
    ctr = max(0.0, float(ctr_pct)) / 100.0
    conv = max(0.0, float(conv_pct)) / 100.0
    ticket = max(0.0, float(ticket_usd))

    impresiones = int(math.floor((pres / cpm) * 1000.0))
    clics = int(math.floor(impresiones * ctr))
    cpc = round(pres / clics, 2) if clics > 0 else 0.0
    ventas = int(math.floor(clics * conv))
    cpa = round(pres / ventas, 2) if ventas > 0 else 0.0
    ingresos = round(ventas * ticket, 2)
    roas = round(ingresos / pres, 2) if pres > 0 else 0.0

    return {
        "presupuesto_usd": round(pres, 2),
        "impresiones": impresiones,
        "clics": clics,
        "cpc_usd": cpc,
        "ventas_estimadas": ventas,
        "cpa_usd": cpa,
        "ingresos_estimados_usd": ingresos,
        "roas": roas,
    }


def armar_enlace_whatsapp(telefono, mensaje):
    limpio = re.sub(r"[^0-9]", "", telefono or "")
    if not limpio:
        return "https://wa.me/"
    return f"https://wa.me/{limpio}?text={quote_plus((mensaje or '').strip())}"


@app.route("/api/p1/estado", methods=["GET"])
def ruta_p1_estado():
    return jsonify({
        "ok": True,
        "parte": 1,
        "aplicacion": NOMBRE_APP,
        "creador": CREADOR_APP,
        "version": VERSION_APP,
        "total_productos": len(obtener_catalogo_completo()),
        "total_grupos": len(obtener_grupos_completos()),
        "total_paises": len(PAISES_DISPONIBLES),
    })


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
