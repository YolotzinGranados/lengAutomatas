import re  # Importamos el módulo 're' para trabajar con expresiones regulares

# Lista de tuplas que define los tipos de tokens y sus respectivas expresiones regulares
TOKENS = [
    ('PALABRA_CLAVE', r'\b(ent|dec|txt|vf|Si|SiNo|Para|Realiza|Mientras)\b'),
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

# Compilamos el regex
token_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKENS)
lexer_re = re.compile(token_regex)

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

def ingresar_codigo():
    print("=== Analizador Léxico Interactivo ===")
    print("Ingrese el código a analizar (presione Enter dos veces para finalizar):")
    print("Ejemplo:")
    print("ent x es 10.\nSi x MayK 5 Realiza {\n    suma x 1.\n}.")

    codigo = []
    while True:
        linea = input()
        if linea == "":
            if len(codigo) > 0 and codigo[-1] == "":
                break
        codigo.append(linea)

    return '\n'.join(codigo)
# Mantén la parte del lexer y del ingreso de código igual que en tu mensaje anterior

# ======================
# Clase Parser mejorada
# ======================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    def ver_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None, None)

    def coincidir(self, tipo):
        actual = self.ver_token()
        if actual[0] == tipo:
            self.pos += 1
            return True
        return False

    def parse(self):
        while self.ver_token()[0] is not None:
            if not self.instruccion():
                self.error("Se esperaba una instrucción válida")
                self.avanzar_hasta_punto()
            elif not self.coincidir("PUNTO_FINAL"):
                self.error("Falta punto final '.' al final de la instrucción")
                self.avanzar_hasta_punto()

    def instruccion(self):
        token = self.ver_token()
        if token[0] == 'PALABRA_CLAVE':
            if token[1] in ['ent', 'dec', 'txt', 'vf']:
                return self.declaracion()
            elif token[1] == 'Si':
                return self.condicional()
            elif token[1] in ['Mientras', 'Para']:
                return self.bucle()
        elif token[0] == 'IDENTIFICADOR':
            return self.asignacion()
        return False

    def declaracion(self):
        if self.coincidir('PALABRA_CLAVE'):
            if self.coincidir('IDENTIFICADOR'):
                return True
            else:
                self.error("Se esperaba un identificador después de la palabra clave")
        return False

    def asignacion(self):
        if self.coincidir('IDENTIFICADOR'):
            if self.coincidir('OPERADOR_ASIGNACION'):
                if self.expresion():
                    return True
                else:
                    self.error("Expresión inválida en la asignación")
        return False

    def expresion(self):
        if not self.valor():
            return False
        while self.ver_token()[0] in ['OPERADOR_SUMA', 'OPERADOR_RESTA', 'OPERADOR_MULTIPLICACION', 'OPERADOR_DIVISION']:
            self.coincidir(self.ver_token()[0])
            if not self.valor():
                return False
        return True

    def valor(self):
        return self.coincidir('IDENTIFICADOR') or self.coincidir('NUMERO_ENTERO') or self.coincidir('NUMERO_DECIMAL')

    def condicional(self):
        if self.ver_token()[1] == 'Si':
            self.coincidir('PALABRA_CLAVE')  # 'Si'
            if not self.condicion():
                self.error("Condición inválida en 'Si'")
                return False
            if self.ver_token()[1] != 'Realiza':
                self.error("Se esperaba 'Realiza' en 'Si'")
                return False
            self.coincidir('PALABRA_CLAVE')  # 'Realiza'
            if not self.coincidir('LLAVE_ABRE'):
                self.error("Se esperaba '{' después de 'Realiza'")
                return False
            while self.ver_token()[0] != 'LLAVE_CIERRA' and self.ver_token()[0] is not None:
                if not self.instruccion():
                    self.error("Instrucción inválida dentro del bloque 'Si'")
                    self.avanzar_hasta_punto()
                elif not self.coincidir('PUNTO_FINAL'):
                    self.error("Falta punto final dentro del bloque 'Si'")
                    self.avanzar_hasta_punto()
            if not self.coincidir('LLAVE_CIERRA'):
                self.error("Falta '}' al final del bloque 'Si'")
                return False

            # Soporte para SiNo
            if self.ver_token()[1] == 'SiNo':
                self.coincidir('PALABRA_CLAVE')  # 'SiNo'
                if not self.coincidir('LLAVE_ABRE'):
                    self.error("Se esperaba '{' después de 'SiNo'")
                    return False
                while self.ver_token()[0] != 'LLAVE_CIERRA' and self.ver_token()[0] is not None:
                    if not self.instruccion():
                        self.error("Instrucción inválida dentro del bloque 'SiNo'")
                        self.avanzar_hasta_punto()
                    elif not self.coincidir('PUNTO_FINAL'):
                        self.error("Falta punto final dentro del bloque 'SiNo'")
                        self.avanzar_hasta_punto()
                if not self.coincidir('LLAVE_CIERRA'):
                    self.error("Falta '}' al final del bloque 'SiNo'")
                    return False
            return True
        return False

    def bucle(self):
        if self.ver_token()[1] in ['Mientras', 'Para']:
            self.coincidir('PALABRA_CLAVE')
            if not self.condicion():
                self.error("Condición inválida en bucle")
                return False
            if self.ver_token()[1] != 'Realiza':
                self.error("Se esperaba 'Realiza' en el bucle")
                return False
            self.coincidir('PALABRA_CLAVE')
            if not self.coincidir('LLAVE_ABRE'):
                self.error("Se esperaba '{' después de 'Realiza'")
                return False
            while self.ver_token()[0] != 'LLAVE_CIERRA' and self.ver_token()[0] is not None:
                if not self.instruccion():
                    self.error("Instrucción inválida dentro del bucle")
                    self.avanzar_hasta_punto()
                elif not self.coincidir('PUNTO_FINAL'):
                    self.error("Falta punto final dentro del bucle")
                    self.avanzar_hasta_punto()
            if not self.coincidir('LLAVE_CIERRA'):
                self.error("Falta '}' al final del bucle")
                return False
            return True
        return False

    def condicion(self):
        if not self.expresion():
            return False
        if not self.coincidir('OPERADOR_COMPARACION'):
            return False
        if not self.expresion():
            return False
        return True

    def error(self, mensaje):
        tipo, valor, linea = self.ver_token()
        self.errores.append(f"Error de sintaxis en línea {linea}: {mensaje}. Token problemático: '{valor}'")
        self.pos += 1  # Avanza para evitar bucle infinito

    def avanzar_hasta_punto(self):
        while self.ver_token()[0] not in ['PUNTO_FINAL', None, 'LLAVE_CIERRA']:
            self.pos += 1
        if self.ver_token()[0] == 'PUNTO_FINAL':
            self.pos += 1

