from django.shortcuts import render , redirect
from .models import Category

def categories(request):
    categories = Category.objects.all()
    return render(request , 'categories/categories.html' , {'categories' : categories})