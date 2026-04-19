from django.db import models


class Category(models.Model):
    title_ru = models.CharField(max_length=255)
    title_kz = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ru


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")
    original_id = models.IntegerField(unique=True)
    text_ru = models.TextField()
    text_kz = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    question_media = models.CharField(max_length=500, blank=True)
    explanation_ru = models.TextField(blank=True)
    explanation_kz = models.TextField(blank=True)
    explanation_en = models.TextField(blank=True)
    explanation_media = models.CharField(max_length=500, blank=True)
    explanation2_media = models.CharField(max_length=500, blank=True)
    correct_answer_index = models.PositiveSmallIntegerField()  # 0-based index in answers

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Q{self.original_id}: {self.text_ru[:60]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    original_id = models.IntegerField()
    text_ru = models.TextField()
    text_kz = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"A{self.original_id}: {self.text_ru[:60]}"
