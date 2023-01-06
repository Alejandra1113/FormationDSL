from itertools import chain
import re
from pygtrie import Trie
from Grammar import comma,plus,minus,star,div,opar,cpar,lt,gt,lte
from Grammar import gte ,eq ,andop ,orop ,notop ,dot ,ocbra ,ccbra
from Grammar import rem,wloop,deff,condif,condelse,iter_aof,obra,cbra
from Grammar import at, of , from_op , borrow , st_at , to , lineup , step , heading
from Grammar import args, take, with_op, definition, begin_with, end, assing, in_op
from Grammar import num, Id,bool_value, type_id, rpos, direc, eof
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


# TODO Numeros negativos


variable_tokens = {
  'num'              :  (num,              r'\d+'),                                                                                       # Numbers      
  'bool_value'       :  (bool_value,       r'(?:true)|(?:false)'),                                                                        # Bool Values          
  'type_id'          :  (type_id,          r'(?:int)|(?:bool)|(?:group)|(?:array)|(?:vector)'),                                           # Type Identifiers                
  'rpos'             :  (rpos,             r'(?:next)|(?:prev)'),                                                                         # Relative Position          
  'direc'            :  (direc,            r'(?:up)|(?:up_right)|(?:right)|(?:down_right)|(?:down)|(?:down_left)|(?:left)|(?:up_left)'),  # Directions                      
  'Id'               :  (Id,               r'(?:[a-zA-Z]_*)+')                                                                            # Identifiers      
}
  

fixed_tokens = Trie()
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
fixed_tokens['while']               = wloop                  
fixed_tokens['def']                 = deff                 
fixed_tokens['if']                  = condif              
fixed_tokens['else']                = condelse              
fixed_tokens['allof']               = iter_aof                
fixed_tokens['[']                   = obra               
fixed_tokens[']']                   = cbra               
fixed_tokens['at']                  = at                  
fixed_tokens['of']                  = of                  
fixed_tokens['from']                = from_op               
fixed_tokens['borrow']              = borrow                  
fixed_tokens['starting at']         = st_at                        
fixed_tokens['to']                  = to                  
fixed_tokens['line_up']             = lineup                  
fixed_tokens['step']                = step                  
fixed_tokens['heading']             = heading                  
fixed_tokens['args']                = args                  
fixed_tokens['take']                = take                  
fixed_tokens['with']                = with_op               
fixed_tokens['definition']          = definition                  
fixed_tokens['begin_with']          = begin_with                  
fixed_tokens['end']                 = end                  
fixed_tokens['=']                   = assing             
fixed_tokens['in']                  = in_op               





def tokenize(code,keywords,variable_tokens):
    special_match = [
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    token_specification = chain(map(lambda item : (item[0],item[1][1]),variable_tokens.items()),special_match)
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    column = -1
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'num':
            value = int(value)
            kind = num
        elif kind == 'bool_value':
            kind = bool_value
            if(value == 'true'):
                value = True
            else:
                value = False
        elif kind == 'Id':
            try:
                kind = keywords[value]
            except:
                kind = Id
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        else:
            kind, _ =  variable_tokens[kind][0]
        yield Token(kind, value, line_num, column)
    yield Token(eof,'$',line_num,column + 1)

code = """




"""

