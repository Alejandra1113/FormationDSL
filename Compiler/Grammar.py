from pycompiler import Grammar, Terminal, NonTerminal, EOF, Epsilon

G = Grammar()
comma,plus,minus,star,div,opar,cpar,lt,gt,lte = G.Terminals(', + - * / ( ) < > <=')
gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra = G.Terminals('>= == & | ! . { }')
rem,wloop,deff,condif,condelse,iter_aof,obra,cbra = G.Terminals('% while def if else all_of [ ]')
at, of , from_op , borrow , st_at , to , lineup , step , heading  = G.Terminals('at of from borrow st_at to lineup step heading')
args, take, with_op, definition, begin_with, end, assing, in_op = G.Terminals('args take with definition begin_with end = in')
num, Id,bool_value, type_id, rpos, direc = G.Terminals('num Id bool_value type_id rpos direc')
eof = G.EOF
