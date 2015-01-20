from django.core import exceptions
from django.db import models
from jsonfield import JSONField, JSONCharField
from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from cr_server import settings
from cr_app import codes
import collections
import json

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
    category = models.CharField(max_length=160, choices=codes.INSIGHT_CATEGORIES)

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

    def sync_insight_vote(self, vote):

        insight = self.insight_votes[vote.insight.category][vote.insight.name]
        total_vote_count = insight["vote_total"]
        insight_votes = insight["insight_votes"][json.dumps(vote.choice.pk)]
        insight_votes_count = insight_votes['count']

        if (insight_votes_count >=0) and (total_vote_count >=0):
            insight.__setitem__("vote_total", total_vote_count+1)
            insight_votes.__setitem__('count', insight_votes_count+1)

    # def modify_insight_vote(self, old_vote, new_vote):
    #
    #     new_insight = self.insight_votes[new_vote.insight.category][new_vote.insight.name]
    #     old_insight = self.insight_votes[old_vote.insight.category][old_vote.insight.name]
    #
    #     if old_vote.insight != new_vote.insight:
    #
    #         old_vote_total = old_insight["vote_total"]
    #         new_vote_total = new_insight["vote_total"]
    #
    #         if old_vote_total > 0:
    #             old_insight.__setitem__("vote_total", old_vote_total-1)
    #             new_insight.__setitem__("vote_total", new_vote_total+1)
    #
    #     if (old_vote.choice != new_vote.choice):
    #         old_insight_votes = old_insight["insight_votes"][json.dumps(old_vote.choice.pk)]
    #         new_insight_votes = new_insight["insight_votes"][json.dumps(new_vote.choice.pk)]
    #
    #         old_insight_choice_count = old_insight["insight_votes"][json.dumps(old_vote.choice.pk)]['count']
    #         new_insight_choice_count = new_insight["insight_votes"][json.dumps(new_vote.choice.pk)]['count']
    #
    #         if old_insight_choice_count > 0:
    #             old_insight_votes.__setitem__('count', old_insight_choice_count-1)
    #             new_insight_votes.__setitem__('count', new_insight_choice_count+1)

    def remove_insight_vote(self, vote):
        insight = self.insight_votes[vote.insight.category][vote.insight.name]
        total_vote_count = insight["vote_total"]
        insight_votes = insight["insight_votes"][json.dumps(vote.choice.pk)]
        insight_votes_count = insight_votes['count']

        if (insight_votes_count >0) and (total_vote_count >0):
            insight.__setitem__("vote_total", total_vote_count-1)
            insight_votes.__setitem__('count', insight_votes_count-1)


class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    article = models.ForeignKey(Article, related_name="questions")
    title = models.CharField(max_length=160)
    upvotes = models.PositiveIntegerField(default=0)
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
            raise exceptions.ValidationError("You have already upvoted this question", code=codes.ALREADY_UPVOTED, params={"pk": existing_upvote.pk})


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
            existing_vote = Vote.objects.get(user=self.user, article=self.article, insight=self.insight)

            if existing_vote is not None:
                raise exceptions.ValidationError("You can't vote twice", code=codes.DUPLICATE_VOTE, params={"pk": existing_vote.pk})

        except exceptions.ObjectDoesNotExist:
            pass



#recievers for keeping an articles insight_votes dict in sync with submitted Votes
#this way when when the front end asks for vote counts, the data is right on the article
#they won't have to perform a long query for it
@receiver(m2m_changed, sender=Article.insights.through)
def update_insight_votes_keys(sender, instance, action, model, pk_set, **kwargs):

        if (action == 'post_add') or (action == 'post_remove'):
            article = instance
            article.insight_votes = dict()

            for insight in article.insights.all():

                if insight.category in article.insight_votes:
                    category_dict = article.insight_votes[insight.category]
                else:
                    category_dict = article.insight_votes[insight.category] = {}

                if insight.name in article.insight_votes[insight.category]:
                    insight_dict = article.insight_votes[insight.category][insight.name]
                else:
                    insight_dict =article.insight_votes[insight.category][insight.name] = {}

                insight_dict["category"] = insight.category
                insight_dict["pk"] = insight.pk
                insight_dict["name"] = insight.name

                insight_votes = article.votes.filter(insight=insight)

                insight_dict["vote_total"] = insight_votes.count()
                insight_dict["enabled"] = True
                insight_dict["insight_votes"] = {choice.pk:{"choice":choice.choice_text,"count":insight_votes.filter(choice=choice).count()} for choice in insight.choices.all()}

            article.save()


@receiver(pre_save, sender=Vote)
def update_insight_votes_on_add(sender, instance, **kwargs):
    vote = instance
    article = Article.objects.get(pk=instance.article.pk)

    if not vote.pk:
        article.sync_insight_vote(vote)

    # else:
    #     old_vote = Vote.objects.get(pk=vote.pk)
    #     article.modify_insight_vote(old_vote, vote)

    article.save()


@receiver(post_delete, sender=Vote)
def update_insight_votes_on_delete(sender, instance, **kwargs):
    vote = instance
    article = Article.objects.get(pk=instance.article.pk)
    article.remove_insight_vote(vote)
    article.save()