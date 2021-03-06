from urllib.parse import quote_plus

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import PostForm
from .models import Post
# Create your views here.

def posts_home(request):
	form = PostForm()

	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)

def posts_create(request):
	# if not request.user.is_staff or not request.user.is_superuser:
		# raise Http404

	if not request.user.is_authenticated():
		 if not request.user.is_superuser or not request.user.is_staff:
			 raise Http404

	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		# print form.cleaned_data.get("title")
		instance.save()
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())


	#if request.method == "POST":
		#print (request.POST.get("content"))
		#print (request.POST.get("title"))
		#or
		#title= (request.POST.get("title"))
		#Post.objects.create(title=title)
	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)
def posts_detail(request, id=None):#retrieve
	#instance = Post.objects.get(id=2)
	instance = get_object_or_404(Post, id=id)
	if instance.draft or instance.publish > timezone.now().date():
		if not request.user.is_superuser or not request.user.is_staff:
			raise Http404
	share_string = quote_plus(instance.content)
	context = {
			"title":"instance.title",
			"instance": instance,
			"share_string":share_string,
		}
	#if request.user.is_authenticated():
	#	context={
	#		"title":"My user list"
	#	}
	#else:
	#	context = {
	#		"object_list":queryset,
	#		"title":"list"
	#	}
	return render(request,"post_detail.html",context)
	#return HttpResponse("<h1>list</h1>")


def post_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.active()
	if request.user.is_staff or request.user.is_superuser :
		queryset_list = Post.objects.all()

	query = request.GET.get("query")
	if query:
		queryset_list = queryset_list.filter(
						Q(title__icontains=query)|
						Q(content__icontains=query)|
						Q(user__first_name__icontains=query)|
						Q(user__last_name__icontains=query)
						).distinct()
	#filter(draft=False).filter(publish__lte=timezone.now())#.order_by("-timestamp")
	paginator = Paginator(queryset_list, 5) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)
	context = {
		"object_list":queryset,
		"title":"list",
		"page_request_var":page_request_var,
		"today":today,
		}
	#if request.user.is_authenticated():
	#	context={
	#		"title":"My user list"
	#	}
	#else:
	#	context = {
	#		"object_list":queryset,
	#		"title":"list"
	#	}
	return render(request,"post_list.html",context)
	#return HttpResponse("<h1>list</h1>")

def posts_update(request, id=None):
	if not request.user.is_authenticated():
		 if not request.user.is_superuser or not request.user.is_staff:
			 raise Http404
	instance = get_object_or_404(Post, id=id)
	form = PostForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		# print form.cleaned_data.get("title")
		instance.save()
		#messages.success(request, "Item saved")
		messages.success(request, "<a href='#'>Item</a> saved",extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title":instance.title,
			"instance": instance,
			"form": form,
		}
	return render(request,"post_form.html",context)

def posts_delete(request, id=None):
	if not request.user.is_authenticated():
		 if not request.user.is_superuser or not request.user.is_staff:
			 raise Http404
	instance = get_object_or_404(Post, id=id)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("posts:list")
