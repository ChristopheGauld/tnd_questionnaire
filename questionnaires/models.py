import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Questionnaire(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    introduction = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240] or str(self.public_id)
        super().save(*args, **kwargs)

    def get_public_url(self):
        return reverse('questionnaire_start', kwargs={'public_id': self.public_id})

    def __str__(self):
        return self.title


class Page(models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.CASCADE,
        related_name='pages',
    )
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['questionnaire', 'order', 'id']
        unique_together = [('questionnaire', 'order')]

    def __str__(self):
        return f'{self.order}. {self.title}'


class Question(models.Model):
    TEXT = 'text'
    TEXTAREA = 'textarea'
    NUMBER = 'number'
    DATE = 'date'
    EMAIL = 'email'
    PHONE = 'phone'
    SINGLE = 'single'
    MULTIPLE = 'multiple'
    SCALE = 'scale'
    DISPLAY = 'display'

    QUESTION_TYPES = [
        (TEXT, 'Texte court'),
        (TEXTAREA, 'Texte long'),
        (NUMBER, 'Nombre'),
        (DATE, 'Date'),
        (EMAIL, 'E-mail'),
        (PHONE, 'Téléphone'),
        (SINGLE, 'Choix unique'),
        (MULTIPLE, 'Choix multiple'),
        (SCALE, 'Échelle'),
        (DISPLAY, 'Texte informatif'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='questions')
    prompt = models.TextField()
    help_text = models.TextField(blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=TEXT)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    source_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['page', 'order', 'id']
        unique_together = [('page', 'order')]

    def has_options(self):
        return self.options.exists()

    def __str__(self):
        return self.prompt[:90]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['question', 'order', 'id']
        unique_together = [('question', 'order')]

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.label
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


class Response(models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.CASCADE,
        related_name='responses',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    participant_code = models.CharField(max_length=120, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    @property
    def is_complete(self):
        return self.completed_at is not None

    def __str__(self):
        code = self.participant_code or self.token
        return f'{self.questionnaire} - {code}'


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    value = models.JSONField(blank=True, default=dict)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('response', 'question')]
        ordering = ['response', 'question__page__order', 'question__order']

    def as_export_value(self):
        raw = self.value.get('value', '')
        if isinstance(raw, list):
            return '; '.join(str(item) for item in raw)
        return raw

    def __str__(self):
        return f'{self.response_id} / {self.question_id}'

# Create your models here.
