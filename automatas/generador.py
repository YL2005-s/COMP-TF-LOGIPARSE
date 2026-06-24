def generar_automatas() -> dict:
    """
    Genera los datos para visualizar AFND, AFD y tabla de transiciones
    del analizador léxico de LogiParse.
    Se enfoca en los tokens principales del DSL logístico.
    """

    afnd = {
        'estados': ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'qE'],
        'estado_inicial': 'q0',
        'estados_aceptacion': ['q1', 'q2', 'q3', 'q4', 'q5'],
        'transiciones': [
            {'desde': 'q0', 'con': '#', 'hacia': 'q1', 'descripcion': 'Inicio de segmento'},
            {'desde': 'q1', 'con': 'H,I,F', 'hacia': 'q1', 'descripcion': 'Primera letra del segmento'},
            {'desde': 'q1', 'con': 'D,T,R', 'hacia': 'q1', 'descripcion': 'Segunda letra del segmento'},
            {'desde': 'q1', 'con': 'ε', 'hacia': 'q2', 'descripcion': 'HDR reconocido'},
            {'desde': 'q1', 'con': 'ε', 'hacia': 'q3', 'descripcion': 'ITM reconocido'},
            {'desde': 'q1', 'con': 'ε', 'hacia': 'q4', 'descripcion': 'FTR reconocido'},
            {'desde': 'q0', 'con': '[0-9]', 'hacia': 'q5', 'descripcion': 'Inicio de número/RUC/fecha'},
            {'desde': 'q5', 'con': '[0-9]', 'hacia': 'q5', 'descripcion': 'Dígitos consecutivos'},
            {'desde': 'q0', 'con': '[a-z]', 'hacia': 'q2', 'descripcion': 'Inicio de producto/texto'},
            {'desde': 'q2', 'con': '[a-z\\-]', 'hacia': 'q2', 'descripcion': 'Caracteres de producto'},
            {'desde': 'q0', 'con': 'otro', 'hacia': 'qE', 'descripcion': 'Token no reconocido'},
        ],
        'descripcion': 'AFND para reconocimiento de tokens del formato IDoc logístico'
    }

    afd = {
        'estados': ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'qE'],
        'estado_inicial': 'q0',
        'estados_aceptacion': ['q2', 'q3', 'q4', 'q5', 'q6'],
        'transiciones': [
            {'desde': 'q0', 'con': '#', 'hacia': 'q1', 'descripcion': 'Inicio segmento doc'},
            {'desde': 'q1', 'con': 'H', 'hacia': 'q2', 'descripcion': 'HDR → encabezado'},
            {'desde': 'q1', 'con': 'I', 'hacia': 'q3', 'descripcion': 'ITM → ítem'},
            {'desde': 'q1', 'con': 'F', 'hacia': 'q4', 'descripcion': 'FTR → pie'},
            {'desde': 'q0', 'con': '[0-9]', 'hacia': 'q5', 'descripcion': 'Inicio numérico'},
            {'desde': 'q5', 'con': '[0-9]', 'hacia': 'q5', 'descripcion': 'Dígitos continuos'},
            {'desde': 'q5', 'con': '.', 'hacia': 'q6', 'descripcion': 'Inicio decimal'},
            {'desde': 'q6', 'con': '[0-9]', 'hacia': 'q6', 'descripcion': 'Decimales'},
            {'desde': 'q0', 'con': '[a-z]', 'hacia': 'q5', 'descripcion': 'Inicio texto/producto'},
            {'desde': 'q0', 'con': 'otro', 'hacia': 'qE', 'descripcion': 'Error'},
            {'desde': 'qE', 'con': 'cualquiera','hacia': 'qE', 'descripcion': 'Estado de error'},
        ],
        'descripcion': 'AFD determinista equivalente para el reconocimiento de tokens logísticos'
    }

    tabla = {
        'estados': ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'qE'],
        'simbolos': ['#', 'H', 'I', 'F', '[0-9]', '[a-z]', '.', 'otro'],
        'transiciones': {
            'q0': {'#': 'q1', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'q5', '[a-z]': 'q5', '.': 'qE',  'otro': 'qE'},
            'q1': {'#': 'qE', 'H': 'q2', 'I': 'q3', 'F': 'q4', '[0-9]': 'qE', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
            'q2': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'qE', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
            'q3': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'qE', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
            'q4': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'qE', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
            'q5': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'q5', '[a-z]': 'q5', '.': 'q6',  'otro': 'qE'},
            'q6': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'q6', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
            'qE': {'#': 'qE', 'H': 'qE', 'I': 'qE', 'F': 'qE', '[0-9]': 'qE', '[a-z]': 'qE', '.': 'qE',  'otro': 'qE'},
        },
        'descripcion': 'Tabla de transiciones del AFD para tokens del formato IDoc logístico'
    }

    turing = {
        'descripcion': 'Máquina de Turing que modela el procesamiento transpilador TXT→SQL de LogiParse',
        'cinta_ejemplo': ['H','D','R','|','O','R','D','-','2','0','2','6','-','0','0','1','□'],
        'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','qACEPT','qREJECT'],
        'estado_inicial': 'q0',
        'estado_aceptacion': 'qACEPT',
        'estado_rechazo': 'qREJECT',
        'alfabeto_entrada': ['H','D','R','I','T','M','F','|','0-9','a-z','-','.','□'],
        'alfabeto_cinta': ['H','D','R','I','T','M','F','|','0-9','a-z','-','.','□','✓','✗'],
        'transiciones': [
            {
                'desde': 'q0',
                'lee': 'H/I/F',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q1',
                'descripcion': 'Lee tipo de segmento HDR/ITM/FTR'
            },
            {
                'desde': 'q1',
                'lee': '|',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q2',
                'descripcion': 'Lee separador de campo'
            },
            {
                'desde': 'q2',
                'lee': '0-9/a-z',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q3',
                'descripcion': 'Lee valor del campo (token)'
            },
            {
                'desde': 'q3',
                'lee': '0-9/a-z/-',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q3',
                'descripcion': 'Continúa leyendo el valor del campo'
            },
            {
                'desde': 'q3',
                'lee': '|',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q2',
                'descripcion': 'Siguiente campo de la misma línea'
            },
            {
                'desde': 'q3',
                'lee': '□',
                'escribe': '□',
                'mueve': 'R',
                'hacia': 'q4',
                'descripcion': 'Fin de línea — valida semántica'
            },
            {
                'desde': 'q4',
                'lee': 'H/I/F',
                'escribe': '✓',
                'mueve': 'R',
                'hacia': 'q1',
                'descripcion': 'Siguiente línea del documento'
            },
            {
                'desde': 'q4',
                'lee': '□',
                'escribe': '□',
                'mueve': 'R',
                'hacia': 'q5',
                'descripcion': 'Fin del documento — inicia traducción'
            },
            {
                'desde': 'q5',
                'lee': '✓',
                'escribe': 'SQL',
                'mueve': 'R',
                'hacia': 'q6',
                'descripcion': 'Genera INSERT INTO ordenes'
            },
            {
                'desde': 'q6',
                'lee': '✓',
                'escribe': 'SQL',
                'mueve': 'R',
                'hacia': 'q7',
                'descripcion': 'Genera INSERT INTO detalle_orden'
            },
            {
                'desde': 'q7',
                'lee': '□',
                'escribe': '□',
                'mueve': 'R',
                'hacia': 'qACEPT',
                'descripcion': 'SQL generado — traducción completada'
            },
            {
                'desde': 'q0',
                'lee': 'otro',
                'escribe': '✗',
                'mueve': 'R',
                'hacia': 'qREJECT',
                'descripcion': 'Token no reconocido — error léxico'
            }
        ],
        'tabla': {
            'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','qACEPT','qREJECT'],
            'simbolos': ['H/I/F','|','0-9','a-z','-','.','□','otro'],
            'transiciones': {
                'q0':      {'H/I/F':'q1/✓/R', '|':'qR/✗/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qR/✗/R', 'otro':'qR/✗/R'},
                'q1':      {'H/I/F':'qR/✗/R', '|':'q2/✓/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qR/✗/R', 'otro':'qR/✗/R'},
                'q2':      {'H/I/F':'qR/✗/R', '|':'qR/✗/R', '0-9':'q3/✓/R', 'a-z':'q3/✓/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qR/✗/R', 'otro':'qR/✗/R'},
                'q3':      {'H/I/F':'qR/✗/R', '|':'q2/✓/R', '0-9':'q3/✓/R', 'a-z':'q3/✓/R', '-':'q3/✓/R', '.':'q3/✓/R', '□':'q4/□/R', 'otro':'qR/✗/R'},
                'q4':      {'H/I/F':'q1/✓/R', '|':'qR/✗/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'q5/□/R', 'otro':'qR/✗/R'},
                'q5':      {'H/I/F':'qR/✗/R', '|':'qR/✗/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qR/✗/R', 'otro':'q6/SQL/R'},
                'q6':      {'H/I/F':'qR/✗/R', '|':'qR/✗/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qA/□/R', 'otro':'q7/SQL/R'},
                'q7':      {'H/I/F':'qR/✗/R', '|':'qR/✗/R', '0-9':'qR/✗/R', 'a-z':'qR/✗/R', '-':'qR/✗/R', '.':'qR/✗/R', '□':'qA/□/R', 'otro':'qR/✗/R'},
                'qACEPT':  {'H/I/F':'—', '|':'—', '0-9':'—', 'a-z':'—', '-':'—', '.':'—', '□':'—', 'otro':'—'},
                'qREJECT': {'H/I/F':'—', '|':'—', '0-9':'—', 'a-z':'—', '-':'—', '.':'—', '□':'—', 'otro':'—'},
            }
        }
    }

    return {'afnd': afnd, 'afd': afd, 'tabla': tabla, 'turing': turing}


AUTOMATAS_POR_TOKEN = {

  'mis_segmentos_doc': {
    'afnd': {
      'estados': ['q0','qH0','qH1','qH2','qH3','qI0','qI1','qI2','qI3','qF0','qF1','qF2','qF3'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['qH3','qI3','qF3'],
      'transiciones': [
        {'desde':'q0','con':'ε','hacia':'qH0','descripcion':'Rama HDR'},
        {'desde':'qH0','con':'H','hacia':'qH1','descripcion':''},
        {'desde':'qH1','con':'D','hacia':'qH2','descripcion':''},
        {'desde':'qH2','con':'R','hacia':'qH3','descripcion':'Acepta HDR'},
        {'desde':'q0','con':'ε','hacia':'qI0','descripcion':'Rama ITM'},
        {'desde':'qI0','con':'I','hacia':'qI1','descripcion':''},
        {'desde':'qI1','con':'T','hacia':'qI2','descripcion':''},
        {'desde':'qI2','con':'M','hacia':'qI3','descripcion':'Acepta ITM'},
        {'desde':'q0','con':'ε','hacia':'qF0','descripcion':'Rama FTR'},
        {'desde':'qF0','con':'F','hacia':'qF1','descripcion':''},
        {'desde':'qF1','con':'T','hacia':'qF2','descripcion':''},
        {'desde':'qF2','con':'R','hacia':'qF3','descripcion':'Acepta FTR'},
      ],
      'descripcion': 'AFND para ^(HDR|ITM|FTR)$ — unión de 3 rutas vía ε'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3','q6','q9'],
      'transiciones': [
        {'desde':'q0','con':'H','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'D','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'R','hacia':'q3','descripcion':'Acepta HDR'},
        {'desde':'q0','con':'I','hacia':'q4','descripcion':''},
        {'desde':'q4','con':'T','hacia':'q5','descripcion':''},
        {'desde':'q5','con':'M','hacia':'q6','descripcion':'Acepta ITM'},
        {'desde':'q0','con':'F','hacia':'q7','descripcion':''},
        {'desde':'q7','con':'T','hacia':'q8','descripcion':''},
        {'desde':'q8','con':'R','hacia':'q9','descripcion':'Acepta FTR'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD determinizado por subconjuntos del AFND anterior'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','qE'],
      'simbolos': ['H','D','R','I','T','M','F','otro'],
      'transiciones': {
        'q0':{'H':'q1','D':'qE','R':'qE','I':'q4','T':'qE','M':'qE','F':'q7','otro':'qE'},
        'q1':{'H':'qE','D':'q2','R':'qE','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'q2':{'H':'qE','D':'qE','R':'q3','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'q3':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'q4':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'q5','M':'qE','F':'qE','otro':'qE'},
        'q5':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'qE','M':'q6','F':'qE','otro':'qE'},
        'q6':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'q7':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'q8','M':'qE','F':'qE','otro':'qE'},
        'q8':{'H':'qE','D':'qE','R':'q9','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'q9':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
        'qE':{'H':'qE','D':'qE','R':'qE','I':'qE','T':'qE','M':'qE','F':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_segmentos_doc'
    }
  },

  'mis_codigos_orden': {
    'afnd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q10'],
      'transiciones': [
        {'desde':'q0','con':'[A-Z]','hacia':'q1','descripcion':'Letra inicial'},
        {'desde':'q1','con':'[A-Z]','hacia':'q1','descripcion':'Letras adicionales'},
        {'desde':'q1','con':'-','hacia':'q2','descripcion':'Separador'},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'Año dígito 1'},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':'Año dígito 2'},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':'Año dígito 3'},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':'Año dígito 4'},
        {'desde':'q6','con':'-','hacia':'q7','descripcion':'Separador'},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':'Secuencia dígito 1'},
        {'desde':'q8','con':'[0-9]','hacia':'q9','descripcion':'Secuencia dígito 2'},
        {'desde':'q9','con':'[0-9]','hacia':'q10','descripcion':'Acepta'},
      ],
      'descripcion': 'AFND para ^[A-Z]+-\\d{4}-\\d{3}$'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q10'],
      'transiciones': [
        {'desde':'q0','con':'[A-Z]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[A-Z]','hacia':'q1','descripcion':'loop'},
        {'desde':'q1','con':'-','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':''},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':''},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':''},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':''},
        {'desde':'q6','con':'-','hacia':'q7','descripcion':''},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':''},
        {'desde':'q8','con':'[0-9]','hacia':'q9','descripcion':''},
        {'desde':'q9','con':'[0-9]','hacia':'q10','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — ya determinista, sin ambigüedad de ramas'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','qE'],
      'simbolos': ['[A-Z]','-','[0-9]','otro'],
      'transiciones': {
        'q0':{'[A-Z]':'q1','-':'qE','[0-9]':'qE','otro':'qE'},
        'q1':{'[A-Z]':'q1','-':'q2','[0-9]':'qE','otro':'qE'},
        'q2':{'[A-Z]':'qE','-':'qE','[0-9]':'q3','otro':'qE'},
        'q3':{'[A-Z]':'qE','-':'qE','[0-9]':'q4','otro':'qE'},
        'q4':{'[A-Z]':'qE','-':'qE','[0-9]':'q5','otro':'qE'},
        'q5':{'[A-Z]':'qE','-':'qE','[0-9]':'q6','otro':'qE'},
        'q6':{'[A-Z]':'qE','-':'q7','[0-9]':'qE','otro':'qE'},
        'q7':{'[A-Z]':'qE','-':'qE','[0-9]':'q8','otro':'qE'},
        'q8':{'[A-Z]':'qE','-':'qE','[0-9]':'q9','otro':'qE'},
        'q9':{'[A-Z]':'qE','-':'qE','[0-9]':'q10','otro':'qE'},
        'q10':{'[A-Z]':'qE','-':'qE','[0-9]':'qE','otro':'qE'},
        'qE':{'[A-Z]':'qE','-':'qE','[0-9]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_codigos_orden'
    }
  },

  'mis_variables_ruc': {
    'afnd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q11'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':'Dígito 1'},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':'Dígito 2'},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'Dígito 3'},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':'Dígito 4'},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':'Dígito 5'},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':'Dígito 6'},
        {'desde':'q6','con':'[0-9]','hacia':'q7','descripcion':'Dígito 7'},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':'Dígito 8'},
        {'desde':'q8','con':'[0-9]','hacia':'q9','descripcion':'Dígito 9'},
        {'desde':'q9','con':'[0-9]','hacia':'q10','descripcion':'Dígito 10'},
        {'desde':'q10','con':'[0-9]','hacia':'q11','descripcion':'Dígito 11 — Acepta'},
      ],
      'descripcion': 'AFND para ^\\d{11}$ — cadena exacta de 11 dígitos'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q11'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':''},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':''},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':''},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':''},
        {'desde':'q6','con':'[0-9]','hacia':'q7','descripcion':''},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':''},
        {'desde':'q8','con':'[0-9]','hacia':'q9','descripcion':''},
        {'desde':'q9','con':'[0-9]','hacia':'q10','descripcion':''},
        {'desde':'q10','con':'[0-9]','hacia':'q11','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — cadena lineal, idéntico al AFND (ya determinista)'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','qE'],
      'simbolos': ['[0-9]','otro'],
      'transiciones': {
        'q0':{'[0-9]':'q1','otro':'qE'}, 'q1':{'[0-9]':'q2','otro':'qE'},
        'q2':{'[0-9]':'q3','otro':'qE'}, 'q3':{'[0-9]':'q4','otro':'qE'},
        'q4':{'[0-9]':'q5','otro':'qE'}, 'q5':{'[0-9]':'q6','otro':'qE'},
        'q6':{'[0-9]':'q7','otro':'qE'}, 'q7':{'[0-9]':'q8','otro':'qE'},
        'q8':{'[0-9]':'q9','otro':'qE'}, 'q9':{'[0-9]':'q10','otro':'qE'},
        'q10':{'[0-9]':'q11','otro':'qE'}, 'q11':{'[0-9]':'qE','otro':'qE'},
        'qE':{'[0-9]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_variables_ruc'
    }
  },

  'mis_variables_fecha': {
    'afnd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q8'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':'DD dígito 1'},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':'DD dígito 2'},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'MM dígito 1'},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':'MM dígito 2'},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':'YYYY dígito 1'},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':'YYYY dígito 2'},
        {'desde':'q6','con':'[0-9]','hacia':'q7','descripcion':'YYYY dígito 3'},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':'YYYY dígito 4 — Acepta'},
      ],
      'descripcion': 'AFND para ^\\d{8}$ — formato DDMMYYYY'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q8'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':''},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':''},
        {'desde':'q4','con':'[0-9]','hacia':'q5','descripcion':''},
        {'desde':'q5','con':'[0-9]','hacia':'q6','descripcion':''},
        {'desde':'q6','con':'[0-9]','hacia':'q7','descripcion':''},
        {'desde':'q7','con':'[0-9]','hacia':'q8','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — cadena lineal de 8 dígitos'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','q4','q5','q6','q7','q8','qE'],
      'simbolos': ['[0-9]','otro'],
      'transiciones': {
        'q0':{'[0-9]':'q1','otro':'qE'}, 'q1':{'[0-9]':'q2','otro':'qE'},
        'q2':{'[0-9]':'q3','otro':'qE'}, 'q3':{'[0-9]':'q4','otro':'qE'},
        'q4':{'[0-9]':'q5','otro':'qE'}, 'q5':{'[0-9]':'q6','otro':'qE'},
        'q6':{'[0-9]':'q7','otro':'qE'}, 'q7':{'[0-9]':'q8','otro':'qE'},
        'q8':{'[0-9]':'qE','otro':'qE'}, 'qE':{'[0-9]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_variables_fecha'
    }
  },

  'mis_motivos_traslado': {
    'afnd': {
      'estados': ['q0','qV1','qV2','qV3','qV4','qV5','qC1','qC2','qC3','qC4','qC5','qC6','qC7',
                  'qD1','qD2','qD3','qD4','qD5','qD6','qD7','qD8','qD9','qD10'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['qV5','qC7','qD10'],
      'transiciones': [
        {'desde':'q0','con':'ε','hacia':'qV1','descripcion':'Rama VENTA'},
        {'desde':'qV1','con':'V-E-N-T-A','hacia':'qV5','descripcion':'Reconoce VENTA'},
        {'desde':'q0','con':'ε','hacia':'qC1','descripcion':'Rama COMPRA'},
        {'desde':'qC1','con':'C-O-M-P-R-A','hacia':'qC7','descripcion':'Reconoce COMPRA'},
        {'desde':'q0','con':'ε','hacia':'qD1','descripcion':'Rama DEVOLUCION'},
        {'desde':'qD1','con':'D-E-V-O-L-U-C-I-O-N','hacia':'qD10','descripcion':'Reconoce DEVOLUCION'},
      ],
      'descripcion': 'AFND para ^(VENTA|COMPRA|DEVOLUCION)$ — unión de 3 palabras vía ε'
    },
    'afd': {
      'estados': ['q0','q1','q2','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q2'],
      'transiciones': [
        {'desde':'q0','con':'V/C/D','hacia':'q1','descripcion':'Primera letra'},
        {'desde':'q1','con':'resto palabra','hacia':'q2','descripcion':'Acepta palabra completa'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD simplificado — match exacto de palabra completa'
    },
    'tabla': {
      'estados': ['q0','q1','q2','qE'],
      'simbolos': ['V/C/D','resto','otro'],
      'transiciones': {
        'q0':{'V/C/D':'q1','resto':'qE','otro':'qE'},
        'q1':{'V/C/D':'qE','resto':'q2','otro':'qE'},
        'q2':{'V/C/D':'qE','resto':'qE','otro':'qE'},
        'qE':{'V/C/D':'qE','resto':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_motivos_traslado'
    }
  },

  'mis_tipos_moneda': {
    'afnd': {
      'estados': ['q0','qP1','qP2','qP3','qU1','qU2','qU3'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['qP3','qU3'],
      'transiciones': [
        {'desde':'q0','con':'ε','hacia':'qP1','descripcion':'Rama PEN'},
        {'desde':'qP1','con':'P','hacia':'qP2','descripcion':''},
        {'desde':'qP2','con':'E-N','hacia':'qP3','descripcion':'Acepta PEN'},
        {'desde':'q0','con':'ε','hacia':'qU1','descripcion':'Rama USD'},
        {'desde':'qU1','con':'U','hacia':'qU2','descripcion':''},
        {'desde':'qU2','con':'S-D','hacia':'qU3','descripcion':'Acepta USD'},
      ],
      'descripcion': 'AFND para ^(PEN|USD)$'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3'],
      'transiciones': [
        {'desde':'q0','con':'P','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'E','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'N','hacia':'q3','descripcion':'Acepta PEN'},
        {'desde':'q0','con':'U','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'S','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'D','hacia':'q3','descripcion':'Acepta USD'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD determinizado'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','qE'],
      'simbolos': ['P','E','N','U','S','D','otro'],
      'transiciones': {
        'q0':{'P':'q1','E':'qE','N':'qE','U':'q1','S':'qE','D':'qE','otro':'qE'},
        'q1':{'P':'qE','E':'q2','N':'qE','U':'qE','S':'q2','D':'qE','otro':'qE'},
        'q2':{'P':'qE','E':'qE','N':'q3','U':'qE','S':'qE','D':'q3','otro':'qE'},
        'q3':{'P':'qE','E':'qE','N':'qE','U':'qE','S':'qE','D':'qE','otro':'qE'},
        'qE':{'P':'qE','E':'qE','N':'qE','U':'qE','S':'qE','D':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_tipos_moneda'
    }
  },

  'mis_codigos_item': {
    'afnd': {
      'estados': ['q0','q1','q2','q3'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':'Dígito 1'},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':'Dígito 2'},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'Dígito 3 — Acepta'},
      ],
      'descripcion': 'AFND para ^\\d{3}$'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[0-9]','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — idéntico al AFND, sin ambigüedad'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','qE'],
      'simbolos': ['[0-9]','otro'],
      'transiciones': {
        'q0':{'[0-9]':'q1','otro':'qE'}, 'q1':{'[0-9]':'q2','otro':'qE'},
        'q2':{'[0-9]':'q3','otro':'qE'}, 'q3':{'[0-9]':'qE','otro':'qE'},
        'qE':{'[0-9]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_codigos_item'
    }
  },

  'mis_nombres_producto': {
    'afnd': {
      'estados': ['q0','q1','q2','q3'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3'],
      'transiciones': [
        {'desde':'q0','con':'[a-z]','hacia':'q1','descripcion':'Primera palabra'},
        {'desde':'q1','con':'[a-z]','hacia':'q1','descripcion':'loop letras'},
        {'desde':'q1','con':'-','hacia':'q2','descripcion':'Separador'},
        {'desde':'q2','con':'[a-z]','hacia':'q3','descripcion':'Segunda palabra'},
        {'desde':'q3','con':'[a-z]','hacia':'q3','descripcion':'loop letras — Acepta'},
      ],
      'descripcion': 'AFND para ^[a-z]+-[a-z]+$'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q3'],
      'transiciones': [
        {'desde':'q0','con':'[a-z]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[a-z]','hacia':'q1','descripcion':'loop'},
        {'desde':'q1','con':'-','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[a-z]','hacia':'q3','descripcion':''},
        {'desde':'q3','con':'[a-z]','hacia':'q3','descripcion':'loop — Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — ya determinista'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','qE'],
      'simbolos': ['[a-z]','-','otro'],
      'transiciones': {
        'q0':{'[a-z]':'q1','-':'qE','otro':'qE'},
        'q1':{'[a-z]':'q1','-':'q2','otro':'qE'},
        'q2':{'[a-z]':'q3','-':'qE','otro':'qE'},
        'q3':{'[a-z]':'q3','-':'qE','otro':'qE'},
        'qE':{'[a-z]':'qE','-':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_nombres_producto'
    }
  },

  'mis_unidades_medida': {
    'afnd': {
      'estados': ['q0','qK1','qK2','qS1','qS2','qS3','qC1','qC2','qC3','qC4','qU1','qU2','qU3','qU4'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['qK2','qS3','qC4','qU4'],
      'transiciones': [
        {'desde':'q0','con':'ε','hacia':'qK1','descripcion':'Rama KG'},
        {'desde':'qK1','con':'K-G','hacia':'qK2','descripcion':'Acepta KG'},
        {'desde':'q0','con':'ε','hacia':'qS1','descripcion':'Rama SAC'},
        {'desde':'qS1','con':'S-A-C','hacia':'qS3','descripcion':'Acepta SAC'},
        {'desde':'q0','con':'ε','hacia':'qC1','descripcion':'Rama CAJA'},
        {'desde':'qC1','con':'C-A-J-A','hacia':'qC4','descripcion':'Acepta CAJA'},
        {'desde':'q0','con':'ε','hacia':'qU1','descripcion':'Rama UNID'},
        {'desde':'qU1','con':'U-N-I-D','hacia':'qU4','descripcion':'Acepta UNID'},
      ],
      'descripcion': 'AFND para ^(KG|SAC|CAJA|UNID)$ — unión de 4 palabras'
    },
    'afd': {
      'estados': ['q0','q1','q2','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q2'],
      'transiciones': [
        {'desde':'q0','con':'K/S/C/U','hacia':'q1','descripcion':'Primera letra'},
        {'desde':'q1','con':'resto palabra','hacia':'q2','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD simplificado por palabra completa'
    },
    'tabla': {
      'estados': ['q0','q1','q2','qE'],
      'simbolos': ['K/S/C/U','resto','otro'],
      'transiciones': {
        'q0':{'K/S/C/U':'q1','resto':'qE','otro':'qE'},
        'q1':{'K/S/C/U':'qE','resto':'q2','otro':'qE'},
        'q2':{'K/S/C/U':'qE','resto':'qE','otro':'qE'},
        'qE':{'K/S/C/U':'qE','resto':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_unidades_medida'
    }
  },

  'mis_estados_orden': {
    'afnd': {
      'estados': ['q0','qP1','qP2','qO1','qO2','qA1','qA2'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['qP2','qO2','qA2'],
      'transiciones': [
        {'desde':'q0','con':'ε','hacia':'qP1','descripcion':'Rama PENDIENTE'},
        {'desde':'qP1','con':'PENDIENTE','hacia':'qP2','descripcion':'Acepta'},
        {'desde':'q0','con':'ε','hacia':'qO1','descripcion':'Rama PROCESADO'},
        {'desde':'qO1','con':'PROCESADO','hacia':'qO2','descripcion':'Acepta'},
        {'desde':'q0','con':'ε','hacia':'qA1','descripcion':'Rama ANULADO'},
        {'desde':'qA1','con':'ANULADO','hacia':'qA2','descripcion':'Acepta'},
      ],
      'descripcion': 'AFND para ^(PENDIENTE|PROCESADO|ANULADO)$'
    },
    'afd': {
      'estados': ['q0','q1','q2','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q2'],
      'transiciones': [
        {'desde':'q0','con':'P/A','hacia':'q1','descripcion':'Primera letra'},
        {'desde':'q1','con':'resto palabra','hacia':'q2','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD simplificado por palabra completa'
    },
    'tabla': {
      'estados': ['q0','q1','q2','qE'],
      'simbolos': ['P/A','resto','otro'],
      'transiciones': {
        'q0':{'P/A':'q1','resto':'qE','otro':'qE'},
        'q1':{'P/A':'qE','resto':'q2','otro':'qE'},
        'q2':{'P/A':'qE','resto':'qE','otro':'qE'},
        'qE':{'P/A':'qE','resto':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_estados_orden'
    }
  },

  'mis_variables_decimales': {
    'afnd': {
      'estados': ['q0','q1','q2','q3','q4'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q4'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':'Parte entera'},
        {'desde':'q1','con':'[0-9]','hacia':'q1','descripcion':'loop entero'},
        {'desde':'q1','con':'.','hacia':'q2','descripcion':'Punto decimal'},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':'Decimal 1'},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':'Decimal 2 — Acepta'},
      ],
      'descripcion': 'AFND para ^\\d+\\.\\d{2}$'
    },
    'afd': {
      'estados': ['q0','q1','q2','q3','q4','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q4'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[0-9]','hacia':'q1','descripcion':'loop'},
        {'desde':'q1','con':'.','hacia':'q2','descripcion':''},
        {'desde':'q2','con':'[0-9]','hacia':'q3','descripcion':''},
        {'desde':'q3','con':'[0-9]','hacia':'q4','descripcion':'Acepta'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — ya determinista'
    },
    'tabla': {
      'estados': ['q0','q1','q2','q3','q4','qE'],
      'simbolos': ['[0-9]','.','otro'],
      'transiciones': {
        'q0':{'[0-9]':'q1','.':'qE','otro':'qE'},
        'q1':{'[0-9]':'q1','.':'q2','otro':'qE'},
        'q2':{'[0-9]':'q3','.':'qE','otro':'qE'},
        'q3':{'[0-9]':'q4','.':'qE','otro':'qE'},
        'q4':{'[0-9]':'qE','.':'qE','otro':'qE'},
        'qE':{'[0-9]':'qE','.':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_variables_decimales'
    }
  },

  'mis_variables_numericas': {
    'afnd': {
      'estados': ['q0','q1'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q1'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':'Primer dígito'},
        {'desde':'q1','con':'[0-9]','hacia':'q1','descripcion':'loop — Acepta en cada paso'},
      ],
      'descripcion': 'AFND para ^\\d+$ — uno o más dígitos'
    },
    'afd': {
      'estados': ['q0','q1','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q1'],
      'transiciones': [
        {'desde':'q0','con':'[0-9]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[0-9]','hacia':'q1','descripcion':'loop'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — idéntico al AFND, ya mínimo'
    },
    'tabla': {
      'estados': ['q0','q1','qE'],
      'simbolos': ['[0-9]','otro'],
      'transiciones': {
        'q0':{'[0-9]':'q1','otro':'qE'},
        'q1':{'[0-9]':'q1','otro':'qE'},
        'qE':{'[0-9]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_variables_numericas'
    }
  },

  'mis_variables_texto': {
    'afnd': {
      'estados': ['q0','q1'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q1'],
      'transiciones': [
        {'desde':'q0','con':'[A-Za-z0-9.-]','hacia':'q1','descripcion':'Primer carácter'},
        {'desde':'q1','con':'[A-Za-z0-9.-]','hacia':'q1','descripcion':'loop — Acepta en cada paso'},
      ],
      'descripcion': 'AFND para ^[A-Za-z0-9\\-\\.]+$'
    },
    'afd': {
      'estados': ['q0','q1','qE'],
      'estado_inicial': 'q0',
      'estados_aceptacion': ['q1'],
      'transiciones': [
        {'desde':'q0','con':'[A-Za-z0-9.-]','hacia':'q1','descripcion':''},
        {'desde':'q1','con':'[A-Za-z0-9.-]','hacia':'q1','descripcion':'loop'},
        {'desde':'q0','con':'otro','hacia':'qE','descripcion':'Error'},
      ],
      'descripcion': 'AFD — idéntico al AFND, ya mínimo'
    },
    'tabla': {
      'estados': ['q0','q1','qE'],
      'simbolos': ['[A-Za-z0-9.-]','otro'],
      'transiciones': {
        'q0':{'[A-Za-z0-9.-]':'q1','otro':'qE'},
        'q1':{'[A-Za-z0-9.-]':'q1','otro':'qE'},
        'qE':{'[A-Za-z0-9.-]':'qE','otro':'qE'},
      },
      'descripcion': 'Tabla de transiciones — token mis_variables_texto'
    }
  },
}


def generar_automatas_por_token():
    return AUTOMATAS_POR_TOKEN
