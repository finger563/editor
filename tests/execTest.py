#!/usr/bin/evn python

code_str = """
def f(x):
    x = x + 1
    return x

print 'output = {}'.format(f(4))
"""

exec code_str

print 'my output = {}'.format(f(4))

func_str = """
def func(obj, otherArg):
    test = obj.method(otherArg)
    return test
"""

class obj:
    def __init__(self):
        pass

    def method(self, arg):
        return arg / 2

exec func_str

print 'func output = {}'.format(func(obj(),8))
