from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon
from semantic.language import *

Gram = Grammar()
comma,plus,minus,star,div,opar,cpar,lt,gt,lte = Gram.Terminals(', + - * / ( ) < > <=')
gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra, two_points = Gram.Terminals('>= == & | ! . { } :')
rem,wloop,deff,condif,condelse,iter_aof, groups ,obra,cbra = Gram.Terminals('% while def if else all_of groups [ ]')
at, of , from_op , borrow , st_at , to , lineup , step , heading  = Gram.Terminals('at of from borrow st_at to lineup step heading')
args, take, with_op, definition, begin_with, end, assign, in_op = Gram.Terminals('args take with definition begin_with end = in')
num, Id,bool_value, type_id, rpos, direc = Gram.Terminals('num Id bool_value type_id rpos direc')
eof = Gram.EOF

G = Grammar()
E = G.NonTerminal('E', True)
T,F,X,Y = G.NonTerminals('T F X Y')
plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')




D, P, P1, B, A, As, BExp, B2Exp, BTerm, ELSE, IExp, X, T, Y, F, N, VExp, XV, VT, R, RN, ARG, M, G, I, I2 = Gram.NonTerminals('D P P1 B A As BExp B2Exp BTerm ELSE IExp X T Y F N VExp XV VT R RN ARG M G I I2')

S = Gram.NonTerminal('S',True)


S %= definition + D + groups + G + begin_with + num + R + end, lambda h, s: ProgramNode(s[1], s[6])

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D, lambda h, s: [DefinitionsNode(s[0])] + s[8] | Gram.Epsilon

P %= type_id + Id + P1, lambda h,s: [ParamNode(s[1],s[0])] + s[2] | Gram.Epsilon

P1 %=  comma + type_id + Id + P1, lambda h,s: [ParamNode(s[2],s[1])] + s[3] | Gram.Epsilon 

B %= A + B, lambda h,s: [s[0]] + s[1] | wloop + opar + BExp + cpar + ocbra + B + ccbra + B, lambda h,s: [LoopNode(s[2], s[5])] + s[6] 
B %= condif + opar + BExp + cpar + ocbra + B + ccbra + ELSE + B, lambda h,s: [ConditionNode(s[2], s[5])] + [] + s[8]  
B %= iter_aof + Id + at + VExp + of + rpos + B, lambda h,s: [IterNode(s[1],s[3],s[5])] + s[6] 
B %= from_op + Id + borrow + IExp + st_at + IExp + to + Id + B, lambda h,s: [BorrowNode(s[1], s[7], s[3], s[4])] + s[8] 
B %= Id + obra + IExp + cbra + VExp + of + Id + obra + IExp + cbra + B | Id + opar + ARG + cpar + B, lambda h,s: [CallNode(s[0], s[2])] + s[4] 
B %= Id + dot + Id + opar + ARG + cpar + B, lambda h,s: [CallNode( s[2], [s[0]] + s[4])] + s[5] | Gram.Epsilon, lambda h,s: [ ] 


A %= type_id + Id + assign + As | Id + obra + IExp + cbra + assign + As | Id + assign + As | type_id + Id + assign + from_op + Id + take + IExp + st_at + IExp

As %= Id + dot + Id + opar + ARG + cpar  | Id + obra + IExp + cbra | I | M 



BExp %= notop + BExp, lambda h,s: NotNode(s[1]) | BTerm + B2Exp | opar + BExp + cpar + B2Exp

B2Exp %= andop + BExp | orop + BExp | Gram.Epsilon

BTerm %=  IExp + eq + IExp | VExp + eq + VExp | IExp + gte + IExp | IExp + lte + IExp | IExp + lt + IExp | IExp + gt + IExp | bool_value | Id

ELSE %= condelse + ocbra + B + ccbra | Gram.Epsilon

IExp %= T + X

X %= plus + IExp + X | minus + IExp + X | Gram.Epsilon

T %= F + Y

Y %= F + Y | div + F + Y | rem + F + Y | Gram.Epsilon

F %= opar + IExp + cpar | Id | num

N %= IExp | Gram.Epsilon

VExp %= VT + XV

XV %= plus + VExp + XV | minus + VExp + XV | IExp | Gram.Epsilon

VT %= opar + IExp + comma + IExp + cpar | opar + VExp + cpar  | direc + N | Id



R %= lineup + Id + with_op + I + in_op + VExp + heading + direc + args + ARG + RN, lambda h,s: CallNode(s[1], [s[3],s[5],s[7]]+ s[10])

RN %= step + R  | Gram.Epsilon | R

ARG %= M + ARG, lambda h,s: [s[0]] + s[1] |  comma + M + ARG,  lambda h,s: [s[1]] + s[2]| Gram.Epsilon, lambda h,s : []

M %= BExp | IExp | VExp

G %= Id + assign + I

I %=  obra + num + I2 + cbra  |  obra + num + two_points + num + cbra 

I2 %=  comma + num + I2 | Gram.Epsilon

print(Gram)
