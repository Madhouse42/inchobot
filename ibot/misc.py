# encoding: utf-8
import inspect


def list_functions(mod):
    return [(func.__name__, func) for func in mod.__dict__.itervalues()
            if inspect.isfunction(func) and
               inspect.getmodule(func) == mod]


