from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage



def home(reqest): 
    # return HttpResponse("hello Home")
    return render(reqest,'index.html')

def about(reqest):
    return HttpResponse("hello About")

def contact(reqest):
    return HttpResponse("hello Contact")

def upload(reqest):
    return HttpResponse("hello Upload")
