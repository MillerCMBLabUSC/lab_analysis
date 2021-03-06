'''
Allows pickling of methods.  Found from:
  * http://stackoverflow.com/q/1816958/721964
which led to:
  * http://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods#edit2155350
'''

import types
import copy_reg


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
