from itertools import chain
from operator import concat
import re
from pygtrie import Trie
from Grammar import comma,plus,minus,star,div,opar,cpar,lt,gt,lte, groups
from Grammar import gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra
from Grammar import rem,wloop,deff,condif,condelse,iter_aof,obra,cbra
from Grammar import at, of , from_op , borrow , st_at , to , lineup , step , heading
from Grammar import args, take, with_op, definition, begin_with, end, assign, in_op, two_points
from Grammar import num, Id,bool_value, type_id, rpos, direc, eof, return_term, continue_term, break_term
class Token:
    """
    Basic token class. 
    
    Parameters
    ----------
    lex : str
        Token's lexeme.
    token_type : Enum
        Token's type.
    """
    
    def __init__(self ,token_type, lex, row, column):
        self.lex = lex
        self.token_type = token_type
        self.row = row
        self.column = column

    def __repr__(self) -> str:
        return f'-------------------\ntoken_type: {self.token_type}\ntoken_lex: {self.lex}\n------------------------'
    

 
variable_tokens = {  
   'num'              :  (num,              r'(?:\d+)'),                                                                                   # Numbers      
   'bool_value'       :  (bool_value,       r'(?:true(\W|\Z))|(?:false(\W|\Z))'),                                                          # Bool Values          
   'type_id'          :  (type_id,          r'(?:int(\W|\Z))|(?:bool(\W|\Z))|(?:group(\W|\Z))|(?:array(\W|\Z))|(?:vector(\W|\Z))'),        # Type Identifiers                
   'rpos'             :  (rpos,             r'(?:next(\W|\Z))|(?:prev(\W|\Z))'),                                                           # Relative Position          
   'direc'            :  (direc,            r'(?:up_right(\W|\Z))|(?:down_right(\W|\Z))|(?:down_left(\W|\Z))|(?:up_left(\W|\Z))|(?:up(\W|\Z))|(?:right(\W|\Z))|(?:down(\W|\Z))|(?:left(\W|\Z))'),  # Directions       
   'two_no_word'      :  ("Two No word",    r'(//)|(<=)|(>=)|(==)'),                                                                       # Non word
   'one_no_word'      :  ("One No word",    r'[^A-Za-z0-9_\n\t ]{1}'),                                                                     # Non word
   'Id'               :  (Id,               r'(?:(([a-zA-Z]_*)+))')                                                                        # Identifiers      
}




fixed_tokens = Trie()
fixed_tokens['groups']              = groups
fixed_tokens[':']                   = two_points                                       
fixed_tokens[',']                   = comma                                       
fixed_tokens['+']                   = plus               
fixed_tokens['-']                   = minus              
fixed_tokens['*']                   = star               
fixed_tokens['//']                  = div                 
fixed_tokens['(']                   = opar               
fixed_tokens[')']                   = cpar               
fixed_tokens['<']                   = lt                 
fixed_tokens['>']                   = gt                 
fixed_tokens['<=']                  = lte                 
fixed_tokens['>=']                  = gte                 
fixed_tokens['==']                  = eq                  
fixed_tokens['&']                   = andop              
fixed_tokens['|']                   = orop               
fixed_tokens['!']                   = notop              
fixed_tokens['.']                   = dot                 
fixed_tokens['{']                   = ocbra              
fixed_tokens['}']                   = ccbra              
fixed_tokens['%']                   = rem                
fixed_tokens['[']                   = obra               
fixed_tokens[']']                   = cbra               
fixed_tokens['=']                   = assign           
fixed_tokens['while']               = wloop                  
fixed_tokens['def']                 = deff                 
fixed_tokens['if']                  = condif              
fixed_tokens['else']                = condelse              
fixed_tokens['all_of']               = iter_aof                
fixed_tokens['at']                  = at                  
fixed_tokens['of']                  = of                  
fixed_tokens['from']                = from_op               
fixed_tokens['borrow']              = borrow                  
fixed_tokens['starting_at']         = st_at                        
fixed_tokens['to']                  = to                  
fixed_tokens['line_up']              = lineup                  
fixed_tokens['step']                = step                  
fixed_tokens['heading']             = heading                  
fixed_tokens['args']                = args                  
fixed_tokens['take']                = take                  
fixed_tokens['with']                = with_op               
fixed_tokens['definition']          = definition                  
fixed_tokens['begin_with']          = begin_with                  
fixed_tokens['end']                 = end                  
fixed_tokens['in']                  = in_op   
fixed_tokens['return']              = return_term 
fixed_tokens['continue']            = continue_term 
fixed_tokens['break']               = break_term            





def tokenize(code,keywords,variable_tokens):
    special_match = [
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    token_specification = chain(map(lambda item : (item[0],item[1][1]),variable_tokens.items()),special_match)
    tok_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_specification))
    line_num = 1
    line_start = 0
    column = -1
    prev_prev_token = None
    prev_token = None
    current_index = 0
    while(current_index < len(code)):
        step_back = False
        
        for mo in tok_regex.finditer( code,current_index):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start
            current_index = mo.span()[1]
            if kind == 'num':
                try:
                    value = int(value)
                    kind = num
                    if(prev_prev_token and prev_token and prev_token.token_type == minus and prev_prev_token.token_type not in [cpar, num, Id]):
                        prev_token = None
                        value = -value
                except ValueError:
                    raise RuntimeError(f'{value!r} at {line_num} is not a valid number')
            elif kind == 'bool_value':
                kind = bool_value
                if(re.match(r'true(\W|\Z)',value)):
                    value = True
                else:
                    value = False
                step_back = True
            elif kind == 'direc':
                kind = direc
                step_back = True
                if(re.match(r'up_right(\W|\Z)',value)):
                    value = (-1,1)
                elif(re.match(r'right(\W|\Z)',value)):
                    value = (0,1)
                elif(re.match(r'down_right(\W|\Z)',value)):
                    value = (1,1)
                elif(re.match(r'down(\W|\Z)',value)):
                    value = (1,0)
                elif(re.match(r'down_left(\W|\Z)',value)):
                    value = (1,-1)
                elif(re.match(r'left(\W|\Z)',value)):
                    value = (0,-1)
                elif(re.match(r'up_left(\W|\Z)',value)):
                    value = (-1,-1)
                elif(re.match(r'up(\W|\Z)',value)):
                    value = (-1,0)
            elif kind == 'Id' or kind == 'one_no_word' or kind == 'two_no_word':
                try:
                    kind = keywords[value]
                except:
                    if kind == 'Id':
                        kind = Id
                    else:
                        raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            elif kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num} at column {column}' )
            else:
                kind, _ =  variable_tokens[kind]
                if(re.search(r'\W\Z',value)):
                    value = value[:len(value) - 1]
                step_back = True
            if(prev_prev_token):
                yield prev_prev_token
            prev_prev_token = prev_token
            prev_token = Token(kind, value, line_num, column)
            if(step_back):
                current_index -= 1
                break
    if(prev_prev_token):
        yield prev_prev_token
    if(prev_token):
        yield prev_token
            
    yield Token(eof,'$',line_num,column + 1)

code1 = r"""

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

groups



    group_a = [1,2,3]
       group_b =   [4,5]

begin_with 5
    line_up dos_filas with group_a in (0,0) heading up args()
    line_up dos_columnas with group_b in (2,0) heading up_left args()
step
    line_up dos_columnas with group_a in (0,0) heading up args()
    line_up dos_filas with group_b in (0,2) heading up args()
end
"""

code2 = r"""
    5-6
    a = -6
"""

code3 = r"""
    int+1
    int algoint

"""
code4 = r"""
5 + 6
"""


def preprocess(code):
    pattern = re.compile(r'(?P<alias>(([a-zA-Z]_*)+))[ \t]*=[ \t]*(?P<value>\[(\d+,)*\d+\])')
    end_replace, start_index = re.search('groups',code).span()
    end_index, start_replace = re.search('begin_with',code).span()
    repl = {}
    for match in pattern.finditer(code,start_index,endpos=end_index):
        repl[match.group('alias')] = match.group('value')

    repl_pattern = '|'.join([f'({key})' for key in repl.keys()])
    def create_repl_func(repl_dict):
        def repl_func(match):
            return repl_dict[match.group()]
        return repl_func
    post_group_code = code[end_index:]
    post_group_final = re.sub(repl_pattern,create_repl_func(repl),post_group_code)
    return code[:end_replace] + post_group_final

# print(preprocess(code1))


# tokens = tokenize(code3,fixed_tokens,variable_tokens)
# for token in tokens:
#     print(token)








