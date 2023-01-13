from Compiler.semantic.types import Type, Array
from pycompiler import Production, Sentence, Symbol, EOF, Epsilon

class ContainerSet:
    def __init__(self, *values, contains_epsilon=False):
        self.set = set(values)
        self.contains_epsilon = contains_epsilon

    def add(self, value):
        n = len(self.set)
        self.set.add(value)
        return n != len(self.set)

    def extend(self, values):
        change = False
        for value in values:
            change |= self.add(value)
        return change

    def set_epsilon(self, value=True):
        last = self.contains_epsilon
        self.contains_epsilon = value
        return last != self.contains_epsilon

    def update(self, other):
        n = len(self.set)
        self.set.update(other.set)
        return n != len(self.set)

    def epsilon_update(self, other):
        return self.set_epsilon(self.contains_epsilon | other.contains_epsilon)

    def hard_update(self, other):
        return self.update(other) | self.epsilon_update(other)

    def find_match(self, match):
        for item in self.set:
            if item == match:
                return item
        return None

    def __len__(self):
        return len(self.set) + int(self.contains_epsilon)

    def __str__(self):
        return '%s-%s' % (str(self.set), self.contains_epsilon)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.set)

    def __nonzero__(self):
        return len(self) > 0

    def __eq__(self, other):
        if isinstance(other, set):
            return self.set == other
        return isinstance(other, ContainerSet) and self.set == other.set and self.contains_epsilon == other.contains_epsilon


def inspect(item, grammar_name='G', mapper=None):
    try:
        return mapper[item]
    except (TypeError, KeyError ):
        if isinstance(item, dict):
            items = ',\n   '.join(f'{inspect(key, grammar_name, mapper)}: {inspect(value, grammar_name, mapper)}' for key, value in item.items() )
            return f'{{\n   {items} \n}}'
        elif isinstance(item, ContainerSet):
            args = f'{ ", ".join(inspect(x, grammar_name, mapper) for x in item.set) } ,' if item.set else ''
            return f'ContainerSet({args} contains_epsilon={item.contains_epsilon})'
        elif isinstance(item, EOF):
            return f'{grammar_name}.EOF'
        elif isinstance(item, Epsilon):
            return f'{grammar_name}.Epsilon'
        elif isinstance(item, Symbol):
            return f"G['{item.Name}']"
        elif isinstance(item, Sentence):
            items = ', '.join(inspect(s, grammar_name, mapper) for s in item._symbols)
            return f'Sentence({items})'
        elif isinstance(item, Production):
            left = inspect(item.Left, grammar_name, mapper)
            right = inspect(item.Right, grammar_name, mapper)
            return f'Production({left}, {right})'
        elif isinstance(item, tuple) or isinstance(item, list):
            ctor = ('(', ')') if isinstance(item, tuple) else ('[',']')
            return f'{ctor[0]} {("%s, " * len(item)) % tuple(inspect(x, grammar_name, mapper) for x in item)}{ctor[1]}'
        else:
            raise ValueError(f'Invalid: {item}')

def pprint(item, header=""):
    if header:
        print(header)

    if isinstance(item, dict):
        for key, value in item.items():
            print(f'{key}  --->  {value}')
    elif isinstance(item, list):
        print('[')
        for x in item:
            print(f'   {repr(x)}')
        print(']')
    else:
        print(item)

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

    def __init__(self, lex, token_type):
        self.lex = lex
        self.token_type = token_type

    def __str__(self):
        return f'{self.token_type}: {self.lex}'

    def __repr__(self):
        return str(self)

    @property
    def is_valid(self):
        return True

class UnknownToken(Token):
    def __init__(self, lex):
        Token.__init__(self, lex, None)

    def transform_to(self, token_type):
        return Token(self.lex, token_type)

    @property
    def is_valid(self):
        return False

def tokenizer(G, fixed_tokens):
    def decorate(func):
        def tokenize_text(text):
            tokens = []
            for lex in text.split():
                try:
                    token = fixed_tokens[lex]
                except KeyError:
                    token = UnknownToken(lex)
                    try:
                        token = func(token)
                    except TypeError:
                        pass
                tokens.append(token)
            tokens.append(Token('$', G.EOF))
            return tokens

        if hasattr(func, '__call__'):
            return tokenize_text
        elif isinstance(func, str):
            return tokenize_text(func)
        else:
            raise TypeError('Argument must be "str" or a callable object.')
    return decorate

def update_err_type(errors, set_type, get_type):
    if type(get_type) != TypeError and type(set_type) != type(get_type):
        err = TypeError(f"error de tipo, se recibio un {get_type} y se esperaba un {set_type}")
        errors.append(err)
        return err
    if type(get_type) == TypeError:
        return TypeError(f"error de tipo, se recibio un {get_type} y se esperaba un {set_type}")
    if type(set_type) == Array and type(set_type.sub_type) != type(get_type.sub_type):
        err = TypeError(f"error de tipo, se recibio un array de {get_type.sub_type} y se esperaba un {set_type.sub_type}")
        errors.append(err)
        return err
    return get_type

def update_errs(errors, new_errs):
    if new_errs:
        errors += new_errs

def check_types(args_1, args_2):
    for get_type, set_arg in zip(args_1, args_2):
        set_type = set_arg.type
        if set_type != get_type:
            return False
    return True

def exist_func(args, funcs):
    for info in funcs:
        if check_types(args, info.params):
            return True, info
    return False, None

def get_type(get_type):
    types_class = filter(lambda x : x.__name__ != "Array", Type.__subclasses__())
    for type_class in types_class:
        if get_type == type_class.name:
            return type_class(), None
    return get_type, [f"tipo {get_type} no definido"]