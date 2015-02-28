from django.contrib import admin
from django import forms
from cr_app import models
from django.db.models import Q, F

# class ManagePublisherInline(admin.StackedInline):
#     model = models.Publisher

class ManageInsightChoiceInline(admin.StackedInline):
    model = models.CRInsightChoice

class CRInsightAdmin(admin.ModelAdmin):
    inlines = [ManageInsightChoiceInline]

class VoteForm(forms.ModelForm):
    class Meta:
        model = models.Vote

    def __init__(self, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        try:
            self.fields['choice'].queryset = models.CRInsightChoice.objects.filter(insight=self.instance.insight)
        except Exception:
            pass

        try:
            self.fields["insight"].queryset = models.CRInsight.objects.filter(articles__pk=self.instance.article.pk)
        except Exception:
            pass

class ManageQuestionsInline(admin.StackedInline):
    model = models.Question
    readonly_fields = ["upvotes", "answered"]

class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ["upvotes"]

class ManageVotesInline(admin.StackedInline):
    model = models.Vote
    # form = VoteForm

class VoteAdmin(admin.ModelAdmin):
    form = VoteForm
    pass

class ArticleAdmin(admin.ModelAdmin):
    inlines = [ManageQuestionsInline]
    readonly_fields = ['insight_votes', 'pk']

# Register your models here.
admin.site.register(models.Author)
admin.site.register(models.Publisher)
admin.site.register(models.Vote)
admin.site.register(models.Answer)
admin.site.register(models.UpVote)


admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.CRInsight, CRInsightAdmin)

