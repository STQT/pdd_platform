import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.questions.models import Category, Question, Answer


class Command(BaseCommand):
    help = "Import questions from questions.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="questions.json",
            help="Path to questions.json",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            self.stderr.write(f"File not found: {path}")
            return

        data = json.loads(path.read_text(encoding="utf-8"))
        self.stdout.write(f"Importing {len(data)} questions...")

        categories: dict[int, Category] = {}
        for item in data:
            cid = item["category_id"]
            if cid not in categories:
                cat, _ = Category.objects.get_or_create(
                    id=cid,
                    defaults={
                        "title_ru": item["category_title"],
                        "title_kz": item.get("category_title_kz", ""),
                        "order": cid,
                    },
                )
                categories[cid] = cat

        created = updated = 0
        for item in data:
            category = categories[item["category_id"]]
            q_text = item["question"]
            answers_data = item["answers"]
            correct_id = item["correct_answer_id"]

            # Find correct answer index (0-based)
            correct_idx = next(
                (i for i, a in enumerate(answers_data) if a["id"] == correct_id), 0
            )

            media = item.get("media") or {}
            q_media = media.get("question_file", "") or ""
            e_media = media.get("explanation_file", "") or ""

            # Strip "media/" prefix — stored relative to MEDIA_ROOT
            q_media = q_media.replace("media/", "", 1) if q_media.startswith("media/") else q_media
            e_media = e_media.replace("media/", "", 1) if e_media.startswith("media/") else e_media

            question, is_new = Question.objects.update_or_create(
                original_id=item["id"],
                defaults={
                    "category": category,
                    "text_ru": q_text.get("ru", ""),
                    "text_kz": q_text.get("kz", ""),
                    "text_en": q_text.get("en", ""),
                    "question_media": q_media,
                    "explanation_media": e_media,
                    "correct_answer_index": correct_idx,
                },
            )

            if is_new:
                created += 1
            else:
                updated += 1

            # Recreate answers
            question.answers.all().delete()
            for order, ans in enumerate(answers_data):
                Answer.objects.create(
                    question=question,
                    original_id=ans["id"],
                    text_ru=ans["title"].get("ru", ""),
                    text_kz=ans["title"].get("kz", ""),
                    text_en=ans["title"].get("en", ""),
                    order=order,
                    is_correct=(ans["id"] == correct_id),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated | "
                f"{Category.objects.count()} categories"
            )
        )
