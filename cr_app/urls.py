__author__ = 'jordanbradley'

from django.conf.urls import patterns, include, url
from django.contrib import admin
from cr_app import views

urlpatterns = patterns('',

    url(r'^article/(?P<pk>[\d]+)/topics/?', views.GetArticleInsightVotes.as_view(), name='article-insight-votes'),
    url(r'^article/(?P<pk>[\d]+)/questions/?', views.GetArticleQuestions.as_view(), name='article-questions'),

    url(r'^article/(?P<article_pk>[\d]+)/question/(?P<question_pk>[\d]+)/upvote/(?P<upvote_pk>[\d]+)/?', views.DeleteArticleQuestionUpvote.as_view(), name='delete-upvote-article-question'),
    url(r'^article/(?P<article_pk>[\d]+)/question/(?P<question_pk>[\d]+)/upvote/?', views.PostArticleQuestionUpvote.as_view(), name='upvote-article-question'),

    url(r'^article/(?P<article_pk>[\d]+)/question/(?P<question_pk>[\d]+)/?', views.GetOrUpdateArticleQuestion.as_view(), name='article-question'),
    url(r'^article/(?P<article_pk>[\d]+)/question/ask/?', views.PostArticleQuestion.as_view(), name='ask-article-question'),

    url(r'^article/(?P<article_pk>[\d]+)/topic/(?P<insight_pk>[\d]+)/vote/(?P<vote_pk>[\d]+)/?', views.GetUpdateOrDeleteArticleVote.as_view(), name='edit-article-vote'),
    url(r'^article/(?P<article_pk>[\d]+)/topic/(?P<insight_pk>[\d]+)/vote/?', views.PostArticleVote.as_view(), name='article-vote'),

    url(r'^article/(?P<pk>[\d]+)?/?', views.GetArticle.as_view(), name='article-instance'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^token-refresh/', 'rest_framework_jwt.views.refresh_jwt_token')
)

#Articles
#GET api/article/id/

#Questions
#GET api/article/id/questions
#GET UPDATE api/article/id/question/id
#POST api/article/id/question/ask

#Insights
#GET api/article/id/topics

#Votes
#UPDATE DELETE api/article/id/topic/id/vote/id
#POST api/article/id/topic/id/vote

#Upvotes
#POST api/article/id/question/id/upvote
#DELETE api/article/id/question/id/upvote/id