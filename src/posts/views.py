from urllib.parse import quote
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q


# Create your views here.
from .forms import PostForm
from .models import Post

def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
        
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        print(form.cleaned_data.get("title"))
        print(form.cleaned_data.get("content"))
        instance.save()
        #message success
        messages.success(request,"Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
        }
    return render(request,"post_form.html",context)

def post_detail(request, slug = None):#retrieve
    #instance = Post.objects.get(id=1)
    #instance = get_object_or_404(Post, title = "Title Abc")
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote(instance.content)
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string":share_string,
        }    
    return render(request,"post_detail.html",context)

def post_list(request):#list items
    today = timezone.now()
    queryset_list = Post.objects.active()#.order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list=Post.objects.all()
        
    
        
    query = request.GET.get("q")
    if query:
        queryset_list=queryset_list.filter(
            Q(title__icontains=query)|
            Q(content__icontains=query)|
            Q(user__first_name__icontains=query)|
            Q(user__last_name__icontains=query)
            ).distinct()
    paginator = Paginator(queryset_list, 2) # Show 25 contacts per page.
    page_request_var = "page"
    page_number = request.GET.get(page_request_var)
    queryset = paginator.get_page(page_number)
       
    context = {
        "object_list": queryset,    
        "title": "List",
        "page_request_var":page_request_var,
        "today":today,
    }    
    #return render(request, 'post_list.html', {'queryset': queryset}) 
    return render(request,"post_list.html",context)    

      

def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    
    instance = get_object_or_404(Post, slug=slug) 
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("title"))
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())
     
    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
        }    
    return render(request,"post_form.html",context)    
    

def post_delete(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    
    instance = get_object_or_404(Post, id=id)
    instance.delete()
    messages.success(request,"Successfully Deleted")
    return redirect("posts:list")


    