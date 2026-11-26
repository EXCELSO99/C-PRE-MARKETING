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
