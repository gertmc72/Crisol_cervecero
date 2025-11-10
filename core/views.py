from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Beer, Thread, Post, Report, Review, Brewery, ReviewPhoto
from .forms import ThreadForm, PostForm, ReportForm, CustomUserCreationForm, ReviewForm, LoginForm, SignupForm


def root_redirect(request):
    """Vista raíz: redirige a home"""
    return redirect('home')


def home(request):
    """Home pública: muestra hilos recientes y cervezas destacadas"""
    q = request.GET.get("q", "").strip()

    # Hilos recientes (5)
    threads = Thread.objects.all()[:5]

    # Cervezas destacadas (5 con mejor rating)
    beers = Beer.objects.filter(avg_rating__gt=0).order_by('-avg_rating')[:5]

    # Si hay búsqueda, buscar en threads y beers
    if q:
        threads = Thread.objects.filter(title__icontains=q)[:5]
        beers = Beer.objects.filter(
            Q(name__icontains=q) | Q(style__icontains=q)
        )[:5]

    return render(request, "home.html", {
        "threads": threads,
        "beers": beers,
        "q": q,
    })


def beer_list(request):
    """Lista de cervezas - pública"""
    beers = Beer.objects.all()
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

    return render(request, "beer_list.html", {
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
    # Obtener las fotos para cada reseña
    for review in reviews:
        review.photos_list = review.photos.all()
    return render(request, "beer_detail.html", {"beer": beer, "reviews": reviews, "threads_count": threads_count})


@login_required
def create_review(request, beer_id=None):
    """
    Crear reseña. Si se proporciona `beer_id` se crea la reseña para esa cerveza.
    Si no, se permite que el usuario escriba el nombre de la cerveza y estilo libremente;
    en ese caso intentamos buscar una `Beer` existente por nombre o crear una nueva (creando
    también la `Brewery` si se proporciona nombre de cervecería).
    """
    beer = None
    if beer_id:
        beer = get_object_or_404(Beer, id=beer_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Determinar la cerveza asociada: preferir beer_id, si no, usar beer_name
            if beer:
                target_beer = beer
            else:
                beer_name = form.cleaned_data.get("beer_name", "").strip()
                style = form.cleaned_data.get("style", "").strip()
                brewery_name = form.cleaned_data.get(
                    "brewery_name", "").strip()
                target_beer = None
                if beer_name:
                    # Buscar cerveza por nombre (insensible mayúsc/minúsc)
                    target_beer = Beer.objects.filter(
                        name__iexact=beer_name).first()
                    if not target_beer:
                        # Crear brewery si se proporcionó nombre
                        brewery = None
                        if brewery_name:
                            brewery, _ = Brewery.objects.get_or_create(
                                name=brewery_name)
                        else:
                            # Crear o usar una cervecería 'Desconocida' para permitir la creación
                            brewery, _ = Brewery.objects.get_or_create(
                                name="Desconocida")

                        target_beer = Beer.objects.create(
                            brewery=brewery,
                            name=beer_name,
                            style=style or "Desconocido",
                        )

            if not (beer or target_beer):
                form.add_error(
                    None, "Debes especificar el nombre de la cerveza o acceder desde la página de una cerveza.")
            else:
                review = Review.objects.create(
                    beer=target_beer if target_beer else beer,
                    user_name=form.cleaned_data["user_name"],
                    brand=form.cleaned_data.get("brand", ""),
                    brewery_name=form.cleaned_data.get("brewery_name", ""),
                    comment=form.cleaned_data["comment"],
                    aroma=form.cleaned_data["aroma"],
                    sabor=form.cleaned_data["sabor"],
                    cuerpo=form.cleaned_data["cuerpo"],
                    apariencia=form.cleaned_data["apariencia"],
                )

                # Guardar las fotos (máximo 3)
                photos = [
                    form.cleaned_data.get("photo1"),
                    form.cleaned_data.get("photo2"),
                    form.cleaned_data.get("photo3"),
                ]

                for photo in photos:
                    if photo:
                        ReviewPhoto.objects.create(review=review, photo=photo)

                messages.success(request, "¡Reseña creada exitosamente!")
                return redirect("beer_detail", beer_id=(target_beer.id if target_beer else beer.id))
    else:
        # Pre-rellenar el nombre de usuario con el usuario actual
        initial = {"user_name": request.user.username}
        form = ReviewForm(initial=initial)

    return render(request, "create_review.html", {
        "beer": beer,
        "form": form,
    })


def threads_list_create(request):
    """Lista todos los hilos y permite crear uno nuevo (solo autenticados)"""
    threads = Thread.objects.all()

    # Filtrar por búsqueda si existe
    q = request.GET.get("q", "").strip()
    if q:
        threads = threads.filter(title__icontains=q)

    if request.method == "POST" and request.user.is_authenticated:
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = Thread.objects.create(
                beer=form.cleaned_data.get("beer"),
                title=form.cleaned_data["title"],
                user=request.user,
                user_name=request.user.username,
            )
            messages.success(request, "¡Hilo creado exitosamente!")
            return redirect("thread_detail", thread_id=thread.id)
    else:
        form = ThreadForm() if request.user.is_authenticated else None

    paginator = Paginator(threads, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "threads.html", {
        "page_obj": page_obj,
        "form": form,
        "q": q,
    })


def thread_detail_reply(request, thread_id):
    """Detalle de hilo - público, pero solo autenticados pueden responder"""
    thread = get_object_or_404(Thread, id=thread_id)
    posts_qs = thread.posts.filter(is_hidden=False).order_by("created_at")

    if request.method == "POST" and request.user.is_authenticated:
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                thread=thread,
                user=request.user,
                user_name=request.user.username,
                body=form.cleaned_data["body"],
            )
            messages.success(request, "¡Respuesta publicada!")
            return redirect("thread_detail", thread_id=thread.id)
    else:
        form = PostForm() if request.user.is_authenticated else None

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
        form = ReportForm(
            initial={"object_type": object_type, "object_id": object_id})

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
    beers_with_counts = Beer.objects.annotate(
        num_reviews=Count("reviews")).filter(num_reviews__gte=5)
    top5 = beers_with_counts.order_by("-avg_rating")[:5]
    if top5.count() < 5:
        top5 = Beer.objects.annotate(num_reviews=Count(
            "reviews")).order_by("-avg_rating")[:5]

    return render(request, "admin_metrics.html", {"totals": totals, "top5": top5})


def signup_view(request):
    """Vista de registro de nuevos usuarios"""
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'¡Cuenta creada exitosamente! Bienvenido/a, {user.username}.')
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


def register(request):
    """Vista de registro (alias para compatibilidad)"""
    return signup_view(request)
