from django.db import models
from tinymce import models as tinymce_models


class Question(models.Model):
    name = models.CharField(max_length=500, unique=True)
    tags = models.CharField(max_length=500, default='gl-all-python,gl-junior')
    recommended_time = models.SmallIntegerField(default=2)
    description = tinymce_models.HTMLField()
    score = models.IntegerField(blank=True, null=True)
    hr_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Option(models.Model):
    letter = models.CharField(max_length=1)
    text = models.TextField()
    is_answer = models.BooleanField(default=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.question}-{self.letter}-{self.text}'

    class Meta:
        unique_together = [['letter', 'question']]
