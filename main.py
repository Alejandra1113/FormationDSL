import pickle
from Compiler.Tokenizer import tokenize, fixed_tokens, variable_tokens
from Compiler.Parser import LR1Parser
from Compiler.Grammar import Gram
from Compiler.visitor import *

_scope = ScopeCheckerVisitor()
_semantic = SemanticCheckerVisitor()
_type = TypeCheckerVisitor()
_cil = CilVisitor()
_print = PrintVisitor()

path = ".\\code.txt"
with open(path, "r") as file:
    text = file.read()

tokens = tokenize(text, fixed_tokens, variable_tokens)
with open(".\\actions", "rb") as file:
    action = pickle.load(file)
with open(".\\goto", "rb") as file:
    goto = pickle.load(file)
parser = LR1Parser(Gram, action, goto, True)
deriv, ast = parser(tokens)

context = ProgramContext()
scope_err = _scope.visit(ast, context, 0)
err = False
if len(scope_err):
    {print(err) for err in scope_err}
    err = True

semantic_err = _semantic.visit(ast, context, 0)
if len(semantic_err):
    {print(err) for err in semantic_err}
    err = True

type_err = _type.visit(ast, context, 0)
if len(type_err):
    {print(err) for err in type_err}
    err = True

if err:
    exit()

ast_cil = _cil.visit(ast)
print(_print.visit(ast_cil))
print("OK")