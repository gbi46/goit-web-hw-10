from bson import ObjectId
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render, get_object_or_404
from .forms import AuthorForm, QuoteForm, TagForm
from .lib import get_mongo_collection
from .models import Author, Quote, Tag
from .parse import create_json_files, get_soup, get_author_details, MAIN_URL, get_quotes_data, add_to_postgres
from pathlib import Path
from .utils import get_data_from_mongo
from .utils import get_data_from_postgres
import json

@login_required()
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'The quote is saved successfully!')
            return  redirect('quotes:add_author')
        else:
            return render(request, 'quotes/add-author.html', {'form': form})
    else:
        return render(request, 'quotes/add-author.html', {'form': AuthorForm()})

def author_view(request, author_id):
    if request.session.get('use_mongo', True):
        collection = get_mongo_collection('local', 'authors')
        author = collection.find_one({'_id': ObjectId(author_id)})
    else:
        author = Author.objects.filter(id=author_id).first()
    return render(request, 'quotes/author_detail.html', {'author': author})

@login_required()
def quote(request):
    authors = Author.objects.all().order_by('fullname')
    tags = Tag.objects.all()

    if request.method == 'POST':
        author_id = request.POST.get('authors')
        author = Author.objects.get(id=author_id)

        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save(commit=False)

            new_quote.author = author
            new_quote.save()

            choice_tags = Tag.objects.filter(name__in=request.POST.getlist('tags'))
            for tag in choice_tags.iterator():
                new_quote.tags.add(tag)

            messages.success(request, 'The quote was added successfully!')
            return redirect(to='quotes:quote')
        else:
            return render(request, 'quotes/quote.html', {"authors": authors, "tags": tags, 'form': form})

    return render(request, 'quotes/quote.html', {"authors": authors, "tags": tags, 'form': QuoteForm()})

def quotes_by_tag_view(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)

    quotes_objects = Quote.objects.prefetch_related('tags').filter(tags=tag)

    per_page = 10
    paginator = Paginator(quotes_objects, per_page)
    page = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(
        request,
        "quotes/quotes_by_tag.html",
        context={
            'page_obj': page_obj,
            'paginator': paginator,
            'tag': tag
        }
    )

def tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/tag.html', {'form': form})

    return render(request, 'quotes/tag.html', {'form': TagForm()})

def main(request, page=1):
    use_mongo = request.session.get("use_mongo", True)
    per_page = 10

    if use_mongo:
        db_data = get_data_from_mongo(page=int(page), per_page=per_page)
    else:
        db_data = get_data_from_postgres(page=int(page), per_page=per_page)

    return render(
        request,
        "quotes/index.html",
        context={
            "authors": db_data['authors'],
            "page_obj": db_data['page_obj'],
            "paginator": db_data['paginator'],
            "popular_tags": db_data['popular_tags'],
            "quotes": db_data['quotes'],
            "use_mongo": use_mongo,
        }
    )

def parse_website(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            request.session['use_mongo'] = True

            create_json_files()
            add_to_postgres()

            messages.success(request, 'The website parsed successfully!')
            return redirect('quotes:switch_database')
    else:
        request.session['use_mongo'] = True
        return render(request, 'quotes/parse_website.html', context={'use_mongo': True})

def switch_database(request):
    use_mongo = request.session.get("use_mongo", False)
    request.session["use_mongo"] = False
    return redirect("quotes:root")