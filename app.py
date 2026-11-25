
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
CLAVES_VALIDAS = {"VIP100", "Celso2026"}
ARCHIVO_DB = os.environ.get("CPRE_MKT_DB_FILE", "cpre_marketing_datos.json")
VERSION_SISTEMA = "C-PRE MARKETING v7.0 INTERNATIONAL SUITE"
AUTOR_SISTEMA = "CREACIONES CELSO"

CONFIGURACION_VISUAL_BASE = {
    "fondo_principal": "#070b19",
    "fondo_panel": "#0f172a",
    "fondo_tarjeta": "#151f38",
    "fondo_entrada": "#090f22",
    "color_oro": "#ffb703",
    "color_coral": "#ff2a6d",
    "color_cian": "#00f5d4",
    "color_esmeralda": "#10b981",
    "color_violeta": "#8b5cf6",
    "texto_principal": "#f8fafc",
    "texto_secundario": "#cbd5e1",
    "fuente_titulos": "Orbitron",
    "fuente_cuerpo": "Space Grotesk",
}

ESTRUCTURA_MODULOS_BASE = [
    {"id": "modBuscador", "orden": 1, "titulo": "1. Buscador Productos", "acento": "cian"},
    {"id": "modLocalizador", "orden": 2, "titulo": "2. Paises y Monedas", "acento": "oro"},
    {"id": "modCopy", "orden": 3, "titulo": "3. Copy y Guiones", "acento": "coral"},
    {"id": "modCalendario", "orden": 4, "titulo": "4. Plan y Tendencias", "acento": "violeta"},
    {"id": "modSimulador", "orden": 5, "titulo": "5. Hoja ROAS y Ventas", "acento": "esmeralda"},
    {"id": "modCuenta", "orden": 6, "titulo": "6. Correo y Progreso", "acento": "oro"},
]


# ==============================================================================
# 02. BASE DE PAISES, MONEDAS, METODOS DE PAGO Y CULTURA COMERCIAL
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
# 06. ESTILOS Y CABECERA DE C-PRE MARKETING
# ==============================================================================
HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE MARKETING · INTERNATIONAL SUITE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-obsidian: #070b19;
  --bg-panel: #0f172a;
  --bg-card: #151f38;
  --bg-input: #090f22;
  --accent-gold: #ffb703;
  --accent-coral: #ff2a6d;
  --accent-cyan: #00f5d4;
  --accent-emerald: #10b981;
  --accent-violet: #8b5cf6;
  --text-main: #f8fafc;
  --text-soft: #cbd5e1;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background: radial-gradient(circle at top right, #1b1035 0%, #070b19 52%, #050814 100%);
  color: var(--text-main);
  font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif;
  font-size: 16px;
}

body {
  padding-bottom: 72px;
}

h1, h2, h3, .brand-font {
  font-family: 'Orbitron', 'Space Grotesk', sans-serif;
  letter-spacing: 0.7px;
}

header {
  background: linear-gradient(90deg, #090d20 0%, #1a103c 50%, #090d20 100%);
  border-bottom: 2px solid var(--accent-gold);
  padding: 14px 14px 10px;
  position: sticky;
  top: 0;
  z-index: 40;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.55);
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
  font-weight: 900;
  background: linear-gradient(90deg, #ffb703, #00f5d4, #ff2a6d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sub-head {
  font-size: 12px;
  color: var(--accent-cyan);
  margin-top: 3px;
  font-weight: 700;
}

.pill-user {
  background: rgba(255, 183, 3, 0.14);
  border: 1px solid var(--accent-gold);
  color: var(--accent-gold);
  padding: 6px 11px;
  border-radius: 999px;
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
  border-radius: 999px;
  background: #131c36;
  color: #e2e8f0;
  border: 1px solid rgba(255, 183, 3, 0.45);
  cursor: pointer;
}

.nav-btn.activo {
  background: linear-gradient(90deg, #ff2a6d 0%, #ffb703 100%);
  color: #070b19;
  border-color: #ffffff;
  font-weight: 900;
}

.wrap {
  max-width: 1020px;
  margin: 0 auto;
  padding: 14px;
}

.card {
  background: linear-gradient(160deg, rgba(21, 31, 56, 0.96) 0%, rgba(12, 19, 38, 0.98) 100%);
  border: 1px solid rgba(0, 245, 212, 0.28);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

.card-gold {
  border-color: rgba(255, 183, 3, 0.55);
}

.card-coral {
  border-color: rgba(255, 42, 109, 0.55);
}

h2 {
  margin: 0 0 10px;
  font-size: 17.5px;
  color: var(--accent-gold);
}

h3 {
  margin: 12px 0 6px;
  font-size: 15px;
  color: var(--accent-cyan);
}

label {
  display: block;
  font-size: 13.5px;
  font-weight: 700;
  color: #e2e8f0;
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
  border-radius: 9px;
  border: 1px solid rgba(0, 245, 212, 0.4);
  background: var(--bg-input);
  color: #ffffff;
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
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  border-radius: 9px;
  border: none;
  background: linear-gradient(90deg, #ffb703 0%, #ff2a6d 100%);
  color: #070b19;
  cursor: pointer;
  margin-top: 10px;
}

button:active {
  transform: scale(0.99);
}

button.cyan-btn {
  background: linear-gradient(90deg, #00f5d4 0%, #3b82f6 100%);
  color: #050814;
}

button.sec-btn {
  background: #172342;
  color: var(--accent-cyan);
  border: 1px solid var(--accent-cyan);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
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
  background: #080e20;
  border: 1px solid rgba(255, 183, 3, 0.4);
  border-radius: 10px;
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
  font-family: 'Orbitron', sans-serif;
  font-size: 16px;
  color: var(--accent-cyan);
  margin-top: 4px;
}

.box-salida {
  background: #070c1b;
  border-left: 4px solid var(--accent-cyan);
  border-radius: 0 10px 10px 0;
  padding: 12px 14px;
  margin-top: 10px;
  font-size: 14.5px;
  line-height: 1.5;
  white-space: pre-line;
  color: #f1f5f9;
}

.box-gold {
  border-left-color: var(--accent-gold);
}

.box-coral {
  border-left-color: var(--accent-coral);
}

.prod-item {
  background: #091024;
  border: 1px solid rgba(139, 92, 246, 0.45);
  border-radius: 12px;
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
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  background: rgba(0, 245, 212, 0.14);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 245, 212, 0.4);
  margin: 3px 4px 3px 0;
}

.tag-gold {
  background: rgba(255, 183, 3, 0.16);
  color: var(--accent-gold);
  border-color: rgba(255, 183, 3, 0.45);
}

.tag-coral {
  background: rgba(255, 42, 109, 0.16);
  color: #ff7aa2;
  border-color: rgba(255, 42, 109, 0.45);
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
  border: 1px solid rgba(0, 245, 212, 0.3);
  padding: 8px;
  text-align: center;
}

table.mkt-table th {
  background: #131e3a;
  color: var(--accent-gold);
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
  background: radial-gradient(circle at center, #1b1138 0%, #060916 100%);
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
  color: var(--accent-gold);
  margin-top: 8px;
  line-height: 1.4;
}

.firma-celso {
  position: fixed;
  right: 12px;
  bottom: 10px;
  background: #090d20;
  border: 1px solid var(--accent-gold);
  color: var(--accent-gold);
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 800;
  padding: 5px 10px;
  border-radius: 6px;
  z-index: 50;
}
</style>
</head>
<body>
"""
HTML_PAGE += """
<!-- PANTALLA 1: CLAVE DE ACCESO -->
<div id="pantallaClave" class="pantalla-fija">
  <div class="card card-gold" style="max-width:440px;width:100%;">
    <h2>C-PRE MARKETING</h2>
    <p style="margin:6px 0 10px;font-size:14px;color:var(--text-soft);">Plataforma Internacional de Productos, Localizacion, Copywriting y Campanas.</p>
    <label for="inpClave">Clave de Acceso:</label>
    <input type="password" id="inpClave" placeholder="Ingresa clave de acceso...">
    <button type="button" onclick="verificarClave()">DESBLOQUEAR</button>
    <div id="msgClave" class="estado-msg"></div>
  </div>
</div>

<!-- PANTALLA 2: BIENVENIDA, CREACIONES CELSO, CORREO Y ACEPTAR -->
<div id="pantallaEntrada" class="pantalla-fija oculto">
  <div class="card card-coral" style="max-width:600px;width:100%;">
    <h2>Bienvenido a C-Pre Marketing</h2>
    <div style="font-family:'Orbitron',sans-serif;font-size:13px;font-weight:800;color:var(--accent-cyan);margin-bottom:8px;">Creaciones Celso</div>
    <div class="box-salida box-gold" style="margin-top:6px;"><strong>Como funciona la aplicacion:</strong>
1. Escribe tu <strong>correo electronico</strong> para guardar y recuperar tu progreso.
2. Pulsa <strong>ACEPTAR</strong> para avanzar directo a los modulos y navegar de izquierda a derecha.
3. Incluye buscador de productos, adaptacion por pais/moneda, generador de copy y guiones, calendario semanal, hoja ROAS y respaldo por correo.</div>
    <label for="inpCorreoEntrada">Correo electronico:</label>
    <input type="email" id="inpCorreoEntrada" placeholder="tu_correo@ejemplo.com">
    <button type="button" onclick="aceptarEntrada()">ACEPTAR</button>
    <div id="msgEntrada" class="estado-msg"></div>
  </div>
</div>

<!-- CABECERA PRINCIPAL Y NAVEGACION HORIZONTAL -->
<header id="cabeceraApp" class="oculto">
  <div class="top-head">
    <div>
      <h1>C-PRE MARKETING</h1>
      <div class="sub-head">Creaciones Celso · Suite Internacional</div>
    </div>
    <div class="pill-user" id="lblCorreoBadge">Sin correo</div>
  </div>
  <nav class="nav-h" aria-label="Modulos de izquierda a derecha">
    <button type="button" class="nav-btn activo" data-sec="modBuscador" onclick="irModulo('modBuscador', this)">1. Buscador Productos</button>
    <button type="button" class="nav-btn" data-sec="modLocalizador" onclick="irModulo('modLocalizador', this)">2. Paises y Monedas</button>
    <button type="button" class="nav-btn" data-sec="modCopy" onclick="irModulo('modCopy', this)">3. Copy y Guiones</button>
    <button type="button" class="nav-btn" data-sec="modCalendario" onclick="irModulo('modCalendario', this)">4. Plan y Tendencias</button>
    <button type="button" class="nav-btn" data-sec="modSimulador" onclick="irModulo('modSimulador', this)">5. Hoja ROAS y Ventas</button>
    <button type="button" class="nav-btn" data-sec="modEmbudo" onclick="irModulo('modEmbudo', this)">6. Embudo CTR y CPA</button>
    <button type="button" class="nav-btn" data-sec="modAudiencias" onclick="irModulo('modAudiencias', this)">7. Audiencias y Ofertas</button>
    <button type="button" class="nav-btn" data-sec="modCuenta" onclick="irModulo('modCuenta', this)">8. Correo y Progreso</button>
  </nav>
</header>

<main id="contenedorModulos" class="wrap oculto">

  <!-- MODULO 1: BUSCADOR UNIVERSAL DE PRODUCTOS -->
  <section id="modBuscador" class="card modulo-panel">
    <h2>1. Buscador Universal de Productos</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Busca cualquier producto por nombre, categoria, pais o palabra clave, o agrega el tuyo propio.</p>

    <div class="grid-2">
      <div>
        <label for="inpBuscarProd">Buscar producto o palabra clave:</label>
        <input type="text" id="inpBuscarProd" placeholder="Ej. audifonos, reloj, termo, perfume..." oninput="filtrarCatalogo()">
      </div>
      <div>
        <label for="selCategoriaFiltro">Categoria:</label>
        <select id="selCategoriaFiltro" onchange="filtrarCatalogo()">
          <option value="TODAS">Todas las categorias</option>
        </select>
      </div>
    </div>

    <div class="grid-3" style="margin-top:10px;">
      <div class="kpi-box"><span>Productos Activos</span><strong id="kpiTotalProds">0</strong></div>
      <div class="kpi-box"><span>Paises Conectados</span><strong id="kpiTotalPaises">12</strong></div>
      <div class="kpi-box"><span>Margen Promedio</span><strong id="kpiMargenProm">0%</strong></div>
    </div>

    <div id="listaProductos"></div>

    <div class="card card-gold" style="margin-top:16px;">
      <h3>Agregar Cualquier Producto al Catalogo</h3>
      <div class="grid-2">
        <div>
          <label for="nuevoProdNombre">Nombre del producto o servicio:</label>
          <input type="text" id="nuevoProdNombre" placeholder="Ej. Lampara LED Recargable">
        </div>
        <div>
          <label for="nuevoProdCat">Categoria:</label>
          <input type="text" id="nuevoProdCat" value="Tecnologia y Gadgets">
        </div>
      </div>
      <div class="grid-2">
        <div>
          <label for="nuevoProdPrecio">Precio de venta (USD):</label>
          <input type="number" id="nuevoProdPrecio" value="35" step="0.1">
        </div>
        <div>
          <label for="nuevoProdCosto">Costo base (USD):</label>
          <input type="number" id="nuevoProdCosto" value="11" step="0.1">
        </div>
      </div>
      <label for="nuevoProdProblema">Problema que resuelve:</label>
      <input type="text" id="nuevoProdProblema" placeholder="Ej. Falta de iluminacion portatil">
      <label for="nuevoProdBeneficio">Beneficio principal:</label>
      <input type="text" id="nuevoProdBeneficio" placeholder="Ej. Luz potente y carga rapida">
      <button type="button" class="cyan-btn" onclick="registrarNuevoProducto()">GUARDAR PRODUCTO</button>
      <div id="msgNuevoProd" class="estado-msg"></div>
    </div>
  </section>

  <!-- MODULO 2: LOCALIZADOR INTERNACIONAL POR PAIS -->
  <section id="modLocalizador" class="card modulo-panel oculto">
    <h2>2. Localizador Internacional por Pais</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Adapta precios, monedas, pagos, horarios pico y enfoque de compra a cada pais.</p>

    <div class="grid-2">
      <div>
        <label for="selPaisDestino">Pais objetivo:</label>
        <select id="selPaisDestino" onchange="actualizarLocalizacion()"></select>
      </div>
      <div>
        <label for="selProductoLoc">Producto seleccionado:</label>
        <select id="selProductoLoc" onchange="seleccionarProductoEnLocalizador()"></select>
      </div>
    </div>

    <div class="grid-2">
      <div>
        <label for="inpPrecioUsdLoc">Precio base en USD ($):</label>
        <input type="number" id="inpPrecioUsdLoc" value="49.90" step="0.1" oninput="actualizarLocalizacion()">
      </div>
      <div>
        <label for="inpCostoUsdLoc">Costo producto en USD ($):</label>
        <input type="number" id="inpCostoUsdLoc" value="14.50" step="0.1" oninput="actualizarLocalizacion()">
      </div>
    </div>

    <div class="grid-4" style="margin-top:10px;">
      <div class="kpi-box"><span>Precio Local</span><strong id="locPrecioLocal">$0</strong></div>
      <div class="kpi-box"><span>Envio Est.</span><strong id="locEnvioLocal">$0</strong></div>
      <div class="kpi-box"><span>Ganancia Neta</span><strong id="locGananciaUsd">$0</strong></div>
      <div class="kpi-box"><span>Margen Est.</span><strong id="locMargenPct">0%</strong></div>
    </div>

    <div id="detallePaisBox" class="box-salida box-gold"></div>

    <h3>Comparador Rapido Multi-Pais (Precio Local Estimado)</h3>
    <div id="tablaComparadorPaises" class="hoja-scroll"></div>
  </section>

  <!-- MODULO 3: ESTUDIO DE COPYWRITING Y GUIONES -->
  <section id="modCopy" class="card modulo-panel oculto">
    <h2>3. Estudio de Copywriting y Guiones</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Genera ganchos, anuncios estructurados, mensajes de WhatsApp y guiones de video corto.</p>

    <div class="grid-2">
      <div>
        <label for="copyNombreProd">Producto o servicio:</label>
        <input type="text" id="copyNombreProd" value="Audifonos Inalambricos ANC Pro">
      </div>
      <div>
        <label for="copyCategoria">Categoria:</label>
        <input type="text" id="copyCategoria" value="Tecnologia y Gadgets">
      </div>
    </div>

    <div class="grid-3">
      <div>
        <label for="copyPais">Pais destino:</label>
        <select id="copyPais"></select>
      </div>
      <div>
        <label for="copyFramework">Formula Copy:</label>
        <select id="copyFramework">
          <option value="AIDA">AIDA</option>
          <option value="PAS">PAS</option>
          <option value="BAB">BAB</option>
          <option value="4U">4U</option>
        </select>
      </div>
      <div>
        <label for="copyPrecioUsd">Precio USD ($):</label>
        <input type="number" id="copyPrecioUsd" value="49.90" step="0.1">
      </div>
    </div>

    <label for="copyPublico">Publico ideal:</label>
    <input type="text" id="copyPublico" value="Estudiantes, trabajadores remotos y amantes de la musica">

    <label for="copyProblema">Problema que resuelve:</label>
    <input type="text" id="copyProblema" value="Ruido externo molesto y cables incomodos">

    <label for="copyBeneficio">Beneficio principal:</label>
    <input type="text" id="copyBeneficio" value="Aislamiento de ruido con bateria de larga duracion">

    <button type="button" onclick="generarKitCopyServidor()">GENERAR GANCHOS, COPY Y GUION</button>

    <h3>Ganchos Iniciales</h3>
    <div id="salidaGanchos" class="box-salida box-coral">Pulsa el boton superior para generar tus ganchos.</div>

    <h3>Anuncio / Descripcion</h3>
    <div id="salidaCopyPrincipal" class="box-salida box-gold">Aqui aparecera tu anuncio estructurado.</div>
    <button type="button" class="sec-btn" onclick="copiarTextoElemento('salidaCopyPrincipal')">COPIAR ANUNCIO</button>

    <h3>Guion de Video Corto</h3>
    <div id="salidaGuionVideo" class="box-salida">Aqui aparecera el guion de video.</div>
    <button type="button" class="sec-btn" onclick="copiarTextoElemento('salidaGuionVideo')">COPIAR GUION</button>

    <h3>Guion de Cierre Rapido por WhatsApp / DM</h3>
    <div id="salidaGuionWhatsapp" class="box-salida box-gold">Aqui aparecera el mensaje listo para responder clientes por chat.</div>
    <button type="button" class="sec-btn" onclick="copiarTextoElemento('salidaGuionWhatsapp')">COPIAR MENSAJE WHATSAPP</button>
  </section>

  <!-- MODULO 4: CALENDARIO DE CONTENIDO Y TENDENCIAS -->
  <section id="modCalendario" class="card modulo-panel oculto">
    <h2>4. Plan Semanal y Tendencias</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Rutina semanal de publicacion y radar de tendencias de marketing.</p>

    <div id="listaCalendario"></div>

    <h3 style="margin-top:16px;">Tendencias de Marketing</h3>
    <div id="listaTendencias"></div>
  </section>

  <!-- MODULO 5: HOJA FINANCIERA DE CAMPANAS Y ROAS -->
  <section id="modSimulador" class="card modulo-panel oculto">
    <h2>5. Hoja Amplia de Campanas, Ventas y ROAS (8x4)</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Completa hasta 8 filas con Precio ($), Costo ($), Unidades e Inversion en Anuncios ($).</p>

    <div class="hoja-scroll">
      <table class="mkt-table">
        <thead>
          <tr>
            <th>Fila</th>
            <th>Precio ($)</th>
            <th>Costo ($)</th>
            <th>Unidades</th>
            <th>Ads ($)</th>
            <th>Ganancia ($)</th>
            <th>ROAS</th>
          </tr>
        </thead>
        <tbody id="cuerpoTablaMkt"></tbody>
      </table>
    </div>

    <div class="grid-4" style="margin-top:10px;">
      <div class="kpi-box"><span>Ingresos</span><strong id="kpiIngresos">$0</strong></div>
      <div class="kpi-box"><span>Ads</span><strong id="kpiAds">$0</strong></div>
      <div class="kpi-box"><span>Ganancia</span><strong id="kpiGanancia">$0</strong></div>
      <div class="kpi-box"><span>ROAS Global</span><strong id="kpiRoasGlobal">0.00x</strong></div>
    </div>

    <button type="button" class="cyan-btn" onclick="calcularTablaMarketing()">CALCULAR TODA LA HOJA</button>
  </section>

  <!-- MODULO 6: SIMULADOR DE EMBUDO CTR, CPC, CONVERSION Y CPA -->
  <section id="modEmbudo" class="card modulo-panel oculto">
    <h2>6. Simulador de Embudo (CTR, CPC, Conversion y CPA)</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Calcula cuantas visitas y compras genera tu presupuesto publicitario segun tu CTR y tasa de cierre.</p>

    <div class="grid-2">
      <div>
        <label for="embPresupuesto">Presupuesto Publicitario ($ USD):</label>
        <input type="number" id="embPresupuesto" value="100" step="1" oninput="calcularEmbudoMarketing()">
      </div>
      <div>
        <label for="embCpm">CPM Estimado - Costo por 1,000 vistas ($):</label>
        <input type="number" id="embCpm" value="8.5" step="0.1" oninput="calcularEmbudoMarketing()">
      </div>
    </div>

    <div class="grid-3">
      <div>
        <label for="embCtr">CTR - Porcentaje de Clics (%):</label>
        <input type="number" id="embCtr" value="2.2" step="0.1" oninput="calcularEmbudoMarketing()">
      </div>
      <div>
        <label for="embConv">Tasa de Conversion (%):</label>
        <input type="number" id="embConv" value="3.5" step="0.1" oninput="calcularEmbudoMarketing()">
      </div>
      <div>
        <label for="embTicket">Ticket Promedio Venta ($):</label>
        <input type="number" id="embTicket" value="49.9" step="0.1" oninput="calcularEmbudoMarketing()">
      </div>
    </div>

    <div class="grid-4" style="margin-top:12px;">
      <div class="kpi-box"><span>Impresiones</span><strong id="kpiEmbImp">0</strong></div>
      <div class="kpi-box"><span>Clics / Visitas</span><strong id="kpiEmbClics">0</strong></div>
      <div class="kpi-box"><span>CPC Promedio</span><strong id="kpiEmbCpc">$0.00</strong></div>
      <div class="kpi-box"><span>Ventas Est.</span><strong id="kpiEmbVentas">0</strong></div>
    </div>

    <div class="grid-3" style="margin-top:8px;">
      <div class="kpi-box"><span>CPA (Costo/Venta)</span><strong id="kpiEmbCpa">$0.00</strong></div>
      <div class="kpi-box"><span>Facturacion Est.</span><strong id="kpiEmbFact">$0.00</strong></div>
      <div class="kpi-box"><span>ROAS Proyectado</span><strong id="kpiEmbRoas">0.00x</strong></div>
    </div>

    <div id="diagnosticoEmbudo" class="box-salida box-gold"></div>
  </section>

  <!-- MODULO 7: GENERADOR DE AUDIENCIAS Y OFERTAS IRRESISTIBLES -->
  <section id="modAudiencias" class="card modulo-panel oculto">
    <h2>7. Segmentacion de Audiencias y Constructor de Ofertas</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Define intereses para Meta Ads / TikTok Ads y arma paquetes 2x1 o bonos que aumenten el valor de cada pedido.</p>

    <div class="grid-2">
      <div>
        <label for="audNicho">Nicho del producto:</label>
        <select id="audNicho" onchange="actualizarAudienciaYOferta()">
          <option value="tech">Tecnologia y Gadgets</option>
          <option value="beauty">Belleza y Cuidado Personal</option>
          <option value="fitness">Fitness y Bienestar</option>
          <option value="home">Hogar y Lifestyle</option>
          <option value="fashion">Moda y Calzado</option>
          <option value="digital">Productos Digitales y Educacion</option>
        </select>
      </div>
      <div>
        <label for="audTipoOferta">Estructura de Oferta:</label>
        <select id="audTipoOferta" onchange="actualizarAudienciaYOferta()">
          <option value="pack2x1">Pack Doble / 2da Unidad con Descuento</option>
          <option value="bono">Producto + Guia o Accesorio Gratis</option>
          <option value="envio">Envio Prioritario + Garantia Extendida</option>
          <option value="flash">Oferta Relampago 24 Horas</option>
        </select>
      </div>
    </div>

    <div class="grid-2">
      <div>
        <label for="audProdNombre">Nombre del producto:</label>
        <input type="text" id="audProdNombre" value="Audifonos Inalambricos ANC Pro" oninput="actualizarAudienciaYOferta()">
      </div>
      <div>
        <label for="audPrecioBase">Precio unitario ($ USD):</label>
        <input type="number" id="audPrecioBase" value="49.90" step="0.1" oninput="actualizarAudienciaYOferta()">
      </div>
    </div>

    <h3>Segmentacion Recomendada para Campanas</h3>
    <div id="salidaAudiencia" class="box-salida"></div>

    <h3>Oferta Lista para Publicar</h3>
    <div id="salidaOfertaIrresistible" class="box-salida box-coral"></div>
    <button type="button" class="sec-btn" onclick="copiarTextoElemento('salidaOfertaIrresistible')">COPIAR OFERTA</button>
  </section>

  <!-- MODULO 8: CORREO ELECTRONICO Y GUARDADO DE PROGRESO -->
  <section id="modCuenta" class="card modulo-panel oculto">
    <h2>8. Correo Electronico y Progreso</h2>
    <p style="margin:0 0 8px;font-size:14px;color:var(--text-soft);">Guarda o carga tu progreso vinculado a tu correo electronico.</p>

    <label for="inpCorreoCuenta">Correo electronico:</label>
    <input type="email" id="inpCorreoCuenta" placeholder="tu_correo@ejemplo.com">

    <label for="txtNotasCampana">Notas de campana y registros:</label>
    <textarea id="txtNotasCampana" placeholder="Escribe tus notas, precios, contactos o enlaces..."></textarea>

    <div class="grid-2">
      <button type="button" onclick="guardarProgresoUsuario()">GUARDAR PROGRESO</button>
      <button type="button" class="sec-btn" onclick="cargarProgresoUsuario()">CARGAR PROGRESO</button>
    </div>
    <div id="msgCuenta" class="estado-msg">Listo para guardar o cargar tu progreso.</div>
  </section>

</main>

<div class="firma-celso">CREACIONES CELSO</div>

<script id="jsonPaises" type="application/json">__PAISES_JSON__</script>
<script id="jsonCatalogo" type="application/json">__CATALOGO_JSON__</script>
<script id="jsonCalendario" type="application/json">__CALENDARIO_JSON__</script>
<script id="jsonTendencias" type="application/json">__TENDENCIAS_JSON__</script>

<script>
const PAISES = JSON.parse(document.getElementById("jsonPaises").textContent);
let CATALOGO = JSON.parse(document.getElementById("jsonCatalogo").textContent);
const CALENDARIO = JSON.parse(document.getElementById("jsonCalendario").textContent);
const TENDENCIAS = JSON.parse(document.getElementById("jsonTendencias").textContent);

function normalizar(t) {
  return String(t || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "");
}

function escaparHtml(t) {
  return String(t || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function entrarDirectoAModulos(correoNormalizado) {
  document.getElementById("inpCorreoCuenta").value = correoNormalizado;
  document.getElementById("lblCorreoBadge").textContent = correoNormalizado;
  document.getElementById("pantallaClave").classList.add("oculto");
  document.getElementById("pantallaEntrada").classList.add("oculto");
  document.getElementById("cabeceraApp").classList.remove("oculto");
  document.getElementById("contenedorModulos").classList.remove("oculto");
}

async function verificarClave() {
  const clave = document.getElementById("inpClave").value.trim();
  const msg = document.getElementById("msgClave");
  try {
    const r = await fetch("/api/clave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clave: clave })
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById("pantallaClave").classList.add("oculto");
      document.getElementById("pantallaEntrada").classList.remove("oculto");
    } else {
      msg.textContent = "Clave incorrecta. Usa VIP100 o Celso2026.";
    }
  } catch (e) {
    msg.textContent = "Error al validar la clave.";
  }
}

async function aceptarEntrada() {
  const correo = document.getElementById("inpCorreoEntrada").value.trim().toLowerCase();
  const msg = document.getElementById("msgEntrada");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Ingresa un correo electronico valido para continuar.";
    return;
  }
  entrarDirectoAModulos(correo);
  await cargarProgresoUsuario();
}

function irModulo(idModulo, btn) {
  document.querySelectorAll(".modulo-panel").forEach(p => p.classList.add("oculto"));
  const destino = document.getElementById(idModulo);
  if (destino) destino.classList.remove("oculto");
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("activo"));
  if (btn) btn.classList.add("activo");
}

function inicializarSelectores() {
  const selPaisDest = document.getElementById("selPaisDestino");
  const selCopyPais = document.getElementById("copyPais");
  selPaisDest.innerHTML = "";
  selCopyPais.innerHTML = "";

  PAISES.forEach(p => {
    const op1 = document.createElement("option");
    op1.value = p.codigo;
    op1.textContent = `${p.nombre} (${p.moneda})`;
    selPaisDest.appendChild(op1);

    const op2 = document.createElement("option");
    op2.value = p.codigo;
    op2.textContent = `${p.nombre} (${p.moneda})`;
    selCopyPais.appendChild(op2);
  });

  actualizarSelectoresProductos();
}

function actualizarSelectoresProductos() {
  const selCat = document.getElementById("selCategoriaFiltro");
  const catActual = selCat.value || "TODAS";
  const categorias = new Set(["TODAS"]);
  CATALOGO.forEach(p => categorias.add(p.categoria));

  selCat.innerHTML = "";
  categorias.forEach(c => {
    const op = document.createElement("option");
    op.value = c;
    op.textContent = c === "TODAS" ? "Todas las categorias" : c;
    if (c === catActual) op.selected = true;
    selCat.appendChild(op);
  });

  const selProdLoc = document.getElementById("selProductoLoc");
  selProdLoc.innerHTML = "";
  CATALOGO.forEach((p, idx) => {
    const op = document.createElement("option");
    op.value = idx;
    op.textContent = `${p.nombre} ($${p.precio_base_usd})`;
    selProdLoc.appendChild(op);
  });
}

function filtrarCatalogo() {
  const q = normalizar(document.getElementById("inpBuscarProd").value);
  const cat = document.getElementById("selCategoriaFiltro").value;
  const cont = document.getElementById("listaProductos");
  cont.innerHTML = "";

  const filtrados = CATALOGO.filter(p => {
    const coincideCat = (cat === "TODAS" || p.categoria === cat);
    if (!coincideCat) return false;
    if (!q) return true;
    const texto = normalizar(
      [
        p.nombre,
        p.categoria,
        p.subcategoria,
        p.beneficio_estrella,
        p.problema_que_resuelve,
        (p.mercados_top || []).join(" "),
        (p.palabras_clave || []).join(" ")
      ].join(" ")
    );
    return texto.includes(q);
  });

  document.getElementById("kpiTotalProds").textContent = filtrados.length;
  let sumaMargen = 0;
  filtrados.forEach(p => { sumaMargen += Number(p.margen_pct || 0); });
  const prom = filtrados.length ? (sumaMargen / filtrados.length).toFixed(1) : "0";
  document.getElementById("kpiMargenProm").textContent = prom + "%";

  if (!filtrados.length) {
    cont.innerHTML = `<div class="box-salida">No se encontraron productos con ese filtro. Puedes registrarlo abajo.</div>`;
    return;
  }

  filtrados.forEach(prod => {
    const idxReal = CATALOGO.indexOf(prod);
    const card = document.createElement("div");
    card.className = "prod-item";
    const mercados = (prod.mercados_top || []).slice(0, 4).join(", ");
    card.innerHTML =
      `<div class="prod-top">` +
      `<div><strong style="font-size:16px;color:#ffffff;">${escaparHtml(prod.nombre)}</strong>` +
      `<div style="margin-top:4px;">` +
      `<span class="tag">${escaparHtml(prod.categoria)}</span>` +
      `<span class="tag tag-gold">Demanda ${prod.demanda_score}/100</span>` +
      `<span class="tag tag-coral">Margen ${prod.margen_pct}%</span>` +
      `</div></div>` +
      `<div style="text-align:right;min-width:86px;">` +
      `<div style="font-family:'Orbitron',sans-serif;font-weight:900;color:#00f5d4;font-size:16px;">$${prod.precio_base_usd}</div>` +
      `<div style="font-size:11.5px;color:#94a3b8;">Costo $${prod.costo_base_usd}</div>` +
      `</div></div>` +
      `<div style="margin-top:8px;font-size:14px;color:#e2e8f0;"><strong>Beneficio:</strong> ${escaparHtml(prod.beneficio_estrella)}</div>` +
      `<div style="margin-top:4px;font-size:13.5px;color:#cbd5e1;"><strong>Mercados:</strong> ${escaparHtml(mercados)}</div>` +
      `<div class="grid-2" style="margin-top:8px;">` +
      `<button type="button" class="sec-btn" onclick="enviarProductoALocalizador(${idxReal})">ADAPTAR A PAIS</button>` +
      `<button type="button" class="sec-btn" onclick="enviarProductoACopy(${idxReal})">CREAR ANUNCIO</button>` +
      `</div>`;
    cont.appendChild(card);
  });
}

function enviarProductoALocalizador(idx) {
  const prod = CATALOGO[idx];
  if (!prod) return;
  document.getElementById("selProductoLoc").value = idx;
  document.getElementById("inpPrecioUsdLoc").value = prod.precio_base_usd;
  document.getElementById("inpCostoUsdLoc").value = prod.costo_base_usd;
  actualizarLocalizacion();
  const btn = document.querySelector('.nav-btn[data-sec="modLocalizador"]');
  irModulo("modLocalizador", btn);
}

function enviarProductoACopy(idx) {
  const prod = CATALOGO[idx];
  if (!prod) return;
  document.getElementById("copyNombreProd").value = prod.nombre;
  document.getElementById("copyCategoria").value = prod.categoria;
  document.getElementById("copyPrecioUsd").value = prod.precio_base_usd;
  document.getElementById("copyPublico").value = prod.publico_ideal || "";
  document.getElementById("copyProblema").value = prod.problema_que_resuelve || "";
  document.getElementById("copyBeneficio").value = prod.beneficio_estrella || "";
  const btn = document.querySelector('.nav-btn[data-sec="modCopy"]');
  irModulo("modCopy", btn);
  generarKitCopyServidor();
}

async function registrarNuevoProducto() {
  const nombre = document.getElementById("nuevoProdNombre").value.trim();
  const categoria = document.getElementById("nuevoProdCat").value.trim() || "General";
  const precio = parseFloat(document.getElementById("nuevoProdPrecio").value) || 0;
  const costo = parseFloat(document.getElementById("nuevoProdCosto").value) || 0;
  const problema = document.getElementById("nuevoProdProblema").value.trim() || "Necesidad diaria";
  const beneficio = document.getElementById("nuevoProdBeneficio").value.trim() || "Solucion practica inmediata";
  const msg = document.getElementById("msgNuevoProd");

  if (!nombre || precio <= 0) {
    msg.textContent = "Escribe el nombre del producto y un precio valido en USD.";
    return;
  }

  try {
    const r = await fetch("/api/productos/agregar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nombre: nombre,
        categoria: categoria,
        precio_base_usd: precio,
        costo_base_usd: costo,
        problema: problema,
        beneficio: beneficio
      })
    });
    const d = await r.json();
    if (d.ok && d.producto) {
      CATALOGO.push(d.producto);
      actualizarSelectoresProductos();
      filtrarCatalogo();
      document.getElementById("nuevoProdNombre").value = "";
      msg.textContent = `Producto "${nombre}" agregado.`;
    }
  } catch (e) {
    msg.textContent = "Error al guardar el producto.";
  }
}

function seleccionarProductoEnLocalizador() {
  const idx = parseInt(document.getElementById("selProductoLoc").value || "0", 10);
  const prod = CATALOGO[idx];
  if (prod) {
    document.getElementById("inpPrecioUsdLoc").value = prod.precio_base_usd;
    document.getElementById("inpCostoUsdLoc").value = prod.costo_base_usd;
  }
  actualizarLocalizacion();
}

function actualizarLocalizacion() {
  const cod = document.getElementById("selPaisDestino").value;
  const pais = PAISES.find(p => p.codigo === cod) || PAISES[0];
  const precioUsd = parseFloat(document.getElementById("inpPrecioUsdLoc").value) || 0;
  const costoUsd = parseFloat(document.getElementById("inpCostoUsdLoc").value) || 0;

  const precioLocal = (precioUsd * pais.tasa_usd).toFixed(2);
  const envioLocal = (pais.envio_usd * pais.tasa_usd).toFixed(2);
  const gananciaUsd = (precioUsd - costoUsd - pais.envio_usd).toFixed(2);
  const margenPct = precioUsd > 0 ? ((parseFloat(gananciaUsd) / precioUsd) * 100).toFixed(1) : "0.0";

  document.getElementById("locPrecioLocal").textContent = `${pais.simbolo}${precioLocal}`;
  document.getElementById("locEnvioLocal").textContent = `${pais.simbolo}${envioLocal}`;
  document.getElementById("locGananciaUsd").textContent = `$${gananciaUsd}`;
  document.getElementById("locMargenPct").textContent = `${margenPct}%`;

  document.getElementById("detallePaisBox").textContent =
    `Pais: ${pais.nombre} (${pais.moneda})\n` +
    `Idioma: ${pais.idioma}\n` +
    `Plataformas: ${pais.plataformas_top}\n` +
    `Metodos de pago: ${pais.metodos_pago}\n` +
    `Horario pico: ${pais.horario_pico}\n` +
    `Enfoque cultural: ${pais.angulo_cultural}\n` +
    `Objecion comun: ${pais.objecion_frecuente}\n` +
    `Respuesta recomendada: ${pais.solucion_objecion}\n` +
    `Llamado a la accion: "${pais.cta_local}"`;

  renderizarComparadorMultiPais(precioUsd, costoUsd);
}

function renderizarComparadorMultiPais(precioUsd, costoUsd) {
  const cont = document.getElementById("tablaComparadorPaises");
  let html = `<table class="mkt-table"><thead><tr><th>Pais</th><th>Moneda</th><th>Precio Local</th><th>Envio Est.</th><th>Ganancia Neta (USD)</th></tr></thead><tbody>`;
  PAISES.forEach(p => {
    const pLoc = (precioUsd * p.tasa_usd).toFixed(2);
    const eLoc = (p.envio_usd * p.tasa_usd).toFixed(2);
    const gUsd = (precioUsd - costoUsd - p.envio_usd).toFixed(2);
    html +=
      `<tr>` +
      `<td><strong>${escaparHtml(p.nombre)}</strong></td>` +
      `<td>${escaparHtml(p.moneda)}</td>` +
      `<td style="color:#00f5d4;font-weight:700;">${escaparHtml(p.simbolo)}${pLoc}</td>` +
      `<td>${escaparHtml(p.simbolo)}${eLoc}</td>` +
      `<td style="color:#10b981;font-weight:700;">$${gUsd}</td>` +
      `</tr>`;
  });
  html += `</tbody></table>`;
  cont.innerHTML = html;
}

async function generarKitCopyServidor() {
  const payload = {
    nombre: document.getElementById("copyNombreProd").value.trim(),
    categoria: document.getElementById("copyCategoria").value.trim(),
    pais_codigo: document.getElementById("copyPais").value,
    framework: document.getElementById("copyFramework").value,
    precio_usd: parseFloat(document.getElementById("copyPrecioUsd").value) || 0,
    costo_usd: 0,
    publico: document.getElementById("copyPublico").value.trim(),
    problema: document.getElementById("copyProblema").value.trim(),
    beneficio: document.getElementById("copyBeneficio").value.trim()
  };

  try {
    const r = await fetch("/api/generar_kit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    if (d.ok && d.kit) {
      document.getElementById("salidaGanchos").textContent =
        d.kit.ganchos.map((g, i) => `${i + 1}. ${g}`).join("\n");
      document.getElementById("salidaCopyPrincipal").textContent = d.kit.copy_principal;
      document.getElementById("salidaGuionVideo").textContent = d.kit.guion_video_corto;
      const p = d.kit.pais;
      document.getElementById("salidaGuionWhatsapp").textContent =
        `Hola! Gracias por escribir sobre *${d.kit.producto}*.\n` +
        `Beneficio principal: ${payload.beneficio}.\n` +
        `Precio para ${p.nombre}: *${p.simbolo}${d.kit.precio_local} (${p.moneda})*.\n` +
        `Metodos de pago disponibles: ${p.metodos_pago}.\n` +
        `Deseas que te reserve una unidad ahora mismo?`;
    }
  } catch (e) {
    document.getElementById("salidaCopyPrincipal").textContent = "Error al generar el anuncio.";
  }
}

function copiarTextoElemento(idEl) {
  const txt = document.getElementById(idEl).textContent;
  if (navigator.clipboard && txt) {
    navigator.clipboard.writeText(txt);
  }
}

function renderizarCalendarioYTendencias() {
  const contCal = document.getElementById("listaCalendario");
  contCal.innerHTML = "";
  CALENDARIO.forEach(item => {
    const div = document.createElement("div");
    div.className = "prod-item";
    div.innerHTML =
      `<div class="prod-top"><strong style="color:#ffb703;">${escaparHtml(item.dia)} · ${escaparHtml(item.objetivo)}</strong>` +
      `<span class="tag">${escaparHtml(item.formato)}</span></div>` +
      `<div style="margin-top:6px;font-size:14px;">${escaparHtml(item.estructura)}</div>` +
      `<div style="margin-top:4px;font-size:12.5px;color:#00f5d4;">Indicador: ${escaparHtml(item.kpi)}</div>`;
    contCal.appendChild(div);
  });

  const contTend = document.getElementById("listaTendencias");
  contTend.innerHTML = "";
  TENDENCIAS.forEach(t => {
    const div = document.createElement("div");
    div.className = "box-salida box-coral";
    div.innerHTML = `<strong>${escaparHtml(t.titulo)}</strong> [${escaparHtml(t.impacto)}]\n${escaparHtml(t.detalle)}`;
    contTend.appendChild(div);
  });
}

function construirTablaMarketing(filasGuardadas) {
  const tbody = document.getElementById("cuerpoTablaMkt");
  tbody.innerHTML = "";
  for (let i = 0; i < 8; i++) {
    const f = (filasGuardadas && filasGuardadas[i]) ? filasGuardadas[i] : ["", "", "", ""];
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td><strong>#${i + 1}</strong></td>` +
      `<td><input type="number" step="0.1" class="m-precio" value="${escaparHtml(f[0])}"></td>` +
      `<td><input type="number" step="0.1" class="m-costo" value="${escaparHtml(f[1])}"></td>` +
      `<td><input type="number" step="1" class="m-unid" value="${escaparHtml(f[2])}"></td>` +
      `<td><input type="number" step="0.1" class="m-ads" value="${escaparHtml(f[3])}"></td>` +
      `<td class="m-ganancia" style="font-weight:900;color:#10b981;">$0.00</td>` +
      `<td class="m-roas" style="font-weight:900;color:#ffb703;">0.00x</td>`;
    tbody.appendChild(tr);
  }
  calcularTablaMarketing();
}

function calcularTablaMarketing() {
  let ingTotal = 0;
  let adsTotal = 0;
  let ganTotal = 0;

  document.querySelectorAll("#cuerpoTablaMkt tr").forEach(tr => {
    const precio = parseFloat(tr.querySelector(".m-precio").value) || 0;
    const costo = parseFloat(tr.querySelector(".m-costo").value) || 0;
    const unid = parseFloat(tr.querySelector(".m-unid").value) || 0;
    const ads = parseFloat(tr.querySelector(".m-ads").value) || 0;

    const ingresoFila = precio * unid;
    const gananciaFila = ingresoFila - (costo * unid) - ads;
    const roasFila = ads > 0 ? (ingresoFila / ads) : 0;

    ingTotal += ingresoFila;
    adsTotal += ads;
    ganTotal += gananciaFila;

    tr.querySelector(".m-ganancia").textContent = "$" + gananciaFila.toFixed(2);
    tr.querySelector(".m-roas").textContent = roasFila.toFixed(2) + "x";
  });

  const roasGlobal = adsTotal > 0 ? (ingTotal / adsTotal) : 0;
  document.getElementById("kpiIngresos").textContent = "$" + ingTotal.toFixed(2);
  document.getElementById("kpiAds").textContent = "$" + adsTotal.toFixed(2);
  document.getElementById("kpiGanancia").textContent = "$" + ganTotal.toFixed(2);
  document.getElementById("kpiRoasGlobal").textContent = roasGlobal.toFixed(2) + "x";
}

function calcularEmbudoMarketing() {
  const presupuesto = parseFloat(document.getElementById("embPresupuesto").value) || 0;
  const cpm = parseFloat(document.getElementById("embCpm").value) || 0;
  const ctr = parseFloat(document.getElementById("embCtr").value) || 0;
  const conv = parseFloat(document.getElementById("embConv").value) || 0;
  const ticket = parseFloat(document.getElementById("embTicket").value) || 0;

  const impresiones = cpm > 0 ? Math.round((presupuesto / cpm) * 1000) : 0;
  const clics = Math.round(impresiones * (ctr / 100));
  const cpc = clics > 0 ? (presupuesto / clics) : 0;
  const ventas = Math.round(clics * (conv / 100));
  const cpa = ventas > 0 ? (presupuesto / ventas) : 0;
  const facturacion = ventas * ticket;
  const roas = presupuesto > 0 ? (facturacion / presupuesto) : 0;

  document.getElementById("kpiEmbImp").textContent = impresiones.toLocaleString("es-ES");
  document.getElementById("kpiEmbClics").textContent = clics.toLocaleString("es-ES");
  document.getElementById("kpiEmbCpc").textContent = "$" + cpc.toFixed(2);
  document.getElementById("kpiEmbVentas").textContent = ventas.toString();
  document.getElementById("kpiEmbCpa").textContent = "$" + cpa.toFixed(2);
  document.getElementById("kpiEmbFact").textContent = "$" + facturacion.toFixed(2);
  document.getElementById("kpiEmbRoas").textContent = roas.toFixed(2) + "x";

  let estado = "Embudo equilibrado.";
  if (ctr < 1.2) {
    estado = "Alerta en Gancho: El CTR esta bajo; mejora los primeros 3 segundos del video o la imagen principal.";
  } else if (conv < 2.0) {
    estado = "Alerta en Cierre: Llegan visitas pero pocas compran; refuerza la oferta, prueba social y facilidad de pago.";
  } else if (roas >= 3.0) {
    estado = "Campana escalable: El retorno proyectado supera 3x; puedes aumentar presupuesto gradualmente.";
  }
  document.getElementById("diagnosticoEmbudo").textContent =
    `Diagnostico del Embudo:\n` +
    `• De ${impresiones.toLocaleString("es-ES")} personas alcanzadas, ${clics} hacen clic.\n` +
    `• Con ${conv}% de cierre se proyectan ${ventas} ventas a un costo de $${cpa.toFixed(2)} por cliente.\n` +
    `• Recomendacion: ${estado}`;
}

function actualizarAudienciaYOferta() {
  const nicho = document.getElementById("audNicho").value;
  const tipoOferta = document.getElementById("audTipoOferta").value;
  const prod = document.getElementById("audProdNombre").value.trim() || "Producto Estrella";
  const precio = parseFloat(document.getElementById("audPrecioBase").value) || 0;

  const mapaAudiencias = {
    tech: "Edad: 18 - 44 anos | Intereses: Gadgets, tecnologia movil, accesorios electronicos, compras online, gaming y productividad.",
    beauty: "Edad: 18 - 52 anos | Intereses: Cuidado de la piel, cosmetica, fragancias, bienestar personal y rutinas diarias.",
    fitness: "Edad: 20 - 48 anos | Intereses: Entrenamiento en casa, gimnasios, vida saludable, ergonomia y deportes.",
    home: "Edad: 24 - 55 anos | Intereses: Organizacion del hogar, decoracion practica, articulos de cocina y comodidad.",
    fashion: "Edad: 18 - 42 anos | Intereses: Moda urbana, calzado comodo, tendencias de temporada y estilo diario.",
    digital: "Edad: 20 - 50 anos | Intereses: Emprendimiento, marketing digital, comercio electronico, herramientas y formacion."
  };

  document.getElementById("salidaAudiencia").textContent =
    `Publico sugerido para Meta Ads / TikTok Ads:\n${mapaAudiencias[nicho] || mapaAudiencias.tech}\n` +
    `Ubicaciones recomendadas: Reels, TikTok Feed, Stories y mensajes directos.`;

  let ofertaTexto = "";
  if (tipoOferta === "pack2x1") {
    const packPrecio = (precio * 1.75).toFixed(2);
    ofertaTexto = `OFERTA PACK DOBLE - ${prod}:\nLleva 1 unidad por $${precio.toFixed(2)} o lleva el Pack de 2 unidades por solo $${packPrecio} (ahorras 25% en la segunda unidad).`;
  } else if (tipoOferta === "bono") {
    ofertaTexto = `OFERTA CON BONO INCLUIDO - ${prod}:\nOrdena hoy por $${precio.toFixed(2)} y recibe gratis nuestra guia rapida de uso y mantenimiento valorada en $15.`;
  } else if (tipoOferta === "envio") {
    ofertaTexto = `OFERTA ENVIO PRIORITARIO - ${prod}:\nAdquiere ${prod} por $${precio.toFixed(2)} con despacho prioritario y garantia de satisfaccion incluida.`;
  } else {
    const flashPrecio = (precio * 0.85).toFixed(2);
    ofertaTexto = `OFERTA RELAMPAGO 24 HORAS - ${prod}:\nPrecio regular $${precio.toFixed(2)} -> Hoy por tiempo limitado en $${flashPrecio}.`;
  }
  document.getElementById("salidaOfertaIrresistible").textContent = ofertaTexto;
}

function obtenerFilasTablaMarketing() {
  const filas = [];
  document.querySelectorAll("#cuerpoTablaMkt tr").forEach(tr => {
    filas.push([
      tr.querySelector(".m-precio").value,
      tr.querySelector(".m-costo").value,
      tr.querySelector(".m-unid").value,
      tr.querySelector(".m-ads").value
    ]);
  });
  return filas;
}

async function guardarProgresoUsuario() {
  const correo = document.getElementById("inpCorreoCuenta").value.trim().toLowerCase();
  const msg = document.getElementById("msgCuenta");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo electronico valido.";
    return;
  }
  document.getElementById("lblCorreoBadge").textContent = correo;
  const payload = {
    correo: correo,
    progreso: {
      pais_destino: document.getElementById("selPaisDestino").value,
      copy_producto: document.getElementById("copyNombreProd").value,
      copy_beneficio: document.getElementById("copyBeneficio").value,
      notas: document.getElementById("txtNotasCampana").value,
      tabla_mkt: obtenerFilasTablaMarketing()
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

async function cargarProgresoUsuario() {
  const correo = document.getElementById("inpCorreoCuenta").value.trim().toLowerCase();
  const msg = document.getElementById("msgCuenta");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo electronico valido.";
    return;
  }
  document.getElementById("lblCorreoBadge").textContent = correo;
  try {
    const r = await fetch("/api/progreso/cargar?correo=" + encodeURIComponent(correo));
    const d = await r.json();
    if (!d.encontrado) {
      msg.textContent = "No hay progreso previo para " + correo + ". Puedes guardar tu trabajo actual.";
      return;
    }
    const p = d.progreso || {};
    if (p.pais_destino) document.getElementById("selPaisDestino").value = p.pais_destino;
    if (p.copy_producto) document.getElementById("copyNombreProd").value = p.copy_producto;
    if (p.copy_beneficio) document.getElementById("copyBeneficio").value = p.copy_beneficio;
    if (typeof p.notas === "string") document.getElementById("txtNotasCampana").value = p.notas;
    if (Array.isArray(p.tabla_mkt)) construirTablaMarketing(p.tabla_mkt);
    actualizarLocalizacion();
    msg.textContent = "Progreso cargado para " + correo + ".";
  } catch (e) {
    msg.textContent = "Error al cargar el progreso.";
  }
}

document.getElementById("inpClave").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    verificarClave();
  }
});

document.getElementById("inpCorreoEntrada").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    aceptarEntrada();
  }
});

inicializarSelectores();
filtrarCatalogo();
actualizarLocalizacion();
renderizarCalendarioYTendencias();
construirTablaMarketing([]);
calcularEmbudoMarketing();
actualizarAudienciaYOferta();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    catalogo = obtener_catalogo_completo()
    return (
        HTML_PAGE
        .replace("__PAISES_JSON__", json.dumps(PAISES_MARKETING, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__CATALOGO_JSON__", json.dumps(catalogo, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__CALENDARIO_JSON__", json.dumps(PLANTILLAS_CALENDARIO_SEMANAL, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__TENDENCIAS_JSON__", json.dumps(TENDENCIAS_MARKETING_ACTUAL, ensure_ascii=True).replace("</", "<\\/"))
    )


@app.route("/api/clave", methods=["POST"])
def api_clave():
    datos = request.get_json(silent=True) or {}
    clave = (datos.get("clave") or "").strip()
    return jsonify({"ok": clave in CLAVES_VALIDAS})


@app.route("/api/productos/agregar", methods=["POST"])
def api_agregar_producto():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    categoria = (datos.get("categoria") or "General").strip()
    try:
        precio = float(datos.get("precio_base_usd") or 0)
    except Exception:
        precio = 0.0
    try:
        costo = float(datos.get("costo_base_usd") or 0)
    except Exception:
        costo = 0.0
    problema = (datos.get("problema") or "Necesidad diaria").strip()
    beneficio = (datos.get("beneficio") or "Solucion rapida y practica").strip()

    if not nombre or precio <= 0:
        return jsonify({"ok": False, "mensaje": "Datos incompletos."}), 400

    db = cargar_db()
    nuevo_id = f"PRD-USR-{len(db['productos_personalizados']) + 101}"
    nuevo_prod = crear_producto_catalogo(
        nuevo_id,
        nombre,
        categoria,
        "Personalizado",
        round(precio, 2),
        round(costo, 2),
        90,
        "Nuevo registro",
        "Global",
        ["Estados Unidos", "Mexico", "Colombia", "Venezuela", "Espana"],
        "Compradores interesados en soluciones practicas.",
        problema,
        beneficio,
        f"Mira como {nombre} ayuda con {problema.lower()} en segundos.",
        f"ATENCION: {problema}\nINTERES: {nombre}\nDESEO: {beneficio}\nACCION: Pidelo hoy.",
        [normalizar_texto(nombre), normalizar_texto(categoria)],
        ["TikTok", "Instagram", "WhatsApp"],
    )
    db["productos_personalizados"].append(nuevo_prod)
    guardar_db(db)
    return jsonify({"ok": True, "producto": nuevo_prod})


@app.route("/api/generar_kit", methods=["POST"])
def api_generar_kit():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "Producto").strip()
    categoria = (datos.get("categoria") or "General").strip()
    pais_codigo = (datos.get("pais_codigo") or "US").strip().upper()
    framework = (datos.get("framework") or "AIDA").strip().upper()
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

    kit = generar_kit_marketing_dinamico(
        nombre,
        categoria,
        precio_usd,
        costo_usd,
        beneficio,
        problema,
        publico,
        pais_codigo,
        framework,
    )
    return jsonify({"ok": True, "kit": kit})


@app.route("/api/progreso/guardar", methods=["POST"])
def api_guardar_progreso():
    datos = request.get_json(silent=True) or {}
    correo = validar_correo(datos.get("correo"))
    progreso = datos.get("progreso") or {}
    if not correo:
        return jsonify({"ok": False, "mensaje": "Correo electronico invalido."}), 400

    db = cargar_db()
    db["usuarios"][correo] = {
        "actualizado": datetime.utcnow().isoformat(),
        "datos": progreso,
    }
    guardar_db(db)
    return jsonify({"ok": True, "mensaje": f"Progreso guardado para {correo}."})


@app.route("/api/progreso/cargar", methods=["GET"])
def api_cargar_progreso():
    correo = validar_correo(request.args.get("correo"))
    if not correo:
        return jsonify({"encontrado": False})
    db = cargar_db()
    registro = db.get("usuarios", {}).get(correo)
    if not registro:
        return jsonify({"encontrado": False})
    return jsonify({"encontrado": True, "progreso": registro.get("datos", {})})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
