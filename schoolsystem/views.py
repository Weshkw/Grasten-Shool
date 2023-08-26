
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse,FileResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Student,landingPageImage,FeesStructure,CustomUser,TeachingStaff,NonTeachingStaff,New,Bill,StaffGovernmentDeduction,StudentResult,FeePayment, EducationalResource 
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def home(request):
    student_admission = None  # Initialize student_admission as None

    # Check if the user is authenticated and has a corresponding student record
    if request.user.is_authenticated:
        try:
            student_admission = Student.objects.get(student_admission_number=request.user.id_number)
        except Student.DoesNotExist:
            pass  # Student record doesn't exist, student_admission remains None


        # Query the database to get all images
    all_images = landingPageImage.objects.order_by('-pk')
    
    # Organize images by category
    images_by_category = {}
    for image in all_images:
        category = image.landing_page_picture_category
        if category in images_by_category:
            images_by_category[category].append(image)
        else:
            images_by_category[category] = [image]

    context = {'student_admission': student_admission,'images_by_category': images_by_category,}
    return render(request, 'schoolsystem/home.html', context)


    
    


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        id_number = request.POST.get('id_number')
        password = request.POST.get('password')

        # Use lower() method on the id_number input
        user = authenticate(request, username=id_number.lower(), password=password)  
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Return to the login page with an error message
            messages.error(request, 'Invalid Index Number, TSC Number, or password.')
            return render(request, 'schoolsystem/login.html')

    return render(request,'schoolsystem/login.html')
        


def logout_user(request):
    logout(request)
    return redirect('home')


def register(request):
    if request.method == 'POST':
        id_number = request.POST.get('id_number')
        first_name = request.POST.get('first_name')
        second_name = request.POST.get('second_name')
        surname = request.POST.get('surname')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        # Check if the id_number exists in any of the user types
        if not (CustomUser.objects.filter(id_number=id_number).exists() or
                Student.objects.filter(student_admission_number=id_number).exists() or
                TeachingStaff.objects.filter(tsc_number=id_number).exists() or
                NonTeachingStaff.objects.filter(id_number=id_number).exists()):
            
            messages.error(request, 'ID number, index number, or TSC number does not exist.')
            return redirect('register')

        # Create the user
        user = CustomUser.objects.create_user(
            id_number=id_number,
            first_name=first_name,
            second_name=second_name,
            surname=surname,
            phone_number=phone_number,
            password=password
        )
        messages.success(request, 'User created successfully.')
        return redirect('login')

    return render(request,'schoolsystem/userregistration.html')


def reset_password(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        surname = request.POST.get('surname')
        phone_number = request.POST.get('phone_number')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')

        # Retrieve the user based on provided details
        try:
            user = CustomUser.objects.get(
                first_name=first_name,
                surname=surname,
                phone_number=phone_number
            )
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid user details.')
            return redirect('reset_password')

        # Set the new password
        user.set_password(new_password)
        user.save()

        messages.success(request, 'Password reset successful.')
        return redirect('login')

    return render(request, 'schoolsystem/reset_password.html')


def news(request):
    latest_news = New.objects.order_by('-date_uploaded', '-pk')[:6]

    context={'latest_news':latest_news}
    return render(request,'schoolsystem/news.html',context)

def fees_structure_detail(request):
    fees_structures = FeesStructure.objects.all()
    context = {
        
        'fees_structures': fees_structures,
    }
    return render(request, 'schoolsystem/feestructure.html', context)


@login_required
def view_fee_payments(request):
    logged_in_id_number = request.user.id_number

    try:
        student_admission = Student.objects.get(student_admission_number=logged_in_id_number)
        
        # Query FeePayment instances related to the student
        fee_payments = FeePayment.objects.filter(student=student_admission).order_by('-pk')
    except Student.DoesNotExist:
        student_admission = None
        fee_payments = []

    return render(request, 'schoolsystem/view_fee_payments.html', {'student_admission': student_admission, 'fee_payments': fee_payments})


@login_required(login_url='login')
def educational_resources(request):
    user_id_number = request.user.id_number

    # Initialize student_grade_level with a default value
    student_grade_level = None
    
    try:
        # Retrieve the student based on the user's ID number
        student_admission = Student.objects.get(student_admission_number=user_id_number)
        student_grade_level = student_admission.grade_level

        # Retrieve the educational resources for the user's grade level
        resources = EducationalResource.objects.filter(appropriate_grade=student_grade_level)
    except Student.DoesNotExist:
        student_admission = None
        resources = []

    if not student_admission:
        # If the user is not a student, show all educational resources
        resources = EducationalResource.objects.order_by('-pk')

    context = {'resources': resources, 'student_admission': student_admission, 'student_grade_level': student_grade_level}
    return render(request, 'schoolsystem/educational_resources.html', context)



def all_resources_view(request):
    resources = EducationalResource.objects.order_by('-pk')
    context = {'resources': resources}
    return render(request, 'schoolsystem/all_resources.html', context)

    
@login_required
def view_student_results(request):
    # Step 1: Identify the logged-in user
    logged_in_user = request.user

    # Step 2: Retrieve the student associated with the logged-in user's ID number
    try:
        student = Student.objects.get(student_admission_number=logged_in_user.id_number)
    except Student.DoesNotExist:
        # Handle the case where the user is not associated with any student
        return HttpResponse( 'This account doesnt belong to a student')

    # Step 3: Display the instances of StudentResult for that particular student
    student_results = StudentResult.objects.filter(student=student).order_by('-pk')

    context = {
        'student': student,
        'student_results': student_results,
    }

    return render(request, 'schoolsystem/student_results.html', context)



def search_results_view(request):
    query = request.GET.get('q')

    # Requirement 1: Anyone can search and see all feestructures and news
    feestructures = FeesStructure.objects.filter(
        Q(fees_structure_description__icontains=query)
    )
    news = New.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query)
    )
    results = {
        'feestructures': feestructures,
        'news': news,
    }

    if query:
        user = request.user
        resources = None

        # Requirement 2: Students can search and see all feestructures, news, and resources and instances of their fees and studentresults
        if user.is_authenticated:
            try:
                student = Student.objects.get(student_admission_number=user.id_number)
                is_student = True
            except Student.DoesNotExist:
                is_student = False

            if is_student:
                student_results = StudentResult.objects.filter(
                    (Q(year__icontains=query) |
                    Q(term_or_semester_name__icontains=query) |
                    Q(examination__icontains=query) |
                    Q(score__icontains=query) |
                    Q(teacher_comments__icontains=query)) &
                    Q(student=student)  # Filter by the student
                )
                results['student_results'] = student_results

                fees = FeePayment.objects.filter(
                    (Q(student__full_name__icontains=query) |
                    Q(term_or_semester_name__term_or_semester_name__icontains=query) |
                    Q(amount_paid__icontains=query)) &
                    Q(student=student)  # Filter by the student
                )
                results['fees'] = fees

            # Requirement 2: authenticated users who are not Students should only see  EducationalResource
            resources = EducationalResource.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(subject__name__icontains=query) |
                Q(category__icontains=query) |
                Q(appropriate_grade__icontains=query)
            )
            results['resources'] = resources

        # Requirement 3: Unauthenticated users can only search feestructures and news.
        elif not user.is_authenticated:
            results['feestructures'] = feestructures
            results['news'] = news

    # Rendering the search results
    return render(request, 'schoolsystem/search_results.html', {'results': results})



     
   








