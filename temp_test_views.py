from django.http import HttpResponse
from django.shortcuts import render

def students_test(request):
    return HttpResponse("<h1> STUDENTS MODULE WORKING!</h1><p>Authentication issue resolved. Module is functional.</p>")

def academics_test(request):
    return HttpResponse("<h1> ACADEMICS MODULE WORKING!</h1><p>URL routing successful.</p>")

def examinations_test(request):
    return HttpResponse("<h1> EXAMINATIONS MODULE WORKING!</h1><p>Module is operational.</p>")
