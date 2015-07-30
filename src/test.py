#!/usr/bin/env python
import collections

if __name__ == '__main__':

    l1=[1, 2, 3]
    l2=[1,2,3]
    test = 'lambda x,y: collections.Counter(x) == collections.Counter(y)'
    print test
    print eval(test)(l1,l2)
