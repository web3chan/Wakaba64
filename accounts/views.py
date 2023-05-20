import logging

from django.shortcuts import render, redirect
from django.http import HttpResponseServerError

from django.contrib.auth import authenticate, login

def auth(request):
    "Main authentication function"
    if request.method == "POST" and "pass" in request.POST:
        code = request.POST["pass"]

        if request.user.is_authenticated:
            return HttpResponseServerError("User is already authenticated")

        if len(code) != 32:
            return HttpResponseServerError("Invalid pass length")

        username, password = code[:16], code[16:]
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            logging.info(f"User logged in: {user}")
            if "next" in request.POST:
                return redirect(request.POST["next"])

        return redirect("auth")

    else:
        return render(request, 'accounts/index.html', {"request": request})