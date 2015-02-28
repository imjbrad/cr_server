from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver

__author__ = 'jordanbradley'

from cr_app.models import Article, Vote
from django.db.models import Q
import urlparse, urllib

class ArticleHelper(object):

    @staticmethod
    def clean_article_url(url):
        url = url.rstrip("/") #strip trailing slash
        url = urlparse.urlparse(url, "http")[0:3] + (("",)*3) #keep only scheme, netloc and path
        url = urlparse.urlunparse(url) #stich back together
        return url

    @staticmethod
    def find_article_with(article_url=None, article_id=None):
        article = None

        if (article_url is None) and (article_id is None):
            raise ValueError("Must Provide an article url or id to search for")

        if article_url is not None:
            article_url = urllib.unquote(article_url)
            article_url = ArticleHelper.clean_article_url(article_url)

        try:
            article = Article.objects.get(Q(url__exact=article_url) | Q(pk=article_id))
        except Article.DoesNotExist:
            pass

        return article

    #deprecated
    @staticmethod
    def collect_article_votes(article):

        if type(article) != Article:
            raise ValueError("Must Provide an Article")

        insights = article.insights.all()

        # {insight
        #     choice - votecount
        #     choice - votecoint
        # }

        insights_votes = {}
        votes = article.votes.all()

        for vote in votes:
            if vote.insight in insights_votes:
                insight_choices = insights_votes[vote.insight]
                insight_choices[vote.choice] += 1

            else:
                insight_choices = insights_votes[vote.insight] = {}
                for insight_choice in vote.insight.choices.all():
                    insight_choices[insight_choice] = 0
                    if vote.choice == insight_choice:
                        insight_choices[vote.choice] += 1



        article_data = {
            "pk": article.pk,
            "title": article.title,
            "authors": article.authors.all(),
            "date": article.date,
            "publisher": article.publisher,
            "insights_votes": insights_votes
        }

        return article_data

class ArticleInsightManager(object):
    pass