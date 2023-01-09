import re

plus, minus, star, div, opar, cpar, num, fun, comma = G.Terminals('+ - * / ( ) num fun ,')

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
    
    def __init__(self, lex, token_type, row, column):
        self.lex = lex
        self.token_type = token_type
        self.row = row
        self.column = column
        


      
fixed_tokens = {
    ','                   : { 'lex' : ','               , 'token_type' : comma      },
    '+'                   : { 'lex' : '+'               , 'token_type' : plus       },
    '-'                   : { 'lex' : '-'               , 'token_type' : minus      },
    '*'                   : { 'lex' : '*'               , 'token_type' : star       },
    '//'                  : { 'lex' : '/'               , 'token_type' : div        },
    '('                   : { 'lex' : '('               , 'token_type' : opar       },
    ')'                   : { 'lex' : ')'               , 'token_type' : cpar       },
    '<'                   : { 'lex' : '<'               , 'token_type' : lt         },
    '>'                   : { 'lex' : '>'               , 'token_type' : gt         },
    '<='                  : { 'lex' : '<='              , 'token_type' : lte        },
    '>='                  : { 'lex' : '>='              , 'token_type' : gte        },
    '=='                  : { 'lex' : '=='              , 'token_type' : eq         },
    '&'                   : { 'lex' : '&'               , 'token_type' : andop      },
    '|'                   : { 'lex' : '|'               , 'token_type' : orop       },
    '!'                   : { 'lex' : '!'               , 'token_type' : notop      },
    '.'                   : { 'lex' : '.'               , 'token_type' : dot        },   
    '{'                   : { 'lex' : '{'               , 'token_type' : ocbra      },
    '}'                   : { 'lex' : '}'               , 'token_type' : ccbra      },
    '%'                   : { 'lex' : '%'               , 'token_type' : rem        },
    'while'               : { 'lex' : 'while'           , 'token_type' : wloop      },
    'def'                 : { 'lex' : 'def'             , 'token_type' : deff       },
    'int'                 : { 'lex' : 'int'             , 'token_type' : typeof     },
    'bool'                : { 'lex' : 'bool'            , 'token_type' : typeof     },
    'group'               : { 'lex' : 'group'           , 'token_type' : typeof     },
    'array'               : { 'lex' : 'array'           , 'token_type' : typeof     },
    'vector'              : { 'lex' : 'int'             , 'token_type' : typeof     },
    'if'                  : { 'lex' : 'if'              , 'token_type' : condif     },
    'else'                : { 'lex' : 'else'            , 'token_type' : condelse   },
    'all of'              : { 'lex' : 'all_of'          , 'token_type' : iter_aof   },
    r'([a-z, A-Z])*'      : { 'lex' : r'([a-z, A-Z])*'  , 'token_type' : iD         }, 
    r'(-?[1-9])+([0-9])*' : { 'lex' : r'-?([1-9])+([0-9])*' , 'token_type' : num    },
    '['                   : { 'lex' : '['               , 'token_type' : obra       }, 
    ']'                   : { 'lex' : ']'               , 'token_type' : cbra       },
    'at'                  : { 'lex' : 'at'              , 'token_type' : at         },
    'of'                  : { 'lex' : 'of'              , 'token_type' : of         },
    'next'                : { 'lex' : 'next'            , 'token_type' : rposs      },
    'prev'                : { 'lex' : 'prev'            , 'token_type' : rposs      },
    'up'                  : { 'lex' : 'up'              , 'token_type' : direc      },
    'down'                : { 'lex' : 'down'            , 'token_type' : direc      },
    'rigth'               : { 'lex' : 'rigth'           , 'token_type' : direc      },
    'left'                : { 'lex' : 'left'            , 'token_type' : direc      },
    'from'                : { 'lex' : 'from'            , 'token_type' : From       },
    'borrow'              : { 'lex' : 'borrow'          , 'token_type' : borrow     },
    'starting_at'         : { 'lex' : 'st_at'           , 'token_type' : st_at      },
    'to'                  : { 'lex' : 'to'              , 'token_type' : to         },
      
}

# lineup, step, heading, args, take, with, definition, groips, begin_with, end , $, true, false, =, in