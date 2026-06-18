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

    return {'afnd': afnd, 'afd': afd, 'tabla': tabla}
