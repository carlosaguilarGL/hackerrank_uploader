from .models import Question, Option
import csv
from django.db import transaction

@transaction.atomic
def create_questions(content):
    """
    Create Questions and Options from a CSV content stream.
    This method is not optimized for large amount of questions since it
    creates the questions 1 by 1
    """
    questions = []
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    skip_status = ['done', 'skip']
    for row in csv.DictReader(content):
        if row['Status'].lower() in skip_status:
            continue
        answers = row['Answers']
        hr_id = None
        try:
            question = Question.objects.get(name=row['Name'])
            hr_id = question.hr_id
            question.delete()
        except Question.DoesNotExist:
            pass
        finally:
            question = Question.objects.create(
                name=row['Name'],
                tags=row['Tags'],
                recommended_time=row['Recommended_time'],
                description=row['Description'],
                score=row['Score'],
                hr_id=hr_id
            )
        question.option_set.set([
            Option.objects.create(
                letter=letter,
                text=row[letter],
                is_answer=letter in answers,
                question=question
            )
            for letter in letters if letter in row and row[letter]
        ])
        questions.append(question)
    return questions