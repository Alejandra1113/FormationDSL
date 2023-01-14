import pickle
from Compiler.Tokenizer import tokenize, fixed_tokens, variable_tokens
from Compiler.visitor.code_gen import python_tamplate
from Compiler.Parser import LR1Parser
from Compiler.Grammar import Gram
from Compiler.visitor import *

_gen = CodeGenVisitor(*python_tamplate)
_semantic = SemanticCheckerVisitor()
_scope = ScopeCheckerVisitor()
_type = TypeCheckerVisitor()
_print = PrintVisitor()
_cil = CilVisitor()

code_path = ".\\code.txt"
with open(code_path, "r") as file:
    text = file.read()

tokens = tokenize(text, fixed_tokens, variable_tokens)
with open(".\\actions", "rb") as file:
    action = pickle.load(file)
with open(".\\goto", "rb") as file:
    goto = pickle.load(file)
parser = LR1Parser(Gram, action, goto, True)
deriv, ast = parser(tokens)

context = ProgramContext()
scope_err = _scope.visit(ast, context)
err = False
if len(scope_err):
    {print(err) for err in scope_err}
    err = True

semantic_err = _semantic.visit(ast, context)
if len(semantic_err):
    {print(err) for err in semantic_err}
    err = True

type_err = _type.visit(ast, context)
if len(type_err):
    {print(err) for err in type_err}
    err = True

if err:
    exit()

ast_cil = _cil.visit(ast)
code = _gen.visit(ast_cil)

gen_path = ".\\code_gen.py"
with open(gen_path, "w") as file:
    text = file.write(code)
exec(code)