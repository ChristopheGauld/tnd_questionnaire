from django.contrib import admin

from .models import Answer, Option, Page, Question, Questionnaire, Response


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ('order', 'prompt', 'question_type', 'required', 'help_text', 'source_reference')


class PageInline(admin.StackedInline):
    model = Page
    extra = 0
    fields = ('order', 'title', 'instructions')


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'public_id', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title',)
    readonly_fields = ('public_id', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PageInline]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionnaire', 'order')
    list_filter = ('questionnaire',)
    search_fields = ('title', 'instructions')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_prompt', 'page', 'question_type', 'required', 'order')
    list_filter = ('question_type', 'required', 'page__questionnaire')
    search_fields = ('prompt', 'help_text', 'source_reference')
    inlines = [OptionInline]

    @admin.display(description='Question')
    def short_prompt(self, obj):
        return obj.prompt[:100]


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'participant_code', 'started_at', 'completed_at')
    list_filter = ('questionnaire', 'completed_at')
    search_fields = ('participant_code', 'token')
    readonly_fields = ('token', 'started_at', 'updated_at', 'completed_at')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'answered_at')
    list_filter = ('response__questionnaire',)
    search_fields = ('question__prompt', 'response__participant_code')

# Register your models here.
