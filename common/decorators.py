# Decorators for views go in here
from functools import wraps

from django.shortcuts import redirect

def passes_test(test_fcn, redirect_name):
    """
    To continue with this view
        1) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if test_fcn(request, *args, **kwargs):
                return func(request, *args, **kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator

def user_passes_test(test_fcn, redirect_name):
    """
    To continue with this view
        1) request comes form an authenticated user
        2) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if request.user.is_authenticated() \
                    and request.user.isa('skaa') \
                    and test_fcn(request, *args, **kwargs):
                return func(request, *args, **kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator

def doc_passes_test(test_fcn, redirect_name):
    """
    To continue with this view
        1) request comes form an authenticated user
        2) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if request.user.is_authenticated() \
                and request.user.isa('doctor') \
                and test_fcn(request, *args, **kwargs):

                return func(request, *args, **kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator


