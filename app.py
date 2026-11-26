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
  <!-- LINKS A GRUPOS DE WHATSAPP Y GOOGLE GROUPS -->
  <section id="secGrupos" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Links de Grupos de WhatsApp y Google Groups</h2>
    </div>
    <p class="desc-texto">Abre enlaces de WhatsApp o Google Groups, arma un enlace directo de WhatsApp y guarda tus propios grupos para contactar clientes, socios o comunidades.</p>

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

    <h3>Grupos y Comunidades</h3>
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
          <input type="text" id="grpNombre" placeholder="Ej. Grupo Emprendedores">
        </div>
      </div>
      <label for="grpUrl">URL del grupo (https://...):</label>
      <input type="text" id="grpUrl" placeholder="https://chat.whatsapp.com/... o https://groups.google.com/...">
      <label for="grpDesc">Descripcion breve:</label>
      <input type="text" id="grpDesc" placeholder="Tema principal del grupo">
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
    <p class="desc-texto">Calcula conversion estimada, envio, margen y medios de pago por pais para adaptar tus publicaciones a cada mercado.</p>

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
        <input type="number" id="paisPrecioUsd" value="95.00" step="0.1" oninput="actualizarPais()">
      </div>
      <div>
        <label for="paisCostoUsd">Costo base (USD):</label>
        <input type="number" id="paisCostoUsd" value="32.00" step="0.1" oninput="actualizarPais()">
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

  <!-- ANUNCIOS, GANCHOS Y GUIONES -->
  <section id="secCopy" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Anuncios, Ganchos y Guiones</h2>
    </div>
    <p class="desc-texto">Genera ganchos de apertura, anuncios estructurados, guiones de video corto y mensajes base para chat.</p>

    <div class="grid-2">
      <div>
        <label for="cNombre">Producto o servicio:</label>
        <input type="text" id="cNombre" value="Reloj Deportivo Clasico">
      </div>
      <div>
        <label for="cCat">Categoria:</label>
        <input type="text" id="cCat" value="Relojes y Accesorios">
      </div>
    </div>

    <div class="grid-3">
      <div>
        <label for="cPais">Pais:</label>
        <select id="cPais"></select>
      </div>
      <div>
        <label for="cFormula">Formula:</label>
        <select id="cFormula">
          <option value="AIDA">AIDA</option>
          <option value="PAS">PAS</option>
          <option value="BAB">BAB</option>
          <option value="4U">4U</option>
        </select>
      </div>
      <div>
        <label for="cPrecio">Precio USD:</label>
        <input type="number" id="cPrecio" value="95.00" step="0.1">
      </div>
    </div>

    <label for="cPublico">Publico objetivo:</label>
    <input type="text" id="cPublico" value="Compradores que buscan relojes practicos y duraderos">

    <label for="cProblema">Problema:</label>
    <input type="text" id="cProblema" value="Necesidad de hora clara, cronometro y control diario">

    <label for="cBeneficio">Beneficio principal:</label>
    <input type="text" id="cBeneficio" value="Diseno resistente para uso diario y deportivo">

    <button type="button" class="btn-oro" onclick="generarTextos()">GENERAR GANCHOS, COPY Y GUION</button>

    <h3>Ganchos de Apertura</h3>
    <div id="resGanchos" class="caja-salida">Pulsa el boton para generar ganchos.</div>

    <h3>Texto de Anuncio</h3>
    <div id="resCopy" class="caja-salida">Aqui aparecera el anuncio.</div>
    <button type="button" class="btn-plata" onclick="copiarTexto('resCopy')">COPIAR ANUNCIO</button>

    <h3>Guion de Video Corto</h3>
    <div id="resGuion" class="caja-salida">Aqui aparecera el guion de video.</div>
    <button type="button" class="btn-plata" onclick="copiarTexto('resGuion')">COPIAR GUION</button>

    <h3>Mensaje Base para Chat / WhatsApp</h3>
    <div id="resChat" class="caja-salida">Aqui aparecera la respuesta base para chat.</div>
    <button type="button" class="btn-plata" onclick="copiarTexto('resChat')">COPIAR MENSAJE CHAT</button>
  </section>

  <!-- PLAN SEMANAL Y SENALES -->
  <section id="secPlan" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Plan Semanal y Senales</h2>
    </div>
    <p class="desc-texto">Rutina diaria de publicacion y criterios de seguimiento para mantener constancia en tus campanas.</p>
    <div id="listaPlan"></div>
    <h3>Senales de Campana</h3>
    <div id="listaSenales"></div>
  </section>

  <!-- HOJA ROAS -->
  <section id="secRoas" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Hoja de Ventas, Costos y ROAS</h2>
    </div>
    <p class="desc-texto">Completa hasta 8 filas con precio, costo unitario, unidades e inversion en anuncios para revisar utilidad y retorno.</p>

    <div class="scroll-tabla">
      <table class="hoja-mkt">
        <thead>
          <tr>
            <th>Fila</th>
            <th>Precio ($)</th>
            <th>Costo ($)</th>
            <th>Unidades</th>
            <th>Ads ($)</th>
            <th>Utilidad ($)</th>
            <th>ROAS</th>
          </tr>
        </thead>
        <tbody id="cuerpoRoas"></tbody>
      </table>
    </div>

    <div class="grid-4" style="margin-top:10px;">
      <div class="kpi-card"><span>Ingresos</span><strong id="rIngresos">$0.00</strong></div>
      <div class="kpi-card"><span>Ads</span><strong id="rAds">$0.00</strong></div>
      <div class="kpi-card"><span>Utilidad</span><strong id="rUtilidad">$0.00</strong></div>
      <div class="kpi-card"><span>ROAS Global</span><strong id="rRoas">0.00x</strong></div>
    </div>

    <button type="button" class="btn-oro" onclick="calcularRoas()">CALCULAR HOJA</button>
  </section>

  <!-- EMBUDO Y CPA -->
  <section id="secEmbudo" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Simulador de Embudo (CTR, CPC, Conversion y CPA)</h2>
    </div>
    <p class="desc-texto">Estima impresiones, clics, costo por clic, ventas, CPA y retorno antes de invertir fuerte.</p>

    <div class="grid-2">
      <div>
        <label for="ePres">Presupuesto ($ USD):</label>
        <input type="number" id="ePres" value="100" step="1" oninput="calcularEmbudo()">
      </div>
      <div>
        <label for="eCpm">CPM estimado ($ por 1,000 impresiones):</label>
        <input type="number" id="eCpm" value="8.5" step="0.1" oninput="calcularEmbudo()">
      </div>
    </div>

    <div class="grid-3">
      <div>
        <label for="eCtr">CTR (%):</label>
        <input type="number" id="eCtr" value="2.2" step="0.1" oninput="calcularEmbudo()">
      </div>
      <div>
        <label for="eConv">Conversion (%):</label>
        <input type="number" id="eConv" value="3.5" step="0.1" oninput="calcularEmbudo()">
      </div>
      <div>
        <label for="eTicket">Ticket promedio ($):</label>
        <input type="number" id="eTicket" value="95.0" step="0.1" oninput="calcularEmbudo()">
      </div>
    </div>

    <div class="grid-4" style="margin-top:12px;">
      <div class="kpi-card"><span>Impresiones</span><strong id="eImp">0</strong></div>
      <div class="kpi-card"><span>Clics</span><strong id="eClics">0</strong></div>
      <div class="kpi-card"><span>CPC</span><strong id="eCpc">$0.00</strong></div>
      <div class="kpi-card"><span>Ventas Est.</span><strong id="eVentas">0</strong></div>
    </div>

    <div class="grid-3" style="margin-top:8px;">
      <div class="kpi-card"><span>CPA</span><strong id="eCpa">$0.00</strong></div>
      <div class="kpi-card"><span>Facturacion</span><strong id="eFact">$0.00</strong></div>
      <div class="kpi-card"><span>ROAS</span><strong id="eRoas">0.00x</strong></div>
    </div>

    <div id="eLectura" class="caja-salida"></div>
  </section>

  <!-- AUDIENCIAS Y OFERTAS -->
  <section id="secOfertas" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Audiencias y Constructor de Ofertas</h2>
    </div>
    <p class="desc-texto">Define perfiles por categoria y redacta ofertas claras para publicar o enviar por chat.</p>

    <div class="grid-2">
      <div>
        <label for="oCat">Categoria:</label>
        <select id="oCat" onchange="actualizarOferta()">
          <option value="relojes">Relojes y Accesorios</option>
          <option value="ropa">Ropa y Camisetas</option>
          <option value="tech">Tecnologia y Gadgets</option>
          <option value="home">Hogar y Estilo de Vida</option>
          <option value="biz">Negocios y Servicios</option>
        </select>
      </div>
      <div>
        <label for="oTipo">Tipo de oferta:</label>
        <select id="oTipo" onchange="actualizarOferta()">
          <option value="pack">Pack de 2 unidades</option>
          <option value="bono">Producto con complemento</option>
          <option value="envio">Condicion de envio y respaldo</option>
          <option value="flash">Promocion temporal</option>
        </select>
      </div>
    </div>

    <div class="grid-2">
      <div>
        <label for="oProd">Producto o servicio:</label>
        <input type="text" id="oProd" value="Reloj Deportivo Clasico" oninput="actualizarOferta()">
      </div>
      <div>
        <label for="oPrecio">Precio base ($ USD):</label>
        <input type="number" id="oPrecio" value="95.00" step="0.1" oninput="actualizarOferta()">
      </div>
    </div>

    <h3>Audiencia Sugerida</h3>
    <div id="resAud" class="caja-salida"></div>

    <h3>Oferta Lista</h3>
    <div id="resOferta" class="caja-salida"></div>
    <button type="button" class="btn-plata" onclick="copiarTexto('resOferta')">COPIAR OFERTA</button>
  </section>

  <!-- GUARDADO DE PROGRESO -->
  <section id="secProgreso" class="sec-panel card-box oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Cuenta y Guardado de Progreso</h2>
    </div>
    <p class="desc-texto">Guarda o recupera tus notas, datos de campana y hoja de ROAS asociados a tu cuenta.</p>

    <div class="grid-2">
      <div>
        <label for="pCorreo">Correo:</label>
        <input type="email" id="pCorreo" placeholder="tu_correo@ejemplo.com">
      </div>
      <div>
        <label for="pUsuario">Nombre de usuario:</label>
        <input type="text" id="pUsuario" placeholder="Nombre de usuario">
      </div>
    </div>

    <label for="pNotas">Notas de campana:</label>
    <textarea id="pNotas" placeholder="Escribe notas, ideas, presupuestos o seguimientos..."></textarea>

    <div class="grid-2">
      <button type="button" class="btn-oro" onclick="guardarProgreso()">GUARDAR PROGRESO</button>
      <button type="button" class="btn-plata" onclick="cargarProgreso()">CARGAR PROGRESO</button>
    </div>
    <div id="msgProg" class="estado-txt"></div>
  </section>

  <!-- GUIA: PARA QUE SIRVE, COMO FUNCIONA Y DIFERENCIAS -->
  <section id="secGuia" class="sec-panel card-box card-oro oculto">
    <div class="sub-header-bar">
      <button type="button" class="btn-atras" onclick="irDesdeMenu('secMenu')">&#8592; Menu</button>
      <h2 style="margin:0;">Para Que Sirve, Como Funciona y Diferencias</h2>
    </div>

    <h3>Para que sirve esta aplicacion</h3>
    <div id="gSirve" class="caja-salida"></div>

    <h3>Como funciona</h3>
    <div id="gFunciona" class="caja-salida"></div>

    <h3>En que se diferencia de otras aplicaciones</h3>
    <div id="gDiferencia" class="caja-salida"></div>
  </section>

</main>

<div class="firma-fija">Operaciones y Ventas</div>

<script id="jsonPaises" type="application/json">__PAISES_JSON__</script>
<script id="jsonCatalogo" type="application/json">__CATALOGO_JSON__</script>
<script id="jsonGrupos" type="application/json">__GRUPOS_JSON__</script>
<script id="jsonPlan" type="application/json">__PLAN_JSON__</script>
<script id="jsonSenales" type="application/json">__SENALES_JSON__</script>
<script id="jsonAjustes" type="application/json">__AJUSTES_JSON__</script>
<script id="jsonGuia" type="application/json">__GUIA_JSON__</script>
"""
<script>
const PAISES = JSON.parse(document.getElementById("jsonPaises").textContent);
let CATALOGO = JSON.parse(document.getElementById("jsonCatalogo").textContent);
let GRUPOS = JSON.parse(document.getElementById("jsonGrupos").textContent);
const PLAN = JSON.parse(document.getElementById("jsonPlan").textContent);
const SENALES = JSON.parse(document.getElementById("jsonSenales").textContent);
const AJUSTES_DEF = JSON.parse(document.getElementById("jsonAjustes").textContent);
const GUIA_APP = JSON.parse(document.getElementById("jsonGuia").textContent);

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
let timerSplash = null;
let segSplash = 5;

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

function cerrarSplashInmediato() {
  if (timerSplash) {
    clearInterval(timerSplash);
    timerSplash = null;
  }
  const sp = document.getElementById("vistaSplash");
  if (sp) sp.classList.add("oculto");
  const ini = document.getElementById("vistaInicio");
  if (ini && document.getElementById("mainApp").classList.contains("oculto") && document.getElementById("vistaAjustes").classList.contains("oculto")) {
    ini.classList.remove("oculto");
  }
}

function iniciarSplashCincoSegundos() {
  segSplash = 5;
  const lbl = document.getElementById("splashContador");
  if (lbl) lbl.textContent = "Entrando en 5s...";
  timerSplash = setInterval(() => {
    segSplash -= 1;
    if (segSplash > 0) {
      if (lbl) lbl.textContent = `Entrando en ${segSplash}s...`;
    } else {
      cerrarSplashInmediato();
    }
  }, 1000);
}

function iniciarFigurasGeometricas() {
  const canvas = document.getElementById("canvasFiguras");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const colores = [
    "rgba(212, 175, 55, 0.26)",
    "rgba(242, 211, 121, 0.21)",
    "rgba(203, 213, 225, 0.19)",
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
    if (sesion.ajustes["figuras_geometricas_color"] !== false) {
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

(function iniciarBurbuja() {
  let ctxAudio = null;
  function obtenerCtx() {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    if (!ctxAudio) ctxAudio = new Ctx();
    if (ctxAudio.state === "suspended") ctxAudio.resume().catch(() => {});
    return ctxAudio;
  }
  window.plocBurbuja = function(freqBase, dur) {
    const ctx = obtenerCtx();
    if (!ctx) return;
    try {
      const t0 = ctx.currentTime;
      const f1 = freqBase || 275;
      const f2 = f1 * 1.85;
      const d = dur || 0.065;
      const osc = ctx.createOscillator();
      const flt = ctx.createBiquadFilter();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(f1, t0);
      osc.frequency.exponentialRampToValueAtTime(f2, t0 + d);
      flt.type = "lowpass";
      flt.frequency.setValueAtTime(900, t0);
      flt.Q.setValueAtTime(3.2, t0);
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.linearRampToValueAtTime(0.11, t0 + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
      osc.connect(flt);
      flt.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t0);
      osc.stop(t0 + d + 0.01);
    } catch (e) {}
  };
  document.addEventListener("pointerdown", function(ev) {
    obtenerCtx();
    const el = ev.target && ev.target.closest ? ev.target.closest("button, a.enlace-grupo, .nav-item, .btn-atras") : null;
    if (!el) return;
    if (el.classList.contains("btn-oro")) window.plocBurbuja(315, 0.075);
    else if (el.classList.contains("btn-atras")) window.plocBurbuja(230, 0.06);
    else window.plocBurbuja(275, 0.065);
  }, { passive: true });
})();

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
  document.getElementById("vistaSplash").classList.add("oculto");
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
    const r = await fetch("/api/cuenta", {
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

    document.getElementById("pCorreo").value = correo;
    document.getElementById("pUsuario").value = sesion.usuario;
    document.getElementById("kpiMenuCuenta").textContent = sesion.usuario;
    aplicarCabeceraCuenta();
    if (d.cuenta.progreso) {
      aplicarProgreso(d.cuenta.progreso);
    }

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

  const selPaisBuscar = document.getElementById("selPaisBuscar");
  const selLanPais = document.getElementById("lanPais");
  const selPais = document.getElementById("selPais");
  const selCopyPais = document.getElementById("cPais");
  [selPaisBuscar, selLanPais, selPais, selCopyPais].forEach(sel => {
    if (!sel) return;
    const prev = sel.value;
    sel.innerHTML = "";
    PAISES.forEach(m => {
      const op = document.createElement("option");
      op.value = m.codigo;
      op.textContent = `${m.nombre} (${m.moneda})`;
      if (prev && prev === m.codigo) op.selected = true;
      sel.appendChild(op);
    });
  });

  actualizarKpisMenu();
}

function pintarCatalogo() {
  const codPais = document.getElementById("selPaisBuscar").value || "VE";
  const paisObj = PAISES.find(x => x.codigo === codPais) || PAISES[0];
  const q = norm(document.getElementById("txtBuscarProd").value);
  const pMax = parseFloat(document.getElementById("numPrecioMax").value) || 0;
  const cat = document.getElementById("selCatBuscar").value;
  const cont = document.getElementById("listaCatalogo");
  cont.innerHTML = "";

  const items = CATALOGO.filter(p => {
    if (cat !== "TODAS" && p.categoria !== cat) return false;
    if (pMax > 0 && parseFloat(p.precio_base_usd || 0) > pMax) return false;
    if (!q) return true;
    const blob = norm([
      p.nombre, p.categoria, p.problema, p.beneficio, p.publico, p.autor,
      p.pais_codigo || "", paisObj.nombre
    ].join(" "));
    return blob.includes(q);
  });

  document.getElementById("estadoBusqueda").textContent =
    `Pais activo: ${paisObj.nombre} (${paisObj.moneda}) · ${items.length} producto(s) en catalogo${pMax > 0 ? " hasta $" + pMax : ""}.`;

  if (!items.length) {
    cont.innerHTML = `<div class="caja-salida">No se encontraron productos con ese filtro en el catalogo. Puedes pulsar "BUSCAR EN WEB PUBLICA" para consultar resultados externos.</div>`;
    return;
  }

  items.forEach(p => {
    const idx = CATALOGO.indexOf(p);
    const precioLocal = (parseFloat(p.precio_base_usd || 0) * (paisObj.tasa_usd || 1)).toFixed(2);
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
      `<span class="chip chip-oro">${esc(paisObj.simbolo)}${precioLocal} en ${esc(paisObj.nombre)}</span>` +
      `<span class="chip">Stock: ${p.stock ?? 0}</span>` +
      `</div></div>` +
      `<div style="text-align:right;"><strong style="color:#d4af37;font-size:16px;">$${p.precio_base_usd}</strong>` +
      `<div style="font-size:12px;color:#cbd5e1;">Por: ${esc(p.autor || "Base")}</div></div></div>` +
      `<div style="margin-top:8px;font-size:13.5px;"><strong>Beneficio:</strong> ${esc(p.beneficio)}</div>` +
      `<div style="margin-top:3px;font-size:13px;color:#cbd5e1;"><strong>Resuelve:</strong> ${esc(p.problema)}</div>` +
      `<div style="margin-top:8px;"><button type="button" class="btn-plata" onclick="enviarItemAPais(${idx})">CALCULAR EN PAISES</button>${enlaceHtml}</div>`;
    cont.appendChild(card);
  });
}

async function buscarEnWebPublica() {
  const codPais = document.getElementById("selPaisBuscar").value || "VE";
  const paisObj = PAISES.find(x => x.codigo === codPais) || PAISES[0];
  const q = document.getElementById("txtBuscarProd").value.trim();
  const pMax = parseFloat(document.getElementById("numPrecioMax").value) || 0;
  const cont = document.getElementById("listaWebResultados");
  const estado = document.getElementById("estadoBusqueda");

  if (!q) {
    estado.textContent = "Escribe que producto deseas buscar en la web publica (ej. relojes o camisetas).";
    return;
  }

  estado.textContent = `Buscando "${q}" en ${paisObj.nombre}...`;
  cont.innerHTML = "";

  try {
    const url = `/api/buscar_web?q=${encodeURIComponent(q)}&pais=${encodeURIComponent(paisObj.nombre)}&precio_max=${encodeURIComponent(pMax)}`;
    const r = await fetch(url);
    const d = await r.json();
    const resList = Array.isArray(d.resultados) ? d.resultados : [];
    if (!resList.length) {
      cont.innerHTML = `<div class="caja-salida">No se obtuvieron resultados web publicos para esa consulta en este momento.</div>`;
      estado.textContent = `Consulta finalizada para "${q}" en ${paisObj.nombre}.`;
      return;
    }

    estado.textContent = `Se encontraron ${resList.length} resultado(s) web publicos para "${q}" en ${paisObj.nombre}.`;
    resList.forEach(item => {
      const div = document.createElement("div");
      div.className = "item-tarjeta";
      const pDet = (item.precio_detectado !== null && item.precio_detectado !== undefined)
        ? `<span class="chip chip-oro">Ref. aprox: ${item.precio_detectado}</span>`
        : `<span class="chip">${esc(paisObj.moneda)}</span>`;
      div.innerHTML =
        `<div class="item-top"><strong style="color:#d4af37;">${esc(item.titulo)}</strong>${pDet}</div>` +
        `<div style="font-size:13px;color:#cbd5e1;margin-top:6px;">${esc(item.resumen || "Resultado web publico")}</div>` +
        `<a class="enlace-grupo" href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">VER ENLACE PUBLICO</a>`;
      cont.appendChild(div);
    });
  } catch (e) {
    estado.textContent = "No se pudo completar la consulta web en este momento.";
  }
}

function limpiarFormularioProducto() {
  document.getElementById("lanEditId").value = "";
  document.getElementById("lanNombre").value = "";
  document.getElementById("lanCategoria").value = "Productos y Servicios";
  document.getElementById("lanPrecio").value = "25";
  document.getElementById("lanCosto").value = "5";
  document.getElementById("lanStock").value = "20";
  document.getElementById("lanProblema").value = "";
  document.getElementById("lanBeneficio").value = "";
  document.getElementById("lanEnlace").value = "";
  document.getElementById("btnGuardarLanzamiento").textContent = "LANZAR PRODUCTO A LA APLICACION";
}

function editarProductoLanzado(itemId) {
  const p = CATALOGO.find(x => x.id === itemId);
  if (!p) return;
  document.getElementById("lanEditId").value = p.id;
  document.getElementById("lanNombre").value = p.nombre || "";
  document.getElementById("lanCategoria").value = p.categoria || "Productos y Servicios";
  document.getElementById("lanPais").value = p.pais_codigo || "VE";
  document.getElementById("lanPrecio").value = p.precio_base_usd || 0;
  document.getElementById("lanCosto").value = p.costo_base_usd || 0;
  document.getElementById("lanStock").value = p.stock ?? 0;
  document.getElementById("lanProblema").value = p.problema || "";
  document.getElementById("lanBeneficio").value = p.beneficio || "";
  document.getElementById("lanEnlace").value = p.enlace_contacto || "";
  document.getElementById("btnGuardarLanzamiento").textContent = "GUARDAR CAMBIOS DEL PRODUCTO";
  document.getElementById("msgLanzar").textContent = `Editando "${p.nombre}".`;
  window.scrollTo(0, 0);
}

async function borrarProductoLanzado(itemId) {
  const msg = document.getElementById("msgLanzar");
  try {
    const r = await fetch(`/api/productos/${encodeURIComponent(itemId)}`, { method: "DELETE" });
    const d = await r.json();
    if (d.ok) {
      CATALOGO = CATALOGO.filter(p => p.id !== itemId);
      cargarSelectores();
      pintarCatalogo();
      pintarLanzados();
      msg.textContent = "Producto eliminado.";
    }
  } catch (e) {
    msg.textContent = "Error al eliminar el producto.";
  }
}

function pintarLanzados() {
  const cont = document.getElementById("listaLanzados");
  const lanzados = CATALOGO.filter(p => p.es_lanzamiento_usuario);
  cont.innerHTML = "";
  if (!lanzados.length) {
    cont.innerHTML = `<div class="caja-salida">Aun no has creado productos propios. Usa el formulario de arriba para lanzar el primero y administrarlo aqui.</div>`;
    return;
  }
  lanzados.forEach(p => {
    const div = document.createElement("div");
    div.className = "item-tarjeta";
    div.innerHTML =
      `<div class="item-top"><strong>${esc(p.nombre)}</strong><span class="chip chip-oro">$${p.precio_base_usd}</span></div>` +
      `<div style="font-size:13px;color:#cbd5e1;margin-top:4px;">${esc(p.beneficio)} · Stock: ${p.stock ?? 0} · Pais: ${esc(p.pais_codigo || "VE")}</div>` +
      `<div class="grid-2" style="margin-top:8px;">` +
      `<button type="button" class="btn-plata" onclick="editarProductoLanzado('${esc(p.id)}')">EDITAR</button>` +
      `<button type="button" class="btn-plata" onclick="borrarProductoLanzado('${esc(p.id)}')">ELIMINAR</button>` +
      `</div>`;
    cont.appendChild(div);
  });
}

async function lanzarProductoUsuario() {
  const editId = document.getElementById("lanEditId").value.trim();
  const nombre = document.getElementById("lanNombre").value.trim();
  const categoria = document.getElementById("lanCategoria").value.trim() || "Productos y Servicios";
  const paisCodigo = document.getElementById("lanPais").value || "VE";
  const precio = parseFloat(document.getElementById("lanPrecio").value) || 0;
  const costo = parseFloat(document.getElementById("lanCosto").value) || 0;
  const stock = parseInt(document.getElementById("lanStock").value, 10) || 0;
  const problema = document.getElementById("lanProblema").value.trim() || "Necesidad de clientes";
  const beneficio = document.getElementById("lanBeneficio").value.trim() || "Solucion directa";
  const enlace = document.getElementById("lanEnlace").value.trim();
  const msg = document.getElementById("msgLanzar");

  if (!nombre || precio <= 0) {
    msg.textContent = "Escribe el nombre del producto y un precio mayor a cero.";
    return;
  }

  const payload = {
    nombre: nombre,
    categoria: categoria,
    pais_codigo: paisCodigo,
    precio_base_usd: precio,
    costo_base_usd: costo,
    stock: stock,
    problema: problema,
    beneficio: beneficio,
    enlace_contacto: enlace,
    autor: sesion.usuario || sesion.correo || "Usuario"
  };

  try {
    if (editId) {
      const r = await fetch(`/api/productos/${encodeURIComponent(editId)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const d = await r.json();
      if (d.ok && d.producto) {
        CATALOGO = CATALOGO.map(item => item.id === editId ? d.producto : item);
        cargarSelectores();
        pintarCatalogo();
        pintarLanzados();
        limpiarFormularioProducto();
        msg.textContent = `Producto "${nombre}" actualizado.`;
      }
    } else {
      const r = await fetch("/api/lanzar_producto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const d = await r.json();
      if (d.ok && d.producto) {
        CATALOGO.push(d.producto);
        cargarSelectores();
        pintarCatalogo();
        pintarLanzados();
        limpiarFormularioProducto();
        msg.textContent = `Producto "${nombre}" lanzado al catalogo.`;
      }
    }
  } catch (e) {
    msg.textContent = "Error al guardar el producto.";
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
    const r = await fetch("/api/grupos/agregar", {
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

async function generarTextos() {
  const payload = {
    nombre: document.getElementById("cNombre").value.trim(),
    categoria: document.getElementById("cCat").value.trim(),
    pais_codigo: document.getElementById("cPais").value,
    formula: document.getElementById("cFormula").value,
    precio_usd: parseFloat(document.getElementById("cPrecio").value) || 0,
    costo_usd: 0,
    publico: document.getElementById("cPublico").value.trim(),
    problema: document.getElementById("cProblema").value.trim(),
    beneficio: document.getElementById("cBeneficio").value.trim(),
  };

  try {
    const r = await fetch("/api/anuncios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    if (d.ok && d.kit) {
      document.getElementById("resGanchos").textContent =
        d.kit.ganchos.map((g, idx) => `${idx + 1}. ${g}`).join("\n");
      document.getElementById("resCopy").textContent = d.kit.copy_principal;
      document.getElementById("resGuion").textContent = d.kit.guion_video;
      const p = d.kit.pais;
      document.getElementById("resChat").textContent =
        `Hola, gracias por consultar por *${d.kit.producto}*.\n` +
        `Beneficio principal: ${payload.beneficio}.\n` +
        `Referencia en ${p.nombre}: *${p.simbolo}${d.kit.precio_local} (${p.moneda})*.\n` +
        `Medios de pago: ${p.pagos}.\n` +
        `Deseas confirmar disponibilidad o resolver alguna duda?`;
    }
  } catch (e) {
    document.getElementById("resCopy").textContent = "Error al generar los textos.";
  }
}

function pintarPlanYSenales() {
  const contPlan = document.getElementById("listaPlan");
  contPlan.innerHTML = "";
  PLAN.forEach(item => {
    const div = document.createElement("div");
    div.className = "item-tarjeta";
    div.innerHTML =
      `<div class="item-top"><strong style="color:#d4af37;">${esc(item.dia)} · ${esc(item.objetivo)}</strong>` +
      `<span class="chip">${esc(item.formato)}</span></div>` +
      `<div style="margin-top:6px;font-size:13.5px;">${esc(item.estructura)}</div>` +
      `<div style="margin-top:4px;font-size:12.5px;color:#cbd5e1;">Indicador: ${esc(item.kpi)}</div>`;
    contPlan.appendChild(div);
  });

  const contSen = document.getElementById("listaSenales");
  contSen.innerHTML = "";
  SENALES.forEach(s => {
    const box = document.createElement("div");
    box.className = "caja-salida";
    box.innerHTML = `<strong>${esc(s.titulo)}</strong> [${esc(s.enfoque)}]\n${esc(s.detalle)}`;
    contSen.appendChild(box);
  });
}

function construirRoas(filasGuardadas) {
  const tbody = document.getElementById("cuerpoRoas");
  tbody.innerHTML = "";
  for (let i = 0; i < 8; i++) {
    const f = (filasGuardadas && filasGuardadas[i]) ? filasGuardadas[i] : ["", "", "", ""];
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td><strong>#${i + 1}</strong></td>` +
      `<td><input type="number" step="0.1" class="roas-p" value="${esc(f[0])}" oninput="calcularRoas()"></td>` +
      `<td><input type="number" step="0.1" class="roas-c" value="${esc(f[1])}" oninput="calcularRoas()"></td>` +
      `<td><input type="number" step="1" class="roas-u" value="${esc(f[2])}" oninput="calcularRoas()"></td>` +
      `<td><input type="number" step="0.1" class="roas-a" value="${esc(f[3])}" oninput="calcularRoas()"></td>` +
      `<td class="roas-ut" style="font-weight:700;color:#d4af37;">$0.00</td>` +
      `<td class="roas-rx" style="font-weight:700;color:#f8fafc;">0.00x</td>`;
    tbody.appendChild(tr);
  }
  calcularRoas();
}

function calcularRoas() {
  let ing = 0;
  let ads = 0;
  let ut = 0;

  document.querySelectorAll("#cuerpoRoas tr").forEach(tr => {
    const p = parseFloat(tr.querySelector(".roas-p").value) || 0;
    const c = parseFloat(tr.querySelector(".roas-c").value) || 0;
    const u = parseFloat(tr.querySelector(".roas-u").value) || 0;
    const a = parseFloat(tr.querySelector(".roas-a").value) || 0;

    const ingFila = p * u;
    const utFila = ingFila - (c * u) - a;
    const rFila = a > 0 ? (ingFila / a) : 0;

    ing += ingFila;
    ads += a;
    ut += utFila;

    tr.querySelector(".roas-ut").textContent = "$" + utFila.toFixed(2);
    tr.querySelector(".roas-rx").textContent = rFila.toFixed(2) + "x";
  });

  const roasGlobal = ads > 0 ? (ing / ads) : 0;
  document.getElementById("rIngresos").textContent = "$" + ing.toFixed(2);
  document.getElementById("rAds").textContent = "$" + ads.toFixed(2);
  document.getElementById("rUtilidad").textContent = "$" + ut.toFixed(2);
  document.getElementById("rRoas").textContent = roasGlobal.toFixed(2) + "x";
}

function calcularEmbudo() {
  const pres = parseFloat(document.getElementById("ePres").value) || 0;
  const cpm = parseFloat(document.getElementById("eCpm").value) || 0;
  const ctr = parseFloat(document.getElementById("eCtr").value) || 0;
  const conv = parseFloat(document.getElementById("eConv").value) || 0;
  const ticket = parseFloat(document.getElementById("eTicket").value) || 0;

  const imp = cpm > 0 ? Math.round((pres / cpm) * 1000) : 0;
  const clics = Math.round(imp * (ctr / 100));
  const cpc = clics > 0 ? (pres / clics) : 0;
  const ventas = Math.round(clics * (conv / 100));
  const cpa = ventas > 0 ? (pres / ventas) : 0;
  const fact = ventas * ticket;
  const roas = pres > 0 ? (fact / pres) : 0;

  document.getElementById("eImp").textContent = imp.toLocaleString("es-ES");
  document.getElementById("eClics").textContent = clics.toLocaleString("es-ES");
  document.getElementById("eCpc").textContent = "$" + cpc.toFixed(2);
  document.getElementById("eVentas").textContent = String(ventas);
  document.getElementById("eCpa").textContent = "$" + cpa.toFixed(2);
  document.getElementById("eFact").textContent = "$" + fact.toFixed(2);
  document.getElementById("eRoas").textContent = roas.toFixed(2) + "x";

  let obs = "Parametros en rango de prueba.";
  if (ctr < 1.2) {
    obs = "CTR bajo: revisa el gancho o la pieza visual inicial.";
  } else if (conv < 2.0) {
    obs = "Conversion baja: revisa la oferta, claridad de pagos y seguimiento.";
  } else if (roas >= 3.0) {
    obs = "Retorno estimado favorable para pruebas controladas.";
  }

  document.getElementById("eLectura").textContent =
    `Resumen del embudo:\n` +
    `- Alcance estimado: ${imp.toLocaleString("es-ES")} impresiones y ${clics} clics.\n` +
    `- Proyeccion: ${ventas} ventas con CPA estimado de $${cpa.toFixed(2)}.\n` +
    `- Observacion: ${obs}`;
}

function actualizarOferta() {
  const cat = document.getElementById("oCat").value;
  const tipo = document.getElementById("oTipo").value;
  const prod = document.getElementById("oProd").value.trim() || "Producto o Servicio";
  const precio = parseFloat(document.getElementById("oPrecio").value) || 0;

  const audMap = {
    relojes: "Edad: 18 - 50 anos. Intereses: relojeria, accesorios de uso diario, regalo y estilo personal.",
    ropa: "Edad: 18 - 45 anos. Intereses: camisetas, moda casual, comodidad y compras online.",
    tech: "Edad: 18 - 44 anos. Intereses: tecnologia movil, accesorios, productividad y herramientas.",
    home: "Edad: 24 - 55 anos. Intereses: hogar, organizacion, cocina y comodidad.",
    biz: "Edad: 20 - 50 anos. Intereses: emprendimiento, ventas, atencion y herramientas de trabajo."
  };

  document.getElementById("resAud").textContent =
    `Audiencia sugerida:\n${audMap[cat] || audMap.tech}\n` +
    `Formatos sugeridos: video corto, carrusel y mensajeria directa.`;

  let oferta = "";
  if (tipo === "pack") {
    oferta = `Oferta de 2 unidades - ${prod}:\n1 unidad por $${precio.toFixed(2)} o 2 unidades por $${(precio * 1.75).toFixed(2)}.`;
  } else if (tipo === "bono") {
    oferta = `Oferta con complemento - ${prod}:\nLleva ${prod} por $${precio.toFixed(2)} con guia practica incluida.`;
  } else if (tipo === "envio") {
    oferta = `Oferta con respaldo - ${prod}:\nPrecio $${precio.toFixed(2)} con informacion clara de despacho y atencion.`;
  } else {
    oferta = `Promocion por tiempo limitado - ${prod}:\nPrecio base $${precio.toFixed(2)} -> Condicion activa en $${(precio * 0.85).toFixed(2)}.`;
  }
  document.getElementById("resOferta").textContent = oferta;
}

function leerFilasRoas() {
  const out = [];
  document.querySelectorAll("#cuerpoRoas tr").forEach(tr => {
    out.push([
      tr.querySelector(".roas-p").value,
      tr.querySelector(".roas-c").value,
      tr.querySelector(".roas-u").value,
      tr.querySelector(".roas-a").value
    ]);
  });
  return out;
}

function aplicarProgreso(p) {
  if (!p || typeof p !== "object") return;
  if (p.c_nombre) document.getElementById("cNombre").value = p.c_nombre;
  if (p.c_beneficio) document.getElementById("cBeneficio").value = p.c_beneficio;
  if (typeof p.notas === "string") document.getElementById("pNotas").value = p.notas;
  if (Array.isArray(p.filas_roas)) construirRoas(p.filas_roas);
}

async function guardarProgreso() {
  const correo = document.getElementById("pCorreo").value.trim().toLowerCase() || sesion.correo;
  const usuario = document.getElementById("pUsuario").value.trim() || sesion.usuario;
  const msg = document.getElementById("msgProg");

  if (!correo || !correo.includes("@")) {
    msg.textContent = "Ingresa un correo electronico valido.";
    return;
  }

  sesion.correo = correo;
  if (usuario) sesion.usuario = usuario;
  aplicarCabeceraCuenta();

  const payload = {
    correo: correo,
    usuario: sesion.usuario,
    clave: sesion.clave,
    ajustes: sesion.ajustes,
    progreso: {
      c_nombre: document.getElementById("cNombre").value,
      c_beneficio: document.getElementById("cBeneficio").value,
      notas: document.getElementById("pNotas").value,
      filas_roas: leerFilasRoas()
    }
  };

  try {
    const r = await fetch("/api/progreso/guardar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    msg.textContent = d.mensaje || "Progreso guardado.";
  } catch (e) {
    msg.textContent = "Error al guardar el progreso.";
  }
}

async function cargarProgreso() {
  const correo = document.getElementById("pCorreo").value.trim().toLowerCase() || sesion.correo;
  const msg = document.getElementById("msgProg");

  if (!correo || !correo.includes("@")) {
    msg.textContent = "Ingresa un correo electronico valido.";
    return;
  }

  try {
    const url = "/api/progreso/cargar?correo=" + encodeURIComponent(correo) + "&clave=" + encodeURIComponent(sesion.clave || "");
    const r = await fetch(url);
    const d = await r.json();
    if (!d.encontrado) {
      msg.textContent = "No hay progreso previo guardado para este correo.";
      return;
    }
    if (d.usuario) {
      sesion.usuario = d.usuario;
      document.getElementById("pUsuario").value = d.usuario;
    }
    if (d.ajustes && typeof d.ajustes === "object") {
      sesion.ajustes = Object.assign({}, sesion.ajustes, d.ajustes);
      aplicarCabeceraCuenta();
    }
    aplicarProgreso(d.progreso || {});
    msg.textContent = "Progreso cargado para " + correo + ".";
  } catch (e) {
    msg.textContent = "Error al cargar el progreso.";
  }
}

function copiarTexto(idElem) {
  const el = document.getElementById(idElem);
  if (el && navigator.clipboard && el.textContent) {
    navigator.clipboard.writeText(el.textContent).catch(() => {});
  }
}

function pintarGuia() {
  document.getElementById("gSirve").textContent = GUIA_APP.para_que_sirve || "";
  document.getElementById("gFunciona").textContent = GUIA_APP.como_funciona || "";
  document.getElementById("gDiferencia").textContent = GUIA_APP.que_la_diferencia || "";
}

iniciarFigurasGeometricas();
cargarSelectores();
pintarCatalogo();
pintarLanzados();
pintarGrupos();
actualizarLinkWa();
actualizarPais();
pintarPlanYSenales();
construirRoas([]);
calcularEmbudo();
actualizarOferta();
pintarGuia();
iniciarSplashCincoSegundos();
</script>
</body>
</html>
"""
# ==============================================================================
# 08. TOQUE PICANTE: GANCHOS CON FILO Y ANGULO DE CIERRE (PARTE 6)
# ==============================================================================
def generar_ganchos_picantes(producto, pais_nombre="Venezuela", precio_usd=49.0, problema=""):
    prod = (producto or "este producto").strip()
    pais = (pais_nombre or "tu mercado").strip()
    prob = (problema or "perder tiempo o dinero con opciones mediocres").strip()
    try:
        precio_fmt = f"${float(precio_usd):.2f}"
    except Exception:
        precio_fmt = str(precio_usd or "$0.00")

    return [
        f"Deja de conformarte con {prob.lower()}: mira lo que hace {prod} por {precio_fmt}.",
        f"La mayoria en {pais} paga de mas o elige mal por no revisar esto antes de comprar {prod}.",
        f"Tres segundos bastan para ver por que {prod} deja atras a lo de siempre.",
        f"Si vas a moverte en {pais} con {prod}, hazlo bien desde el primer dia.",
        f"Sin vueltas ni relleno: asi funciona {prod} y por que conviene revisarlo hoy.",
    ]


def evaluar_angulo_cierre(precio_usd, costo_usd, pais_codigo="VE"):
    pais = obtener_pais_mkt(pais_codigo)
    try:
        p = float(precio_usd or 0)
        c = float(costo_usd or 0)
    except Exception:
        p, c = 0.0, 0.0

    margen = round(p - c - float(pais.get("envio_usd", 0.0)), 2)
    if margen >= 25:
        angulo = "Ataque directo por valor y margen: resalta beneficios, respaldo y respuesta rapida por chat."
    elif margen >= 10:
        angulo = "Cierre por practicidad y precio local: muestra moneda local y medios de pago sin friccion."
    else:
        angulo = "Cierre por volumen o combo: agrupa unidades o complementa la oferta para cuidar el retorno."

    return {
        "pais": pais.get("nombre", pais_codigo),
        "moneda": pais.get("moneda", ""),
        "margen_estimado_usd": margen,
        "angulo_recomendado": angulo,
    }


# ==============================================================================
# 09. RUTAS DEL SERVIDOR FLASK Y ARRANQUE FINAL (PARTE 6)
# ==============================================================================
@app.route("/")
def inicio():
    catalogo = obtener_catalogo_completo()
    grupos = obtener_grupos_completos()
    html = (
        HTML_PARTE_DOS
        .replace("__PAISES_JSON__", json.dumps(PAISES_MKT, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__CATALOGO_JSON__", json.dumps(catalogo, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__GRUPOS_JSON__", json.dumps(grupos, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__PLAN_JSON__", json.dumps(PLAN_SEMANAL, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__SENALES_JSON__", json.dumps(SENALES_MKT, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__AJUSTES_JSON__", json.dumps(AJUSTES_PRIVACIDAD, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__GUIA_JSON__", json.dumps(GUIA_APLICACION, ensure_ascii=True).replace("</", "<\\/"))
    )
    resp = make_response(html)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.route("/api/cuenta", methods=["POST"])
def ruta_cuenta():
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
                "progreso": reg.get("progreso", {}),
            },
        })

    ajustes_ini = {a["clave"]: bool(a["activo"]) for a in AJUSTES_PRIVACIDAD}
    cuentas[correo] = {
        "correo": correo,
        "usuario": usuario,
        "clave_hash": h,
        "creado": datetime.utcnow().isoformat(),
        "ultimo_acceso": datetime.utcnow().isoformat(),
        "ajustes": ajustes_ini,
        "progreso": {},
    }
    guardar_db(db)
    return jsonify({
        "ok": True,
        "cuenta": {
            "correo": correo,
            "usuario": usuario,
            "ajustes": ajustes_ini,
            "progreso": {},
        },
    })


@app.route("/api/lanzar_producto", methods=["POST"])
def ruta_lanzar_producto():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    categoria = (datos.get("categoria") or "Productos y Servicios").strip()
    pais_codigo = (datos.get("pais_codigo") or "VE").strip().upper()
    try:
        precio = float(datos.get("precio_base_usd") or 0)
    except Exception:
        precio = 0.0
    try:
        costo = float(datos.get("costo_base_usd") or 0)
    except Exception:
        costo = 0.0
    try:
        stock = max(0, int(datos.get("stock") or 20))
    except Exception:
        stock = 20
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
        pais_codigo=pais_codigo,
        stock=stock,
    )
    lanzados.append(nuevo)
    guardar_db(db)
    return jsonify({"ok": True, "producto": nuevo})


@app.route("/api/productos/<item_id>", methods=["PUT", "DELETE"])
def ruta_producto_item(item_id):
    if request.method == "DELETE":
        eliminado = eliminar_producto_lanzado(item_id)
        if not eliminado:
            return jsonify({"ok": False, "mensaje": "Producto no encontrado."}), 404
        return jsonify({"ok": True, "eliminado": item_id})

    datos = request.get_json(silent=True) or {}
    actualizado = actualizar_producto_lanzado(item_id, datos)
    if not actualizado:
        return jsonify({"ok": False, "mensaje": "No se pudo actualizar el producto."}), 400
    return jsonify({"ok": True, "producto": actualizado})


@app.route("/api/buscar_web", methods=["GET"])
def ruta_buscar_web():
    q = (request.args.get("q") or "").strip()
    pais = (request.args.get("pais") or "").strip()
    try:
        precio_max = float(request.args.get("precio_max") or 0)
    except Exception:
        precio_max = 0.0
    resultados = buscar_productos_web_publicos(q, pais, precio_max=precio_max)
    return jsonify({"ok": True, "resultados": resultados})


@app.route("/api/grupos/agregar", methods=["POST"])
def ruta_grupos_agregar():
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


@app.route("/api/anuncios", methods=["POST"])
def ruta_anuncios():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "Producto").strip()
    categoria = (datos.get("categoria") or "General").strip()
    pais_codigo = (datos.get("pais_codigo") or "VE").strip().upper()
    formula = (datos.get("formula") or "AIDA").strip().upper()
    try:
        precio_usd = float(datos.get("precio_usd") or 29.90)
    except Exception:
        precio_usd = 29.90
    try:
        costo_usd = float(datos.get("costo_usd") or 8.0)
    except Exception:
        costo_usd = 8.0
    publico = (datos.get("publico") or "Publico general").strip()
    problema = (datos.get("problema") or "Necesidad cotidiana").strip()
    beneficio = (datos.get("beneficio") or "Utilidad directa").strip()

    kit = construir_kit_marketing(
        nombre,
        categoria,
        precio_usd,
        costo_usd,
        beneficio,
        problema,
        publico,
        pais_codigo,
        formula,
    )
    pais_obj = kit.get("pais", {})
    kit["ganchos_picantes"] = generar_ganchos_picantes(
        nombre, pais_obj.get("nombre", pais_codigo), precio_usd, problema
    )
    kit["angulo_cierre"] = evaluar_angulo_cierre(precio_usd, costo_usd, pais_codigo)
    return jsonify({"ok": True, "kit": kit})


@app.route("/api/ganchos_picantes", methods=["POST"])
def ruta_ganchos_picantes():
    datos = request.get_json(silent=True) or {}
    ganchos = generar_ganchos_picantes(
        datos.get("producto", ""),
        datos.get("pais", ""),
        datos.get("precio_usd", 0),
        datos.get("problema", ""),
    )
    return jsonify({"ok": True, "ganchos": ganchos})


@app.route("/api/progreso/guardar", methods=["POST"])
def ruta_progreso_guardar():
    datos = request.get_json(silent=True) or {}
    correo = validar_correo_limpio(datos.get("correo"))
    usuario = (datos.get("usuario") or "").strip()
    clave = (datos.get("clave") or "").strip()
    progreso = datos.get("progreso") or {}
    ajustes = datos.get("ajustes")

    if not correo:
        return jsonify({"ok": False, "mensaje": "Correo electronico invalido."}), 400

    db = cargar_db()
    cuentas = db.setdefault("cuentas", {})
    reg = cuentas.get(correo)

    if reg and reg.get("clave_hash") and clave:
        if reg["clave_hash"] != hash_clave(clave, correo):
            return jsonify({"ok": False, "mensaje": "Clave personal incorrecta."}), 403

    if not reg:
        reg = {
            "correo": correo,
            "usuario": usuario or "Usuario",
            "clave_hash": hash_clave(clave or "default", correo),
            "creado": datetime.utcnow().isoformat(),
            "ajustes": {a["clave"]: bool(a["activo"]) for a in AJUSTES_PRIVACIDAD},
            "progreso": {},
        }
        cuentas[correo] = reg

    if usuario:
        reg["usuario"] = usuario
    if isinstance(ajustes, dict):
        reg["ajustes"] = ajustes
    reg["progreso"] = progreso
    reg["actualizado"] = datetime.utcnow().isoformat()
    guardar_db(db)
    return jsonify({"ok": True, "mensaje": f"Progreso guardado para {correo}."})


@app.route("/api/progreso/cargar", methods=["GET"])
def ruta_progreso_cargar():
    correo = validar_correo_limpio(request.args.get("correo"))
    clave = (request.args.get("clave") or "").strip()
    if not correo:
        return jsonify({"encontrado": False})

    db = cargar_db()
    reg = db.get("cuentas", {}).get(correo)
    if not reg:
        return jsonify({"encontrado": False})

    if reg.get("clave_hash") and clave:
        if reg["clave_hash"] != hash_clave(clave, correo):
            return jsonify({"encontrado": False})

    return jsonify({
        "encontrado": True,
        "usuario": reg.get("usuario", ""),
        "ajustes": reg.get("ajustes", {}),
        "progreso": reg.get("progreso", {}),
    })


@app.route("/api/embudo", methods=["POST"])
def ruta_embudo():
    datos = request.get_json(silent=True) or {}
    try:
        res = calcular_embudo_metricas(
            datos.get("presupuesto_usd", 100.0),
            datos.get("cpm_usd", 8.5),
            datos.get("ctr_pct", 2.2),
            datos.get("conv_pct", 3.5),
            datos.get("ticket_usd", 95.0),
        )
        return jsonify({"ok": True, "embudo": res})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.route("/api/whatsapp/link", methods=["GET"])
def ruta_whatsapp_link():
    tel = request.args.get("telefono", "")
    msg = request.args.get("mensaje", "")
    return jsonify({"ok": True, "url": armar_url_whatsapp(tel, msg)})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
