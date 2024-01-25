from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404


def logout_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Replace 'logout' with the appropriate URL name or path
        return view_func(request, *args, **kwargs)

    return wrapper


def login_required_my(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Replace 'logout' with the appropriate URL name or path
        return view_func(request, *args, **kwargs)

    return wrapper

# def match_message_user_id_or_staff(view_func):
#     def wrapper(request, *args, **kwargs):
#         pk = kwargs.get('pk')  # gets pk from link request
#         msg = get_object_or_404(Reviews, id=pk)  # find message by given id
#
#         try:
#             if request.user.id != msg.user.id and not request.user.is_staff:
#                 # redirect to home page if different id for current user and room host
#                 return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#         except AttributeError:
#             # this happens if user account is deleted (CASCADE in db)
#             pass
#
#         return view_func(request, *args, **kwargs)
#
#     return wrapper
