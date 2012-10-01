# Decorators for views go in here
from functools import wraps

from django.shortcuts import redirect

def passes_test(test_fcn, redirect_name, *args, **kwargs):
    """
    To continue with this view
        1) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *inner_args, **inner_kwargs):
            if test_fcn(request, *args, **kwargs):
                return func(request, *inner_args, **inner_kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator

def user_passes_test(test_fcn, redirect_name, *args, **kwargs):
    """
    To continue with this view
        1) request comes form an authenticated user
        2) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *inner_args, **inner_kwargs):
            if request.user.is_authenticated() and test_fcn(request, *args, **kwargs):
                return func(request, *inner_args, **inner_kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator

def doc_passes_test(test_fcn, redirect_name, *args, **kwargs):
    """
    To continue with this view
        1) request comes form an authenticated user
        2) test_fcn(request) returns True
    If these conditions aren't met, we redirect the user according the the param
    """
    def decorator(func):
        def inner_decorator(request, *inner_args, **inner_kwargs):
            if request.user.is_authenticated() \
                and request.user.get_profile().is_doctor \
                and test_fcn(request, *args, **kwargs):

                return func(request, *inner_args, **inner_kwargs)
            else:
                return redirect(redirect_name)
        return wraps(func)(inner_decorator)
    return decorator


