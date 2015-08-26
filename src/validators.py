"""
Input validators 

The functions in the validators
class allow inputs to be checked 
against basic types.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

class validators:
    def type(val, _type):
        retVal = False
        if isinstance(val, _type):
            retVal = True
        else:
            try:
                tmp = _type(val)
                retVal = True
            except:
                pass
        return retVal

    def type_in_range(val, _type, lower, upper, includes_bounds = True):
        if self.type(val, _type):
            if includes_bounds:
                return _type(val) >= lower and _type(val) <= upper
            else:
                return _type(val) > lower and _type(val) < upper
        return False
        
    def double(val):
        return self.type(val, float)

    def double_in_range(val, lower, upper, includes_bounds = True):
        return self.type_in_range(val, float, lower, upper, includes_bounds)
        
    def float(val):
        return self.type(val, float)

    def float_in_range(val, lower, upper, includes_bounds = True):
        return self.type_in_range(val, float, lower, upper, includes_bounds)
        
    def int(val):
        return self.type(val, int)

    def int_in_range(val, lower, upper, includes_bounds = True):
        return self.type_in_range(val, int, lower, upper, includes_bounds)
        
    def string(val):
        return self.type(val, basestring)

    def list(val, l):
        return val in l

