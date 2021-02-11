import requests
from .models import Question, Option
from django.conf import settings
from django.contrib import messages


def send_to_hacker_rank(modeladmin, request, queryset):
    api_url = 'https://www.hackerrank.com/x/api/v3/questions'
    api_key = settings.HACKER_RANK_ACCESS_KEY
    auth=(api_key, '')

    if not api_key:
        raise Exception('Hacker rank access key not set on .env file')

    def create_question(data: dict, q: Question):
        q.hr_id = requests.post(api_url, auth=auth, json=data).json()['id']
        q.status = Question.Status.UPLOADED
        q.save()
        modeladmin.message_user(
            request, f'Question {q} was successfully created in Hacker Rank',
            messages.SUCCESS
        )
        
    def serialize_question(q: Question) -> dict:
        answers = q.answers
        return {
            "type": q.type,
            "name": q.name,
            "problem_statement": q.description,
            "recommended_duration": q.recommended_time,
            "tags": [t.strip() for t in q.tags.split(',')],
            "answer": answers if len(answers) > 1 else answers[0],
            "options": [o.text for o in q.option_set.all()],
            "max_score": q.score,
        }

    for q in queryset:
        data = serialize_question(q)
        try:
            if q.hr_id:
                url = f'{api_url}/{q.hr_id}'
                # Look for the question in haker rank to updated it
                res = requests.get(url, auth=auth)
                # check if exists and if is not archived
                if res.status_code == 200 and res.json()['status'] == 'active':
                    requests.put(url, auth=auth, json=data)
                    q.status = Question.Status.UPDATED
                    modeladmin.message_user(
                        request,
                        f'Question {q} was successfully updated in Hacker Rank',
                        messages.INFO
                    )
                    q.save()
                else:
                    create_question(data, q)
            else:
                create_question(data, q)
        except Exception:
            modeladmin.message_user(
                request, f'Question {q} failed to be added to Hacker Rank',
                messages.ERROR
            )
            q.status = Question.Status.FAILED
            q.save()
