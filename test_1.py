from Compiler import tokenize, code1, fixed_tokens, variable_tokens
from Compiler import LR1Parser, Gram
from Compiler.visitor import *
import pickle

# print(code3)
tokens = tokenize(
r"""

definition

def dos_filas(){
    int temp  = G.len() // 2
    int resto = G.len() % 2
    int i = 0
    while(i < temp + resto){
        if(i < temp - 1){
            G[temp + 1] down of G[i]
        }
        if( i > 0)
        {
            G[temp + i - 1] left of G[temp + 1]
        }
    }
}

def dos_columnas()
{
    group prim = from G take G.len()//2 starting_at 0
    all_of prim at down of prev
    all_of G at down of prev
    prim[0] left of G[0]
}

begin_with 5
    line_up dos_filas with [1,2,3] in (0,0) heading up args()
    line_up dos_columnas with [4,5] in (2,0) heading up_left args()
step
    line_up dos_columnas with [1,2,3] in (0,0) heading up args()
    line_up dos_filas with [4,5] in (0,2) heading up args()
end

""", fixed_tokens, variable_tokens)

with open(".\\actions", "rb") as file:
    action = pickle.load(file)
with open(".\\goto", "rb") as file:
    goto = pickle.load(file)
parser = LR1Parser(Gram, action, goto, True)
# parser = LR1Parser(Gram, True)

# with open(".\\actions", "wb") as file:
#     pickle.dump(parser.action, file)
# with open(".\\goto", "wb") as file:
#     pickle.dump(parser.goto, file)

deriv, ast = parser(tokens)

_scope = ScopeCheckerVisitor()
_semantic = SemanticCheckerVisitor()
_type = TypeCheckerVisitor()

context = ProgramContext()
scope_err = _scope.visit(ast, context, 0)
semantic_err = _semantic.visit(ast, context, 0)
type_err = _type.visit(ast, context, 0)
print("OK")