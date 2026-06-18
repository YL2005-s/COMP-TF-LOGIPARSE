import re

# ─── DEFINICIÓN DE TOKENS ────────────────────────────────────────────────────
TOKENS = [
    ('mis_segmentos_doc',    r'^(HDR|ITM|FTR)$'),
    ('mis_codigos_orden',    r'^[A-Z]+-\d{4}-\d{3}$'),
    ('mis_variables_ruc',    r'^\d{11}$'),
    ('mis_variables_fecha',  r'^\d{8}$'),
    ('mis_motivos_traslado', r'^(VENTA|COMPRA|DEVOLUCION)$'),
    ('mis_tipos_moneda',     r'^(PEN|USD)$'),
    ('mis_codigos_item',     r'^\d{3}$'),
    ('mis_nombres_producto', r'^[a-z]+-[a-z]+$'),
    ('mis_unidades_medida',  r'^(KG|SAC|CAJA|UNID)$'),
    ('mis_estados_orden',    r'^(PENDIENTE|PROCESADO|ANULADO)$'),
    ('mis_variables_decimales', r'^\d+\.\d{2}$'),
    ('mis_variables_numericas', r'^\d+$'),
    ('mis_variables_texto',  r'^[A-Za-z0-9\-\.]+$'),
]

SEPARADOR = '|'


def clasificar_token(valor: str) -> str:
    for nombre, patron in TOKENS:
        if re.match(patron, valor):
            return nombre
    return 'DESCONOCIDO'


def analizar_lexico(contenido: str) -> dict:
    """
    Recibe el contenido del archivo TXT y retorna
    todos los tokens identificados por línea.
    """
    lineas   = contenido.strip().split('\n')
    tokens   = []
    errores  = []

    for num_linea, linea in enumerate(lineas, 1):
        linea = linea.strip()
        if not linea:
            continue

        partes = linea.split(SEPARADOR)
        tokens_linea = []

        for pos, valor in enumerate(partes):
            tipo = clasificar_token(valor)
            token = {
                'linea':    num_linea,
                'posicion': pos + 1,
                'lexema':   valor,
                'token':    tipo,
            }
            tokens_linea.append(token)

            if tipo == 'DESCONOCIDO':
                errores.append(
                    f"Error léxico — Línea {num_linea}, posición {pos+1}: "
                    f"token no reconocido '{valor}'"
                )

        tokens.append({
            'num_linea':    num_linea,
            'contenido':    linea,
            'tokens':       tokens_linea
        })

    return {
        'lineas':  tokens,
        'errores': errores,
        'valido':  len(errores) == 0,
        'total_tokens': sum(len(l['tokens']) for l in tokens)
    }


def get_expresiones_regulares() -> list:
    """Retorna la lista de tokens con sus expresiones regulares."""
    _meta = {
        'mis_segmentos_doc': {
            'descripcion': 'Identificador del tipo de segmento en el documento IDoc',
            'lenguaje':    'L = { HDR, ITM, FTR }',
            'gramatica':   'SEG → HDR | ITM | FTR',
            'producciones': ['SEG → HDR', 'SEG → ITM', 'SEG → FTR'],
        },
        'mis_codigos_orden': {
            'descripcion': 'Código único de orden en formato PREFIJO-AÑO-SECUENCIA',
            'lenguaje':    'L = { s-aaaa-nnn | s ∈ [A-Z]+, a ∈ {0-9}, n ∈ {0-9} }',
            'gramatica':   "COD → LETRA+ '-' DIGITO{4} '-' DIGITO{3}",
            'producciones': ['COD → PREF SEP AÑO SEP SEQ', 'PREF → [A-Z]+', 'AÑO → [0-9]{4}', 'SEQ → [0-9]{3}'],
        },
        'mis_variables_ruc': {
            'descripcion': 'Registro Único de Contribuyente peruano de 11 dígitos',
            'lenguaje':    'L = { w ∈ {0-9}* | |w| = 11 }',
            'gramatica':   'RUC → D D D D D D D D D D D',
            'producciones': ['RUC → D{11}', 'D → [0-9]'],
        },
        'mis_variables_fecha': {
            'descripcion': 'Fecha en formato DDMMYYYY sin separadores',
            'lenguaje':    'L = { w ∈ {0-9}* | |w| = 8 }',
            'gramatica':   'FECHA → DD MM YYYY',
            'producciones': ['FECHA → DD MM YYYY', 'DD → [0-9]{2}', 'MM → [0-9]{2}', 'YYYY → [0-9]{4}'],
        },
        'mis_motivos_traslado': {
            'descripcion': 'Motivo del traslado de mercadería entre empresas',
            'lenguaje':    'L = { VENTA, COMPRA, DEVOLUCION }',
            'gramatica':   'MOT → VENTA | COMPRA | DEVOLUCION',
            'producciones': ['MOT → VENTA', 'MOT → COMPRA', 'MOT → DEVOLUCION'],
        },
        'mis_tipos_moneda': {
            'descripcion': 'Tipo de moneda de la transacción comercial',
            'lenguaje':    'L = { PEN, USD }',
            'gramatica':   'MON → PEN | USD',
            'producciones': ['MON → PEN', 'MON → USD'],
        },
        'mis_codigos_item': {
            'descripcion': 'Número de ítem dentro de la orden con ceros a la izquierda',
            'lenguaje':    'L = { w ∈ {0-9}* | |w| = 3 }',
            'gramatica':   'ITEM → D D D',
            'producciones': ['ITEM → D{3}', 'D → [0-9]'],
        },
        'mis_nombres_producto': {
            'descripcion': 'Nombre de producto en formato palabra-palabra en minúsculas',
            'lenguaje':    "L = { a-b | a,b ∈ [a-z]+ }",
            'gramatica':   "PROD → PALABRA '-' PALABRA",
            'producciones': ['PROD → PAL SEP PAL', 'PAL → [a-z]+', "SEP → '-'"],
        },
        'mis_unidades_medida': {
            'descripcion': 'Unidad de medida del producto en la orden logística',
            'lenguaje':    'L = { KG, SAC, CAJA, UNID }',
            'gramatica':   'UNI → KG | SAC | CAJA | UNID',
            'producciones': ['UNI → KG', 'UNI → SAC', 'UNI → CAJA', 'UNI → UNID'],
        },
        'mis_estados_orden': {
            'descripcion': 'Estado actual de procesamiento de la orden logística',
            'lenguaje':    'L = { PENDIENTE, PROCESADO, ANULADO }',
            'gramatica':   'EST → PENDIENTE | PROCESADO | ANULADO',
            'producciones': ['EST → PENDIENTE', 'EST → PROCESADO', 'EST → ANULADO'],
        },
        'mis_variables_decimales': {
            'descripcion': 'Número decimal con exactamente dos cifras decimales',
            'lenguaje':    "L = { w.dd | w ∈ {0-9}+, d ∈ {0-9} }",
            'gramatica':   "DEC → NUM '.' D D",
            'producciones': ["DEC → NUM '.' DD", 'NUM → [0-9]+', 'DD → [0-9]{2}'],
        },
        'mis_variables_numericas': {
            'descripcion': 'Número entero positivo sin decimales',
            'lenguaje':    'L = { w ∈ {0-9}+ }',
            'gramatica':   'NUM → D+',
            'producciones': ['NUM → D+', 'D → [0-9]'],
        },
        'mis_variables_texto': {
            'descripcion': 'Cadena alfanumérica libre para valores de texto general',
            'lenguaje':    r'L = { w ∈ (A-Za-z0-9\-\.)+ }',
            'gramatica':   'TXT → CHAR+',
            'producciones': ['TXT → CHAR+', r'CHAR → [A-Za-z0-9\-\.]'],
        },
    }
    return [
        {
            'token':       nombre,
            'expresion':   patron,
            'ejemplos':    _ejemplos(nombre),
            'descripcion': _meta[nombre]['descripcion'],
            'lenguaje':    _meta[nombre]['lenguaje'],
            'gramatica':   _meta[nombre]['gramatica'],
            'producciones': _meta[nombre]['producciones'],
        }
        for nombre, patron in TOKENS
    ]


def _ejemplos(nombre: str) -> str:
    ejemplos = {
        'mis_segmentos_doc':     'HDR, ITM, FTR',
        'mis_codigos_orden':     'ORD-2026-001, ALI-2025-099',
        'mis_variables_ruc':     '20100055237, 20481559927',
        'mis_variables_fecha':   '10062026, 01012025',
        'mis_motivos_traslado':  'VENTA, COMPRA, DEVOLUCION',
        'mis_tipos_moneda':      'PEN, USD',
        'mis_codigos_item':      '001, 002, 099',
        'mis_nombres_producto':  'aceite-vegetal, leche-evaporada',
        'mis_unidades_medida':   'KG, SAC, CAJA, UNID',
        'mis_estados_orden':     'PENDIENTE, PROCESADO, ANULADO',
        'mis_variables_decimales': '15.50, 45.00, 1500.75',
        'mis_variables_numericas': '100, 50, 3',
        'mis_variables_texto':   'texto libre alfanumérico',
    }
    return ejemplos.get(nombre, '')
