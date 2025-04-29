import re  # Importamos el módulo 're' para trabajar con expresiones regulares


# Lista de tuplas que define los tipos de tokens y sus respectivas expresiones regulares
TOKENS = [
    # Palabras clave del lenguaje
    ('PALABRA_CLAVE', r'\b(ent|dec|txt|vf|Si|SiNo|Para|Realiza|Mientras)\b'),
    
    # Operadores aritméticos representados con palabras clave
    ('OPERADOR_SUMA', r'\bsuma\b'),
    ('OPERADOR_RESTA', r'\bresta\b'),
    ('OPERADOR_MULTIPLICACION', r'\bmulti\b'),
    ('OPERADOR_DIVISION', r'\bdivision\b'),
    
    # Operadores lógicos y de comparación
    ('OPERADOR_ASIGNACION', r'\b(igual|es)\b'),
    ('OPERADOR_LOGICO', r'\b(y|o)\b'),
    ('OPERADOR_COMPARACION', r'\b(MayK|MenK|MayIg|MenIg|DifA)\b'),
    
    # Caracteres especiales usados en la sintaxis del lenguaje
    ('PARENTESIS_ABRE', r'\('),
    ('PARENTESIS_CIERRA', r'\)'),
    ('LLAVE_ABRE', r'\{'),
    ('LLAVE_CIERRA', r'\}'),
    ('PUNTO_FINAL', r'\.'),
    ('COMENTARIO', r'\$.*'),  # Línea de comentario: todo lo que empieza con '$' hasta el final
    
    # Números: tanto decimales como enteros, incluyendo negativos
    ('NUMERO_DECIMAL', r'-?\d+\.\d+'),
    ('NUMERO_ENTERO', r'-?\d+'),
    
    # Identificadores: nombres de variables válidos
    ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    
    # Espacios en blanco: serán ignorados en el análisis
    ('ESPACIO', r'\s+'),
]

# Se compila una expresión regular general a partir de todos los patrones anteriores
token_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKENS)
lexer_re = re.compile(token_regex)

# Función principal que realiza el análisis léxico del código fuente
def analizador_lexico(codigo):
    tokens = []           # Lista donde se almacenarán los tokens reconocidos
    pos = 0               # Posición actual en el texto
    linea_actual = 1      # Línea actual del análisis
    errores = []          # Lista para almacenar mensajes de error léxico
    
    # Se procesa el código mientras haya texto que analizar
    while pos < len(codigo):
        match = lexer_re.match(codigo, pos)  # Intentar encontrar un token desde la posición actual
        if match:
            tipo = match.lastgroup          # Tipo de token encontrado (según el nombre de grupo)
            valor = match.group(tipo)       # Valor exacto que coincide
            
            # Se ignoran espacios en blanco y comentarios
            if tipo in ['ESPACIO', 'COMENTARIO']:
                linea_actual += valor.count('\n')  # Actualiza línea si hay saltos
                pos = match.end()                  # Avanza la posición
                continue
            
            # Caso especial: asegurarse que 'es' no sea parte de un identificador
            if tipo == 'OPERADOR_ASIGNACION' and valor == 'es':
                if (pos > 0 and re.match(r'[a-zA-Z0-9_]', codigo[pos-1])) or \
                   (match.end() < len(codigo) and re.match(r'[a-zA-Z0-9_]', codigo[match.end()])):
                    tipo = 'IDENTIFICADOR'  # Tratar como identificador si está dentro de otro texto
            
            # Se añade el token a la lista, con su tipo, valor y línea correspondiente
            tokens.append((tipo, valor, linea_actual))
            
            linea_actual += valor.count('\n')  # Actualiza la línea si el token incluye saltos
            pos = match.end()                  # Avanza la posición
        else:
            # Si no se encuentra ningún token válido, se considera error léxico
            inicio_error = pos
            while pos < len(codigo) and not lexer_re.match(codigo, pos):
                pos += 1
            error = codigo[inicio_error:pos]  # Extrae el texto no reconocido
            errores.append(f"Error léxico en línea {linea_actual}: Símbolo desconocido '{error}'")
            linea_actual += error.count('\n')  # Actualiza la línea si hay saltos
    
    return tokens, errores  # Retorna las listas de tokens y errores encontrados

# Función para permitir al usuario ingresar el código a analizar desde la consola
def ingresar_codigo():
    print("=== Analizador Léxico Interactivo ===")
    print("Ingrese el código a analizar (presione Enter dos veces para finalizar):")
    print("Ejemplo de entrada válida:")
    print("ent x es 10.")
    print("Si x MayK 5 Realiza { suma x 1. }.")
    
    codigo = []
    while True:
        linea = input()
        # Detecta doble Enter para finalizar la entrada
        if linea == "":
            if len(codigo) > 0 and codigo[-1] == "":
                break
        codigo.append(linea)
    
    return '\n'.join(codigo)  # Une las líneas ingresadas como un solo bloque de texto

# Punto de entrada principal del programa
if __name__ == "__main__":
    codigo_usuario = ingresar_codigo()  # Se solicita el código al usuario
    tokens, errores = analizador_lexico(codigo_usuario)  # Se analizan los tokens y errores
    
    print("\n=== Resultado del análisis léxico ===")
    print(f"\nTokens reconocidos ({len(tokens)}):")
    for token in tokens:
        print(f"Línea {token[2]}: {token[0]:<25} -> '{token[1]}'")  # Muestra tipo y valor del token
    
    if errores:
        print(f"\nErrores encontrados ({len(errores)}):")
        for error in errores:
            print(error)  # Muestra errores léxicos encontrados
    else:
        print("\nNo se encontraron errores léxicos.")
    
    print("\n=== Fin del análisis ===")