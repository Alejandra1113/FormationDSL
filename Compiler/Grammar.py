from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon

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


S %= definition + D + groups + G + begin_with + num + R + end

D %= deff + Id + opar + P + cpar + ocbra + B + ccbra + D | Gram.Epsilon

P %= type_id + Id + P1 | Gram.Epsilon

P1 %=  comma + type_id + Id + P1 | Gram.Epsilon

B %= A + B | wloop + opar + BExp + cpar + ocbra + B + ccbra + B | condif + opar + BExp + cpar + ocbra + B + ccbra + ELSE + B | iter_aof + Id + at + VExp + of + rpos + B | from_op + Id + borrow + IExp + st_at + IExp + to + Id + B | Id + obra + IExp + cbra + VExp + of + Id + obra + IExp + cbra + B | Id + opar + ARG + cpar | Id + dot + Id + opar + ARG + cpar | Gram.Epsilon

A %= type_id + Id + assign + As | Id + obra + IExp + cbra + assign + As | Id + assign + As | type_id + Id + assign + I | type_id + Id + assign + from_op + Id + take + IExp + st_at + IExp

As %= Id + dot + Id + opar + ARG + cpar  | Id + obra + IExp + cbra | I | M 

BExp %= notop + BExp | BTerm + B2Exp | opar + BExp + cpar + B2Exp

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

R %= lineup + Id + with_op + I + in_op + VExp + heading + direc + args + ARG + RN

RN %= step + R  | Gram.Epsilon | R

ARG %= M + ARG |  comma + M + ARG | Gram.Epsilon

M %= BExp | IExp | VExp

G %= Id + assign + I

I %=  obra + num + I2 + cbra  |  obra + num + two_points + num + cbra 

I2 %=  comma + num + I2 | Gram.Epsilon

print(Gram)
git push -u origin Parser-branch