from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import (
    EducationalResource,
    FeePayment,
    FeesStructure,
    LandingPageImage,
    LogoImage,
    NewsArticle,
    Student,
    StudentResult,
)

LATEST_NEWS_COUNT = 6


def home(request):
    images = LandingPageImage.objects.all()
    galleries = [
        (label, [image for image in images if image.category == category])
        for category, label in LandingPageImage.CATEGORY_CHOICES
    ]
    context = {
        "student": Student.for_user(request.user),
        "galleries": galleries,
        "logo": LogoImage.objects.last(),
    }
    return render(request, "schoolsystem/home.html", context)


def news(request):
    latest_news = NewsArticle.objects.all()[:LATEST_NEWS_COUNT]
    return render(request, "schoolsystem/news.html", {"latest_news": latest_news})


def fees_structure(request):
    return render(
        request,
        "schoolsystem/fees_structure.html",
        {"fees_structures": FeesStructure.objects.all()},
    )


def account_help(request):
    return render(request, "schoolsystem/account_help.html")


@login_required
def educational_resources(request):
    """Resources for the student's grade, or the whole library for staff and with ?all=1."""
    student = Student.for_user(request.user)
    resources = EducationalResource.objects.select_related("subject")
    show_all = student is None or request.GET.get("all") == "1"
    if not show_all:
        resources = resources.filter(
            appropriate_grade__in=[student.grade_level, EducationalResource.ALL_STUDENTS]
        )
    context = {"resources": resources, "student": student, "show_all": show_all}
    return render(request, "schoolsystem/educational_resources.html", context)


@login_required
def student_results(request):
    student = Student.for_user(request.user)
    results = student.results.all() if student else StudentResult.objects.none()
    return render(
        request, "schoolsystem/student_results.html", {"student": student, "results": results}
    )


@login_required
def fee_payments(request):
    student = Student.for_user(request.user)
    payments = (
        student.fee_payments.select_related("term").with_running_balance()
        if student
        else FeePayment.objects.none()
    )
    return render(
        request, "schoolsystem/fee_payments.html", {"student": student, "payments": payments}
    )


def search(request):
    """Search what the visitor may see: public pages for everyone, the library for
    signed-in users, and their own results and fees for students."""
    query = request.GET.get("q", "").strip()
    results = {}
    if query:
        results["fees_structures"] = FeesStructure.objects.filter(
            fees_structure_description__icontains=query
        )
        results["news"] = NewsArticle.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        if request.user.is_authenticated:
            results["resources"] = EducationalResource.objects.select_related("subject").filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(subject__name__icontains=query)
                | Q(category__icontains=query)
            )
        student = Student.for_user(request.user)
        if student:
            results["student_results"] = student.results.filter(
                Q(examination__icontains=query)
                | Q(term__icontains=query)
                | Q(teacher_comments__icontains=query)
            )
            results["fee_payments"] = (
                student.fee_payments.select_related("term")
                .filter(term__name__icontains=query)
                .with_running_balance()
            )
    context = {
        "query": query,
        "results": results,
        "has_results": any(found.exists() for found in results.values()),
    }
    return render(request, "schoolsystem/search_results.html", context)
