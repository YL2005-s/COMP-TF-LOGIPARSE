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
    return [
        {'token': nombre, 'expresion': patron, 'ejemplos': _ejemplos(nombre)}
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
