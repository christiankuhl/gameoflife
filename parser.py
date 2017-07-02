import ply.lex as lex
import ply.yacc as yacc

KEYWORDS = ("run", "load", "save", "insert", "clear", "quit", "exit")
PARAMS = ("topology", "width", "height")
DOMAINS = ("'KleinBottle'", "'MoebiusBand'", "'Torus'", "'Cylinder'", "'Plane'")

class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, game_instance, **kw):
        self.names = {}
        self.game_instance = game_instance
        # Build the lexer and parser
        lex.lex(module=self)
        yacc.yacc(module=self)

    def parse(self, s):
        yacc.parse(s)

class GameParser(Parser):
    """
    This class is a parser for the game's control/config language. It is an
    adaption of David Beazleys classcalc example contained in PLY, hence an
    elementary calculator is also included :)
    """
    tokens = (
        'NAME', 'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS',
        'LPAREN', 'RPAREN', 'PARAM', 'KEY', 'STRING'
    )
    # Reserved words
    reserved = dict(((k, 'PARAM') for k in PARAMS), **{k: 'KEY' for k in KEYWORDS})
    # Tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\*\*'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_STRING = r'\'[a-zA-Z_]*\''

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = GameParser.reserved.get(t.value, 'NAME')
        return t

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS'),
    )

    def p_statement_setparam(self, p):
        "statement : PARAM expression"
        try:
            setattr(self.game_instance, p[1], p[2])
        except Exception as e:
            print(e)

    def p_statement_keyword_arg(self, p):
        "statement : KEY expression"
        try:
            getattr(self.game_instance, p[1])(p[2])
        except Exception as e:
            print(e)

    def p_statement_keyword_noarg(self, p):
        "statement : KEY"
        try:
            getattr(self.game_instance, p[1])()
        except Exception as e:
            print(e)

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.names[p[1]] = p[3]

    def p_statement_expr(self, p):
        'statement : expression'
        print(p[1])

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
        """
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_expression_string(self, p):
        'expression : STRING'
        p[0] = p[1].strip("'")

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    p = GameParser()
    p.run()
