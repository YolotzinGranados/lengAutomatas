import re

# -----------------------------------------
# Definición de los tokens y expresiones regulares
# -----------------------------------------
TOKENS = [
    ('PALABRA_CLAVE', r'\b(ent|dec|txt|vf|Si|SiNo|Para|Realiza|Mientras)\b'),
    ('RETORNAR', r'\bretorna\b'),
    ('OPERADOR_SUMA', r'\bsuma\b'),
    ('OPERADOR_RESTA', r'\bresta\b'),
    ('OPERADOR_MULTIPLICACION', r'\bmulti\b'),
    ('OPERADOR_DIVISION', r'\bdivision\b'),
    ('OPERADOR_ASIGNACION', r'\b(igual|es)\b'),
    ('OPERADOR_LOGICO', r'\b(y|o)\b'),
    ('OPERADOR_COMPARACION', r'\b(MayK|MenK|MayIg|MenIg|DifA)\b'),
    ('PARENTESIS_ABRE', r'\('),
    ('PARENTESIS_CIERRA', r'\)'),
    ('LLAVE_ABRE', r'\{'),
    ('LLAVE_CIERRA', r'\}'),
    ('PUNTO_FINAL', r'\.'),
    ('COMENTARIO', r'\$.*'),
    ('NUMERO_DECIMAL', r'-?\d+\.\d+'),
    ('NUMERO_ENTERO', r'-?\d+'),
    ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('ESPACIO', r'\s+'),
]

token_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKENS)
lexer_re = re.compile(token_regex)

# -----------------------------------------
# Función: Analizador Léxico
# -----------------------------------------
def analizador_lexico(codigo):
    tokens = []
    pos = 0
    linea_actual = 1
    errores = []

    while pos < len(codigo):
        match = lexer_re.match(codigo, pos)
        if match:
            tipo = match.lastgroup
            valor = match.group(tipo)

            if tipo in ['ESPACIO', 'COMENTARIO']:
                linea_actual += valor.count('\n')
                pos = match.end()
                continue

            if tipo == 'OPERADOR_ASIGNACION' and valor == 'es':
                if (pos > 0 and re.match(r'[a-zA-Z0-9_]', codigo[pos-1])) or \
                   (match.end() < len(codigo) and re.match(r'[a-zA-Z0-9_]', codigo[match.end()])):
                    tipo = 'IDENTIFICADOR'

            tokens.append((tipo, valor, linea_actual))
            linea_actual += valor.count('\n')
            pos = match.end()
        else:
            inicio_error = pos
            while pos < len(codigo) and not lexer_re.match(codigo, pos):
                pos += 1
            error = codigo[inicio_error:pos]
            errores.append(f"Error léxico en línea {linea_actual}: Símbolo desconocido '{error}'")
            linea_actual += error.count('\n')

    return tokens, errores

# -----------------------------------------
# Función: Analizador Sintáctico
# -----------------------------------------
def analizador_sintactico(tokens):
    errores = []
    i = 0
    n = len(tokens)

    def esperar(tipos):
        nonlocal i
        if i < n and tokens[i][0] in tipos:
            i += 1
            return True
        return False

    while i < n:
        tipo, valor, linea = tokens[i]

        # Declaración con o sin operación
        if tipo == 'PALABRA_CLAVE' and valor in ['ent', 'dec', 'txt', 'vf']:
            i += 1
            if esperar(['IDENTIFICADOR']) and esperar(['OPERADOR_ASIGNACION']):
                # Caso: ent x es suma a b.
                if i < n and tokens[i][0] == 'IDENTIFICADOR' and tokens[i][1] in ['suma', 'resta', 'multi', 'division']:
                    i += 1
                    if esperar(['IDENTIFICADOR', 'NUMERO_ENTERO', 'NUMERO_DECIMAL']) and esperar(['IDENTIFICADOR', 'NUMERO_ENTERO', 'NUMERO_DECIMAL']) and esperar(['PUNTO_FINAL']):
                        continue
                    else:
                        errores.append(f"Error sintáctico en línea {linea}: Expresión de operación mal formada.")
                        while i < n and tokens[i][0] != 'PUNTO_FINAL':
                            i += 1
                        i += 1
                        continue
                elif esperar(['NUMERO_ENTERO', 'NUMERO_DECIMAL', 'IDENTIFICADOR']) and esperar(['PUNTO_FINAL']):
                    continue
                else:
                    errores.append(f"Error sintáctico en línea {linea}: Asignación mal formada.")
                    while i < n and tokens[i][0] != 'PUNTO_FINAL':
                        i += 1
                    i += 1
                    continue
            else:
                errores.append(f"Error sintáctico en línea {linea}: Declaración mal formada.")
                while i < n and tokens[i][0] != 'PUNTO_FINAL':
                    i += 1
                i += 1

        # Instrucción retorna
        elif tipo == 'RETORNAR':
            i += 1
            if esperar(['IDENTIFICADOR', 'NUMERO_ENTERO', 'NUMERO_DECIMAL']) and esperar(['PUNTO_FINAL']):
                continue
            else:
                errores.append(f"Error sintáctico en línea {linea}: Expresión inválida en 'retorna'.")
                while i < n and tokens[i][0] != 'PUNTO_FINAL':
                    i += 1
                i += 1

        # Otras instrucciones (Si, Mientras...) pueden ir aquí
        else:
            errores.append(f"Error sintáctico en línea {linea}: Instrucción desconocida o incompleta.")
            while i < n and tokens[i][0] != 'PUNTO_FINAL':
                i += 1
            i += 1

    return errores
# -----------------------------------------
# Función: Ejecutor / Intérprete
# -----------------------------------------
def ejecutar(tokens):
    memoria = {}
    i = 0
    n = len(tokens)

    def obtener_valor(t):
        if t[0] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL']:
            return float(t[1]) if '.' in t[1] else int(t[1])
        return memoria.get(t[1], 0)

    while i < n:
        tipo, valor, _ = tokens[i]

        if tipo == 'PALABRA_CLAVE' and valor in ['ent', 'dec', 'txt', 'vf']:
            tipo_var = valor
            nombre = tokens[i+1][1]
            memoria[nombre] = 0 if tipo_var in ['ent', 'dec'] else ""
            i += 4
            continue

        if tipo == 'IDENTIFICADOR' and tokens[i+1][0] == 'OPERADOR_ASIGNACION':
            nombre = valor
            if tokens[i+2][0] == 'IDENTIFICADOR':
                op = tokens[i+2][1]
                if op in ['suma', 'resta', 'multi', 'division']:
                    arg1 = obtener_valor(tokens[i+3])
                    arg2 = obtener_valor(tokens[i+4])
                    if op == 'suma':
                        memoria[nombre] = arg1 + arg2
                    elif op == 'resta':
                        memoria[nombre] = arg1 - arg2
                    elif op == 'multi':
                        memoria[nombre] = arg1 * arg2
                    elif op == 'division':
                        memoria[nombre] = arg1 / arg2 if arg2 != 0 else 0
                    i += 6
                    continue
            memoria[nombre] = obtener_valor(tokens[i+2])
            i += 4
            continue

        if tipo == 'RETORNAR':
            valor_retorno = obtener_valor(tokens[i+1])
            return {'__retorno__': valor_retorno, **memoria}

        if tipo == 'PALABRA_CLAVE' and valor == 'Si':
            cond = (obtener_valor(tokens[i+1]), tokens[i+2][1], obtener_valor(tokens[i+3]))
            oper = tokens[i+2][1]
            comparar = {
                'MayK': lambda a, b: a > b,
                'MenK': lambda a, b: a < b,
                'MayIg': lambda a, b: a >= b,
                'MenIg': lambda a, b: a <= b,
                'DifA': lambda a, b: a != b
            }
            i += 5
            bloque_si = []
            while tokens[i][0] != 'LLAVE_CIERRA':
                bloque_si.append(tokens[i])
                i += 1
            i += 1
            tiene_sino = tokens[i][1] == 'SiNo' if i < n else False
            bloque_sino = []
            if tiene_sino:
                i += 2
                while tokens[i][0] != 'LLAVE_CIERRA':
                    bloque_sino.append(tokens[i])
                    i += 1
                i += 2
            else:
                i += 1

            if comparar[oper](cond[0], cond[2]):
                resultado = ejecutar(bloque_si)
            elif tiene_sino:
                resultado = ejecutar(bloque_sino)
            else:
                resultado = None

            if resultado and '__retorno__' in resultado:
                return resultado
            continue

        if tipo == 'PALABRA_CLAVE' and valor == 'Mientras':
            var_izq = tokens[i+1]
            operador = tokens[i+2][1]
            var_der = tokens[i+3]
            i += 5
            cuerpo = []
            while tokens[i][0] != 'LLAVE_CIERRA':
                cuerpo.append(tokens[i])
                i += 1
            i += 2
            comparar = {
                'MayK': lambda a, b: a > b,
                'MenK': lambda a, b: a < b,
                'MayIg': lambda a, b: a >= b,
                'MenIg': lambda a, b: a <= b,
                'DifA': lambda a, b: a != b
            }
            while comparar[operador](obtener_valor(var_izq), obtener_valor(var_der)):
                resultado = ejecutar(cuerpo)
                if resultado and '__retorno__' in resultado:
                    return resultado
            continue

        i += 1

    return memoria

# -----------------------------------------
# Función: Ingreso de código
# -----------------------------------------
def ingresar_codigo():
    print("=== Analizador Léxico y Sintáctico Interactivo ===")
    print("Ingrese el código a analizar (presione Enter dos veces para finalizar):")
    codigo = []
    while True:
        linea = input()
        if linea == "" and len(codigo) > 0 and codigo[-1] == "":
            break
        codigo.append(linea)
    return '\n'.join(codigo)

# -----------------------------------------
# Programa principal
# -----------------------------------------
if __name__ == "__main__":
    codigo_usuario = ingresar_codigo()
    tokens, errores_lexicos = analizador_lexico(codigo_usuario)

    print("\n=== Resultado del análisis léxico ===")
    for token in tokens:
        print(f"Línea {token[2]}: {token[0]:<25} -> '{token[1]}'")

    if errores_lexicos:
        print("\nErrores léxicos encontrados:")
        for error in errores_lexicos:
            print(error)
    else:
        print("\nNo se encontraron errores léxicos.")
        errores_sintacticos = analizador_sintactico(tokens)
        print("\n=== Resultado del análisis sintáctico ===")
        if errores_sintacticos:
            for error in errores_sintacticos:
                print(error)
        else:
            print("No se encontraron errores sintácticos.")
            print("\n=== Resultado de la ejecución ===")
            memoria = ejecutar(tokens)
            if '__retorno__' in memoria:
                print(f"\nValor retornado: {memoria['__retorno__']}")
            for var, val in memoria.items():
                if var != '__retorno__':
                    print(f"{var} = {val}")
    print("\n=== Fin del análisis ===")
