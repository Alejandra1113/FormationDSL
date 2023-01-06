from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon

G = Grammar()
comma, plus, minus, star, div, opar, cpar, lt, gt, lte = G.Terminals(', + - * / ( ) < > <=')
gte, eq, andop, orop, notop, dot, ocbra, ccbra = G.Terminals('>= == & | ! . { ccbra ')
rem, wloop, deff, condif, condelse, iter_aof, obra, cbra = G.Terminals('% while def if else all_of [ ]')
at, of, from_op, borrow, st_at, to, lineup, step, heading = G.Terminals('at of from borrow st_at to lineup step heading')
args, take, with_op, definition, begin_with, end, assign, in_op = G.Terminals('args take with definition begin_with end = in')
num, Id, bool_value, type_id, rpos, direc = G.Terminals('num Id bool_value type_id rpos direc')
eof = G.EOF


D, P, P1, B, A, As, BExp, B2Exp, BTerm, ELSE, IExp, X, T, Y, F, N, VExp, XV, VT, R, RN, ARG, M, G, I, I2 = G.NonTerminals('D P P1 B A As BExp B2Exp BTerm ELSE IExp X T Y F N VExp XV VT R RN ARG M G I I2')

S %= definition + D + groups + G + begin_with + num + R + end

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D | Epsilon

P %= type_id + Id + P1 | Epsilon

P1 %=  comma + type_id + Id + P1 | Epsilon

B %= A + B | wloop + opar + BExp + cpar + ocbra + B + ccbra + B | condif + opar + BExp + cpar + ocbra + B + ccbra + ELSE + B | iter_aof + Id + at + VExp + of + rpos + B | from_op + Id + borrow + IExp + st_at + IExp + to + Id + B | Id + obra + IExp + cbra + VExp + of + Id + obra + IExp + cbra + B | Id + opar + ARG + cpar | Id + dot + Id + opar + ARG + cpar | Epsilon

A %= type_id + Id + assign + As | Id + obra + IExp + cbra + assign + As | Id + assign + As | type_id + Id + assign + I | type_id + Id + assign + from_op + Id + take + IExp + st_at + IExp

As %= M | I | Id + dot + Id + opar + ARG + cpar | Id + obra + IExp + cbra 

BExp %= notop + BExp | BTerm + B2Exp | opar + BExp + cpar + B2Exp

B2Exp %= andop + BExp | orop + BExp | Epsilon

BTerm %= Id | bool_value | IExp + eq + IExp | VExp + eq + VExp | IExp + gte + IExp | IExp + lte + IExp | IExp + lt + IExp | IExp + gt + IExp

ELSE %= condelse + ocbra + B + ccbra | Epsilon

IExp %= T + X

X %= plus + IExp + X | minus + IExp + X | Epsilon

T %= F + Y

Y %= F + Y | div + F + Y | rem + F + Y | Epsilon

F %= num | opar + IExp + cpar | Id

N %= IExp | Epsilon

VExp %= VT + XV

XV %= plus + VExp + XV | minus + VExp + XV | IExp | Epsilon

VT %= opar + IExp + comma + IExp + cpar | opar + VExp + cpar | Id | direc + N

R %= lineup + Id + with_op + I + in_op + VExp + heading + direc + args + ARG + RN

RN %= step + R | R | Epsilon

ARG %= M + ARG |  comma + M + ARG | Epsilon

M %= BExp | IExp | VExp

G %= Id + assign + I

I %=  obra + num + I2 + cbra  |  obra + num + : + num + cbra 

I2 %=  comma + num + I2 | Epsilon
