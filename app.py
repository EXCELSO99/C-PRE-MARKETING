import os
import json
import re
import math
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from urllib.parse import quote_plus
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# ==============================================================================
# 01. CONFIGURACION GENERAL DEL SERVIDOR Y PERSISTENCIA (PARTE 1 DE 6)
# ==============================================================================
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
ARCHIVO_DB = os.environ.get("CPRE_MKT_6000_DB", "cpre_marketing_6000_db.json")
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY", "").strip()
SEARCH_API_URL = os.environ.get("SEARCH_API_URL", "https://html.duckduckgo.com/html/").strip()

NOMBRE_APLICACION = "C-Pre Marketing"
CREADOR_APLICACION = "Creaciones Celso"
VERSION_SUITE = "20.0-SUITE-COMPLETA"

PALETA_ESTUDIO = {
    "negro_base": "#090a0d",
    "negro_panel": "#12141a",
    "negro_tarjeta": "#181b23",
    "negro_campo": "#0d0f14",
    "dorado": "#d4af37",
    "dorado_claro": "#f2d379",
    "plateado": "#cbd5e1",
    "borde": "#64748b",
    "blanco": "#f8fafc",
}

AJUSTES_PRIVACIDAD = [
    {
        "clave": "acceso_gratuito_sin_cobros",
        "titulo": "01. Acceso gratuito sin cobros ocultos",
        "descripcion": "Uso libre de la aplicacion sin tarifas ni bloqueos externos.",
        "activo": True,
    },
    {
        "clave": "proteccion_clave_cuenta",
        "titulo": "02. Clave personal por cuenta",
        "descripcion": "Asocia tu correo, nombre de usuario y clave personal para resguardar tu espacio.",
        "activo": True,
    },
    {
        "clave": "separacion_datos_cuenta",
        "titulo": "03. Separacion de datos por cuenta",
        "descripcion": "Cada cuenta guarda sus notas, campanas y registros financieros.",
        "activo": True,
    },
    {
        "clave": "guardado_persistente",
        "titulo": "04. Guardado persistente del progreso",
        "descripcion": "Almacena tus cambios en el archivo de datos del servidor.",
        "activo": True,
    },
    {
        "clave": "sin_rastreo_terceros",
        "titulo": "05. Sin rastreadores publicitarios externos",
        "descripcion": "No incluye scripts de seguimiento de terceros.",
        "activo": True,
    },
    {
        "clave": "correo_en_cabecera",
        "titulo": "06. Correo visible en la barra superior",
        "descripcion": "Muestra el correo de la cuenta activa en la parte superior.",
        "activo": True,
    },
    {
        "clave": "copia_directa_enlaces_copy",
        "titulo": "07. Copia rapida de textos y enlaces",
        "descripcion": "Permite copiar guiones, ofertas y enlaces con un toque.",
        "activo": True,
    },
    {
        "clave": "figuras_geometricas_color",
        "titulo": "08. Figuras geometricas intercambiando color",
        "descripcion": "Muestra figuras geometricas animadas cambiando entre tonos dorados y plateados.",
        "activo": True,
    },
    {
        "clave": "validacion_lanzamientos",
        "titulo": "09. Validacion al lanzar productos",
        "descripcion": "Revisa nombre y precio antes de publicar un producto en el catalogo.",
        "activo": True,
    },
    {
        "clave": "avisos_estado_claros",
        "titulo": "10. Notificaciones de estado",
        "descripcion": "Informa cuando se guarda, carga, busca o lanza un registro.",
        "activo": True,
    },
]

GUIA_APLICACION = {
    "para_que_sirve": (
        "Sirve para buscar productos por palabra clave, pais y precio maximo en el catalogo y en "
        "resultados web publicos permitidos, lanzar y administrar tus propios productos, entrar o "
        "guardar enlaces de grupos de WhatsApp y Google Groups, adaptar precios y pagos por pais, "
        "generar ganchos, anuncios y guiones, planificar tu semana, calcular ventas y ROAS, simular "
        "embudos con CTR/CPC/CPA y guardar tu progreso por cuenta."
    ),
    "como_funciona": (
        "Entras con tu correo, nombre de usuario y clave personal (o revisas Ajustes y Privacidad). "
        "Desde el Menu Principal accedes a cada seccion y regresas cuando quieras con la flecha arriba "
        "a la izquierda o el boton de regreso al menu principal."
    ),
    "que_la_diferencia": (
        "Reune en una sola aplicacion el buscador con filtro por pais y precio, la gestion y "
        "lanzamiento directo de productos del usuario, los enlaces de grupos de WhatsApp y Google, "
        "los anuncios y guiones, el plan semanal, la hoja ROAS, el embudo y el guardado por cuenta."
    ),
}


# ==============================================================================
# 02. PAISES, GRUPOS (WHATSAPP / GOOGLE), PLAN SEMANAL Y SENALES
# ==============================================================================
PAISES_MKT = [
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
        "codigo": "FR",
        "nombre": "Francia",
        "moneda": "EUR",
        "simbolo": "EUR ",
        "tasa_usd": 0.92,
        "envio_usd": 5.5,
        "pagos": "Carte Bancaire, PayPal, Apple Pay, Google Pay",
        "horario": "12:00 - 14:00 y 19:30 - 22:30 CET",
        "cta": "Commandez aujourd hui avec livraison suivie",
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

GRUPOS_BASE = [
    {
        "id": "GRP-WA-01",
        "canal": "WhatsApp",
        "nombre": "Red de Emprendedores y Ventas WhatsApp",
        "descripcion": "Grupo para compartir ofertas, ideas de marketing y contactar compradores.",
        "url": "https://chat.whatsapp.com/",
    },
    {
        "id": "GRP-WA-02",
        "canal": "WhatsApp",
        "nombre": "Creadores de Contenido y Video Corto",
        "descripcion": "Espacio para ganchos, guiones para Reels/TikTok/Shorts y pruebas de anuncios.",
        "url": "https://chat.whatsapp.com/",
    },
    {
        "id": "GRP-GG-01",
        "canal": "Grupos de Google",
        "nombre": "Google Groups · Marketing Digital y Comercio",
        "descripcion": "Debates sobre campanas, segmentacion, precios locales y crecimiento de ventas.",
        "url": "https://groups.google.com/",
    },
    {
        "id": "GRP-GG-02",
        "canal": "Grupos de Google",
        "nombre": "Google Groups · Lanzamiento de Productos",
        "descripcion": "Comunidad para validar ideas de productos, resolver dudas y organizar lanzamientos.",
        "url": "https://groups.google.com/",
    },
]

PLAN_SEMANAL = [
    {
        "dia": "Lunes",
        "objetivo": "Gancho inicial y presentacion",
        "formato": "Video corto (Reels / TikTok / Shorts)",
        "estructura": "Primeros 3 segundos con gancho directo + demostracion del uso.",
        "kpi": "Retencion inicial y reproducciones.",
    },
    {
        "dia": "Martes",
        "objetivo": "Criterios de eleccion",
        "formato": "Carrusel o pieza informativa",
        "estructura": "Que revisar antes de decidir y errores comunes al elegir.",
        "kpi": "Guardados y compartidos.",
    },
    {
        "dia": "Miercoles",
        "objetivo": "Uso en situacion real",
        "formato": "Demostracion practica",
        "estructura": "Mostrar como resuelve el problema en el dia a dia.",
        "kpi": "Comentarios y consultas.",
    },
    {
        "dia": "Jueves",
        "objetivo": "Aclaracion de dudas",
        "formato": "Respuestas frecuentes",
        "estructura": "Explicar precio, moneda local, pagos y tiempos de entrega.",
        "kpi": "Mensajes directos y clics.",
    },
    {
        "dia": "Viernes",
        "objetivo": "Propuesta comercial clara",
        "formato": "Anuncio o publicacion de oferta",
        "estructura": "Beneficio principal + condicion vigente + llamado a la accion.",
        "kpi": "Contactos y pedidos.",
    },
    {
        "dia": "Sabado",
        "objetivo": "Integracion en rutina",
        "formato": "Historia o clip breve",
        "estructura": "Mostrar uso en jornada de descanso o actividad personal.",
        "kpi": "Interaccion y respuestas.",
    },
    {
        "dia": "Domingo",
        "objetivo": "Resumen y cierre semanal",
        "formato": "Recordatorio directo",
        "estructura": "Sintesis de beneficios, pagos y como solicitarlo.",
        "kpi": "Conversiones de cierre.",
    },
]

SENALES_MKT = [
    {
        "titulo": "Claridad desde los primeros segundos",
        "enfoque": "Retencion",
        "detalle": "Ir directo al punto evita que el usuario pase de largo sin entender el valor.",
    },
    {
        "titulo": "Moneda y pagos locales visibles",
        "enfoque": "Conversion",
        "detalle": "Mostrar el equivalente local y los medios de pago habituales reduce dudas.",
    },
    {
        "titulo": "Control de costos y retorno",
        "enfoque": "Finanzas",
        "detalle": "Comparar gasto publicitario, costo unitario y ventas evita perder margen.",
    },
    {
        "titulo": "Seguimiento ordenado por chat",
        "enfoque": "Cierre",
        "detalle": "Contestar con precision y un siguiente paso claro facilita concretar pedidos.",
    },
]


# ==============================================================================
# 03. CATALOGO DE PRODUCTOS, GESTION DE USUARIO Y BUSQUEDA CON PAIS/PRECIO
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
    pais_codigo="VE",
    stock=25,
    estado="Activo",
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
        "pais_codigo": (pais_codigo or "VE").strip().upper(),
        "stock": max(0, int(stock or 0)),
        "estado": (estado or "Activo").strip(),
    }


CATALOGO_BASE = [
    armar_producto(
        "PRD-01",
        "Reloj Deportivo Clasico",
        "Relojes y Accesorios",
        95.00,
        32.00,
        "Necesidad de hora clara, cronometro y control diario",
        "Diseno resistente para uso diario y deportivo",
        "Compradores en Venezuela y mercados latinos",
        "Creaciones Celso",
        False,
        pais_codigo="VE",
        stock=18,
    ),
    armar_producto(
        "PRD-02",
        "Reloj Inteligente Pulsera Metalica",
        "Relojes y Accesorios",
        100.00,
        35.00,
        "Falta de aviso practico de llamadas y rutinas",
        "Pantalla nitida con correa comoda y bateria duradera",
        "Usuarios de relojes en Venezuela",
        "Creaciones Celso",
        False,
        pais_codigo="VE",
        stock=12,
    ),
    armar_producto(
        "PRD-03",
        "Camiseta Algodon Corte Urbano",
        "Ropa y Camisetas",
        22.00,
        6.50,
        "Prendas que pierden forma o comodidad tras lavados",
        "Algodon suave con costura firme para uso cotidiano",
        "Compradores en Francia y Europa",
        "Creaciones Celso",
        False,
        pais_codigo="FR",
        stock=40,
    ),
    armar_producto(
        "PRD-04",
        "Camiseta Basica Cuello Redondo",
        "Ropa y Camisetas",
        18.50,
        5.20,
        "Buscar camisetas versátiles para combinar a diario",
        "Tela transpirable de ajuste limpio en varios talles",
        "Publico de moda casual en Francia",
        "Creaciones Celso",
        False,
        pais_codigo="FR",
        stock=55,
    ),
    armar_producto(
        "PRD-05",
        "Audifonos Inalambricos ANC Pro",
        "Tecnologia y Gadgets",
        49.90,
        14.50,
        "Ruido externo y cables incomodos al moverte",
        "Audio inalambrico nitido con reduccion de ruido y buena bateria",
        "Estudiantes, trabajadores remotos y viajeros",
        "Creaciones Celso",
        False,
        pais_codigo="VE",
        stock=30,
    ),
    armar_producto(
        "PRD-06",
        "Termo Acero Termico 1L",
        "Hogar y Estilo de Vida",
        24.90,
        6.20,
        "Bebidas que pierden temperatura durante el dia",
        "Conserva temperatura por horas con cierre seguro",
        "Estudiantes, conductores y oficina",
        "Creaciones Celso",
        False,
        pais_codigo="VE",
        stock=24,
    ),
]


# ==============================================================================
# 04. PERSISTENCIA, CUENTAS, BUSQUEDA WEB PUBLICA Y MOTOR DE MARKETING
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
    lista = list(GRUPOS_BASE)
    for g in db.get("grupos_personalizados", []):
        if isinstance(g, dict) and g.get("nombre"):
            lista.append(g)
    return lista


def obtener_pais_mkt(codigo):
    cod = (codigo or "VE").strip().upper()
    for p in PAISES_MKT:
        if p["codigo"] == cod:
            return p
    return PAISES_MKT[0]


def extraer_precio_aprox(texto):
    m = re.search(r"(?:\$|€|eur|usd|mx\$|col\$|ar\$|clp\$|s/)\s*([0-9]+(?:[.,][0-9]{1,2})?)", (texto or "").lower())
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except Exception:
        return None


def buscar_productos_web_publicos(consulta, pais_nombre, precio_max=0.0):
    q_limpia = (consulta or "").strip()
    if not q_limpia:
        return []

    partes_q = [q_limpia]
    if pais_nombre and normalizar_texto(pais_nombre) not in normalizar_texto(q_limpia):
        partes_q.append(pais_nombre)
    if precio_max and precio_max > 0:
        partes_q.append(f"{precio_max:g}")
    query_final = " ".join(partes_q)

    resultados = []
    try:
        if SEARCH_API_KEY and "serper" in SEARCH_API_URL.lower():
            req = urllib.request.Request(
                SEARCH_API_URL,
                data=json.dumps({"q": query_final, "num": 8}).encode("utf-8"),
                headers={
                    "X-API-KEY": SEARCH_API_KEY,
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="replace"))
                for item in payload.get("organic", [])[:8]:
                    titulo = (item.get("title") or "").strip()
                    url = (item.get("link") or "").strip()
                    resumen = (item.get("snippet") or "").strip()
                    if titulo and url.startswith("http"):
                        resultados.append({
                            "titulo": titulo,
                            "url": url,
                            "resumen": resumen,
                            "precio_detectado": extraer_precio_aprox(f"{titulo} {resumen}"),
                            "fuente": "Web Publica",
                        })
        else:
            url_busqueda = f"{SEARCH_API_URL}?q={quote_plus(query_final)}"
            req = urllib.request.Request(
                url_busqueda,
                headers={"User-Agent": "Mozilla/5.0 (compatible; CPreMarketingBot/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                html_raw = resp.read().decode("utf-8", errors="replace")
                enlaces = re.findall(
                    r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                    html_raw,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                snippets = re.findall(
                    r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>|<div[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</div>',
                    html_raw,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                for idx, (href, tit_html) in enumerate(enlaces[:8]):
                    titulo = re.sub(r"<[^>]+>", "", tit_html).strip()
                    snip_raw = ""
                    if idx < len(snippets):
                        snip_raw = snippets[idx][0] or snippets[idx][1] or ""
                    resumen = re.sub(r"<[^>]+>", "", snip_raw).strip()
                    url_final = href.strip()
                    if "uddg=" in url_final:
                        m_u = re.search(r"uddg=([^&]+)", url_final)
                        if m_u:
                            url_final = urllib.parse.unquote(m_u.group(1))
                    if titulo and url_final.startswith("http"):
                        resultados.append({
                            "titulo": titulo,
                            "url": url_final,
                            "resumen": resumen,
                            "precio_detectado": extraer_precio_aprox(f"{titulo} {resumen}"),
                            "fuente": "Resultados Web Publicos",
                        })
    except Exception:
        return []

    filtrados = []
    for r_item in resultados:
        p_det = r_item.get("precio_detectado")
        if precio_max and precio_max > 0 and p_det is not None and p_det > precio_max:
            continue
        filtrados.append(r_item)
    return filtrados


def construir_kit_marketing(
    nombre,
    categoria,
    precio_usd,
    costo_usd,
    beneficio,
    problema,
    publico,
    codigo_pais,
    formula,
):
    pais = obtener_pais_mkt(codigo_pais)
    precio_local = round(precio_usd * pais["tasa_usd"], 2)
    envio_local = round(pais["envio_usd"] * pais["tasa_usd"], 2)
    margen_usd = round(precio_usd - costo_usd - pais["envio_usd"], 2)

    ganchos = [
        f"Si buscas {categoria.lower()}, mira como funciona {nombre} en pocos segundos.",
        f"Deja atras {problema.lower()} con {nombre}.",
        f"Asi se presenta {nombre} en {pais['nombre']} desde {pais['simbolo']}{precio_local}.",
        f"Una forma practica de lograr {beneficio.lower()} en el dia a dia.",
        f"Mira la diferencia real al usar {nombre}.",
    ]

    if formula == "PAS":
        copy_txt = (
            f"[PROBLEMA] {problema}\n"
            f"[AGITACION] Seguir con {problema.lower()} resta comodidad en tu rutina.\n"
            f"[SOLUCION] {nombre} ofrece {beneficio.lower()}.\n"
            f"[{pais['nombre'].upper()}] Referencia: {pais['simbolo']}{precio_local} ({pais['moneda']}) | Pagos: {pais['pagos']}.\n"
            f"[ACCION] {pais['cta']}."
        )
    elif formula == "BAB":
        copy_txt = (
            f"[ANTES] Enfrentar {problema.lower()}.\n"
            f"[DESPUES] Contar con {beneficio.lower()} de forma practica.\n"
            f"[PUENTE] {nombre} pensado para {publico.lower()}.\n"
            f"[{pais['nombre'].upper()}] {pais['simbolo']}{precio_local} ({pais['moneda']}) | {pais['cta']}."
        )
    elif formula == "4U":
        copy_txt = (
            f"[HOY] Enfoque para {pais['nombre']} (horario sugerido: {pais['horario']}).\n"
            f"[PROPUESTA] {nombre}: {beneficio}.\n"
            f"[PRECIO] {pais['simbolo']}{precio_local} ({pais['moneda']}).\n"
            f"[UTILIDAD] Atiende {problema.lower()}. {pais['cta']}."
        )
    else:
        copy_txt = (
            f"[ATENCION] {ganchos[0]}\n"
            f"[INTERES] {nombre} aborda {problema.lower()} mediante {beneficio.lower()}.\n"
            f"[DESEO] Ideal para {publico.lower()} en {pais['nombre']}. Medios: {pais['pagos']}.\n"
            f"[ACCION] Precio: {pais['simbolo']}{precio_local} ({pais['moneda']}). {pais['cta']}."
        )

    guion = (
        f"00:00 - 00:03 [GANCHO]: '{ganchos[1]}'\n"
        f"00:03 - 00:10 [PROBLEMA]: Muestra de forma breve '{problema}'.\n"
        f"00:10 - 00:20 [DEMOSTRACION]: Presenta '{nombre}' y su beneficio '{beneficio}'.\n"
        f"00:20 - 00:26 [CIERRE]: '{pais['cta']} ({pais['simbolo']}{precio_local})'."
    )

    return {
        "producto": nombre,
        "categoria": categoria,
        "pais": pais,
        "precio_usd": precio_usd,
        "precio_local": precio_local,
        "envio_local": envio_local,
        "margen_usd": margen_usd,
        "ganchos": ganchos,
        "copy_principal": copy_txt,
        "guion_video": guion,
    }


def calcular_embudo_metricas(presupuesto_usd, cpm_usd, ctr_pct, conv_pct, ticket_usd):
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
    facturacion = round(ventas * ticket, 2)
    roas = round(facturacion / pres, 2) if pres > 0 else 0.0

    return {
        "presupuesto_usd": round(pres, 2),
        "impresiones": impresiones,
        "clics": clics,
        "cpc_usd": cpc,
        "ventas": ventas,
        "cpa_usd": cpa,
        "facturacion_usd": facturacion,
        "roas": roas,
    }


def armar_url_whatsapp(telefono, mensaje):
    limpio = re.sub(r"[^0-9]", "", telefono or "")
    if not limpio:
        return "https://wa.me/"
    return f"https://wa.me/{limpio}?text={quote_plus((mensaje or '').strip())}"
# ==============================================================================
# 05. GESTION DE PRODUCTOS DEL USUARIO Y EVALUACION FINANCIERA (PARTE 2)
# ==============================================================================
def actualizar_producto_lanzado(item_id, cambios):
    db = cargar_db()
    lanzados = db.setdefault("productos_lanzados", [])
    for idx, prod in enumerate(lanzados):
        if prod.get("id") == item_id:
            nombre = (cambios.get("nombre") or prod.get("nombre") or "").strip()
            categoria = (cambios.get("categoria") or prod.get("categoria") or "General").strip()
            try:
                precio = float(cambios.get("precio_base_usd", prod.get("precio_base_usd", 0)))
            except Exception:
                precio = float(prod.get("precio_base_usd", 0))
            try:
                costo = float(cambios.get("costo_base_usd", prod.get("costo_base_usd", 0)))
            except Exception:
                costo = float(prod.get("costo_base_usd", 0))
            problema = (cambios.get("problema") or prod.get("problema") or "").strip()
            beneficio = (cambios.get("beneficio") or prod.get("beneficio") or "").strip()
            publico = (cambios.get("publico") or prod.get("publico") or "Publico general").strip()
            enlace = (cambios.get("enlace_contacto") if "enlace_contacto" in cambios else prod.get("enlace_contacto", "")).strip()
            pais_codigo = (cambios.get("pais_codigo") or prod.get("pais_codigo") or "VE").strip().upper()
            try:
                stock = max(0, int(cambios.get("stock", prod.get("stock", 10))))
            except Exception:
                stock = int(prod.get("stock", 10))
            estado = (cambios.get("estado") or prod.get("estado") or "Activo").strip()

            if not nombre or precio <= 0:
                return None

            actualizado = armar_producto(
                prod.get("id"),
                nombre,
                categoria,
                precio,
                costo,
                problema,
                beneficio,
                publico=publico,
                autor=prod.get("autor", "Usuario"),
                es_lanzamiento_usuario=True,
                enlace_contacto=enlace,
                pais_codigo=pais_codigo,
                stock=stock,
                estado=estado,
            )
            lanzados[idx] = actualizado
            guardar_db(db)
            return actualizado
    return None


def eliminar_producto_lanzado(item_id):
    db = cargar_db()
    lanzados = db.setdefault("productos_lanzados", [])
    antes = len(lanzados)
    db["productos_lanzados"] = [p for p in lanzados if p.get("id") != item_id]
    if len(db["productos_lanzados"]) < antes:
        guardar_db(db)
        return True
    return False


def evaluar_oportunidad_producto(precio_usd, costo_usd, envio_usd=3.5, comision_pct=5.0):
    p = max(0.0, float(precio_usd or 0))
    c = max(0.0, float(costo_usd or 0))
    env = max(0.0, float(envio_usd or 0))
    com = round(p * (max(0.0, float(comision_pct or 0)) / 100.0), 2)
    ganancia_neta = round(p - c - env - com, 2)
    margen_real_pct = round((ganancia_neta / p) * 100, 1) if p > 0 else 0.0
    cpa_maximo = round(max(0.0, ganancia_neta * 0.65), 2)

    if margen_real_pct >= 35:
        diagnostico = "Margen solido para escalar pruebas de trafico y ofertas."
    elif margen_real_pct >= 18:
        diagnostico = "Margen moderado: cuida el CPA y optimiza ticket o combos."
    else:
        diagnostico = "Margen ajustado: sube el valor percibido, arma packs o reduce costos."

    return {
        "precio_usd": round(p, 2),
        "costo_usd": round(c, 2),
        "envio_usd": round(env, 2),
        "comision_usd": com,
        "ganancia_neta_usd": ganancia_neta,
        "margen_real_pct": margen_real_pct,
        "cpa_maximo_recomendado_usd": cpa_maximo,
        "diagnostico": diagnostico,
    }


# ==============================================================================
# 06. INTERFAZ WEB CON SPLASH DE 5 SEGUNDOS ($1 AL CENTRO) (PARTE 2)
# ==============================================================================
HTML_PARTE_DOS = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-Pre Marketing · Suite de Negocios y Campanas</title>
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
  padding-bottom: 68px;
}

#canvasFiguras {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* PANTALLA INICIAL PREVIA DE 5 SEGUNDOS CON LOGO $1 AL CENTRO */
#vistaSplash {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: radial-gradient(circle at center, rgba(24, 27, 35, 0.96) 0%, rgba(9, 10, 13, 0.99) 75%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  text-align: center;
}

.logo-dolar-uno {
  width: 128px;
  height: 128px;
  border-radius: 28px;
  background: linear-gradient(145deg, #1b1f2b, #0c0e14);
  border: 2px solid var(--dorado);
  box-shadow: 0 0 28px rgba(212, 175, 55, 0.28), inset 0 0 18px rgba(203, 213, 225, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 54px;
  font-weight: 700;
  color: var(--dorado-claro);
  letter-spacing: -2px;
  animation: pulsoLogoUno 1.6s ease-in-out infinite;
}

@keyframes pulsoLogoUno {
  0%, 100% {
    transform: scale(1);
    border-color: var(--dorado);
    color: var(--dorado-claro);
  }
  50% {
    transform: scale(1.05);
    border-color: var(--plateado);
    color: var(--blanco);
  }
}

.splash-sub {
  margin-top: 14px;
  font-size: 14px;
  font-weight: 600;
  color: var(--plateado);
}

.splash-contador {
  margin-top: 6px;
  font-size: 13px;
  color: var(--dorado);
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
  max-width: 1060px;
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
  min-height: 98px;
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

.scroll-tabla {
  width: 100%;
  overflow-x: auto;
  margin-top: 10px;
}

table.hoja-mkt {
  width: 100%;
  min-width: 660px;
  border-collapse: collapse;
}

table.hoja-mkt th,
table.hoja-mkt td {
  border: 1px solid var(--borde);
  padding: 8px;
  text-align: center;
}

table.hoja-mkt th {
  background-color: var(--campo);
  color: var(--dorado);
  font-size: 13px;
}

table.hoja-mkt td input {
  margin: 0;
  height: 42px;
  font-size: 14.5px;
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

<!-- PANTALLA INICIAL PREVIA DE 5 SEGUNDOS CON LOGO $1 AL CENTRO -->
<div id="vistaSplash" role="status" aria-live="polite">
  <div class="logo-dolar-uno">$1</div>
  <div class="splash-sub">Preparando espacio de trabajo y campanas...</div>
  <div class="splash-contador" id="splashContador">Entrando en 5s...</div>
  <button type="button" class="btn-plata" style="max-width:220px;margin-top:14px;" onclick="cerrarSplashInmediato()">CONTINUAR AHORA</button>
</div>
"""
<!-- INICIO: CORREO, NOMBRE DE USUARIO, CLAVE PERSONAL Y AJUSTES/PRIVACIDAD -->
<section id="vistaInicio" class="inicio-centro oculto">
  <div class="wrap-app" style="width:100%;max-width:560px;">
    <div class="card-box card-oro">
      <h2>C-Pre Marketing</h2>
      <div style="font-size:13px;font-weight:700;color:var(--plateado);margin-bottom:8px;">Centro de Operaciones y Ventas</div>
      <p class="desc-texto">
        Ingresa tu correo, nombre de usuario y clave personal para guardar y recuperar tu progreso.
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
    <p class="desc-texto">Configuracion de privacidad, cuenta gratuita, enlaces y figuras geometricas.</p>
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
        <div class="app-sub">Operaciones y Ventas</div>
      </div>
    </div>
    <div class="badge-cuenta" id="badgeCuenta">Cuenta</div>
  </div>

  <nav class="nav-scroll" aria-label="Secciones de la aplicacion">
    <button type="button" class="nav-item activa" data-sec="secMenu" onclick="abrirSeccion('secMenu', this)">Menu Principal</button>
    <button type="button" class="nav-item" data-sec="secBuscar" onclick="abrirSeccion('secBuscar', this)">Buscar Productos</button>
    <button type="button" class="nav-item" data-sec="secLanzar" onclick="abrirSeccion('secLanzar', this)">Manejar Mis Productos</button>
    <button type="button" class="nav-item" data-sec="secGrupos" onclick="abrirSeccion('secGrupos', this)">WhatsApp y Google</button>
    <button type="button" class="nav-item" data-sec="secPaises" onclick="abrirSeccion('secPaises', this)">Paises y Monedas</button>
    <button type="button" class="nav-item" data-sec="secCopy" onclick="abrirSeccion('secCopy', this)">Anuncios y Guiones</button>
    <button type="button" class="nav-item" data-sec="secPlan" onclick="abrirSeccion('secPlan', this)">Plan Semanal</button>
    <button type="button" class="nav-item" data-sec="secRoas" onclick="abrirSeccion('secRoas', this)">Hoja ROAS</button>
    <button type="button" class="nav-item" data-sec="secEmbudo" onclick="abrirSeccion('secEmbudo', this)">Embudo y CPA</button>
    <button type="button" class="nav-item" data-sec="secOfertas" onclick="abrirSeccion('secOfertas', this)">Audiencias y Ofertas</button>
    <button type="button" class="nav-item" data-sec="secProgreso" onclick="abrirSeccion('secProgreso', this)">Progreso</button>
    <button type="button" class="nav-item" data-sec="secGuia" onclick="abrirSeccion('secGuia', this)">Para Que Sirve</button>
  </nav>
</header>

<main id="mainApp" class="wrap-app oculto">

  <!-- MENU PRINCIPAL -->
  <section id="secMenu" class="sec-panel card-box card-oro">
    <h2>Menu Principal</h2>
    <p class="desc-texto">Busca productos por pais y precio, crea y administra tus propios productos, entra a grupos de WhatsApp y Google Groups, y gestiona tus campanas.</p>

    <div class="grid-3">
      <div class="kpi-card"><span>Productos</span><strong id="kpiMenuProds">0</strong></div>
      <div class="kpi-card"><span>Grupos / Enlaces</span><strong id="kpiMenuGrupos">0</strong></div>
      <div class="kpi-card"><span>Cuenta</span><strong id="kpiMenuCuenta">Activa</strong></div>
    </div>

    <div class="grid-2" style="margin-top:12px;">
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secBuscar')">1. Buscar Productos (Pais y Precio)</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secLanzar')">2. Manejar y Lanzar Mis Productos</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secGrupos')">3. Links WhatsApp y Google Groups</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secPaises')">4. Paises, Monedas y Pagos</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secCopy')">5. Anuncios, Ganchos y Guiones</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secPlan')">6. Plan Semanal y Senales</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secRoas')">7. Hoja de Ventas y ROAS</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secEmbudo')">8. Simulador de Embudo y CPA</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secOfertas')">9. Audiencias y Ofertas</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secProgreso')">10. Guardado de Progreso</button>
      <button type="button" class="btn-plata" onclick="irDesdeMenu('secGuia')">11. Para Que Sirve y Diferencias</button>
      <button type="button" class="btn-plata" onclick="verAjustesPrivacidad()">12. Ajustes y Privacidad</button>
    </div>
  </section>

  <!-- BUSCAR PRODUCTOS POR PAIS, PRECIO Y WEB PUBLICA -->
  <section id="secBuscar" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Buscar Productos por Pais y Precio</h2>
    </div>
    <p class="desc-texto">Selecciona un pais, escribe el producto (por ejemplo: relojes o camisetas), filtra por precio maximo y consulta resultados en catalogo y web publica permitida.</p>

    <div class="grid-3">
      <div>
        <label for="selPaisBuscar">Pais:</label>
        <select id="selPaisBuscar" onchange="pintarCatalogo()"></select>
      </div>
      <div>
        <label for="txtBuscarProd">Producto o palabra clave:</label>
        <input type="text" id="txtBuscarProd" placeholder="Ej. relojes, camisetas..." oninput="pintarCatalogo()">
      </div>
      <div>
        <label for="numPrecioMax">Precio maximo (0 = sin tope):</label>
        <input type="number" id="numPrecioMax" value="0" min="0" step="1" oninput="pintarCatalogo()">
      </div>
    </div>

    <div class="grid-2" style="margin-top:8px;">
      <div>
        <label for="selCatBuscar">Categoria del catalogo:</label>
        <select id="selCatBuscar" onchange="pintarCatalogo()">
          <option value="TODAS">Todas las categorias</option>
        </select>
      </div>
      <div style="display:flex;align-items:flex-end;">
        <button type="button" class="btn-oro" style="margin-top:0;" onclick="buscarEnWebPublica()">BUSCAR EN WEB PUBLICA</button>
      </div>
    </div>

    <div id="estadoBusqueda" class="estado-txt"></div>
    <h3>Productos en Catalogo y Lanzamientos</h3>
    <div id="listaCatalogo"></div>

    <h3>Resultados Web Publicos Permitidos</h3>
    <div id="listaWebResultados"></div>
  </section>

  <!-- MANEJAR Y LANZAR MIS PRODUCTOS -->
  <section id="secLanzar" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Manejar y Lanzar Mis Productos</h2>
    </div>
    <p class="desc-texto">Crea, edita, controla stock o elimina tus propios productos y servicios dentro de la aplicacion.</p>

    <input type="hidden" id="lanEditId" value="">

    <div class="grid-3">
      <div>
        <label for="lanNombre">Nombre del producto:</label>
        <input type="text" id="lanNombre" placeholder="Ej. Reloj Casual Acero">
      </div>
      <div>
        <label for="lanCategoria">Categoria:</label>
        <input type="text" id="lanCategoria" value="Productos y Servicios">
      </div>
      <div>
        <label for="lanPais">Pais principal:</label>
        <select id="lanPais"></select>
      </div>
    </div>

    <div class="grid-3">
      <div>
        <label for="lanPrecio">Precio de venta (USD):</label>
        <input type="number" id="lanPrecio" value="25" step="0.1">
      </div>
      <div>
        <label for="lanCosto">Costo base (USD):</label>
        <input type="number" id="lanCosto" value="5" step="0.1">
      </div>
      <div>
        <label for="lanStock">Unidades disponibles:</label>
        <input type="number" id="lanStock" value="20" step="1">
      </div>
    </div>

    <label for="lanProblema">Problema que resuelve:</label>
    <input type="text" id="lanProblema" placeholder="Ej. Falta de orden al responder consultas">

    <label for="lanBeneficio">Beneficio principal:</label>
    <input type="text" id="lanBeneficio" placeholder="Ej. Respuestas claras y seguimiento constante">

    <label for="lanEnlace">Enlace de contacto, WhatsApp o pagina (opcional):</label>
    <input type="text" id="lanEnlace" placeholder="https://wa.me/... o enlace de tu oferta">

    <div class="grid-2">
      <button type="button" class="btn-oro" id="btnGuardarLanzamiento" onclick="lanzarProductoUsuario()">LANZAR PRODUCTO A LA APLICACION</button>
      <button type="button" class="btn-plata" onclick="limpiarFormularioProducto()">LIMPIAR FORMULARIO</button>
    </div>
    <div id="msgLanzar" class="estado-txt"></div>

    <h3>Mis Productos Administrados</h3>
    <div id="listaLanzados"></div>
  </section>
