from pathlib import PurePosixPath

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import F, OuterRef, Subquery, Sum
from django.utils import timezone

GRADE_CHOICES = [
    ("PP1", "PP1"),
    ("PP2", "PP2"),
    *((f"grade{number}", f"Grade {number}") for number in range(1, 10)),
]
GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]
PDF_ONLY = FileExtensionValidator(["pdf"], "Upload a PDF. Convert other documents to PDF first.")


class CustomUserManager(BaseUserManager):
    @classmethod
    def normalize_id_number(cls, id_number):
        return id_number.strip().lower()

    def get_by_natural_key(self, id_number):
        return self.get(id_number=self.normalize_id_number(id_number))

    def create_user(self, id_number, password=None, **extra_fields):
        if not id_number:
            raise ValueError("An ID, admission or TSC number is required.")
        user = self.model(id_number=self.normalize_id_number(id_number), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(id_number, password, **extra_fields)


class CustomUser(AbstractUser):
    """A student, staff member or administrator.

    Students sign in with their admission number, teachers with their TSC number
    and other staff with their national ID number. Numbers are stored in lower case.
    """

    username = None
    last_name = None
    id_number = models.CharField("ID, admission or TSC number", unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)

    objects = CustomUserManager()

    USERNAME_FIELD = "id_number"
    REQUIRED_FIELDS = ["first_name", "surname", "phone_number"]

    def __str__(self):
        return self.id_number

    def save(self, *args, **kwargs):
        self.id_number = CustomUserManager.normalize_id_number(self.id_number)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.second_name, self.surname]))

    def get_short_name(self):
        return self.first_name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    RELATIONSHIP_CHOICES = [
        ("parent or guardian", "Parent or guardian"),
        ("uncle", "Uncle"),
        ("aunt", "Aunt"),
        ("grandparent", "Grandparent"),
        ("cousin", "Cousin"),
        ("trusted family friend", "Trusted family friend"),
    ]
    NATIONALITY_CHOICES = [("kenyan", "Kenyan"), ("others", "Other")]

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100, choices=NATIONALITY_CHOICES)
    student_admission_number = models.CharField(max_length=20, unique=True)
    grade_level = models.CharField(max_length=10, choices=GRADE_CHOICES)
    subjects = models.ManyToManyField(Subject, related_name="students", blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    clubs_organizations = models.TextField(blank=True)
    sports_participation = models.TextField(blank=True)
    awards = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=100, choices=RELATIONSHIP_CHOICES)
    emergency_contact_phone = models.CharField(max_length=20)
    parent_guardian_name = models.CharField(max_length=255)
    parent_guardian_phone = models.CharField(max_length=20)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_admission_number"]

    def __str__(self):
        return f"{self.student_admission_number} – {self.full_name}"

    @classmethod
    def for_user(cls, user):
        """The student record that belongs to a signed-in user, if they are a student."""
        if not user.is_authenticated:
            return None
        return cls.objects.filter(student_admission_number__iexact=user.id_number).first()


class LandingPageImage(models.Model):
    CATEGORY_CHOICES = [
        ("ACADEMICS", "Academics"),
        ("COCURRICULAR", "Co-curricular"),
        ("ICT", "ICT"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    picture = models.ImageField(upload_to="landing_page_pictures/")
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.get_category_display()} picture from {self.date}"


class LogoImage(models.Model):
    """The school logo; uploading a new one replaces the old."""

    logo = models.ImageField(upload_to="logo_images/")

    def __str__(self):
        return self.logo.name

    def save(self, *args, **kwargs):
        LogoImage.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)


class EducationalResource(models.Model):
    CATEGORY_CHOICES = [
        ("Past Examinations", "Past examinations"),
        ("ebooks", "E-books and study guides"),
        ("Educational pictures", "Educational pictures"),
        ("Educational Videos", "Educational videos"),
        ("Educational links", "Educational links"),
        ("General Resources", "General resources"),
    ]
    ALL_STUDENTS = "All students"
    AUDIENCE_CHOICES = [*GRADE_CHOICES, (ALL_STUDENTS, "All students")]
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}

    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="resources")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    appropriate_grade = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    file = models.FileField(upload_to="EducationalResources/", blank=True)
    link = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at", "-pk"]

    def __str__(self):
        return self.title

    @property
    def media_kind(self):
        """How the file should be shown: "image", "video", "download", or "" when there is none."""
        if not self.file:
            return ""
        extension = PurePosixPath(self.file.name).suffix.lower()
        if extension in self.IMAGE_EXTENSIONS:
            return "image"
        if extension in self.VIDEO_EXTENSIONS:
            return "video"
        return "download"


class Term(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    total_fees_payable = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date:%d %B %Y} to {self.end_date:%d %B %Y})"


class FeePaymentQuerySet(models.QuerySet):
    def with_running_balance(self):
        """Annotate each payment with the fees still owed for its term after it was made.

        The total paid so far is a correlated subquery over all of the student's
        payments for the term, so it stays correct however the queryset is filtered.
        """
        paid_to_date = (
            self.model.objects.filter(
                student=OuterRef("student"), term=OuterRef("term"), pk__lte=OuterRef("pk")
            )
            .order_by()
            .values("student", "term")
            .annotate(total=Sum("amount_paid"))
            .values("total")
        )
        return self.annotate(
            paid_to_date=Subquery(paid_to_date),
            balance_after=F("term__total_fees_payable") - F("paid_to_date"),
        )


class FeePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Bank deposit", "Bank deposit"),
        ("Bank Transfer", "Bank transfer"),
        ("M-pesa Payment", "M-Pesa"),
    ]

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="fee_payments")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="fee_payments")
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    objects = FeePaymentQuerySet.as_manager()

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.amount_paid} from {self.student} for {self.term.name}"


class AnyOtherPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="other_payments")
    payment_for = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} from {self.student.full_name} for {self.payment_for}"


class FeesStructure(models.Model):
    fees_structure_description = models.TextField("description")
    fees_structure = models.FileField("PDF", upload_to="fees_structure/", validators=[PDF_ONLY])
    upload_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-upload_date", "-pk"]

    def __str__(self):
        return self.fees_structure_description


class TeachingStaff(models.Model):
    tsc_number = models.CharField("TSC number", max_length=200, unique=True)
    id_number = models.CharField("ID number", max_length=255, unique=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    curriculum_vitae = models.FileField(upload_to="curriculum_vitae/", validators=[PDF_ONLY])
    position = models.TextField()
    awards = models.TextField(blank=True)
    professional_organizations = models.CharField(max_length=200)
    employment_date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "teaching staff"

    def __str__(self):
        return self.full_name


class NonTeachingStaff(models.Model):
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField("ID number", max_length=255, unique=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    curriculum_vitae = models.FileField(
        upload_to="curriculum_vitae/", blank=True, validators=[PDF_ONLY]
    )
    employment_duration = models.CharField(max_length=200, blank=True)
    employment_date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "non-teaching staff"

    def __str__(self):
        return self.full_name


class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="news_images/", blank=True)
    date_uploaded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date_uploaded", "-pk"]

    def __str__(self):
        return self.title


class StudentResult(models.Model):
    EXAMINATION_CHOICES = [
        ("AGRICULTURE", "Agriculture"),
        ("BRAILLE LITERACY", "Braille Literacy Activities"),
        ("BUSINESS STUDIES", "Business Studies"),
        ("COMPUTER SCIENCE", "Computer Science"),
        ("CREATIVE ARTS", "Creative Arts"),
        ("ENGLISH LANGUAGE ACTIVITIES", "English Language Activities"),
        ("ENVIRONMENTAL ACTIVITIES", "Environmental Activities"),
        ("FOREIGN LANGUAGES", "Foreign Languages (German, French, Mandarin, or Arabic)"),
        ("HEALTH EDUCATION", "Health Education"),
        ("HOME SCIENCE", "Home Science"),
        ("HYGIENE AND NUTRITION ACTIVITIES", "Hygiene and Nutrition Activities"),
        ("INDIGENOUS LANGUAGES", "Indigenous Languages"),
        ("INTEGRATED SCIENCE", "Integrated Science"),
        ("KENYA SIGN LANGUAGE", "Kenya Sign Language"),
        ("KISWAHILI LANGUAGE ACTIVITIES", "Kiswahili Language Activities"),
        ("LIFE SKILLS", "Life Skills"),
        ("MATHEMATICAL ACTIVITIES", "Mathematical Activities"),
        ("MATHEMATICS", "Mathematics"),
        ("MOVEMENT AND CREATIVE ACTIVITIES", "Movement and Creative Activities"),
        ("PERFORMING ARTS", "Performing Arts"),
        ("PHYSICAL AND HEALTH EDUCATION", "Physical and Health Education"),
        ("PRE-BRAILLE ACTIVITIES", "Pre-Braille Activities"),
        ("PRE-TECHNICAL AND PRE-CAREER EDUCATION", "Pre-Technical and Pre-Career Education"),
        ("RELIGIOUS EDUCATION ACTIVITIES", "Religious Education Activities"),
        ("RELIGIOUS EDUCATION CRE", "Religious Education (CRE)"),
        ("RELIGIOUS EDUCATION IRE", "Religious Education (IRE)"),
        ("RELIGIOUS EDUCATION HRE", "Religious Education (HRE)"),
        ("SCIENCE AND TECHNOLOGY", "Science and Technology"),
        ("SOCIAL STUDIES", "Social Studies"),
        ("SPORTS AND PHYSICAL EDUCATION", "Sports and Physical Education"),
        ("VISUAL ARTS", "Visual Arts"),
    ]
    TERM_CHOICES = [("TERM 1", "Term 1"), ("TERM 2", "Term 2"), ("TERM 3", "Term 3")]

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="results")
    year = models.PositiveSmallIntegerField()
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    student_grade_level = models.CharField(max_length=10, blank=True, choices=GRADE_CHOICES)
    examination = models.CharField(max_length=50, choices=EXAMINATION_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    teacher_comments = models.CharField(max_length=255, blank=True)
    date_uploaded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-term", "examination"]

    def __str__(self):
        return f"{self.student} – {self.get_examination_display()}: {self.score}"


class StaffGovernmentDeduction(models.Model):
    """A statutory deduction (NHIF and similar) for one member of staff."""

    TEACHING_STAFF = "TS"
    NON_TEACHING_STAFF = "NTS"
    STAFF_CHOICES = [(TEACHING_STAFF, "Teaching staff"), (NON_TEACHING_STAFF, "Non-teaching staff")]

    staff_type = models.CharField(max_length=3, choices=STAFF_CHOICES)
    teaching_staff = models.ForeignKey(
        TeachingStaff, on_delete=models.PROTECT, blank=True, null=True
    )
    non_teaching_staff = models.ForeignKey(
        NonTeachingStaff, on_delete=models.PROTECT, blank=True, null=True
    )
    deducted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    name_of_deduction = models.CharField(max_length=100, default="NHIF")
    date_deducted = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(staff_type="TS", teaching_staff__isnull=False, non_teaching_staff=None)
                    | models.Q(
                        staff_type="NTS", non_teaching_staff__isnull=False, teaching_staff=None
                    )
                ),
                name="deduction_names_exactly_one_staff_member_of_its_type",
            ),
        ]

    def __str__(self):
        return f"{self.name_of_deduction} for {self.staff_member}"

    @property
    def staff_member(self):
        return self.teaching_staff or self.non_teaching_staff


class Bill(models.Model):
    name_of_the_bill = models.CharField(max_length=250, default="Electricity Bill")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_paid"]

    def __str__(self):
        return f"{self.name_of_the_bill} – {self.amount_paid} on {self.date_paid:%d %b %Y}"
