from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon
from semantic.language import *

Gram = Grammar()
comma,plus,minus,star,div,opar,cpar,lt,gt,lte = Gram.Terminals(', + - * / ( ) < > <=')
gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra, two_points = Gram.Terminals('>= == & | ! . { } :')
rem,wloop,deff,condif,condelse,iter_aof, groups ,obra,cbra = Gram.Terminals('% while def if else all_of groups [ ]')
at, of , from_op , borrow , st_at , to , lineup , step , heading  = Gram.Terminals('at of from borrow st_at to lineup step heading')
args, take, with_op, definition, begin_with, end, assign, in_op = Gram.Terminals('args take with definition begin_with end = in')
num, Id, bool_value, type_id, rpos, direc = Gram.Terminals('num Id bool_value type_id rpos direc')
eof = Gram.EOF


D, P, P1, B, A, AS, BE, ELSE, R, RN, ARG, G, I, I2, C, E, T, F, V = Gram.NonTerminals('D P P1 B A AS BE ELSE R RN ARG G I I2 C E T F V')


S = Gram.NonTerminal('S',True)

S %= definition + D + groups + G + begin_with + num + R + end, lambda h, s: ProgramNode(s[1], BeginWithNode(s[5],s[6][1]))

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D, lambda h, s: [DefinitionsNode(s[0])] + s[8] | Gram.Epsilon, lambda h,s: [ ]

P %= type_id + Id + P1, lambda h,s: [ParamNode(s[1],s[0])] + s[2] | Gram.Epsilon, lambda h,s : [ ]

P1 %=  comma + type_id + Id + P1, lambda h,s: [ParamNode(s[2],s[1])] + s[3] | Gram.Epsilon, lambda h,s : [ ]

B %= A + B, lambda h,s: [s[0]] + s[1] | wloop + opar + BE + cpar + ocbra + B + ccbra + B, lambda h,s: [LoopNode(s[2], s[5])] + s[6] 
B %= condif + opar + BE + cpar + ocbra + B + ccbra + ELSE + B, lambda h,s: [ConditionNode(s[2], s[5])] + [] + s[8]  
B %= iter_aof + Id + at + BE + of + rpos + B, lambda h,s: [IterNode(s[1],s[3],s[5])] + s[6] 
B %= from_op + Id + borrow + BE + st_at + BE + to + Id + B, lambda h,s: [BorrowNode(s[1], s[7], s[3], s[4])] + s[8] 
B %= Id + obra + BE + cbra + BE + of + Id + obra + BE + cbra + B, lambda h,s: [LinkNode( GetIndexNode(s[0], s[2]), GetIndexNode(s[6],s[8]), s[4])] + s[10] 
B %= Id + opar + ARG + cpar + B, lambda h,s: [CallNode(s[0], s[2])] + s[4] 
B %= Id + dot + Id + opar + ARG + cpar + B, lambda h,s: [CallNode( s[2], [s[0]] + s[4])] + s[5] | Gram.Epsilon, lambda h,s: [ ] 


A %= type_id + Id + assign + AS, lambda h,s: VarDeclarationNode(s[1],s[0],s[3]) | Id + obra + BE + cbra + assign + AS, lambda h,s: SetIndexNode(s[0],s[2],s[5]) 
A %= Id + assign + AS, lambda h, s: AssignNode(s[0], s[2]) | type_id + Id + assign + from_op + Id + take + BE + st_at + BE, lambda h,s: GroupVarDeclarationNode(s[0], s[1], s[4],s[8], s[6])

AS %= Id + dot + Id + opar + ARG + cpar, lambda h,s: CallNode( s[2], [s[0]] + s[4])  | Id + obra + BE + cbra, lambda h,s: CallNode(s[0], s[2]) | I, lambda h,s: s[0] | BE, lambda h,s: s[0] 


R %= lineup + Id + with_op + I + in_op + BE + heading + direc + args + ARG + RN, lambda h,s: ([BeginCallNode(s[1], s[5], s[7], [s[3]]+s[9])], s[10][1]) if not s[10][0] else ([BeginCallNode(s[1], s[5], s[7], [s[3]]+s[9])]+ s[10][0], s[10][1])

RN %= step + R,  lambda h,s: (None, [StepNode(s[1][0])] + s[1][1]) | Gram.Epsilon, lambda h,s: ([], []) | R, lambda h,s: s[0] 


ARG %= BE + ARG, lambda h,s: [s[0]] + s[1] |  comma + BE + ARG,  lambda h,s: [s[1]] + s[2]| Gram.Epsilon, lambda h,s : []

G %= Id + assign + I, lambda h,s: AssignNode(s[0], s[2]) 

I %=  obra + num + I2 + cbra, lambda h,s:ArrayNode([s[1]] + s[2])  |  obra + num + two_points + num + cbra, lambda h,s: SliceNode(s[1],s[3])  

I2 %=  comma + num + I2, lambda h,s: [s[1]] + s[2] | Gram.Epsilon, lambda h,s: [ ]


BE %=  C + andop + BE, lambda h,s: AndNode(s[0],s[2]) | C + orop + BE, lambda h,s: OrNode(s[0],s[2]) 
BE %= notop + BE , lambda h,s: NotNode(s[1])| C, lambda h,s: s[0]

C %= E + eq + C, lambda h,s: EqNode(s[0],s[2]) | E + lte + C, lambda h,s: EqlNode(s[0],s[2]) | E + gte + C, lambda h,s: EqgNode(s[0],s[2]) 
C %= E + gt + C, lambda h,s: GtNode(s[0],s[2]) | E + lt + C, lambda h,s: LtNode(s[0],s[2]) | E, lambda h,s: s[0]

E %=  E + plus + T, lambda h,s: PlusNode(s[0],s[2]) | E + minus + T, lambda h,s: MinusNode(s[0],s[2]) | T, lambda h,s: s[0]

T %=  T + star + F, lambda h,s: StarNode(s[0],s[2]) | T + div + F, lambda h,s: DivNode(s[0],s[2]) | T + rem + F, lambda h,s: ModNode(s[0],s[2]) | F, lambda h,s: s[0]

F %=  bool_value, lambda h,s: AtomicNode(s[0]) | num, lambda h,s: AtomicNode(s[0]) | V, lambda h,s: s[0] | Id, lambda h,s: AtomicNode(s[0]) | opar + BE + cpar | direc, lambda h,s: s[1]

V %=  opar + E + comma + E + cpar, lambda h,s: VectNode(s[1], s[3])