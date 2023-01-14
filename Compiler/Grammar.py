from Compiler.semantic.types import *
from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon
from Compiler.semantic.language import *

Gram = Grammar()
comma, plus, minus, star, div, opar, cpar, lt, gt, lte = Gram.Terminals(', + - * / ( ) < > <=')
gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra, two_points = Gram.Terminals('>= == & | ! . { } :')
rem, wloop, deff, condif, condelse, iter_aof, groups, obra, cbra = Gram.Terminals('% while def if else all_of groups [ ]')
at, of, from_op, borrow, st_at, to, lineup, step, heading = Gram.Terminals('at of from borrow st_at to lineup step heading')
args, take, with_op, definition, begin_with, end, assign, in_op = Gram.Terminals('args take with definition begin_with end = in')
num, Id, bool_value, type_id, rpos, direc = Gram.Terminals('num Id bool_value type_id rpos direc')
return_term, continue_term, break_term = Gram.Terminals('return continue break')
eof = Gram.EOF


D, P, P1, B, A, AS, BE, ELSE, R, RN, ARG, G, I, I2, C, E, T, F, V, ARR, ARR1, BRK, ARG1 = Gram.NonTerminals('D P P1 B A AS BE ELSE R RN ARG G I I2 C E T F V ARR ARR1 BRK ARG1')


S = Gram.NonTerminal('S', True)

# S %= definition + D + groups + G + begin_with + num + R + end, lambda h, s: ProgramNode(s[2], BeginWithNode(s[6], s[7][2]))
S %= definition + D + begin_with + num + R + end, lambda h, s: ProgramNode(DefinitionsNode(s[2]), BeginWithNode(s[4], [StepNode(s[5][0])] +  s[5][1]))

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D, lambda h, s: [FuncDeclarationNode(s[2], [ParamNode("G", "group")] + s[4], s[7])] + s[9]
D %= Gram.Epsilon, lambda h, s: []

P %= type_id + Id + P1, lambda h, s: [ParamNode(s[2], s[1])] + s[3]
P %= type_id + obra + cbra + Id + P1, lambda h, s: [ParamArrayNode(s[4], s[1])] + s[5]
P %= Gram.Epsilon, lambda h, s: []

P1 %= comma + type_id + Id + P1, lambda h, s: [ParamNode(s[3], s[2])] + s[4]
P1 %= comma + type_id + obra + cbra + Id + P1, lambda h, s: [ParamNode(s[2], s[1])] + s[3]
P1 %= Gram.Epsilon, lambda h, s: []

B %= A + B, lambda h, s: [s[1]] + s[2]
B %= wloop + opar + BE + cpar + ocbra + B + BRK + ccbra + B, lambda h, s: [LoopNode(s[3], s[6] + s[7])] + s[9]
B %= condif + opar + BE + cpar + ocbra + B + BRK + ccbra + ELSE + B, lambda h, s: [ConditionNode(s[3], s[6] + s[7])] + s[9] + s[10]
B %= iter_aof + Id + at + BE + of + rpos + B, lambda h, s: [IterNode(VariableNode(s[2]), s[4], s[6])] + s[7]
B %= from_op + Id + borrow + BE + st_at + BE + to + Id + B, lambda h, s: [BorrowNode(VariableNode(s[2]), VariableNode(s[8]), s[4], s[5])] + s[9]
B %= Id + obra + E + cbra + BE + of + Id + obra + E + cbra + B, lambda h, s: [LinkNode(GetIndexNode(
        VariableNode(s[1]), s[3]), GetIndexNode(VariableNode(s[7]), s[9]), s[5])] + s[11]
B %= Id + opar + ARG + cpar + B, lambda h, s: [CallNode(s[1], s[3])] + s[5]
B %= Id + dot + Id + opar + ARG + cpar + B, lambda h, s: [DynamicCallNode(s[3], VariableNode(s[1]), s[5])] + s[6]
B %= Gram.Epsilon, lambda h, s: []
B %= return_term, lambda h,s: [SpecialNode(s[1])] 


# BRK %= B + BRK, lambda h,s: s[1] + s[2] 
BRK %= break_term, lambda h,s: [SpecialNode(s[1])] 
BRK %= continue_term, lambda h,s: [SpecialNode(s[1])]  
BRK %= Gram.Epsilon, lambda h,s: [] 



ELSE %= condelse + ocbra + B + BRK + ccbra, lambda h,s: [ConditionNode(None, s[3] + s[4])]
ELSE %= Gram.Epsilon, lambda h,s: []

A %= type_id + Id + assign + AS, lambda h, s: VarDeclarationNode(s[2], s[1], s[4])
A %= type_id + obra + cbra + Id + assign + AS, lambda h, s: ArrayDeclarationNode(s[1], s[4], s[6])
A %= Id + obra + E + cbra + assign + AS, lambda h, s: SetIndexNode(s[1], s[3], s[6])
A %= Id + assign + AS, lambda h, s: AssignNode(s[1], s[3])
A %= type_id + Id + assign + from_op + Id + take + BE + st_at + BE, lambda h, s: GroupVarDeclarationNode(s[1], s[2], VariableNode(s[5]), s[9], s[7])

AS %= Id + opar + ARG + cpar, lambda h, s: CallNode(s[1], s[3])
AS %= BE, lambda h, s: s[1]
AS %= obra + ARR + cbra, lambda h,s:  ArrayNode(s[2])


ARR %= E + ARR1, lambda h,s: [s[1]] + s[2]
ARR %= Gram.Epsilon, lambda h, s: []

ARR1 %= comma + E + ARR1, lambda h,s : [s[2]] + s[3] 
ARR1 %= Gram.Epsilon, lambda h, s: []

R %= lineup + Id + with_op + I + in_op + BE + heading + direc + args + opar + ARG + cpar + RN, lambda h, s: ([BeginCallNode(
    s[2], s[6], ConstantNode(s[8], Vector()), [s[4]]+s[11])], s[13][1]) if not s[13][0] else ([BeginCallNode(s[2], s[6], ConstantNode(s[8], Vector()), [s[4]]+s[11])] + s[13][0], s[13][1])


RN %= step + R, lambda h, s: (None, [StepNode(s[2][0])] + s[2][1])
RN %= Gram.Epsilon, lambda h, s: ([], [])
RN %= R, lambda h, s: s[1]


ARG %= BE + ARG1, lambda h, s: [s[1]] + s[2]
ARG %= Gram.Epsilon, lambda h,s : [ ]

ARG1 %= comma + BE + ARG1, lambda h, s: [s[2]] + s[3]
ARG1 %= Gram.Epsilon, lambda h, s: []


I %= obra + num + I2 + cbra, lambda h, s: ConstantNode([s[2]] + s[3], Group())
I %= obra + num + two_points + num + cbra, lambda h, s: SliceNode(s[2], s[4])

I2 %= comma + num + I2, lambda h, s: [s[2]] + s[3]
I2 %= Gram.Epsilon, lambda h, s: []


BE %= C + andop + BE, lambda h, s: AndNode(s[1], s[3])
BE %= C + orop + BE, lambda h, s: OrNode(s[1], s[3])
BE %= notop + BE, lambda h, s: NotNode(s[2])
BE %= C, lambda h, s: s[1]

C %= E + eq + C, lambda h, s: EqNode(s[1], s[3])
C %= E + lte + C, lambda h, s: EqlNode(s[1], s[3])
C %= E + gte + C, lambda h, s: EqgNode(s[1], s[3])
C %= E + gt + C, lambda h, s: GtNode(s[1], s[3])
C %= E + lt + C, lambda h, s: LtNode(s[1], s[3])
C %= E, lambda h, s: s[1]

E %= E + plus + T, lambda h, s: PlusNode(s[1], s[3])
E %= E + minus + T, lambda h, s: MinusNode(s[1], s[3])
E %= T, lambda h, s: s[1]

T %= T + star + F, lambda h, s: StarNode(s[1], s[3])
T %= T + div + F, lambda h, s: DivNode(s[1], s[3])
T %= T + rem + F, lambda h, s: ModNode(s[1], s[3])
T %= F, lambda h, s: s[1]

F %= bool_value, lambda h, s: ConstantNode(s[1], Bool())
F %= num, lambda h, s: ConstantNode(s[1], Int())
F %= V, lambda h, s: s[1]
F %= Id, lambda h, s: VariableNode(s[1])
F %= Id + dot + Id + opar + ARG + cpar, lambda h, s: DynamicCallNode(s[3], VariableNode(s[1]), s[5])
F %= Id + obra + E + cbra, lambda h, s: GetIndexNode(VariableNode(s[1]), s[3])
F %= opar + BE + cpar, lambda h, s: s[2]
F %= direc, lambda h, s: ConstantNode(s[1], Vector())

V %= opar + E + comma + E + cpar, lambda h, s: VectNode(s[2], s[4])
