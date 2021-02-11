from django.contrib import admin
from .models import Question, Option
from .forms import CsvUploadForm
from .helpers import create_questions
from .actions import send_to_hacker_rank
from django.shortcuts import redirect
from django.urls import path
from django.utils.safestring import mark_safe
from django.contrib.messages import constants as messages
import io, csv


class OptionAdmin(admin.TabularInline):
    model = Option


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    change_list_template = "custom_admin/csv_form.html"
    list_display = [
        'id', 'name', 'tags', 'recommended_time', 'description', 'score',
        'options', 'answers', 'hr_id', 'status'
    ]
    list_editable = ['description', 'hr_id', 'status']
    inlines = [OptionAdmin]
    actions = [send_to_hacker_rank]

    @mark_safe
    def options(self, obj):
        return ''.join(
            f'<p>{o.letter}-{o.text}</p>'
            for o in obj.option_set.order_by('letter')
        )

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [path("upload-csv/", self.upload_csv)]
        return additional_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra = extra_context or {}
        extra["csv_upload_form"] = CsvUploadForm()
        return super(QuestionAdmin, self).changelist_view(
            request, extra_context=extra
        )

    def upload_csv(self, request):
        if request.method == "POST":
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                if request.FILES['csv_file'].name.endswith('csv'):
                    try:
                        questions = create_questions(
                            io.TextIOWrapper(request.FILES['csv_file'])
                        )
                    except UnicodeDecodeError as e:
                        self.message_user(
                            request,
                            "There was an error decoding the file:{}".format(e),
                            level=messages.ERROR
                        )
                        return redirect("..")
            else:
                self.message_user(
                request,
                "Incorrect file type: {}".format(
                    request.FILES['csv_file'].name.split(".")[1]
                    ),
                level=messages.ERROR
                )
        else:
            self.message_user(
                request,
                "There was an error in the form {}".format(form.errors),
                level=messages.ERROR
            )

        return redirect("..")
