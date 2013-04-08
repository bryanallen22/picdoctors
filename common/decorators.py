# Decorators for views go in here
from functools import wraps

from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import user_passes_test

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

#
# Someone went into depth on decorators here:
# http://stackoverflow.com/questions/739654/understanding-python-decorators#1594484
# 
# I'm stealing his magic decorator maker here
def decorator_with_args(decorator_to_enhance):
    """ 
    This function is supposed to be used as a decorator.
    It must decorate an other function, that is intended to be used as a decorator.
    Take a cup of coffee.
    It will allow any decorator to accept an arbitrary number of arguments,
    saving you the headache to remember how to do that every time.
    """

    # We use the same trick we did to pass arguments
    def decorator_maker(*args, **kwargs):

        # We create on the fly a decorator that accepts only a function
        # but keeps the passed arguments from the maker.
        def decorator_wrapper(func):

            # We return the result of the original decorator, which, after all, 
            # IS JUST AN ORDINARY FUNCTION (which returns a function).
            # Only pitfall: the decorator must have this specific signature or it won't work:
            return decorator_to_enhance(func, *args, **kwargs)

        return decorator_wrapper

    return decorator_maker
###  # Example of use:
###  # You create the function you will use as a decorator. And stick a decorator on it :-)
###  # Don't forget, the signature is "decorator(func, *args, **kwargs)"
###  @decorator_with_args 
###  def decorated_decorator(func, *args, **kwargs): 
###      def wrapper(function_arg1, function_arg2):
###          print "Decorated with", args, kwargs
###          return func(function_arg1, function_arg2)
###      return wrapper
###  
###  # Then you decorate the functions you wish with your brand new decorated decorator.
###  
###  @decorated_decorator(42, 404, 1024)
###  def decorated_function(function_arg1, function_arg2):
###      print "Hello", function_arg1, function_arg2
###  
###  decorated_function("Universe and", "everything")
###  #outputs:
###  #Decorated with (42, 404, 1024) {}
###  #Hello Universe and everything
###  
###  # Whoooot!

@decorator_with_args
def require_login_as(view_func, *myargs, **mykwargs):
    """
    Make sure the user is logged in with the and fits the roles

    Examples:
        @require_login_as(['skaa', 'doctor'])
        @require_login_as(['skaa', 'doctor'], '/someloginurl/')
    """
    roles = myargs[0]
    def wrapper(request):
        if not request.user.is_authenticated():
            return redirect( reverse('skaa_signin') ) # doctors can sign in there too
        for role in roles:
            if request.user.isa(role):
                return view_func(request)

        # They are signed in, but don't have permission
        return redirect( reverse('permission_denied') )
    return wrapper

