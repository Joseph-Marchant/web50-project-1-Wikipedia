from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from markdown2 import Markdown
import random

from . import util

md = Markdown()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def title(request, page):
    # Make sure the page exists
    if util.get_entry(page) is not None:
        return render(request, "wiki/entry.html", {
            "content": md.convert(util.get_entry(page)),
            "page": page
        })
    # If it doesn't exist, generate error page
    else:
        return error(request, "We couldn't find the page you were looking for.")


def search(request):
    # Get the search term
    term = request.GET.get("q")
    # If the term exists take them to that page
    if util.get_entry(term) is not None:
        return HttpResponseRedirect(reverse("title", args=[term]))
    # Check entries to and see if the search term is in the title of any exisiting pages
    else:
        entries = util.list_entries()
        match = []
        for i in range(len(entries)):
            if term.lower() in entries[i].lower():
                match.append(entries[i])
        # Render the results page with a list of matches. If there are none then the page will display an error
        return render(request, "wiki/search.html", {
            "results": match
        })


# The form I'll need for the new_page route
class New_Page_Form(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={"style": "height: 400px; width: 600px"}))


def new_page(request):
    # If GET then render the form
    if request.method == "GET":
        return render(request, "wiki/new_page.html", {
            "form": New_Page_Form(),
            "title": "Add Page",
            "header": "Create a new page."
        })
    # If not GET then process the data
    else:
        form = New_Page_Form(request.POST)
        if form.is_valid():
            # If the form is valid then check to see if the page already exists
            pages = util.list_entries()
            title = form.cleaned_data["title"]
            for i in range(len(pages)):
                # If the page exists then generate error page
                if title == pages[i]:
                    return error(request, "Page already exists.")    
            # If it doesn't exist then add the title to the content with markdown
            content = markdown_title(title, form.cleaned_data["content"])
            # Save the entry and take them to the page
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("title", args=[title]))
        # If the page is not valid then return the form and send a message
        else:
            return render(request, "wiki/new_page.html", {
                "form": New_Page_Form(form),
                "message": "Form invalid."
            })
 

def markdown_title(title, content):
    # Edit the content to include the title in the markdown with a hash infront of it
    n = "\n"
    content = f"# {title}{n}{n}{content}"
    return content
            

def edit_page(request, page):
    # If GET then generate the page and prepopulate fields
    if request.method == "GET":
        return render(request, "wiki/edit_page.html", {
            "title": page,
            "content": util.get_entry(page)
        })
    # If not GET then save the data
    else:
        # Add the title to the markdown and save
        title = request.POST.get("title")
        content = markdown_title(title, request.POST.get("content"))
        util.save_entry(title, content)
        # Redirect the user to the now edited page
        return HttpResponseRedirect(reverse("title", args=[title]))


def random_page(request):
    # Get all the entries and choose a random one. Then generate that page
    list = util.list_entries()
    page = random.choice(list)
    return HttpResponseRedirect(reverse("title", args=[page]))


def error(request, message):
    # Generate an error page with the message  passed through to the function
    return render(request, "wiki/error.html", {
        "message": message
    })