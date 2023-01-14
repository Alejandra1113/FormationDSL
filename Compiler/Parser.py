from automata import build_LR1_automaton
#from pandas import DataFrame
from errors import ParsingError

class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    GOTO = "GOTO"

    def __init__(self, G, action=None, goto=None, verbose=False):
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
    
    def error(self, msg=None):
        """
        Raises a parsing error.
        """
        raise ParsingError(msg)

    def __call__(self, w):
        stack = [0]
        # cursor = 0
        output = []
        lookahead = next(w)
       # ==========

        ast = []

        while True:
            # print(output)
            state = stack[-1]
            # if self.verbose: print(stack, '<---||--->', w[cursor:])
            
            try:
                action, tag = self.action[(state, lookahead.token_type.Name)]
            except:
                self.error(f"Unexpected token {lookahead.token_type.Name} en la fila {lookahead.row}, columna {lookahead.column}")
            
            
            if action == ShiftReduceParser.SHIFT:
                stack.append(tag)
              # =========================================
                ast.append(lookahead.lex)
              # =========================================
                lookahead = next(w)


            elif action == ShiftReduceParser.REDUCE:
                prod = self.G.Productions[tag]
                left, rigth = prod

              # ===========================================
                attributes = prod.attributes
                assert all(
                    rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
                rule = attributes[0]

                if len(rigth):
                    synteticed = [None] + ast[-len(rigth):]
                    value = rule(None, synteticed)
                    ast[-len(rigth):] = [value]
                else:
                    ast.append(rule(None, None))
              # ===========================================

                for i in rigth:
                    stack.pop()

                _, iD = self.goto.get((stack[-1], left.Name))
                stack.append(iD)
                output.append(prod)

            elif action == ShiftReduceParser.OK:
                if lookahead.token_type.Name != self.G.EOF.Name :
                    self.error("Bad EOF")
                return output, ast[0]
            else:
                raise TypeError


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                next_symbol = item.NextSymbol

                if next_symbol is None:
                    for l in item.lookaheads:
                        if item.production.Left == G.startSymbol and l == G.EOF:
                            LR1Parser._register(
                                self.action, (idx, l.Name), (ShiftReduceParser.OK, None))
                            continue
                        k = G.Productions.index(item.production)
                        LR1Parser._register(
                            self.action, (idx, l.Name),  (ShiftReduceParser.REDUCE, k))

                elif next_symbol.IsNonTerminal:
                    transit = node.transitions.get(next_symbol.Name)
                    if transit:
                        LR1Parser._register(
                            self.goto, (idx, next_symbol.Name),  (None, transit[0].idx))

                else:

                    transit = node.transitions.get(next_symbol.Name)
                    if transit:
                        LR1Parser._register(
                            self.action, (idx, next_symbol.Name), (ShiftReduceParser.SHIFT, transit[0].idx))

                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                pass

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


######################## Visualize DataTable #############################


def encode_value(value):
    try:
        action, tag = value
        if action == ShiftReduceParser.SHIFT:
            return 'S' + str(tag)
        elif action == ShiftReduceParser.REDUCE:
            return repr(tag)
        elif action == ShiftReduceParser.OK:
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
            d[state] = {symbol: value}

    return DataFrame.from_dict(d, orient='index', dtype=str)
