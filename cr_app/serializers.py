from django.core.paginator import Paginator
from rest_framework import serializers, pagination
from cr_app import models

__author__ = 'jordanbradley'

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publisher
        fields = ('pk', 'name')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ('pk', 'name')

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = ("pk", "title", "upvotes", "answered", "article")
        read_only_fields = ('upvotes', 'pk', 'user', "article")

class QuestionUpVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UpVote
        fields = ("pk",)

class AskQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = ('pk', 'title')

class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Vote
        fields = ("pk", "article", "insight", "choice")
        read_only_fields = ("article", "insight")

class PaginatedQuestionSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = QuestionSerializer

class ArticleSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()
    authors = AuthorSerializer(many=True)
    questions = serializers.SerializerMethodField('paginated_questions')

    class Meta:
        model = models.Article
        fields = ('pk', 'title', 'url', 'date', 'insight_votes', 'publisher', 'authors', "questions")

    def paginated_questions(self, obj):
        paginator = Paginator(obj.questions.all().order_by('upvotes').reverse(), 3)
        questions = paginator.page(1)

        serializer = PaginatedQuestionSerializer(questions)
        return serializer.data


class ArticleInsightVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Article
        fields = ('insight_votes',)