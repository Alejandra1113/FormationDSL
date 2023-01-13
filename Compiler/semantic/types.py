import Compiler.semantic.language as lg

__all__ = ['VariableInfo', 'FunctionInfo', 'Type', 'Int',
           'Vector', 'Bool', 'Array', 'Group']


class VariableInfo:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class FunctionInfo:
    def __init__(self, name, params, return_type=None):
        self.name = name
        self.params = params
        self.return_type = return_type


class Type:
    def __init__(self) -> None:
        self.methods = []

    def is_func_defined(self, fname, params):
        if type(params) is int:
            return len(self.get_all_function_info(fname, params))
        return self.get_function_info(fname, params) is not None

    def get_all_function_info(self, fname, n):
        funcs = []
        for info in self.methods:
            if info.name != fname or len(info.params) != n:
                continue
            funcs.append(info)
        return funcs

    def get_function_info(self, fname, params):
        for info in self.methods:
            if info.name != fname or len(info.params) != len(params):
                continue
            all_check = True
            for param_type, arg_type in zip(info.params, params):
                if type(param_type) != type(arg_type):
                    all_check = False
            if all_check:
                return info
        return None

    def __init_subclass__(cls) -> None:
        cls.name = cls.__name__.lower()

    def __eq__(self, __o: object) -> bool:
        return type(__o) == type(self) and self.name == __o.name


class Int(Type):
    pass


class Vector(Type):
    pass


class Bool(Type):
    pass


array_func_dict = [
    FunctionInfo("len", [], Int())
]


class Array(Type):
    def __init__(self, sub_type) -> None:
        self.sub_type = sub_type
        Type.__init__(self)
        self.methods = array_func_dict

    def __eq__(self, __o: object) -> bool:
        return Type.__eq__(self, __o) and self.sub_type == __o.sub_type


class Group(Type):
    def __init__(self) -> None:
        Type.__init__(self)
        self.methods = array_func_dict

    def __eq__(self, __o: object) -> bool:
        return Type.__eq__(self, __o)


class NodeType(Type):
    pass
