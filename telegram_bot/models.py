from django.db import models

# Create your models here.

class Patient(models.Model):
    user_id= models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.full_name}"

class UserTest(models.Model):
    STATUS_CHOICES=(
        ("boshlamagan", "Boshlamagan"),
        ("jarayonda", "Jarayonda"),
        ("tugatgan", "Tugatgan"),
    )

    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="tests")
    test_name = models.CharField(max_length=250)
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="boshlamagan")

    def __str__(self):
        return f"{self.user.full_name} - self{self.test_name}({self.status})"

class TestQuestion(models.Model):
    CATEGORY_CHOICES=[
        ("Umumiy", "Umumiy"),
        ("Bolajon", "Bolajon"),
        ("Nuroniy", "Nuroniy"),
        ("Baxtli Oila", "Baxtli Oila"),
        ("Kardio", "Kardio"),
        ("Neyro", "Neyro"),
        ("Onko", "Onko"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=250,null=True, blank=True)
    question_text = models.TextField()

    def __str__(self):
        return f"{self.question_text}"