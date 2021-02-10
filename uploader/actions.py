from .models import Question, Option

def send_to_hacker_rank(modeladmin, request, queryset):
    for q in queryset:
        print(q)