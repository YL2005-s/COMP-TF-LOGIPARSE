from datetime import datetime


def traducir_a_sql(resultado_lexico: dict, resumen: dict) -> str:
    """
    Genera el script SQL a partir del archivo TXT procesado.
    Formato destino: SQL Server (Ransa Logística)
    """
    lineas = resultado_lexico['lineas']
    itm_data = []

    for linea in lineas:
        tokens = linea['tokens']
        if tokens and tokens[0]['lexema'] == 'ITM':
            itm_data.append([t['lexema'] for t in tokens])

    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    codigo = resumen['codigo_orden']
    ruc_emisor = resumen['ruc_emisor']
    ruc_receptor= resumen['ruc_receptor']
    fecha = resumen['fecha']
    motivo = resumen['motivo']
    moneda = resumen['moneda']
    monto = resumen['monto_total']
    total_items = resumen['total_items']
    estado = resumen['estado']

    sql = f"""-- ═══════════════════════════════════════════════════════
    -- Script generado por LogiParse v1.0
    -- Origen  : Alicorp S.A. (Sistema SAP)
    -- Destino : Ransa Logística (SQL Server)
    -- Archivo : {codigo}.txt
    -- Fecha   : {ahora}
    -- ═══════════════════════════════════════════════════════

    -- 1. Insertar orden principal
    INSERT INTO ordenes (
        codigo,
        ruc_emisor,
        ruc_receptor,
        fecha_emision,
        motivo,
        moneda,
        monto_total,
        total_items,
        estado
    )
    VALUES (
        '{codigo}',
        '{ruc_emisor}',
        '{ruc_receptor}',
        '{fecha}',
        '{motivo}',
        '{moneda}',
        {monto:.2f},
        {total_items},
        '{estado}'
    );

    -- 2. Insertar detalle de ítems
    INSERT INTO detalle_orden (
        orden_id,
        item_num,
        producto,
        cantidad,
        unidad,
        precio_unit,
        subtotal
    )
    VALUES"""

    valores = []
    for itm in itm_data:
        item_num = int(itm[1])
        producto = itm[2]
        cantidad = int(itm[3])
        unidad   = itm[4]
        precio   = float(itm[5])
        subtotal = cantidad * precio
        valores.append(
            f"('{codigo}', {item_num}, '{producto}', {cantidad}, '{unidad}', {precio:.2f}, {subtotal:.2f})"
        )

    sql += '\n' + ',\n'.join(valores) + ';\n'

    sql += f"""
    -- 3. Registrar log de procesamiento
    INSERT INTO log_procesamiento (
        orden_id,
        fecha_proceso,
        sistema_origen,
        sistema_destino,
        estado_proceso
    )
    VALUES (
        '{codigo}',
        '{ahora}',
        'SAP-Alicorp',
        'SQLServer-Ransa',
        'EXITOSO'
    );

    -- ═══════════════════════════════════════════════════════
    -- Fin del script — {total_items} ítem(s) procesado(s)
    -- Monto total: {moneda} {monto:.2f}
    -- ═══════════════════════════════════════════════════════
    """
    return sql
