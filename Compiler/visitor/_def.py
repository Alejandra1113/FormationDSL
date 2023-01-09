

__all__ = ['Context', 'ProgramContext', 'OtherContext']


def check_params(params_1, params_2):
    if len(params_1) != len(params_2):
        return False
    for get_arg, set_arg in zip(params_1, params_2):
        if set_arg.type != get_arg.type:
            return False
    return True


class VariableInfo:
    def __init__(self, name):
        self.name = name


class FunctionInfo:
    def __init__(self, name, params):
        self.name = name
        self.params = params


class Context:
    def __init__(self, parent=None):
        self.parent: Context = parent
        self.children: dict[int, OtherContext] = []

    def create_child_context(self, index):
        child_scope = OtherContext(self)
        self.children[index] = child_scope
        return child_scope

    def get_context(self, index):
        return self.children.get(index) or self


class ProgramContext(Context):
    def __init__(self):
        Context.__init__(self)
        self.local_funcs: list[FunctionInfo] = []

    def define_function(self, fname, params):
        if not self.is_local_func(fname, params):
            func = FunctionInfo(fname, params)
            self.local_funcs.append(func)
            return func

    def is_func_defined(self, fname, params):
        return self.is_local_func(fname, params)

    def is_local_func(self, fname, params):
        return self.get_local_function_info(fname, params) is not None

    def get_local_function_info(self, fname, params):
        for info in self.local_funcs:
            if info.name == fname and check_params(info.params, params):
                return info
        return None


class OtherContext(Context):
    def __init__(self, parent=None):
        self.parent: OtherContext
        Context.__init__(self, parent)
        self.local_vars: list[VariableInfo] = []

    def is_func_defined(self, fname, params):
        return self.parent.is_func_defined(fname, params)

    def define_variable(self, vname):
        if not self.is_var_defined(vname):
            var = VariableInfo(vname)
            self.local_vars.append(var)

    def is_var_defined(self, vname):
        if type(self) == ProgramContext or not self.is_local_var(vname):
            return False
        return self.parent.is_local_var(vname)

    def is_local_var(self, vname):
        return self.get_local_variable_info(vname) is not None

    def get_local_variable_info(self, vname):
        for i in self.local_vars:
            if i.name == vname:
                return i
        return None
