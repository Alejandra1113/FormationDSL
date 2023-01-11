from automata import build_LR1_automaton
from pandas import DataFrame

class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    GOTO = "GOTO"
    
    def __init__(self, G, action = None, goto = None, verbose=False):
        self.G = G
        self.verbose = verbose
        if action is None or goto is None:
            self.action = {}
            self.goto = {}
            self._build_parsing_table()
        else:
            self.action = action
            self.goto = goto
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        # cursor = 0
        output = []
      
       #==========
        ast = []

        while True:
            # print(output)
            state = stack[-1]
            # if self.verbose: print(stack, '<---||--->', w[cursor:])
            action, tag = self.action[(state, lookahead.token_type.Name)]
            
            if action == ShiftReduceParser.SHIFT:
                stack.append(tag)
                lookahead = next(w)
                
              #=========================================
                ast.append(lookahead.lex)
              #=========================================
              
            elif action == ShiftReduceParser.REDUCE:
                prod = self.G.Productions[tag]
                left, rigth = prod
                
              #===========================================  
                attributes = prod.attributes
                assert all(rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
                rule = attributes[0]
                
                if len(rigth):
                    synteticed = [None] + stack[-len(rigth):]
                    value = rule(None, synteticed)
                    ast[-len(rigth):] = [value]
                else:
                    ast.append(rule(None, None))
              #===========================================
                
                for i in rigth:
                    stack.pop()
                
                _ ,iD = self.goto.get((stack[-1],left.Name))
                stack.append(iD)
                output.append(prod)
                
            elif action == ShiftReduceParser.OK:
                    return output, ast[0]
            else:   
                raise TypeError
            
            
class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                next_symbol = item.NextSymbol
                
                if next_symbol is None: 
                    for l in item.lookaheads:
                        if item.production.Left == G.startSymbol and l == G.EOF:
                            LR1Parser._register(self.action, (idx,l.Name), (ShiftReduceParser.OK, None))
                            continue
                        k = G.Productions.index(item.production)
                        LR1Parser._register(self.action, (idx,l.Name),  (ShiftReduceParser.REDUCE, k))
                        
                elif next_symbol.IsNonTerminal:
                    transit = node.transitions.get(next_symbol.Name)
                    if transit:
                        LR1Parser._register(self.goto, (idx,next_symbol.Name),  (None, transit[0].idx))

                else: 
                    
                    transit = node.transitions.get(next_symbol.Name)
                    if transit:
                        LR1Parser._register(self.action, (idx,next_symbol.Name), (ShiftReduceParser.SHIFT, transit[0].idx))
                        
                
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                pass
        
    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value
  
  
def evaluate_reverse_parse(right_parse, operations, tokens):
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    for operation in operations:
        if operation == ShiftReduceParser.SHIFT:
            token = next(tokens)
            stack.append(token.lex)
        
        elif operation == ShiftReduceParser.REDUCE:
            production = next(right_parse)
            head, body = production
            attributes = production.attributes
            assert all(rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
            rule = attributes[0]

            if len(body):
                synteticed = [None] + stack[-len(body):]
                value = rule(None, synteticed)
                stack[-len(body):] = [value]
            else:
                stack.append(rule(None, None))
        else:
            raise Exception('Invalid action!!!')

    assert len(stack) == 1
    assert isinstance(next(tokens).token_type, EOF)
    return stack[0]      

######################## Visualize DataTable #############################       

def encode_value(value):
    try:
        action, tag = value
        if action == ShiftReduceParser.SHIFT:
            return 'S' + str(tag)
        elif action == ShiftReduceParser.REDUCE:
            return repr(tag)
        elif action ==  ShiftReduceParser.OK:
            return action
        else:
            return value
    except TypeError:
        return value

def table_to_dataframe(table):
    d = {}
    for (state, symbol), value in table.items():
        value = encode_value(value)
        try:
            d[state][symbol] = value
        except KeyError:
            d[state] = { symbol: value }

    return DataFrame.from_dict(d, orient='index', dtype=str)