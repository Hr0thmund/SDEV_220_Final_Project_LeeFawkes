from django.shortcuts import render
from django.http import HttpResponse

def main_form(request):
    return HttpResponse("<h1>This is the Web Configurator. Be amazed.</h1>")


