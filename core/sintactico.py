
# ─── GRAMÁTICA BNF ───────────────────────────────────────────────────────────
# documento   → encabezado items+ pie
# encabezado  → HDR SEP codigo_orden SEP ruc SEP ruc SEP fecha SEP motivo SEP moneda
# item        → ITM SEP codigo_item SEP producto SEP cantidad SEP unidad SEP precio
# pie         → FTR SEP total_items SEP monto SEP estado

# Tipos válidos por posición
GRAMATICA = {
    'HDR': {
        'nombre': 'encabezado',
        'campos': 7,
        'tipos':  [
            ['mis_segmentos_doc'],
            ['mis_codigos_orden'],
            ['mis_variables_ruc'],
            ['mis_variables_ruc'],
            ['mis_variables_fecha'],
            ['mis_motivos_traslado'],
            ['mis_tipos_moneda']
        ]
    },
    'ITM': {
        'nombre': 'item',
        'campos': 6,
        'tipos':  [
            ['mis_segmentos_doc'],
            ['mis_codigos_item'],
            ['mis_nombres_producto'],
            ['mis_variables_numericas', 'mis_codigos_item'],  # cantidad puede ser 3 dígitos
            ['mis_unidades_medida'],
            ['mis_variables_decimales']
        ]
    },
    'FTR': {
        'nombre': 'pie',
        'campos': 4,
        'tipos':  [
            ['mis_segmentos_doc'],
            ['mis_variables_numericas', 'mis_codigos_item'],
            ['mis_variables_decimales'],
            ['mis_estados_orden']
        ]
    }
}

PRODUCCIONES = [
    'documento   → encabezado  items+  pie',
    'encabezado  → HDR | codigo_orden | ruc_emisor | ruc_receptor | fecha | motivo | moneda',
    'items       → item+',
    'item        → ITM | codigo_item | producto | cantidad | unidad | precio',
    'pie         → FTR | total_items | monto_total | estado',
    'codigo_orden → mis_codigos_orden',
    'ruc          → mis_variables_ruc',
    'fecha        → mis_variables_fecha',
    'motivo       → mis_motivos_traslado',
    'moneda       → mis_tipos_moneda',
    'producto     → mis_nombres_producto',
    'cantidad     → mis_variables_numericas | mis_codigos_item',
    'unidad       → mis_unidades_medida',
    'precio       → mis_variables_decimales',
    'estado       → mis_estados_orden',
]


def analizar_sintactico(resultado_lexico: dict) -> dict:
    errores = []
    lineas  = resultado_lexico['lineas']
    arbol   = []

    if not lineas:
        return {'errores': ['Documento vacío'], 'valido': False, 'arbol': []}

    segmentos = [l['tokens'][0]['lexema'] for l in lineas if l['tokens']]

    # Verificar que empiece con HDR
    if segmentos[0] != 'HDR':
        errores.append('Error sintáctico: el documento debe iniciar con HDR')

    # Verificar que termine con FTR
    if segmentos[-1] != 'FTR':
        errores.append('Error sintáctico: el documento debe terminar con FTR')

    # Verificar que haya al menos un ITM
    if 'ITM' not in segmentos:
        errores.append('Error sintáctico: el documento debe tener al menos un segmento ITM')

    # Verificar orden: HDR → ITM+ → FTR
    estado = 'INICIO'
    for seg in segmentos:
        if estado == 'INICIO':
            if seg == 'HDR':
                estado = 'HDR_OK'
            else:
                errores.append(f'Error sintáctico: se esperaba HDR, se encontró {seg}')
        elif estado == 'HDR_OK':
            if seg == 'ITM':
                estado = 'ITM_OK'
            else:
                errores.append(f'Error sintáctico: se esperaba ITM después de HDR, se encontró {seg}')
        elif estado == 'ITM_OK':
            if seg not in ['ITM', 'FTR']:
                errores.append(f'Error sintáctico: se esperaba ITM o FTR, se encontró {seg}')

    # Verificar campos por línea
    for linea in lineas:
        tokens   = linea['tokens']
        segmento = tokens[0]['lexema'] if tokens else None
        regla    = GRAMATICA.get(segmento)

        if not regla:
            errores.append(f"Error sintáctico — Línea {linea['num_linea']}: segmento '{segmento}' no reconocido")
            continue

        if len(tokens) != regla['campos']:
            errores.append(
                f"Error sintáctico — Línea {linea['num_linea']} ({segmento}): "
                f"se esperaban {regla['campos']} campos, se encontraron {len(tokens)}"
            )
            continue

        # Verificar que el tipo de cada campo esté en los tipos permitidos
        for i, (token, tipos_esperados) in enumerate(zip(tokens, regla['tipos'])):
            if token['token'] not in tipos_esperados:
                errores.append(
                    f"Error sintáctico — Línea {linea['num_linea']}, campo {i+1}: "
                    f"se esperaba {' o '.join(tipos_esperados)}, "
                    f"se encontró {token['token']} ('{token['lexema']}')"
                )

        arbol.append({
            'segmento': segmento,
            'nombre':   regla['nombre'],
            'campos':   [{'lexema': t['lexema'], 'token': t['token']} for t in tokens]
        })

    return {
        'errores':      errores,
        'valido':       len(errores) == 0,
        'arbol':        arbol,
        'producciones': PRODUCCIONES
    }


def get_plantillas_gramatica():
    nombres_campo = {
        'HDR': ['segmento', 'codigo_orden', 'ruc_emisor', 'ruc_receptor', 'fecha', 'motivo', 'moneda'],
        'ITM': ['segmento', 'codigo_item', 'producto', 'cantidad', 'unidad', 'precio'],
        'FTR': ['segmento', 'total_items', 'monto_total', 'estado'],
    }
    return [
        {
            'segmento': seg,
            'nombre': GRAMATICA[seg]['nombre'],
            'campos': [{'lexema': nombre, 'token': tipo[0]}
                       for nombre, tipo in zip(nombres_campo[seg], GRAMATICA[seg]['tipos'])]
        }
        for seg in ['HDR', 'ITM', 'FTR']
    ]
