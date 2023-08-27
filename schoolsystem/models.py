from django.db import models
from django.db.models import ProtectedError
from django.contrib.auth.models import AbstractUser,BaseUserManager,Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone



class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, first_name, second_name, surname, phone_number, password=None):
        # Use lower() method on the id_number value
        user = self.model(id_number=id_number.lower(), first_name=first_name, second_name=second_name, surname=surname, phone_number=phone_number) 
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, first_name, second_name, surname, phone_number, password):
        # Use lower() method on the id_number value
        user = self.create_user(id_number=id_number.lower(), first_name=first_name, second_name=second_name, surname=surname, phone_number=phone_number, password=password) 
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



class CustomUser(AbstractUser):
    # Remove the uniqueness constraint from the username field
    username = None

    id_number = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)

    # Set the id_number field as the USERNAME_FIELD
    USERNAME_FIELD = 'id_number'

    # Add the additional fields to the REQUIRED_FIELDS
    REQUIRED_FIELDS = ['first_name', 'second_name', 'surname', 'phone_number']

    # Add related_name arguments to the groups and user_permissions fields
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set", # This is the new argument
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set", # This is the new argument
        related_query_name="customuser",
    )

    objects = CustomUserManager()

    def __str__(self):
        return str(self.id_number)
    


class Student(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    GENDER_CHOICES = (
        ('male', 'MALE'),
        ('female', 'FEMALE'),
    ) 
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES )
    NATIONALITY_CHOICES = (
        ('kenyan', 'KENYAN'),
        ('others', 'OTHERS'),
    )
    nationality = models.CharField(max_length=100, choices=NATIONALITY_CHOICES)

    # Identification
    student_admission_number = models.CharField(max_length=20, unique=True)

    # Academic Information
    GRADE_CHOICES = (
        ('PP1', 'PP1'),
        ('PP2', 'PP2'),
        ('grade1', 'GRADE1'),
        ('grade2', 'GRADE2'),
        ('grade3', 'GRADE3'),
        ('grade4', 'GRADE4'),
        ('grade5', 'GRADE5'),
        ('grade6', 'GRADE6'),
        ('grade7', 'GRADE7'),
        ('grade8', 'GRADE8'),
        ('grade9', 'GRADE9'),
    )
    grade_level = models.CharField(max_length=100, choices=GRADE_CHOICES)
    subjects = models.ManyToManyField('Subject', related_name='students')

    # Enrollment Details
    enrollment_date = models.DateField(auto_now_add=True)

    # Extracurricular Activities
    clubs_organizations = models.TextField(blank=True, null=True)
    sports_participation = models.TextField(blank=True, null=True)
    awards = models.TextField(blank=True, null=True)

    # Contact Information
    emergency_contact_name = models.CharField(max_length=255)

    EMERGENCY_CONTACT_RELATIONSHIP_CHOICES = (
        ('parent or guardian', 'PARENT OR GUARDIAN'),
        ('uncle', 'UNCLE'),
        ('aunt', 'AUNT'),
        ('grandparent', 'GRANDPARENT'),
        ('cousin', 'COUSIN'),
        ('trusted family friend', 'TRUSTED FAMILY FRIEND'),
    )
    emergency_contact_relationship = models.CharField(max_length=100, choices=EMERGENCY_CONTACT_RELATIONSHIP_CHOICES)
    emergency_contact_phone = models.CharField(max_length=20)
    parent_guardian_name = models.CharField(max_length=255)
    parent_guardian_phone = models.CharField(max_length=20)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_admission_number



class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class landingPageImage(models.Model):
    PICTURE_CATEGORY = (
        ('ACADEMICS', 'ACADEMICS'),
        ('COCURRICULAR', 'COCURRICULAR'),
        ('ICT', 'ICT'),
    )
    landing_page_picture_category = models.CharField(max_length=100, choices=PICTURE_CATEGORY)
    landing_page_picture = models.ImageField(upload_to='landing_page_pictures/')
    date = models.DateField(auto_now_add=True)
    


class EducationalResource(models.Model):
    MATERIAL_CATEGORIES = (
        ('Past Examinations', 'Past Examinations'),
        ('ebooks', 'Ebooks and Study Guides'),
        ('Educational pictures', 'Educational pictures'),
        ('Educational Videos', 'Educational Videos'),
        ('Educational links', 'Educational links'),
        ('General Resources', 'General Resources'),
    )

    GRADE_CHOICES = (
        ('PP1', 'PP1'),
        ('PP2', 'PP2'),
        ('grade1', 'GRADE1'),
        ('grade2', 'GRADE2'),
        ('grade3', 'GRADE3'),
        ('grade4', 'GRADE4'),
        ('grade5', 'GRADE5'),
        ('grade6', 'GRADE6'),
        ('grade7', 'GRADE7'),
        ('grade8', 'GRADE8'),
        ('grade9', 'GRADE9'),
        ('All students', 'All students'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)  # Make sure to import Subject model
    category = models.CharField(max_length=20, choices=MATERIAL_CATEGORIES)
    appropriate_grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    file = models.FileField(upload_to='EducationalResources/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)  # Add a field for the link
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class AnyOtherPayment(models.Model):
    student = models.ForeignKey(Student,  on_delete=models.PROTECT)
    payment_for = models.CharField(max_length=255) 
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment of {self.amount} made by {self.student.full_name} on {self.payment_date}'
    


class Term_or_semester(models.Model):
    term_or_semester_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    set_totalfees_payable = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        formatted_start_date = self.start_date.strftime('%d %B %Y')
        formatted_end_date = self.end_date.strftime('%d %B %Y')
        return f"{self.term_or_semester_name} ({formatted_start_date} to {formatted_end_date})"



class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    term_or_semester_name = models.ForeignKey(Term_or_semester ,on_delete=models.PROTECT)

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=[
        ('Cash', 'Cash'),
        ('Bank deposit', 'Bank deposit'),
        ('Bank Transfer', 'Bank Transfer'),
        ('M-pesa Payment', 'M-pesa Payment'),
    ])
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True)

    # Define the balance property(updates the fees balances of after each instance of a paerticular student)
   
    @property
    def balance(self):
        total_paid = FeePayment.objects.filter(student=self.student, term_or_semester_name=self.term_or_semester_name, id__lte=self.id).aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0
        balance = self.term_or_semester_name.set_totalfees_payable - total_paid
        return balance

   

class FeesStructure(models.Model):
    fees_structure_description = models.TextField()
    fees_structure = models.FileField(upload_to='fees_structure/')
    upload_date = models.DateField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.fees_structure:
            ext = self.fees_structure.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise ValidationError("Only PDF files are allowed. Ensure you convert the file you want to upload to PDF")
            
    def __str__(self):
        return self.fees_structure_description
    



class TeachingStaff(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    
    #Personal Information
    tsc_number = models.CharField(max_length=200,unique=True)
    id_number=models.CharField( max_length=255,unique=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    curriculum_vitae = models.FileField(upload_to='curriculum vitae/')
    position = models.TextField()
    awards = models.TextField(blank=True, null=True)
    professional_organizations = models.CharField(max_length=200)
    employment_date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    


    def clean(self):
        super().clean()
        if self.curriculum_vitae:
            ext = self.curriculum_vitae.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise ValidationError("Only PDF files are allowed. Ensure you convert the file you want to upload to PDF")
    
    def __str__(self):
        return self.full_name
    

class NonTeachingStaff(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    id_number=models.CharField( max_length=255,unique=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    curriculum_vitae = models.FileField(upload_to='curriculum vitae/',blank=True)
    employment_duration = models.CharField(max_length=200,blank=True)
    employment_date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.curriculum_vitae:
            ext = self.curriculum_vitae.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise ValidationError("Only PDF files are allowed. Ensure you convert the file you want to upload to PDF")
    
    

    def __str__(self):
        return self.full_name
    


class New(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True)
    date_uploaded = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
            

class StudentResult(models.Model):
    year = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    EXAMINATION_CHOICES = (
        ('AGRICULTURE', 'Agriculture'),
        ('BRAILLE LITERACY', 'Braille Literacy Activities'),
        ('BUSINESS STUDIES', 'Business Studies'),
        ('COMPUTER SCIENCE', 'Computer Science'),
        ('CREATIVE ARTS', 'Creative Arts'),
        ('ENGLISH LANGUAGE_ACTIVITIES', 'English Language Activities'),
        ('ENVIRONMENTAL ACTIVITIES', 'Environmental Activities'),
        ('FOREIGN LANGUAGES', 'Foreign Languages (German, French, Mandarin, or Arabic)'),
        ('HEALTH_EDUCATION', 'Health Education'),
        ('HOME SCIENCE', 'Home Science'),
        ('HYGIENE AND_NUTRITION_ACTIVITIES', 'Hygiene and Nutrition Activities'),
        ('INDIGENOUS_LANGUAGES', 'Indigenous Languages'),
        ('INTEGRATED SCIENCE', 'Integrated Science'),
        ('KENYA SIGN LANGUAGE', 'Kenya Sign Language'),
        ('KISWAHILI LANGUAGE_ACTIVITIES', 'Kiswahili Language Activities'),
        ('LIFE_SKILLS', 'Life Skills'),
        ('MATHEMATICAL ACTIVITIES', 'Mathematical Activities'),
        ('MATHEMATICS', 'Mathematics'),
        ('MOVEMENT AND CREATIVE_ACTIVITIES', 'Movement and Creative Activities'),
        ('PERFORMING ARTS', 'Performing Arts'),
        ('PHYSICAL AND_HEALTH_EDUCATION', 'Physical and Health Education'),
        ('PRE_BRAILLE ACTIVITIES', 'Pre Braille Activities'),
        ('PRE_TECHNICAL AND PRE_CAREER_EDUCATION', 'Pre-Technical and Pre-Career Education'),
        ('RELIGIOUS EDUCATION ACTIVITIES', 'Religious Education Activities'),
        ('RELIGIOUS EDUCATION', 'Religious Education (CRE)'),
        ('RELIGIOUS EDUCATION', 'Religious Education (IRE)'),
        ('RELIGIOUS EDUCATION', 'Religious Education (HRE)'),
        ('SCIENCE AND TECHNOLOGY', 'Science and Technology'),
        ('SOCIAL STUDIES', 'Social Studies'),
        ('SPORTS AND PHYSICAL EDUCATION', 'Sports and Physical Education'),
        ('VISUAL ARTS', 'Visual Arts'),
    )
    TERM_CHOICES = (
        ('TERM 1', 'TERM 1'),
        ('TERM 2', 'TERM 2'),
        ('TERM 3', 'TERM 3'),
    )

    GRADE_CHOICES = (
        ('PP1', 'PP1'),
        ('PP2', 'PP2'),
        ('grade1', 'GRADE1'),
        ('grade2', 'GRADE2'),
        ('grade3', 'GRADE3'),
        ('grade4', 'GRADE4'),
        ('grade5', 'GRADE5'),
        ('grade6', 'GRADE6'),
        ('grade7', 'GRADE7'),
        ('grade8', 'GRADE8'),
        ('grade9', 'GRADE9'),
        
    )
    student_grade_level = models.CharField(max_length=200,blank=True,choices= GRADE_CHOICES)
    term_or_semester_name = models.CharField(max_length=200, choices=TERM_CHOICES)
    examination = models.CharField(max_length=200, choices=EXAMINATION_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    
    teacher_comments= models.CharField(max_length=20,blank=True)
    date_uploaded = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.examination}: {self.score}"
    


class StaffGovernmentDeduction(models.Model):
    TEACHING_STAFF = 'TS'
    NON_TEACHING_STAFF = 'NTS'
    STAFF_CHOICES = [
        (TEACHING_STAFF, 'Teaching Staff'),
        (NON_TEACHING_STAFF, 'Non-Teaching Staff'),
    ]

    staff_type = models.CharField(max_length=3, choices=STAFF_CHOICES)
    staff_name = models.ForeignKey(
        to='TeachingStaff',
        on_delete= models.PROTECT,
        blank=True,
        null=True,
    )
    non_teaching_staff_name = models.ForeignKey(
        to='NonTeachingStaff',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    # Add other fields related to government deductions here
    deducted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    name_of_deduction = models.CharField(max_length=100, default='NHIF')
    date_deducted = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.staff_type == self.TEACHING_STAFF and self.staff_name:
            return f"Teaching Staff Deduction for {self.staff_name.full_name}"
        elif self.staff_type == self.NON_TEACHING_STAFF and self.non_teaching_staff_name:
            return f"Non-Teaching Staff Deduction for {self.non_teaching_staff_name.full_name}"
        return "Unnamed Deduction"



class Bill(models.Model):
    name_of_the_bill = models.CharField(max_length=250, default='Electricity Bill')
    amount_payed_for_the_bill = models.DecimalField(max_digits=10, decimal_places=2)
    date_payed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name_of_the_bill} - Amount: {self.amount_payed_for_the_bill} - Date Paid: {self.date_payed}"
    

  
class LogoImage(models.Model):
    logo = models.ImageField(upload_to='logo_images')

    def save(self, *args, **kwargs):
        # Delete any existing logo images before saving the new one
        LogoImage.objects.all().delete()
        super(LogoImage, self).save(*args, **kwargs) 


    



