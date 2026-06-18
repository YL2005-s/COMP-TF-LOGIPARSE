from datetime import datetime


def analizar_semantico(resultado_lexico: dict) -> dict:
    """
    Aplica las 10 reglas semánticas del dominio logístico.
    """
    errores    = []
    advertencias = []
    lineas     = resultado_lexico['lineas']

    hdr_data   = None
    itm_data   = []
    ftr_data   = None

    # Extraer datos por segmento
    for linea in lineas:
        tokens  = linea['tokens']
        if not tokens:
            continue
        seg = tokens[0]['lexema']
        vals = [t['lexema'] for t in tokens]

        if seg == 'HDR':
            hdr_data = vals
        elif seg == 'ITM':
            itm_data.append(vals)
        elif seg == 'FTR':
            ftr_data = vals

    if not hdr_data or not ftr_data:
        return {
            'errores': ['Error semántico: documento incompleto — falta HDR o FTR'],
            'valido':  False,
            'reglas_aplicadas': []
        }

    reglas_aplicadas = []

    # S1 — RUC emisor debe tener 11 dígitos
    ruc_emisor = hdr_data[2]
    if len(ruc_emisor) == 11 and ruc_emisor.isdigit():
        reglas_aplicadas.append({'regla': 'S1', 'descripcion': 'RUC emisor válido', 'estado': '✅', 'valor': ruc_emisor})
    else:
        errores.append(f"Error semántico S1: RUC emisor '{ruc_emisor}' debe tener exactamente 11 dígitos")
        reglas_aplicadas.append({'regla': 'S1', 'descripcion': 'RUC emisor válido', 'estado': '❌', 'valor': ruc_emisor})

    # S2 — RUC receptor debe tener 11 dígitos
    ruc_receptor = hdr_data[3]
    if len(ruc_receptor) == 11 and ruc_receptor.isdigit():
        reglas_aplicadas.append({'regla': 'S2', 'descripcion': 'RUC receptor válido', 'estado': '✅', 'valor': ruc_receptor})
    else:
        errores.append(f"Error semántico S2: RUC receptor '{ruc_receptor}' debe tener exactamente 11 dígitos")
        reglas_aplicadas.append({'regla': 'S2', 'descripcion': 'RUC receptor válido', 'estado': '❌', 'valor': ruc_receptor})

    # S3 — Fecha debe ser válida
    fecha_raw = hdr_data[4]
    try:
        fecha = datetime.strptime(fecha_raw, '%d%m%Y')
        reglas_aplicadas.append({'regla': 'S3', 'descripcion': 'Fecha de emisión válida', 'estado': '✅', 'valor': fecha.strftime('%d/%m/%Y')})
    except ValueError:
        errores.append(f"Error semántico S3: fecha '{fecha_raw}' no es válida — formato esperado DDMMYYYY")
        reglas_aplicadas.append({'regla': 'S3', 'descripcion': 'Fecha de emisión válida', 'estado': '❌', 'valor': fecha_raw})
        fecha = None

    # S4 — Cantidad debe ser mayor a 0
    cantidades_ok = True
    for i, itm in enumerate(itm_data):
        cantidad = int(itm[3])
        if cantidad <= 0:
            errores.append(f"Error semántico S4: cantidad en ítem {i+1} debe ser mayor a 0, se encontró {cantidad}")
            cantidades_ok = False
    reglas_aplicadas.append({'regla': 'S4', 'descripcion': 'Cantidades mayores a 0', 'estado': '✅' if cantidades_ok else '❌', 'valor': f'{len(itm_data)} ítems verificados'})

    # S5 — Precio debe ser mayor a 0
    precios_ok = True
    for i, itm in enumerate(itm_data):
        precio = float(itm[5])
        if precio <= 0:
            errores.append(f"Error semántico S5: precio en ítem {i+1} debe ser mayor a 0, se encontró {precio}")
            precios_ok = False
    reglas_aplicadas.append({'regla': 'S5', 'descripcion': 'Precios mayores a 0', 'estado': '✅' if precios_ok else '❌', 'valor': f'{len(itm_data)} precios verificados'})

    # S6 — Total ítems en FTR debe coincidir con líneas ITM
    total_itm_ftr  = int(ftr_data[1])
    total_itm_real = len(itm_data)
    if total_itm_ftr == total_itm_real:
        reglas_aplicadas.append({'regla': 'S6', 'descripcion': 'Total ítems coincide con FTR', 'estado': '✅', 'valor': f'{total_itm_real} ítems'})
    else:
        errores.append(f"Error semántico S6: FTR indica {total_itm_ftr} ítems pero existen {total_itm_real} líneas ITM")
        reglas_aplicadas.append({'regla': 'S6', 'descripcion': 'Total ítems coincide con FTR', 'estado': '❌', 'valor': f'FTR={total_itm_ftr} vs real={total_itm_real}'})

    # S7 — Monto total debe coincidir con suma de cantidades * precios
    monto_ftr       = float(ftr_data[2])
    monto_calculado = sum(int(itm[3]) * float(itm[5]) for itm in itm_data)
    if abs(monto_ftr - monto_calculado) < 0.01:
        reglas_aplicadas.append({'regla': 'S7', 'descripcion': 'Monto total verificado', 'estado': '✅', 'valor': f'S/. {monto_calculado:.2f}'})
    else:
        errores.append(f"Error semántico S7: monto en FTR es {monto_ftr} pero la suma real es {monto_calculado:.2f}")
        reglas_aplicadas.append({'regla': 'S7', 'descripcion': 'Monto total verificado', 'estado': '❌', 'valor': f'FTR={monto_ftr} vs calculado={monto_calculado:.2f}'})

    # S8 — Motivo válido
    motivo = hdr_data[5]
    if motivo in ['VENTA', 'COMPRA', 'DEVOLUCION']:
        reglas_aplicadas.append({'regla': 'S8', 'descripcion': 'Motivo de traslado válido', 'estado': '✅', 'valor': motivo})
    else:
        errores.append(f"Error semántico S8: motivo '{motivo}' no válido — usar VENTA, COMPRA o DEVOLUCION")
        reglas_aplicadas.append({'regla': 'S8', 'descripcion': 'Motivo de traslado válido', 'estado': '❌', 'valor': motivo})

    # S9 — Moneda válida
    moneda = hdr_data[6]
    if moneda in ['PEN', 'USD']:
        reglas_aplicadas.append({'regla': 'S9', 'descripcion': 'Moneda válida', 'estado': '✅', 'valor': moneda})
    else:
        errores.append(f"Error semántico S9: moneda '{moneda}' no válida — usar PEN o USD")
        reglas_aplicadas.append({'regla': 'S9', 'descripcion': 'Moneda válida', 'estado': '❌', 'valor': moneda})

    # S10 — Estado válido
    estado = ftr_data[3]
    if estado in ['PENDIENTE', 'PROCESADO', 'ANULADO']:
        reglas_aplicadas.append({'regla': 'S10', 'descripcion': 'Estado de orden válido', 'estado': '✅', 'valor': estado})
    else:
        errores.append(f"Error semántico S10: estado '{estado}' no válido — usar PENDIENTE, PROCESADO o ANULADO")
        reglas_aplicadas.append({'regla': 'S10', 'descripcion': 'Estado de orden válido', 'estado': '❌', 'valor': estado})

    return {
        'errores':          errores,
        'valido':           len(errores) == 0,
        'reglas_aplicadas': reglas_aplicadas,
        'resumen': {
            'codigo_orden':  hdr_data[1],
            'ruc_emisor':    ruc_emisor,
            'ruc_receptor':  ruc_receptor,
            'fecha':         fecha.strftime('%Y-%m-%d') if fecha else fecha_raw,
            'motivo':        motivo,
            'moneda':        moneda,
            'total_items':   total_itm_real,
            'monto_total':   monto_calculado,
            'estado':        estado
        }
    }
