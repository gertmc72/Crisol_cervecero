from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Beer, Thread, Post, Report, Review, Brewery
from .forms import ThreadForm, PostForm, ReportForm, CustomUserCreationForm


def root_redirect(request):
    """Vista raíz: siempre redirige a login/registro"""
    return redirect('login')


@login_required
def home(request):
    """Listado de cervezas - requiere autenticación"""
    beers = Beer.objects.all()
    # Filtros simples
    q = request.GET.get("q", "").strip()
    style = request.GET.get("style", "").strip()
    brewery_id = request.GET.get("brewery", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()

    if q:
        beers = beers.filter(name__icontains=q)
    if style:
        beers = beers.filter(style=style)
    if brewery_id:
        beers = beers.filter(brewery_id=brewery_id)
    if min_rating:
        try:
            beers = beers.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass

    breweries = Brewery.objects.all()
    styles = Beer.objects.values_list('style', flat=True).distinct()

    return render(request, "home.html", {
        "beers": beers,
        "q": q,
        "style": style,
        "styles": styles,
        "brewery": brewery_id,
        "breweries": breweries,
        "min_rating": min_rating,
    })


def beer_detail(request, beer_id):
    beer = get_object_or_404(Beer, id=beer_id)
    reviews = beer.reviews.order_by("-created_at")
    threads_count = beer.threads.count()
    return render(request, "beer_detail.html", {"beer": beer, "reviews": reviews, "threads_count": threads_count})


def threads_list_create(request, beer_id):
    beer = get_object_or_404(Beer, id=beer_id)
    threads = beer.threads.order_by("-created_at")

    if request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            Thread.objects.create(
                beer=beer,
                title=form.cleaned_data["title"],
                user_name=form.cleaned_data["user_name"],
            )
            return redirect("threads_list", beer_id=beer.id)
    else:
        form = ThreadForm()

    return render(request, "threads.html", {
        "beer": beer,
        "threads": threads,
        "form": form,
    })


def thread_detail_reply(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    posts_qs = thread.posts.order_by("created_at")

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                thread=thread,
                user_name=form.cleaned_data["user_name"],
                body=form.cleaned_data["body"],
            )
            return redirect("thread_detail", thread_id=thread.id)
    else:
        form = PostForm()

    paginator = Paginator(posts_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "thread_detail.html", {
        "thread": thread,
        "page_obj": page_obj,
        "form": form,
    })


def report_create(request, object_type, object_id):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.objects.create(
                object_type=form.cleaned_data["object_type"],
                object_id=form.cleaned_data["object_id"],
                user_name=form.cleaned_data["user_name"],
                reason=form.cleaned_data["reason"],
            )
            return redirect("moderation_list")
    else:
        form = ReportForm(initial={"object_type": object_type, "object_id": object_id})

    return render(request, "report_form.html", {"form": form})


def moderation_list(request):
    # TODO: proteger vistas de moderación con staff
    reports = Report.objects.filter(status="open").order_by("-created_at")
    return render(request, "moderation_list.html", {"reports": reports})


def moderation_action(request, report_id, action):
    # TODO: proteger vistas de moderación con staff
    report = get_object_or_404(Report, id=report_id)
    if action == "hide" and report.object_type == "post":
        try:
            post = Post.objects.get(id=report.object_id)
            post.is_hidden = True
            post.save()
        except Post.DoesNotExist:
            pass
    if action == "close":
        report.status = "closed"
        report.save()
    return redirect("moderation_list")


def admin_metrics(request):
    # TODO: proteger vistas de moderación con staff
    totals = {
        "reviews": Review.objects.count(),
        "threads": Thread.objects.count(),
        "posts": Post.objects.count(),
    }
    beers_with_counts = Beer.objects.annotate(num_reviews=Count("reviews")).filter(num_reviews__gte=5)
    top5 = beers_with_counts.order_by("-avg_rating")[:5]
    if top5.count() < 5:
        top5 = Beer.objects.annotate(num_reviews=Count("reviews")).order_by("-avg_rating")[:5]

    return render(request, "admin_metrics.html", {"totals": totals, "top5": top5})


def register(request):
    """Vista de registro de nuevos usuarios - NUNCA crea superusers"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asegurar explícitamente que NO sea superuser
            user.is_superuser = False
            user.is_staff = False
            user.save()
            
            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido/a, {user.username}.')
            login(request, user)
            return redirect('home')  # home ahora está en /cervezas/
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
