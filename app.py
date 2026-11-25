
import os
import json
import re
import math
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================================================================
# 01. CONFIGURACION GENERAL DEL SERVIDOR Y PERSISTENCIA DE C-PRE MARKETING
# ==============================================================================
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
CLAVES_VALIDAS = {"VIP100", "Celso2026", "CELSO2026", "vip100", "1234"}
ARCHIVO_DB = os.environ.get("CPRE_MKT_DB_FILE", "cpre_marketing_datos.json")
VERSION_SISTEMA = "C-PRE MARKETING v8.0 INTERNATIONAL SUITE"
AUTOR_SISTEMA = "Creaciones Celso"

CONFIGURACION_VISUAL_BASE = {
    "fondo_oscuro": "#06110e",
    "panel_oscuro": "#0c1f1a",
    "tarjeta_oscura": "#112a24",
    "verde_claro": "#34d399",
    "verde_brillante": "#6ee7b7",
    "blanco_puro": "#ffffff",
    "texto_suave": "#d1fae5",
    "borde_firme": "#10b981",
    "fuente_titulos": "Space Grotesk",
    "fuente_cuerpo": "Space Grotesk",
}

ESTRUCTURA_MODULOS_BASE = [
    {"id": "modBuscador", "orden": 1, "titulo": "1. Buscador Productos"},
    {"id": "modLocalizador", "orden": 2, "titulo": "2. Paises y Monedas"},
    {"id": "modCopy", "orden": 3, "titulo": "3. Copy y Guiones"},
    {"id": "modCalendario", "orden": 4, "titulo": "4. Plan y Tendencias"},
    {"id": "modSimulador", "orden": 5, "titulo": "5. Hoja ROAS y Ventas"},
    {"id": "modEmbudo", "orden": 6, "titulo": "6. Embudo CTR y CPA"},
    {"id": "modAudiencias", "orden": 7, "titulo": "7. Audiencias y Ofertas"},
    {"id": "modCuenta", "orden": 8, "titulo": "8. Correo y Progreso"},
]


# ==============================================================================
# 02. BASE INTERNACIONAL DE PAISES, MONEDAS, PAGOS Y CULTURA COMERCIAL
# ==============================================================================
def crear_ficha_pais(
    codigo,
    nombre,
    region,
    moneda,
    simbolo,
    tasa_usd,
    idioma,
    plataformas_top,
    metodos_pago,
    horario_pico,
    impuesto_pct,
    envio_usd,
    angulo_cultural,
    objecion_frecuente,
    solucion_objecion,
    cta_local,
):
    return {
        "codigo": codigo.strip().upper(),
        "nombre": nombre.strip(),
        "region": region.strip(),
        "moneda": moneda.strip(),
        "simbolo": simbolo,
        "tasa_usd": float(tasa_usd),
        "idioma": idioma.strip(),
        "plataformas_top": plataformas_top.strip(),
        "metodos_pago": metodos_pago.strip(),
        "horario_pico": horario_pico.strip(),
        "impuesto_pct": float(impuesto_pct),
        "envio_usd": float(envio_usd),
        "angulo_cultural": angulo_cultural.strip(),
        "objecion_frecuente": objecion_frecuente.strip(),
        "solucion_objecion": solucion_objecion.strip(),
        "cta_local": cta_local.strip(),
    }


PAISES_MARKETING = [
    crear_ficha_pais(
        "US",
        "Estados Unidos",
        "Norteamerica",
        "USD",
        "$",
        1.0,
        "Ingles / Espanol",
        "TikTok Shop, Meta Ads, Amazon, YouTube Shorts",
        "Tarjeta Credito/Debito, Apple Pay, Google Pay, PayPal, Klarna",
        "18:00 - 22:30 EST",
        7.0,
        6.5,
        "Rapidez de entrega, garantia clara, pruebas reales con videos cortos y resenas visibles.",
        "Sera igual que en el video o de baja calidad?",
        "Mostrar demostracion en vivo sin cortes, envio rastreado y devolucion facil.",
        "Get Yours Today - Fast Shipping & Easy Returns",
    ),
    crear_ficha_pais(
        "VE",
        "Venezuela",
        "Latinoamerica / Caribe",
        "USD / VES",
        "$",
        1.0,
        "Espanol",
        "Instagram Reels, TikTok, WhatsApp Business, Facebook",
        "Pago Movil, Zelle, Binance USDT, Efectivo, Cashea",
        "12:30 - 14:30 y 19:30 - 22:30 VET",
        16.0,
        3.5,
        "Trato directo por WhatsApp, disponibilidad real, facilidad de pago y entregas confiables.",
        "Como coordino el pago y la entrega en mi ciudad?",
        "Explicar paso a paso el pago, confirmacion rapida y entrega directa o agencia.",
        "Escribenos al WhatsApp y asegura tu pedido hoy",
    ),
    crear_ficha_pais(
        "MX",
        "Mexico",
        "Latinoamerica / Norte",
        "MXN",
        "MX$",
        17.2,
        "Espanol",
        "TikTok, Facebook Ads, Mercado Libre, Instagram",
        "Tarjeta, OXXO Pay, Mercado Pago, SPEI, Kueski Pay",
        "13:00 - 15:00 y 20:00 - 23:00 CST",
        16.0,
        4.8,
        "Facilidades en cuotas, pago en efectivo en OXXO o transferencia SPEI y promociones claras.",
        "Puedo pagar sin tarjeta de credito?",
        "Ofrecer opciones como OXXO Pay, SPEI o meses sin intereses segun la tienda.",
        "Pide hoy con envio seguro a todo Mexico",
    ),
    crear_ficha_pais(
        "CO",
        "Colombia",
        "Latinoamerica / Andina",
        "COP",
        "COL$",
        4150.0,
        "Espanol",
        "TikTok, Instagram Reels, WhatsApp, Dropi",
        "Pago Contra Entrega, Nequi, Daviplata, PSE, Tarjeta",
        "12:00 - 14:00 y 19:00 - 22:00 COT",
        19.0,
        3.8,
        "Confianza con pago contra entrega, rapidez en envios nacionales y comunicacion cercana.",
        "Es seguro comprar en linea si nunca he pedido aqui?",
        "Habilitar pago contra entrega en ciudades principales y soporte directo.",
        "Paga al recibir y estrena hoy mismo",
    ),
    crear_ficha_pais(
        "ES",
        "Espana",
        "Europa Occidental",
        "EUR",
        "EUR ",
        0.92,
        "Espanol",
        "Instagram, TikTok, Google Shopping, YouTube",
        "Tarjeta, Bizum, PayPal, Apple Pay, Sequra",
        "14:00 - 16:00 y 20:30 - 23:00 CET",
        21.0,
        5.2,
        "Plazos de entrega en 24/48h, transparencia total en impuestos y garantias claras.",
        "Cuanto tarda en llegar y que incluye el precio?",
        "Indicar tiempo estimado de entrega, precio final claro y atencion al cliente.",
        "Consiguelo ahora con envio rapido en 24/48h",
    ),
    crear_ficha_pais(
        "AR",
        "Argentina",
        "Latinoamerica / Cono Sur",
        "ARS",
        "AR$",
        1050.0,
        "Espanol",
        "Instagram, Mercado Libre, TikTok, WhatsApp",
        "Mercado Pago, Transferencia Bancaria, Cuotas, Tarjeta",
        "13:00 - 15:00 y 20:00 - 23:30 ART",
        21.0,
        4.2,
        "Claridad en precios, beneficios por transferencia o cuotas y tono cercano y directo.",
        "Tienen stock real y como es el envio?",
        "Confirmar disponibilidad inmediata y detalle claro del despacho.",
        "Aprovecha la promo y pedilo hoy",
    ),
    crear_ficha_pais(
        "CL",
        "Chile",
        "Latinoamerica / Cono Sur",
        "CLP",
        "CLP$",
        950.0,
        "Espanol",
        "Instagram, TikTok, Mercado Libre, Facebook",
        "Webpay, Debito/Credito, Mercado Pago, Transferencia",
        "13:00 - 14:30 y 20:00 - 22:30 CLT",
        19.0,
        4.5,
        "Puntualidad en envios, calidad verificada y facilidad de compra con Webpay o debito.",
        "Llega a regiones fuera de Santiago?",
        "Informar cobertura nacional y tiempos estimados por zona.",
        "Compra online con despacho rapido a todo Chile",
    ),
    crear_ficha_pais(
        "PE",
        "Peru",
        "Latinoamerica / Andina",
        "PEN",
        "S/",
        3.75,
        "Espanol",
        "TikTok, Facebook, WhatsApp, Instagram",
        "Yape, Plin, Pago Contra Entrega, Tarjeta",
        "12:30 - 14:30 y 19:30 - 22:30 PET",
        18.0,
        3.2,
        "Pagos rapidos por Yape o Plin, entrega agil y demostraciones practicas en video.",
        "Se puede pagar con Yape o al recibir?",
        "Mostrar metodos locales simples y confirmacion inmediata del pedido.",
        "Pide facil por WhatsApp y paga con Yape o al recibir",
    ),
    crear_ficha_pais(
        "BR",
        "Brasil",
        "Latinoamerica / Mercosur",
        "BRL",
        "R$",
        5.65,
        "Portugues",
        "Instagram Reels, TikTok, Kwai, Shopee",
        "PIX, Cartao Parcelado, Boleto Bancario",
        "12:00 - 14:00 y 19:00 - 22:30 BRT",
        17.0,
        4.9,
        "Rapidez del PIX, parcelamiento sin intereses y demostraciones visuales autenticas.",
        "Tem desconto no PIX e entrega para todo o pais?",
        "Destacar agilidad del pago instantaneo y cobertura de envio.",
        "Garanta o seu agora com envio rapido",
    ),
    crear_ficha_pais(
        "UK",
        "Reino Unido",
        "Europa Occidental",
        "GBP",
        "GBP ",
        0.79,
        "Ingles",
        "TikTok Shop UK, Meta Ads, Google Shopping",
        "Debit Card, Apple Pay, PayPal, Klarna",
        "18:00 - 21:30 GMT",
        20.0,
        5.5,
        "Utilidad practica, claridad en tiempos de entrega y tono directo sin exageraciones.",
        "How fast is delivery and how do returns work?",
        "Mostrar plazos claros, soporte y condiciones simples.",
        "Order Today for Fast UK Delivery",
    ),
    crear_ficha_pais(
        "DE",
        "Alemania",
        "Europa Central",
        "EUR",
        "EUR ",
        0.92,
        "Aleman",
        "Google Shopping, Instagram, Amazon DE, YouTube",
        "PayPal, Klarna, SEPA, Tarjeta",
        "18:30 - 21:30 CET",
        19.0,
        5.8,
        "Datos tecnicos claros, durabilidad, orden y cumplimiento en los plazos.",
        "Sind alle Produktdetails und Lieferzeiten klar angegeben?",
        "Presentar especificaciones concretas y condiciones transparentes.",
        "Jetzt entdecken und direkt bestellen",
    ),
    crear_ficha_pais(
        "AE",
        "Emiratos Arabes Unidos",
        "Medio Oriente",
        "AED",
        "AED ",
        3.67,
        "Arabe / Ingles",
        "TikTok, Snapchat, Instagram, Noon",
        "Apple Pay, Tarjeta, Tabby, Cash on Delivery",
        "20:00 - 00:30 GST",
        5.0,
        6.0,
        "Presentacion cuidada, entrega rapida y comodidad en el metodo de pago.",
        "Is same-day or express delivery available?",
        "Indicar opciones de entrega express y confirmacion rapida.",
        "Order Now with Express Delivery",
    ),
    crear_ficha_pais(
        "CA",
        "Canada",
        "Norteamerica",
        "CAD",
        "CA$",
        1.38,
        "Ingles / Frances",
        "TikTok, Meta Ads, Amazon CA, Google Shopping",
        "Tarjeta Credito/Debito, Interac, Apple Pay, PayPal",
        "18:00 - 22:00 EST",
        13.0,
        6.2,
        "Confiabilidad, envio rastreado en todo el territorio y politicas claras.",
        "Does it ship across all Canadian provinces?",
        "Confirmar cobertura nacional y tiempos de entrega por provincia.",
        "Shop Now with Tracked Canadian Shipping",
    ),
    crear_ficha_pais(
        "EC",
        "Ecuador",
        "Latinoamerica / Andina",
        "USD",
        "$",
        1.0,
        "Espanol",
        "TikTok, Instagram, Facebook, WhatsApp",
        "Transferencia Bancaria, Deuna, Pago Contra Entrega, Tarjeta",
        "12:30 - 14:30 y 19:30 - 22:30 ECT",
        15.0,
        3.9,
        "Precios directos en dolares, atencion rapida por WhatsApp y entrega segura.",
        "Hacen envios a todas las provincias y pagan al recibir?",
        "Aclarar cobertura nacional y opciones de pago directo.",
        "Pide hoy con envio rapido a todo el Ecuador",
    ),
    crear_ficha_pais(
        "PA",
        "Panama",
        "Centroamerica",
        "USD / PAB",
        "$",
        1.0,
        "Espanol",
        "Instagram, TikTok, WhatsApp Business, Google",
        "Yappy, Transferencia ACH, Tarjeta, Efectivo",
        "12:00 - 14:00 y 19:00 - 22:30 EST",
        7.0,
        3.5,
        "Pago instantaneo con Yappy y entrega el mismo dia o siguiente dia.",
        "Aceptan Yappy y entrega a domicilio?",
        "Destacar pago por Yappy y mensajeria rapida en ciudad y provincias.",
        "Pide por WhatsApp y paga facil con Yappy",
    ),
    crear_ficha_pais(
        "DO",
        "Republica Dominicana",
        "Caribe",
        "DOP",
        "RD$",
        60.2,
        "Espanol",
        "Instagram, TikTok, WhatsApp, Facebook",
        "Transferencia Bancaria, Pago Contra Entrega, Tarjeta",
        "12:30 - 14:30 y 19:30 - 23:00 AST",
        18.0,
        4.0,
        "Cercania en el trato, entrega a domicilio rapida y demostraciones reales.",
        "Llega directo a mi puerta y cuando entregan?",
        "Confirmar entrega a domicilio en Santo Domingo y envios al interior.",
        "Ordena hoy con entrega rapida a domicilio",
    ),
]


# ==============================================================================
# 03. CATALOGO UNIVERSAL DE PRODUCTOS DE ALTA DEMANDA INTERNACIONAL
# ==============================================================================
def crear_producto_catalogo(
    pid,
    nombre,
    categoria,
    subcategoria,
    precio_base_usd,
    costo_base_usd,
    demanda_score,
    tendencia,
    pais_origen,
    mercados_top,
    publico_ideal,
    problema_que_resuelve,
    beneficio_estrella,
    gancho_viral,
    copy_aida,
    palabras_clave,
    canales_recomendados,
):
    precio_num = float(precio_base_usd)
    costo_num = float(costo_base_usd)
    margen_usd = round(precio_num - costo_num, 2)
    margen_pct = round((margen_usd / precio_num) * 100, 1) if precio_num > 0 else 0.0
    return {
        "id": pid,
        "nombre": nombre.strip(),
        "categoria": categoria.strip(),
        "subcategoria": subcategoria.strip(),
        "precio_base_usd": round(precio_num, 2),
        "costo_base_usd": round(costo_num, 2),
        "margen_usd": margen_usd,
        "margen_pct": margen_pct,
        "demanda_score": int(demanda_score),
        "tendencia": tendencia.strip(),
        "pais_origen": pais_origen.strip(),
        "mercados_top": list(mercados_top),
        "publico_ideal": publico_ideal.strip(),
        "problema_que_resuelve": problema_que_resuelve.strip(),
        "beneficio_estrella": beneficio_estrella.strip(),
        "gancho_viral": gancho_viral.strip(),
        "copy_aida": copy_aida.strip(),
        "palabras_clave": list(palabras_clave),
        "canales_recomendados": list(canales_recomendados),
    }


CATALOGO_PRODUCTOS_UNIVERSAL = [
    crear_producto_catalogo(
        "PRD-001",
        "Audifonos Inalambricos Cancelacion Activa ANC Pro",
        "Tecnologia y Gadgets",
        "Audio Portatil",
        49.90,
        14.50,
        96,
        "Alta demanda global",
        "Global",
        ["Estados Unidos", "Mexico", "Espana", "Venezuela", "Brasil"],
        "Estudiantes, trabajadores remotos, gamers y viajeros de 16 a 45 anos.",
        "Ruido externo molesto al estudiar, entrenar o viajar y cables enredados.",
        "Aislamiento de ruido con bateria de larga duracion y conexion estable.",
        "Ponte estos audifonos 3 segundos y el ruido de alrededor baja de golpe.",
        "ATENCION: Cansado de que el ruido distraiga al estudiar o entrenar?\nINTERES: Conexion inalambrica rapida y reduccion de ruido ambiental.\nDESEO: Comodidad diaria y autonomia prolongada.\nACCION: Pidelo hoy y aprovecha la disponibilidad.",
        ["audifonos", "bluetooth", "anc", "musica", "tecnologia", "audio"],
        ["TikTok Shop", "Instagram Reels", "YouTube Shorts", "Meta Ads"],
    ),
    crear_producto_catalogo(
        "PRD-002",
        "Reloj Inteligente Deportivo AMOLED Ultra Fit",
        "Tecnologia y Gadgets",
        "Wearables",
        59.00,
        18.00,
        95,
        "Rotacion constante",
        "Global",
        ["Estados Unidos", "Colombia", "Chile", "Espana", "Mexico"],
        "Deportistas, estudiantes y personas que siguen notificaciones y actividad fisica.",
        "Perder avisos al entrenar y no llevar registro simple de pasos o rutina.",
        "Pantalla nitida, modos deportivos y bateria de varios dias de uso.",
        "Mira lo facil que es revisar avisos y actividad diaria sin sacar el telefono.",
        "ATENCION: Quieres ver tus avisos y actividad diaria directo en tu muneca?\nINTERES: Pantalla brillante con multiples modos de uso y bateria duradera.\nDESEO: Practicidad en el gimnasio, la calle o el estudio.\nACCION: Haz tu pedido hoy.",
        ["smartwatch", "reloj", "fitness", "amoled", "deporte", "wearable"],
        ["Meta Ads", "TikTok", "Google Shopping"],
    ),
    crear_producto_catalogo(
        "PRD-003",
        "Mini Proyector Portatil HD Cine en Casa",
        "Tecnologia y Gadgets",
        "Entretenimiento Hogar",
        89.00,
        31.00,
        94,
        "Alto impacto visual",
        "Global",
        ["Estados Unidos", "Mexico", "Argentina", "Espana", "Venezuela"],
        "Familias, parejas, gamers y quienes buscan pantalla grande en casa.",
        "Pantallas pequenas o equipos fijos que no puedes mover de habitacion.",
        "Proyecta imagen amplia en pared o pantalla en pocos minutos.",
        "Convierte una pared lisa en pantalla grande en segundos para ver peliculas o jugar.",
        "ATENCION: Quieres disfrutar pantalla grande sin ocupar el espacio de un televisor enorme?\nINTERES: Formato compacto facil de mover y conectar.\nDESEO: Peliculas, series y partidas en distintos espacios.\nACCION: Asegura el tuyo hoy.",
        ["proyector", "cine", "peliculas", "pantalla", "hogar", "gaming"],
        ["TikTok", "Instagram Reels", "Facebook Ads"],
    ),
    crear_producto_catalogo(
        "PRD-004",
        "Termo Inteligente Acero Inoxidable con Sensor LED",
        "Hogar y Lifestyle",
        "Hidratacion",
        24.90,
        6.20,
        91,
        "Demanda diaria",
        "Global",
        ["Mexico", "Colombia", "Peru", "Venezuela", "Chile"],
        "Estudiantes, trabajadores, conductores y deportistas.",
        "Bebidas que pierden temperatura rapido o no saber si estan muy calientes.",
        "Conserva temperatura por horas con tapa indicadora practica.",
        "Toca la tapa y revisa la temperatura de tu bebida antes de tomar.",
        "ATENCION: Tu cafe o bebida pierde temperatura antes de terminar tu jornada?\nINTERES: Acero inoxidable resistente con tapa de lectura practica.\nDESEO: Lleva tu bebida a todas partes sin derrames.\nACCION: Pide el tuyo hoy.",
        ["termo", "botella", "cafe", "agua", "acero", "hogar"],
        ["TikTok", "WhatsApp Business", "Instagram"],
    ),
    crear_producto_catalogo(
        "PRD-005",
        "Serum Facial Hidratante Vitamina C y Hialuronico",
        "Belleza y Cuidado Personal",
        "Skincare",
        32.00,
        7.50,
        97,
        "Alta recompra",
        "Global",
        ["Estados Unidos", "Colombia", "Mexico", "Espana", "Brasil"],
        "Personas interesadas en rutina diaria de cuidado facial e hidratacion.",
        "Sensacion de piel seca o apagada por sol, viento o falta de descanso.",
        "Textura ligera de rapida absorcion para complementar la rutina diaria.",
        "Asi se aplica este serum en 15 segundos dentro de una rutina facial simple.",
        "ATENCION: Buscas un paso rapido para mantener tu piel hidratada en tu rutina?\nINTERES: Formula ligera de facil aplicacion diaria.\nDESEO: Sensacion fresca sin residuos pesados.\nACCION: Ordena hoy tu presentacion.",
        ["serum", "skincare", "piel", "vitamina c", "belleza", "hidratacion"],
        ["TikTok", "Instagram Reels", "YouTube Shorts"],
    ),
    crear_producto_catalogo(
        "PRD-006",
        "Perfume Concentrado Ambar y Vainilla 100ml",
        "Belleza y Cuidado Personal",
        "Fragancias",
        54.00,
        16.00,
        96,
        "Muy buscado",
        "Global",
        ["Emiratos Arabes Unidos", "Venezuela", "Colombia", "Estados Unidos", "Espana"],
        "Quienes prefieren aromas intensos y duraderos para el dia o la noche.",
        "Fragancias suaves que se desvanecen en poco tiempo.",
        "Aroma envolvente con buena fijacion y presentacion de 100 ml.",
        "Un aroma calido y marcado que acompana durante horas sin necesidad de reaplicar cada rato.",
        "ATENCION: Quieres una fragancia con presencia y buena duracion?\nINTERES: Notas calidas equilibradas en frasco de 100 ml.\nDESEO: Ideal para uso diario, salidas o regalo.\nACCION: Consiguelo hoy.",
        ["perfume", "fragancia", "aroma", "vainilla", "ambar", "regalo"],
        ["TikTok", "Instagram", "WhatsApp Business"],
    ),
    crear_producto_catalogo(
        "PRD-007",
        "Kit Bandas Elasticas de Resistencia Entrenamiento",
        "Fitness y Bienestar",
        "Entrenamiento",
        29.90,
        8.40,
        92,
        "Estable todo el ano",
        "Global",
        ["Estados Unidos", "Mexico", "Argentina", "Espana", "Colombia"],
        "Quienes entrenan en casa, viajan o combinan fuerza y movilidad.",
        "Dificultad para entrenar cuando no tienes maquinas o espacio amplio.",
        "Varios niveles de resistencia en un kit ligero y facil de guardar.",
        "Entrena distintos grupos musculares en casa con un kit que cabe en cualquier bolso.",
        "ATENCION: Quieres variar tus ejercicios en casa o de viaje?\nINTERES: Bandas de distintos niveles con accesorios practicos.\nDESEO: Rutinas flexibles en poco espacio.\nACCION: Pide tu kit hoy.",
        ["fitness", "gym", "bandas", "ejercicio", "casa", "fuerza"],
        ["Instagram Reels", "YouTube Shorts", "Meta Ads"],
    ),
    crear_producto_catalogo(
        "PRD-008",
        "Soporte y Corrector de Postura Ergonomico",
        "Fitness y Bienestar",
        "Ergonomia",
        27.50,
        6.90,
        90,
        "Util en estudio y oficina",
        "Global",
        ["Estados Unidos", "Espana", "Chile", "Mexico", "Peru"],
        "Estudiantes, programadores y personas que pasan horas sentadas.",
        "Incomodidad en hombros o espalda tras largas jornadas frente a pantalla.",
        "Ajuste comodo y recordatorio practico para cuidar la postura.",
        "Si pasas horas sentado estudiando o trabajando, este detalle ayuda a recordar tu postura.",
        "ATENCION: Notas cansancio en hombros al pasar horas frente al telefono o PC?\nINTERES: Diseno ajustable ligero para uso cotidiano.\nDESEO: Mayor comodidad durante tus jornadas.\nACCION: Pidelo hoy.",
        ["postura", "espalda", "ergonomia", "oficina", "estudio", "salud"],
        ["Facebook Ads", "TikTok", "Google Search"],
    ),
    crear_producto_catalogo(
        "PRD-009",
        "Microfono Inalambrico Dual para Video y Voz",
        "Tecnologia y Gadgets",
        "Creacion de Contenido",
        34.00,
        9.80,
        95,
        "Alta demanda en creadores",
        "Global",
        ["Venezuela", "Mexico", "Colombia", "Estados Unidos", "Argentina"],
        "Creadores de contenido, docentes, entrevistadores y emprendedores.",
        "Voz lejana o poco clara al grabar videos con el telefono.",
        "Captacion cercana de voz y conexion sencilla para grabaciones moviles.",
        "Mira como cambia la claridad de la voz al usar un microfono cercano al grabar.",
        "ATENCION: Quieres que tu voz se escuche mas clara en tus videos y notas?\nINTERES: Sistema compacto listo para conectar y grabar.\nDESEO: Graba entrevistas, clases o clips con mayor nitidez.\nACCION: Consiguelo hoy.",
        ["microfono", "creadores", "video", "audio", "voz", "clips"],
        ["TikTok", "Instagram", "YouTube"],
    ),
    crear_producto_catalogo(
        "PRD-010",
        "Organizador Giratorio 360 para Escritorio y Hogar",
        "Hogar y Lifestyle",
        "Organizacion",
        22.00,
        5.50,
        89,
        "Practico y visual",
        "Global",
        ["Mexico", "Colombia", "Espana", "Peru", "Chile"],
        "Quienes buscan orden en escritorios, mesas de estudio o estantes.",
        "Objetos pequenos mezclados que cuestan encontrar cuando los necesitas.",
        "Giro suave de 360 grados para acceder a cada compartimento.",
        "Gira el organizador y ten tus articulos de uso diario a la vista sin desorden.",
        "ATENCION: Pierdes tiempo buscando articulos pequenos en tu mesa o estante?\nINTERES: Compartimentos giratorios de acceso rapido.\nDESEO: Espacio mas limpio y ordenado cada dia.\nACCION: Pide el tuyo hoy.",
        ["organizador", "hogar", "escritorio", "orden", "360", "almacenaje"],
        ["TikTok", "Pinterest", "Facebook Ads"],
    ),
    crear_producto_catalogo(
        "PRD-011",
        "Calzado Urbano Ligero de Uso Diario",
        "Moda y Calzado",
        "Calzado Urbano",
        64.00,
        21.00,
        93,
        "Rotacion continua",
        "Global",
        ["Brasil", "Colombia", "Venezuela", "Mexico", "Estados Unidos"],
        "Personas que caminan bastante y buscan combinacion versatil para diario.",
        "Calzado rigido o pesado que incomoda al caminar largas distancias.",
        "Plantilla comoda y diseno versatil facil de combinar.",
        "Un par ligero y combinable para caminar todo el dia sin complicaciones.",
        "ATENCION: Buscas calzado comodo que combine con tu ropa de todos los dias?\nINTERES: Suela flexible y diseno adaptable a distintos estilos.\nDESEO: Comodidad al caminar, estudiar o salir.\nACCION: Elige tu talla hoy.",
        ["calzado", "zapatillas", "moda", "urbano", "comodidad", "estilo"],
        ["Instagram", "TikTok", "WhatsApp Business"],
    ),
    crear_producto_catalogo(
        "PRD-012",
        "Guia y Plantillas de Marketing y Ventas Digitales",
        "Productos Digitales",
        "Educacion y Negocios",
        39.00,
        2.00,
        98,
        "Entrega digital inmediata",
        "Internacional",
        ["Estados Unidos", "Espana", "Mexico", "Colombia", "Argentina", "Venezuela"],
        "Emprendedores, comercios y creadores que organizan promociones online.",
        "No saber como estructurar ofertas, mensajes o rutinas de publicacion.",
        "Plantillas listas para adaptar a productos, paises y canales digitales.",
        "Ten una estructura clara de mensajes y campanas lista para usar en minutos.",
        "ATENCION: Quieres ordenar tus mensajes y ofertas para vender mejor online?\nINTERES: Plantillas practicas de ganchos, textos y planificacion.\nDESEO: Ahorra tiempo al preparar cada campana.\nACCION: Accede hoy mismo.",
        ["plantillas", "marketing", "ventas", "digital", "guia", "campanas"],
        ["Instagram", "TikTok", "YouTube", "WhatsApp"],
    ),
    crear_producto_catalogo(
        "PRD-013",
        "Aro de Luz LED con Tripode Ajustable para Grabacion",
        "Tecnologia y Gadgets",
        "Iluminacion y Video",
        31.50,
        9.20,
        91,
        "Muy solicitado",
        "Global",
        ["Venezuela", "Colombia", "Mexico", "Peru", "Estados Unidos"],
        "Creadores, tiendas online, maquilladores y transmisiones en vivo.",
        "Videos oscuros o con sombras duras al grabar en interiores.",
        "Tres tonos de luz regulables y soporte estable para telefono.",
        "Mira la diferencia de nitidez en tus videos cuando iluminas bien el rostro.",
        "ATENCION: Tus fotos o videos se ven opacos dentro de casa?\nINTERES: Iluminacion regulable con soporte firme.\nDESEO: Imagen limpia y profesional en cada toma.\nACCION: Pidelo hoy.",
        ["aro de luz", "led", "tripode", "iluminacion", "video", "fotos"],
        ["TikTok", "Instagram", "Mercado Libre"],
    ),
    crear_producto_catalogo(
        "PRD-014",
        "Cafetera Portatil Espresso Manual de Viaje",
        "Hogar y Lifestyle",
        "Cafe y Cocina",
        44.00,
        14.80,
        90,
        "Nicho apasionado",
        "Global",
        ["Estados Unidos", "Espana", "Chile", "Colombia", "Mexico"],
        "Amantes del cafe, viajeros, conductores y trabajadores de oficina.",
        "Depender de cafeterias costosas o cafe instantaneo fuera de casa.",
        "Prepara cafe espresso concentrado sin electricidad en minutos.",
        "Prepara un espresso con espuma en cualquier lugar sin enchufes ni cables.",
        "ATENCION: Extranas un buen cafe cuando sales de viaje o estas en la oficina?\nINTERES: Sistema compacto de presion manual facil de limpiar.\nDESEO: Cafe recien hecho donde quieras.\nACCION: Ordena la tuya hoy.",
        ["cafe", "cafetera", "espresso", "viaje", "portatil", "cocina"],
        ["Instagram Reels", "YouTube Shorts", "Facebook Ads"],
    ),
    crear_producto_catalogo(
        "PRD-015",
        "Mochila Antirrobo Impermeable con Puerto USB",
        "Moda y Calzado",
        "Accesorios y Viaje",
        46.00,
        15.20,
        93,
        "Alta utilidad",
        "Global",
        ["Colombia", "Mexico", "Argentina", "Espana", "Venezuela"],
        "Estudiantes universitarios, trabajadores con laptop y viajeros urbanos.",
        "Preocupacion por lluvia, desorden de cables y seguridad en transporte.",
        "Cierres ocultos, tela repelente al agua y compartimento acolchado.",
        "Todo tu equipo protegido de la lluvia y bien organizado en un solo lugar.",
        "ATENCION: Llevas laptop, cuadernos y accesorios todos los dias en la calle?\nINTERES: Material resistente al agua con cierres discretos.\nDESEO: Orden, comodidad en hombros y tranquilidad.\nACCION: Consigue la tuya hoy.",
        ["mochila", "bolso", "impermeable", "usb", "laptop", "viaje"],
        ["Facebook Ads", "Instagram", "Mercado Libre"],
    ),
    crear_producto_catalogo(
        "PRD-016",
        "Limpiador Ultrasonico Portatil para Lentes y Joyas",
        "Hogar y Lifestyle",
        "Cuidado de Articulos",
        28.90,
        8.10,
        88,
        "Demostracion muy visual",
        "Global",
        ["Estados Unidos", "Espana", "Mexico", "Chile", "Brasil"],
        "Personas que usan lentes diarios, relojes metalicos o accesorios.",
        "Suciedad acumulada en bordes de gafas o piezas pequenas dificiles de limpiar.",
        "Limpieza profunda con agua en 3 minutos sin rayar superficies.",
        "Mira lo que sale de unos lentes aparentemente limpios tras 3 minutos aqui dentro.",
        "ATENCION: Tus lentes o relojes acumulan grasa en esquinas dificiles?\nINTERES: Vibracion de alta frecuencia suave con tus objetos.\nDESEO: Brillo impecable en pocos minutos.\nACCION: Pidelo hoy.",
        ["limpiador", "lentes", "gafas", "reloj", "hogar", "ultrasonico"],
        ["TikTok", "Instagram Reels", "Pinterest"],
    ),
]


# ==============================================================================
# 04. FRAMEWORKS DE COPYWRITING, CALENDARIO SEMANAL Y TENDENCIAS
# ==============================================================================
FRAMEWORKS_COPY = {
    "AIDA": {
        "nombre": "AIDA (Atencion - Interes - Deseo - Accion)",
        "descripcion": "Estructura directa para captar atencion, despertar interes, generar deseo y pedir accion.",
        "pasos": [
            "Atencion: Abre con una frase o situacion clara que frene el avance.",
            "Interes: Muestra como funciona o que lo hace util.",
            "Deseo: Destaca el beneficio practico en el dia a dia.",
            "Accion: Indica el siguiente paso claro para comprar o consultar.",
        ],
    },
    "PAS": {
        "nombre": "PAS (Problema - Agitacion - Solucion)",
        "descripcion": "Parte de un problema concreto, muestra su impacto y presenta la solucion.",
        "pasos": [
            "Problema: Identifica el inconveniente real.",
            "Agitacion: Explica que ocurre si no se resuelve.",
            "Solucion: Presenta el producto y como ayuda.",
        ],
    },
    "BAB": {
        "nombre": "BAB (Antes - Despues - Puente)",
        "descripcion": "Contrasta el estado inicial con el resultado esperado y el camino entre ambos.",
        "pasos": [
            "Antes: Situacion con el problema.",
            "Despues: Escenario mas comodo o resuelto.",
            "Puente: El producto como herramienta de cambio.",
        ],
    },
    "4U": {
        "nombre": "4U (Urgente - Unico - Especifico - Util)",
        "descripcion": "Enfocado en claridad, datos concretos y motivo practico para actuar.",
        "pasos": [
            "Urgente: Motivo para revisar hoy.",
            "Unico: Rasgo distintivo de la propuesta.",
            "Especifico: Precio, plazo o caracteristica medible.",
            "Util: Beneficio claro para quien lo adquiere.",
        ],
    },
}

PLANTILLAS_CALENDARIO_SEMANAL = [
    {
        "dia": "Lunes",
        "objetivo": "Atraccion y Gancho Inicial",
        "formato": "Video Corto (TikTok / Reels / Shorts)",
        "estructura": "Gancho en los primeros 3 segundos + demostracion directa del producto.",
        "kpi": "Retencion inicial y reproducciones.",
    },
    {
        "dia": "Martes",
        "objetivo": "Educacion y Consejos Utiles",
        "formato": "Carrusel o Video Explicativo",
        "estructura": "Errores comunes al elegir y como tomar una buena decision.",
        "kpi": "Guardados y compartidos.",
    },
    {
        "dia": "Miercoles",
        "objetivo": "Prueba Real y Comparativa",
        "formato": "Demostracion en Uso Real",
        "estructura": "Mostrar el producto funcionando en situacion cotidiana.",
        "kpi": "Comentarios y consultas.",
    },
    {
        "dia": "Jueves",
        "objetivo": "Respuesta a Dudas Frecuentes",
        "formato": "Video / Publicacion de Preguntas y Respuestas",
        "estructura": "Aclarar precio, envio, pagos y garantia de forma directa.",
        "kpi": "Clics al enlace o mensaje.",
    },
    {
        "dia": "Viernes",
        "objetivo": "Oferta y Llamado a la Accion",
        "formato": "Anuncio Estructurado (AIDA / PAS)",
        "estructura": "Beneficio principal + condicion vigente + llamada a la accion.",
        "kpi": "Contactos y ventas.",
    },
    {
        "dia": "Sabado",
        "objetivo": "Estilo de Vida y Uso Cotidiano",
        "formato": "Historias o Clip Breve",
        "estructura": "Integrar el producto en una actividad de fin de semana.",
        "kpi": "Interaccion y respuestas.",
    },
    {
        "dia": "Domingo",
        "objetivo": "Resumen y Cierre Semanal",
        "formato": "Recordatorio Directo",
        "estructura": "Sintesis de beneficios + disponibilidad + como pedirlo.",
        "kpi": "Conversiones de cierre.",
    },
]

TENDENCIAS_MARKETING_ACTUAL = [
    {
        "titulo": "Videos autenticos grabados en situaciones reales",
        "impacto": "Alto",
        "detalle": "Mostrar el uso natural del producto suele generar mas confianza que un anuncio acartonado.",
    },
    {
        "titulo": "Adaptacion a moneda y pagos de cada pais",
        "impacto": "Clave Internacional",
        "detalle": "Hablar en la moneda local y mencionar metodos de pago conocidos reduce dudas al comprar.",
    },
    {
        "titulo": "Ganchos claros desde los primeros 3 segundos",
        "impacto": "Alto en Video Corto",
        "detalle": "Ir directo al punto evita que el usuario pase de largo sin ver el beneficio.",
    },
    {
        "titulo": "Seguimiento rapido por mensajeria y WhatsApp",
        "impacto": "Alto en Ventas Directas",
        "detalle": "Responder con claridad y rapidez mejora el cierre de pedidos.",
    },
    {
        "titulo": "Medicion constante de costos, ventas y ROAS",
        "impacto": "Esencial para Escalar",
        "detalle": "Revisar ganancia neta y retorno sobre inversion evita gastar sin rumbo.",
    },
]


# ==============================================================================
# 05. FUNCIONES DE UTILIDAD, PERSISTENCIA Y GENERACION DE CONTENIDO
# ==============================================================================
def normalizar_texto(texto):
    limpio = (texto or "").strip().lower()
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }
    for orig, dest in reemplazos.items():
        limpio = limpio.replace(orig, dest)
    limpio = re.sub(r"\s+", " ", limpio)
    return limpio


def validar_correo(correo):
    limpio = (correo or "").strip().lower()
    if not limpio or "@" not in limpio:
        return ""
    partes = limpio.split("@")
    if len(partes) != 2 or not partes[0] or "." not in partes[1]:
        return ""
    return limpio


def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {
            "usuarios": {},
            "productos_personalizados": [],
            "campanas_guardadas": [],
        }
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("usuarios", {})
                data.setdefault("productos_personalizados", [])
                data.setdefault("campanas_guardadas", [])
                return data
    except Exception:
        pass
    return {
        "usuarios": {},
        "productos_personalizados": [],
        "campanas_guardadas": [],
    }


def guardar_db(data):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def obtener_catalogo_completo():
    db = cargar_db()
    lista = list(CATALOGO_PRODUCTOS_UNIVERSAL)
    extras = db.get("productos_personalizados", [])
    if isinstance(extras, list):
        for item in extras:
            if isinstance(item, dict) and item.get("nombre"):
                lista.append(item)
    return lista


def obtener_pais_por_codigo(codigo):
    cod = (codigo or "US").strip().upper()
    for p in PAISES_MARKETING:
        if p["codigo"] == cod:
            return p
    return PAISES_MARKETING[0]


def generar_kit_marketing_dinamico(
    nombre_producto,
    categoria,
    precio_usd,
    costo_usd,
    beneficio,
    problema,
    publico,
    pais_codigo,
    framework_clave,
):
    pais = obtener_pais_por_codigo(pais_codigo)
    precio_local = round(precio_usd * pais["tasa_usd"], 2)
    costo_local = round(costo_usd * pais["tasa_usd"], 2)
    envio_local = round(pais["envio_usd"] * pais["tasa_usd"], 2)
    margen_neto_usd = round(precio_usd - costo_usd - pais["envio_usd"], 2)
    margen_pct = round((margen_neto_usd / precio_usd) * 100, 1) if precio_usd > 0 else 0.0

    fw = FRAMEWORKS_COPY.get(framework_clave, FRAMEWORKS_COPY["AIDA"])

    ganchos = [
        f"Si buscas {categoria.lower()}, mira como funciona {nombre_producto} en pocos segundos.",
        f"Deja atras {problema.lower()} con {nombre_producto}.",
        f"Asi se ve {nombre_producto} pensado para {pais['nombre']} por {pais['simbolo']}{precio_local}.",
        f"Una forma practica de lograr {beneficio.lower()} sin complicaciones.",
        f"Antes y despues con {nombre_producto}: mira la diferencia en uso real.",
    ]

    if framework_clave == "PAS":
        copy_principal = (
            f"[PROBLEMA] {problema}\n"
            f"[AGITACION] Seguir lidiando con {problema.lower()} consume tiempo y resta comodidad en el dia a dia.\n"
            f"[SOLUCION] {nombre_producto} aporta {beneficio.lower()}.\n"
            f"[{pais['nombre'].upper()}] Referencia: {pais['simbolo']}{precio_local} ({pais['moneda']}) | Pagos: {pais['metodos_pago']}.\n"
            f"[ACCION] {pais['cta_local']}."
        )
    elif framework_clave == "BAB":
        copy_principal = (
            f"[ANTES] Enfrentar {problema.lower()} de forma cotidiana.\n"
            f"[DESPUES] Contar con {beneficio.lower()} de manera mas simple.\n"
            f"[PUENTE] {nombre_producto} enfocado en {publico.lower()}.\n"
            f"[{pais['nombre'].upper()}] {pais['simbolo']}{precio_local} ({pais['moneda']}) | {pais['cta_local']}."
        )
    elif framework_clave == "4U":
        copy_principal = (
            f"[HOY] Disponibilidad activa en {pais['nombre']} (horario sugerido: {pais['horario_pico']}).\n"
            f"[PROPUESTA] {nombre_producto}: {beneficio}.\n"
            f"[DATO CLAVE] Precio estimado {pais['simbolo']}{precio_local} ({pais['moneda']}).\n"
            f"[UTILIDAD] Resuelve {problema.lower()}. {pais['cta_local']}."
        )
    else:
        copy_principal = (
            f"[ATENCION] {ganchos[0]}\n"
            f"[INTERES] {nombre_producto} ayuda frente a {problema.lower()} mediante {beneficio.lower()}.\n"
            f"[DESEO] Pensado para {publico.lower()} en {pais['nombre']}. Pagos habituales: {pais['metodos_pago']}.\n"
            f"[ACCION] Precio: {pais['simbolo']}{precio_local} ({pais['moneda']}). {pais['cta_local']}."
        )

    guion_video_corto = (
        f"00:00 - 00:03 [GANCHO]: '{ganchos[1]}'\n"
        f"00:03 - 00:10 [PROBLEMA]: Muestra de forma breve '{problema}'.\n"
        f"00:10 - 00:20 [DEMOSTRACION]: Muestra '{nombre_producto}' cumpliendo '{beneficio}'.\n"
        f"00:20 - 00:26 [CIERRE]: '{pais['cta_local']} ({pais['simbolo']}{precio_local})'."
    )

    return {
        "producto": nombre_producto,
        "categoria": categoria,
        "pais": pais,
        "precio_usd": precio_usd,
        "precio_local": precio_local,
        "costo_local": costo_local,
        "envio_local": envio_local,
        "margen_neto_usd": margen_neto_usd,
        "margen_pct": margen_pct,
        "framework": fw["nombre"],
        "ganchos": ganchos,
        "copy_principal": copy_principal,
        "guion_video_corto": guion_video_corto,
    }


# ==============================================================================
# 06. ESTILOS UNIFORMES (VERDE CLARO, TONOS OSCUROS Y BLANCO)
# ==============================================================================
HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE MARKETING · INTERNATIONAL SUITE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-dark: #06110e;
  --bg-panel: #0c1f1a;
  --bg-card: #112a24;
  --bg-input: #081713;
  --green-light: #34d399;
  --green-bright: #6ee7b7;
  --green-border: #10b981;
  --white: #ffffff;
  --text-soft: #d1fae5;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-dark);
  color: var(--white);
  font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif;
  font-size: 16px;
}

body {
  padding-bottom: 68px;
}

header {
  background-color: var(--bg-panel);
  border-bottom: 2px solid var(--green-light);
  padding: 14px 14px 10px;
  position: sticky;
  top: 0;
  z-index: 40;
}

.top-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

header h1 {
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  color: var(--green-light);
  letter-spacing: 0.5px;
}

.sub-head {
  font-size: 12.5px;
  color: var(--white);
  margin-top: 2px;
  font-weight: 600;
}

.pill-user {
  background-color: var(--bg-dark);
  border: 1px solid var(--green-light);
  color: var(--green-bright);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  max-width: 48%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-h {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 11px 0 4px;
  -webkit-overflow-scrolling: touch;
}

.nav-btn {
  flex: 0 0 auto;
  width: auto;
  margin: 0;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 700;
  border-radius: 6px;
  background-color: var(--bg-dark);
  color: var(--white);
  border: 1px solid var(--green-border);
  cursor: pointer;
}

.nav-btn.activo {
  background-color: var(--green-light);
  color: #04100c;
  border-color: var(--white);
  font-weight: 700;
}

.wrap {
  max-width: 1020px;
  margin: 0 auto;
  padding: 14px;
}

.card {
  background-color: var(--bg-card);
  border: 1px solid var(--green-border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 14px;
}

h2 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--green-light);
}

h3 {
  margin: 12px 0 6px;
  font-size: 15.5px;
  font-weight: 700;
  color: var(--white);
}

label {
  display: block;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-soft);
  margin-top: 10px;
}

input[type="text"],
input[type="password"],
input[type="email"],
input[type="number"],
textarea,
select {
  width: 100%;
  padding: 12px 13px;
  font-size: 15px;
  font-family: 'Space Grotesk', sans-serif;
  border-radius: 7px;
  border: 1px solid var(--green-light);
  background-color: var(--bg-input);
  color: var(--white);
  margin-top: 6px;
}

textarea {
  min-height: 110px;
  line-height: 1.45;
}

button {
  width: 100%;
  padding: 12px 14px;
  font-size: 14.5px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  border-radius: 7px;
  border: 1px solid var(--green-bright);
  background-color: var(--green-light);
  color: #04100c;
  cursor: pointer;
  margin-top: 10px;
}

button.sec-btn {
  background-color: var(--bg-panel);
  color: var(--white);
  border: 1px solid var(--green-light);
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

.kpi-box {
  background-color: var(--bg-panel);
  border: 1px solid var(--green-border);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.kpi-box span {
  display: block;
  font-size: 11.5px;
  color: var(--text-soft);
  text-transform: uppercase;
}

.kpi-box strong {
  display: block;
  font-size: 16.5px;
  color: var(--green-light);
  margin-top: 4px;
}

.box-salida {
  background-color: var(--bg-panel);
  border-left: 4px solid var(--green-light);
  border-top: 1px solid rgba(52, 211, 153, 0.3);
  border-right: 1px solid rgba(52, 211, 153, 0.3);
  border-bottom: 1px solid rgba(52, 211, 153, 0.3);
  border-radius: 0 8px 8px 0;
  padding: 12px 14px;
  margin-top: 10px;
  font-size: 14.5px;
  line-height: 1.5;
  white-space: pre-line;
  color: var(--white);
}

.prod-item {
  background-color: var(--bg-panel);
  border: 1px solid var(--green-border);
  border-radius: 8px;
  padding: 13px;
  margin-top: 10px;
}

.prod-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.tag {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 5px;
  font-size: 11.5px;
  font-weight: 700;
  background-color: var(--bg-dark);
  color: var(--green-bright);
  border: 1px solid var(--green-border);
  margin: 3px 4px 3px 0;
}

.hoja-scroll {
  width: 100%;
  overflow-x: auto;
  margin-top: 10px;
}

table.mkt-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
}

table.mkt-table th,
table.mkt-table td {
  border: 1px solid var(--green-border);
  padding: 8px;
  text-align: center;
}

table.mkt-table th {
  background-color: var(--bg-panel);
  color: var(--green-light);
  font-size: 13px;
}

table.mkt-table td input {
  margin: 0;
  height: 44px;
  font-size: 15px;
  font-weight: 700;
}

.pantalla-fija {
  position: fixed;
  inset: 0;
  background-color: var(--bg-dark);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  overflow-y: auto;
}

.oculto {
  display: none !important;
}

.estado-msg {
  font-size: 13.5px;
  color: var(--green-bright);
  margin-top: 8px;
  line-height: 1.4;
  font-weight: 600;
}

.firma-celso {
  position: fixed;
  right: 12px;
  bottom: 10px;
  background-color: var(--bg-panel);
  border: 1px solid var(--green-light);
  color: var(--white);
  font-size: 11px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 5px;
  z-index: 50;
}
</style>
</head>
<body>
"""
