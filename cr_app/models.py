from django.core import exceptions
from django.db import models
from jsonfield import JSONField
from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from cr_server import settings
from cr_app import errors

class Publisher(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Author(models.Model):

    name = models.CharField(max_length=30)
    publishers = models.ManyToManyField(Publisher)

    def __str__(self):
        return self.name

#represents an article poll question that can be voted on
class CRInsight(models.Model):

    name = models.CharField(max_length=160)

    def __str__(self):
        return self.name

class CRInsightChoice(models.Model):

    insight = models.ForeignKey(CRInsight, related_name="choices")
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text


class Article(models.Model):

    title = models.CharField(max_length=160)
    url = models.URLField(max_length=2083)
    date = models.DateField()
    authors = models.ManyToManyField(Author, related_name="articles")
    publisher = models.ForeignKey(Publisher, related_name="articles")
    insights = models.ManyToManyField(CRInsight, related_name="articles")
    insight_votes = JSONField(default={}) #will eventually be on firebase

    def __str__(self):
        return self.title

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    article = models.ForeignKey(Article, related_name="questions")
    title = models.CharField(max_length=160)
    upvotes = models.IntegerField(default=0)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def upvote(self, user):
        upvote = UpVote(user=user, question=self)
        upvote.clean()
        upvote.save()

        self.upvotes += 1
        self.save()

        return upvote

    def downvote(self, user, upvote):

        upvote.delete()

        self.upvotes -= 1
        self.save()

    def answer(self):
        if not self.answered:
            self.answered = True

class UpVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    question = models.ForeignKey(Question, related_name="question_upvotes")

    def clean(self):
        existing_upvote = None

        try:
            existing_upvote = UpVote.objects.get(user=self.user, question=self.question)
        except exceptions.ObjectDoesNotExist:
            #exisitng upvote by user on this question doesn't exist, let them save
            pass

        if existing_upvote is not None:
            raise exceptions.ValidationError("You have already upvoted this question", code=errors.ALREADY_UPVOTED, params={"pk": existing_upvote.pk})


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    question = models.ForeignKey(Question, related_name="answers")
    answer = models.TextField()

    def save(self, *args, **kwargs):
        super(Answer, self).save(*args, **kwargs)
        question = Question.objects.get(pk=self.question.pk)
        question.answer()


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    article = models.ForeignKey(Article, related_name="votes")
    insight = models.ForeignKey(CRInsight, related_name="votes")
    choice = models.ForeignKey(CRInsightChoice, related_name="votes")

    def __str__(self):
        return 'Vote for '+self.insight.name.__str__()


    def clean(self, *args, **kwargs):
        super(Vote, self).clean(*args, **kwargs)
        if self.insight not in self.article.insights.all():
            raise exceptions.ValidationError(self.insight.name + " is not enabled for this article")

        if self.choice not in self.insight.choices.all():
            raise exceptions.ValidationError(self.choice.choice_text + " is not an option for this topic")

        existing_vote = None

        try:
            existing_vote = Vote.objects.get(user=self.user, article=self.article, insight=self.insight, choice=self.choice)

            if existing_vote is not None:
                raise exceptions.ValidationError("You can't vote  make the same vote twice", code=errors.DUPLICATE_VOTE, params={"pk": existing_vote.pk})

        except exceptions.ObjectDoesNotExist:
            pass



#recievers for keeping an articles insight_votes dict in sync with submitted Votes
#this way when when the front end asks for vote counts, the data is right on the article
#they won't have to perform a long query for it
@receiver(m2m_changed, sender=Article.insights.through)
def update_insight_votes_keys(sender, instance, action, model, pk_set, **kwargs):
    if action == 'post_add':
        article = instance
        changed = False
        for insight in CRInsight.objects.filter(pk__in=pk_set):
            if insight.name not in article.insight_votes:
                changed = True
                article.insight_votes[insight.name] = {}
                insight_choices = article.insight_votes[insight.name]
                for choice in insight.choices.all():
                    insight_choices[choice.choice_text] = 0
        if changed:
            article.save()

@receiver(pre_save, sender=Vote)
def update_insight_votes_on_add(sender, instance, **kwargs):
    vote = instance
    article = Article.objects.get(pk=vote.article.pk)
    insights_votes = article.insight_votes
    #new vote
    if not vote.pk:
        insight_choices = insights_votes[vote.insight.name]
        insight_choices[vote.choice.choice_text] += 1

    else:
        old_vote = Vote.objects.get(pk=vote.pk)
        if old_vote.choice != vote.choice: #if you're changing your vote choice
            insights_votes[old_vote.insight.name][old_vote.choice.choice_text] -= 1
            insights_votes[vote.insight.name][vote.choice.choice_text] += 1

    # article.save()


@receiver(post_delete, sender=Vote)
def update_insight_votes_on_delete(sender, instance, **kwargs):
    vote = instance
    article = Article.objects.get(pk=vote.article.pk)
    insights_votes = article.insight_votes
    insights_votes[vote.insight.name][vote.choice.choice_text] -= 1

    article.save()

# reciveres for updating a questions upvotes field when an upvote is saved or deleted
# @receiver(post_save, sender=UpVote)
# def update_upvotes_on_add(sender, instance, **kwargs):
#     upvote = instance
#     question = Question.objects.get(pk=upvote.question.pk)
#     question.upvote(user=upvote.user)
#
# @receiver(post_delete, sender=UpVote)
# def update_upvotes_on_delete(sender, instance, **kwargs):
#     upvote = instance
#     question = Question.objects.get(pk=upvote.question.pk)
#     question.downvote(user=upvote.user)
