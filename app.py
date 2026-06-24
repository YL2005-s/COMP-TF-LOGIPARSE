import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify, send_file
from core.lexico import analizar_lexico, get_expresiones_regulares
from core.sintactico import analizar_sintactico, get_plantillas_gramatica
from core.semantico import analizar_semantico
from core.traductor import traducir_a_sql
from automatas.generador import generar_automatas, generar_automatas_por_token
from reporte.pdf_generator import generar_pdf
import io

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/procesar', methods=['POST'])
def procesar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se recibió ningún archivo'}), 400

    archivo = request.files['archivo']
    contenido = archivo.read().decode('utf-8')

    if not contenido.strip():
        return jsonify({'error': 'El archivo está vacío'}), 400

    lexico = analizar_lexico(contenido)
    if not lexico['valido']:
        return jsonify({
            'valido': False,
            'fase_fallo': 'léxico',
            'lexico': lexico,
            'expresiones': get_expresiones_regulares(),
            'automatas': generar_automatas(),
            'automatas_token': generar_automatas_por_token(),
        })

    sintactico = analizar_sintactico(lexico)
    if not sintactico['valido']:
        return jsonify({
            'valido': False,
            'fase_fallo': 'sintáctico',
            'lexico': lexico,
            'sintactico': sintactico,
            'expresiones': get_expresiones_regulares(),
            'automatas': generar_automatas(),
            'automatas_token': generar_automatas_por_token(),
            'plantillas_gramatica': get_plantillas_gramatica(),
        })

    semantico = analizar_semantico(lexico)
    if not semantico['valido']:
        return jsonify({
            'valido': False,
            'fase_fallo': 'semántico',
            'lexico': lexico,
            'sintactico': sintactico,
            'semantico': semantico,
            'expresiones': get_expresiones_regulares(),
            'automatas': generar_automatas(),
            'automatas_token': generar_automatas_por_token(),
            'plantillas_gramatica': get_plantillas_gramatica(),
        })

    sql = traducir_a_sql(lexico, semantico['resumen'])

    return jsonify({
        'valido': True,
        'lexico':  lexico,
        'sintactico': sintactico,
        'semantico': semantico,
        'sql': sql,
        'expresiones': get_expresiones_regulares(),
        'automatas': generar_automatas(),
        'automatas_token': generar_automatas_por_token(),
        'plantillas_gramatica': get_plantillas_gramatica(),
    })


@app.route('/descargar-sql', methods=['POST'])
def descargar_sql():
    data = request.get_json()
    sql = data.get('sql', '')
    buf = io.BytesIO(sql.encode('utf-8'))
    buf.seek(0)
    return send_file(buf, mimetype='text/plain',
                     as_attachment=True,
                     download_name='logiparse_output.sql')


@app.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    data = request.get_json()
    lexico = data.get('lexico', {})
    sintactico = data.get('sintactico', {})
    semantico = data.get('semantico', {})
    sql = data.get('sql', '')

    pdf_bytes = generar_pdf(lexico, sintactico, semantico, sql)
    buf = io.BytesIO(pdf_bytes)
    buf.seek(0)

    try:
        from reportlab.lib.pagesizes import A4
        mimetype = 'application/pdf'
        download_name = 'reporte_logiparse.pdf'
    except ImportError:
        mimetype = 'text/html'
        download_name = 'reporte_logiparse.html'

    return send_file(buf, mimetype=mimetype,
                     as_attachment=True,
                     download_name=download_name)


if __name__ == '__main__':
    app.run(debug=True)
