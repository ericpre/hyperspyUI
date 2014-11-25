# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 23:17:25 2014

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

class BindingList(list):
    """
    A list that has been extended to sync other lists or collections to changes
    in its contents. By custom targets, it can also be used to trigger events
    on addition/removal. Only append and remove actions are required, as
    extend, insert and pop can be inferred (insert loses order however), but
    for reasons of speed, it is recommended to supply all if they are 
    available. Supported targets for add_target are types 'list' and 
    'QListWidget'.
    """
    def __init__(self, target=None, *args, **kwargs):
        super(BindingList, self).__init__(*args, **kwargs)
        self.set_target(target)
        
    def set_target(self, target):
        self.targets = {}
        self.add_target(target)
        
    def add_custom(self, target, append, insert, extend, remove, pop):
        cb = {'ap': append, 'in': insert, 'ex': extend, 're': remove, 'po':pop}
        self.targets[target] = cb
        
    def add_target(self, target):
        if target is None:
            return
        elif isinstance(target, list):
            cb = {'ap': target.append, 'in': target.insert, 
                  'ex': target.extend, 're': target.remove, 'po': target.pop}
#        elif isinstance(target, QList):
#            cb = {'ap': target.append, 'in': target.insert, 
#                  'ex': target.append, 're': target.removeOne, 
#                  'po': target.removeAt}
        elif isinstance(target, QListWidget):
            def qlr(value):
                target.takeItem(self.index(value))
            cb = {'ap': target.addItem, 'in': target.insertItem, 
                  'ex': target.addItems, 're': qlr, 
                  'po': target.takeItem}
        self.targets[target] = cb
        
    def remove_target(self, target):
        self.targets.pop(target, 0)
        
        
    def append(self, object):
        super(BindingList, self).append(object)
        for t in self.targets.values():
            if t['ap'] is not None:
                t['ap'](object)
        
    def insert(self, index, object):
        super(BindingList, self).insert(index, object)
        for t in self.targets.values():
            if t['in'] is not None:
                t['in'](index, object)
            elif t['ap'] is not None:
                t['ap'](object)
        
    def extend(self, iterable):
        super(BindingList, self).extend(iterable)
        for t in self.targets.values():
            if t['ex'] is not None:
                t['ex'](iterable)
            if t['ap'] is not None:
                for v in iterable:
                    t['ap'](v)
        
    def remove(self, value):
        for t in self.targets.values():
            if t['re'] is not None:
                t['re'](value)
        super(BindingList, self).remove(value)
        
    def pop(self, index=-1):
        if index < 0:
            index = len(self) + index
        for t in self.targets.values():
            if t['po'] is not None:
                t['po'](index)
            elif t['re'] is not None:
                v = self[index]
                t['re'](v)
        return super(BindingList, self).pop(index)