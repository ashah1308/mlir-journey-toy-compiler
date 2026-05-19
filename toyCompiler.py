class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value
    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"

def tokenize(src):
    tokens = []
    i = 0
    while i< len(src):
        ch = src[i]
        if ch.isspace():
            i = i+1
            continue
        elif ch == "(":
            tokens.append(Token("LPAREN", "("))
        elif ch == "+":
            tokens.append(Token("PLUS", "+"))
        elif ch == "-":
            tokens.append(Token("MINUS", "-"))
        elif ch == "*":
            tokens.append(Token("MUL", "*"))
        elif ch == ")":
            tokens.append(Token("RPAREN", ")"))
        elif ch.isdigit():
            start = i
            while(i< len(src) and src[i].isdigit()):
                i+=1
            value = int(src[start:i])
            tokens.append(Token("NUMBER", value))
            continue
        elif ch.isalpha() or ch == '_':
            start = i
            while(i < len(src) and (src[i].isalpha() or src[i].isdigit())):
                i+=1
            ident = src[start:i]
            tokens.append(Token("IDENT",ident))
            continue
        else:
            raise SyntaxError(f"Unexpected character: {ch}")
        i = i + 1
    tokens.append(Token("EOF", None))
    return tokens

class Num:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Num({self.value})"

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Var('{self.name}')"
    
class BinOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def __repr__(self):
        return f"BinOp({self.op, self.left, self.right})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self):
        curr_token = self.tokens[self.pos]
        self.pos += 1
        return curr_token
    
    def parse_expr(self):
        left = self.parse_term()
        while self.peek().kind in ("PLUS", "MINUS"):
            op = self.consume().value
            right = self.parse_term()
            left = BinOp(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek().kind == "MUL":
            op = self.consume().value
            right = self.parse_factor()
            left = BinOp(op, left, right)
        return left


    def parse_factor(self):
        curr_token = self.peek()
        if curr_token.kind == "NUMBER":
            return Num(self.consume().value)
        elif curr_token.kind == "IDENT":
            return Var(self.consume().value)
        elif curr_token.kind == "LPAREN":
            self.consume()
            inner = self.parse_expr()
            if self.peek().kind != "RPAREN":
                raise SyntaxError(f"Expected ')' got {self.peek().kind}")
            self.consume()
            return inner

def parse(tokens):
    p = Parser(tokens)
    return p.parse_expr()

def ast_to_str(node):
    if isinstance(node, Num):
        return str(node.value)
    elif isinstance(node, Var):
        return node.name
    elif isinstance(node, BinOp):
        return f"({ast_to_str(node.left)} {node.op} {ast_to_str(node.right)})"          

test_cases = [
    "42",                       # Num(42)
    "a",                        # Var('a')
    "a + b",                    # (a + b)
    "a + b + c",                # ((a + b) + c)         ← left-associative
    "a + b * c",                # (a + (b * c))         ← * tighter than +
    "(a + b) * c",              # ((a + b) * c)         ← parens override
    "a * b + c",                # ((a * b) + c)         ← * tighter than +
    "(a + b) * (c - d)",        # ((a + b) * (c - d))
    "((a))",                    # a                     ← nested parens
]

# for src in test_cases:
#     tokens = tokenize(src)
#     ast = parse(tokens)
#     print(f"{src!r}  →  {ast_to_str(ast)}")

op_to_instr = {"+": "ADD", "-": "SUB", "*": "MUL"}

class CodeGen:
    def __init__(self):
        self.next_reg = 0
        self.instructions = []
    def fresh_reg(self):
        reg = f"r{self.next_reg}"
        self.next_reg += 1
        return reg
    def emit(self, inst_str):
        self.instructions.append(inst_str)
    def gen(self, node):
        if isinstance(node, Num):
            new_reg = self.fresh_reg()
            inst = f"LOAD {new_reg}, {node.value}"
            self.emit(inst)
            return new_reg  
        elif isinstance(node, Var):
            new_reg = self.fresh_reg()
            inst = f"LOAD {new_reg}, {node.name} "
            self.emit(inst)
            return new_reg  
        elif isinstance(node, BinOp):
            left = self.gen(node.left)
            right = self.gen(node.right)
            new_reg = self.fresh_reg()
            inst = f"{op_to_instr[node.op]}  {new_reg}, {left}, {right}"
            self.emit(inst)
            return new_reg

def compile(src):
    tokens = tokenize(src)
    ast = parse(tokens)
    gen = CodeGen()
    gen.gen(ast)
    return gen.instructions

if __name__ == "__main__":
    test_cases = [
        "42",
        "a",
        "a + b",
        "a + b * c",
        "(a + b) * c",
        "a + b + c",
        "(a + b) * (c - d)",
        "1 + 2 * 3 - 4",
    ]

    for src in test_cases:
        print(f"=== {src} ===")
        for instr in compile(src):
            print(f"  {instr}")
        print()