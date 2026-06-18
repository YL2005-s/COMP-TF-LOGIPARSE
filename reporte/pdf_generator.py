from datetime import datetime
import io


def generar_pdf(lexico: dict, sintactico: dict, semantico: dict, sql: str) -> bytes:
    """
    Genera un reporte PDF con los resultados de las 4 fases.
    Usa reportlab si está disponible, sino genera HTML para imprimir.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
        return _generar_pdf_reportlab(lexico, sintactico, semantico, sql)
    except ImportError:
        return _generar_pdf_html(lexico, sintactico, semantico, sql).encode('utf-8')


def _generar_pdf_reportlab(lexico, sintactico, semantico, sql) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=2*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    # Colores
    AZUL    = colors.HexColor('#1a3c5e')
    VERDE   = colors.HexColor('#1a4731')
    ROJO    = colors.HexColor('#4d1e1e')
    GRIS    = colors.HexColor('#21262d')

    titulo_style = ParagraphStyle('titulo', parent=styles['Title'],
                                  textColor=AZUL, fontSize=18, spaceAfter=6)
    sub_style    = ParagraphStyle('sub', parent=styles['Heading2'],
                                  textColor=AZUL, fontSize=13, spaceAfter=4)
    normal_style = styles['Normal']
    ahora        = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    # ── Encabezado ──
    story.append(Paragraph('LogiParse — Reporte de Procesamiento', titulo_style))
    story.append(Paragraph(f'Fecha de generación: {ahora}', normal_style))
    story.append(Spacer(1, 0.4*cm))

    # ── Resumen ──
    resumen = semantico.get('resumen', {})
    story.append(Paragraph('Resumen del documento', sub_style))
    resumen_data = [
        ['Campo', 'Valor'],
        ['Código de orden',  resumen.get('codigo_orden', '-')],
        ['RUC emisor',       resumen.get('ruc_emisor', '-')],
        ['RUC receptor',     resumen.get('ruc_receptor', '-')],
        ['Fecha emisión',    resumen.get('fecha', '-')],
        ['Motivo',           resumen.get('motivo', '-')],
        ['Moneda',           resumen.get('moneda', '-')],
        ['Total ítems',      str(resumen.get('total_items', '-'))],
        ['Monto total',      f"S/. {resumen.get('monto_total', 0):.2f}"],
        ['Estado',           resumen.get('estado', '-')],
    ]
    t = Table(resumen_data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # ── Análisis Léxico ──
    story.append(Paragraph('Fase 1 — Análisis Léxico', sub_style))
    story.append(Paragraph(f"Total tokens: {lexico.get('total_tokens', 0)} | "
                            f"Estado: {'✅ Válido' if lexico['valido'] else '❌ Con errores'}",
                            normal_style))
    story.append(Spacer(1, 0.3*cm))

    # Tabla de tokens
    token_data = [['Línea', 'Posición', 'Lexema', 'Token']]
    for linea in lexico.get('lineas', []):
        for tok in linea.get('tokens', []):
            token_data.append([
                str(tok['linea']),
                str(tok['posicion']),
                tok['lexema'],
                tok['token']
            ])
    t2 = Table(token_data, colWidths=[2*cm, 2.5*cm, 7*cm, 6.5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))

    # ── Análisis Semántico ──
    story.append(Paragraph('Fase 3 — Análisis Semántico', sub_style))
    reglas_data = [['Regla', 'Descripción', 'Estado', 'Valor']]
    for r in semantico.get('reglas_aplicadas', []):
        reglas_data.append([r['regla'], r['descripcion'], r['estado'], r['valor']])
    t3 = Table(reglas_data, colWidths=[2*cm, 7*cm, 2*cm, 7*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.5*cm))

    # ── SQL Generado ──
    story.append(Paragraph('Fase 4 — SQL Generado', sub_style))
    sql_style = ParagraphStyle('sql', parent=styles['Code'],
                               fontSize=7, fontName='Courier',
                               backColor=colors.HexColor('#f6f8fa'),
                               borderColor=colors.HexColor('#d0d7de'),
                               borderWidth=1, borderPadding=8)
    for linea in sql.split('\n')[:40]:
        story.append(Paragraph(linea.replace('<','&lt;').replace('>','&gt;') or '&nbsp;', sql_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _generar_pdf_html(lexico, sintactico, semantico, sql) -> str:
    """Fallback: genera HTML que el navegador puede imprimir como PDF."""
    ahora   = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    resumen = semantico.get('resumen', {})

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>LogiParse — Reporte</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1a1a1a; padding: 2cm; }}
  h1 {{ color: #1a3c5e; border-bottom: 2px solid #1a3c5e; padding-bottom: 8px; }}
  h2 {{ color: #1a3c5e; margin-top: 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
  th {{ background: #1a3c5e; color: white; padding: 8px; text-align: left; }}
  td {{ padding: 6px 8px; border: 1px solid #ddd; }}
  tr:nth-child(even) {{ background: #f0f4f8; }}
  pre {{ background: #f6f8fa; padding: 12px; border: 1px solid #ddd; font-size: 10px; overflow-x: auto; }}
  .ok {{ color: green; }} .err {{ color: red; }}
</style>
</head>
<body>
<h1>LogiParse — Reporte de Procesamiento</h1>
<p><strong>Fecha:</strong> {ahora}</p>

<h2>Resumen</h2>
<table>
<tr><th>Campo</th><th>Valor</th></tr>
<tr><td>Código de orden</td><td>{resumen.get('codigo_orden','-')}</td></tr>
<tr><td>RUC emisor</td><td>{resumen.get('ruc_emisor','-')}</td></tr>
<tr><td>RUC receptor</td><td>{resumen.get('ruc_receptor','-')}</td></tr>
<tr><td>Fecha emisión</td><td>{resumen.get('fecha','-')}</td></tr>
<tr><td>Motivo</td><td>{resumen.get('motivo','-')}</td></tr>
<tr><td>Moneda</td><td>{resumen.get('moneda','-')}</td></tr>
<tr><td>Total ítems</td><td>{resumen.get('total_items','-')}</td></tr>
<tr><td>Monto total</td><td>S/. {resumen.get('monto_total',0):.2f}</td></tr>
<tr><td>Estado</td><td>{resumen.get('estado','-')}</td></tr>
</table>

<h2>Fase 1 — Análisis Léxico</h2>
<p>Total tokens: {lexico.get('total_tokens',0)} | 
Estado: <span class="{'ok' if lexico['valido'] else 'err'}">
{'✅ Válido' if lexico['valido'] else '❌ Con errores'}</span></p>
<table>
<tr><th>Línea</th><th>Posición</th><th>Lexema</th><th>Token</th></tr>
"""
    for linea in lexico.get('lineas', []):
        for tok in linea.get('tokens', []):
            html += f"<tr><td>{tok['linea']}</td><td>{tok['posicion']}</td><td>{tok['lexema']}</td><td>{tok['token']}</td></tr>\n"

    html += f"""</table>
<h2>Fase 3 — Análisis Semántico</h2>
<table>
<tr><th>Regla</th><th>Descripción</th><th>Estado</th><th>Valor</th></tr>
"""
    for r in semantico.get('reglas_aplicadas', []):
        html += f"<tr><td>{r['regla']}</td><td>{r['descripcion']}</td><td>{r['estado']}</td><td>{r['valor']}</td></tr>\n"

    html += f"""</table>
<h2>Fase 4 — SQL Generado</h2>
<pre>{sql}</pre>
</body></html>"""
    return html
