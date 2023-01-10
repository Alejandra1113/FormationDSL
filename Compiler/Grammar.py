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


D, P, P1, B, A, AS, BEXP, B2EXP, BTERM, ELSE, IEXP, X, T, Y, F, N, VEXP, XV, VT, R, RN, ARG, M, G, I, I2 = Gram.NonTerminals('D P P1 B A AS BEXP B2EXP BTERM ELSE IEXP X T Y F N VEXP XV VT R RN ARG M G I I2')

S = Gram.NonTerminal('S',True)

S %= definition + D + groups + G + begin_with + num + R + end, lambda h, s: ProgramNode(s[1], s[6])

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D, lambda h, s: [DefinitionsNode(s[0])] + s[8] | Gram.Epsilon

P %= type_id + Id + P1, lambda h,s: [ParamNode(s[1],s[0])] + s[2] | Gram.Epsilon

P1 %=  comma + type_id + Id + P1, lambda h,s: [ParamNode(s[2],s[1])] + s[3] | Gram.Epsilon 

B %= A + B, lambda h,s: [s[0]] + s[1] | wloop + opar + BEXP + cpar + ocbra + B + ccbra + B, lambda h,s: [LoopNode(s[2], s[5])] + s[6] 
B %= condif + opar + BEXP + cpar + ocbra + B + ccbra + ELSE + B, lambda h,s: [ConditionNode(s[2], s[5])] + [] + s[8]  
B %= iter_aof + Id + at + VEXP + of + rpos + B, lambda h,s: [IterNode(s[1],s[3],s[5])] + s[6] 
B %= from_op + Id + borrow + IEXP + st_at + IEXP + to + Id + B, lambda h,s: [BorrowNode(s[1], s[7], s[3], s[4])] + s[8] 
B %= Id + obra + IEXP + cbra + VEXP + of + Id + obra + IEXP + cbra + B | Id + opar + ARG + cpar + B, lambda h,s: [CallNode(s[0], s[2])] + s[4] 
B %= Id + dot + Id + opar + ARG + cpar + B, lambda h,s: [CallNode( s[2], [s[0]] + s[4])] + s[5] | Gram.Epsilon, lambda h,s: [ ] 


A %= type_id + Id + assign + AS | Id + obra + IEXP + cbra + assign + AS | Id + assign + AS | type_id + Id + assign + from_op + Id + take + IEXP + st_at + IEXP
A %= type_id + Id + assign + AS | Id + obra + IEXP + cbra + assign + AS | Id + assign + AS | type_id + Id + assign + from_op + Id + take + IEXP + st_at + IEXP

AS %= Id + dot + Id + opar + ARG + cpar  | Id + obra + IEXP + cbra | I | M 



BEXP %= notop + BEXP, lambda h,s: NotNode(s[1]) | BTERM + B2EXP | opar + BEXP + cpar + B2EXP

B2EXP %= andop + BEXP | orop + BEXP | Gram.Epsilon

BTERM %=  IEXP + eq + IEXP | VEXP + eq + VEXP | IEXP + gte + IEXP | IEXP + lte + IEXP | IEXP + lt + IEXP | IEXP + gt + IEXP | bool_value | Id

ELSE %= condelse + ocbra + B + ccbra | Gram.Epsilon

IEXP %= T + X

X %= plus + IEXP + X | minus + IEXP + X | Gram.Epsilon

T %= F + Y

Y %= F + Y | div + F + Y | rem + F + Y | Gram.Epsilon

F %= opar + IEXP + cpar | Id | num

N %= IEXP | Gram.Epsilon

VEXP %= VT + XV

XV %= plus + VEXP + XV | minus + VEXP + XV | IEXP | Gram.Epsilon

VT %= opar + IEXP + comma + IEXP + cpar | opar + VEXP + cpar  | direc + N | Id



R %= lineup + Id + with_op + I + in_op + VEXP + heading + direc + args + ARG + RN, lambda h,s: CallNode(s[1], [s[3],s[5],s[7]]+ s[10])

RN %= step + R  | Gram.Epsilon | R

ARG %= M + ARG, lambda h,s: [s[0]] + s[1] |  comma + M + ARG,  lambda h,s: [s[1]] + s[2]| Gram.Epsilon, lambda h,s : []

M %= BEXP | IEXP | VEXP

G %= Id + assign + I

I %=  obra + num + I2 + cbra  |  obra + num + two_points + num + cbra 

I2 %=  comma + num + I2 | Gram.Epsilon

# B -> C and B | C or B | not B | C
# C -> E == C | E != C | E <= C | E >= C | E > C | E < C | E
# E -> E + T | E - T | T
# T -> T * F | T / F | T % F | F
# F -> bool | num | V | id | ( B )

# V -> ( E, E )