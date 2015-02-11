from django.core.paginator import Paginator
from rest_framework import serializers, pagination
from cr_app import models
from app_user.models import User
import json

__author__ = 'jordanbradley'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email')

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publisher
        fields = ('pk', 'name')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ('pk', 'name')

class QuestionSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = models.Question
        fields = ("pk", "title", "upvotes", "answered", "article", "user", "following")
        read_only_fields = ('upvotes', 'pk', 'user', "article", 'answered',"following")

    def get_following(self, obj):
        pass

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
    num_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    current_page = serializers.ReadOnlyField(source='number')
    per_page = serializers.ReadOnlyField(source='paginator.per_page')
    test = serializers.SerializerMethodField('method')

    class Meta:
        object_serializer_class = QuestionSerializer

    def method(self, obj):
        pass


class ArticleInsightVotesSerializer(serializers.ModelSerializer):
    insight_votes = serializers.SerializerMethodField('insight_votes_json')

    class Meta:
        model = models.Article
        fields = ('insight_votes',)

    def insight_votes_json(self, obj):
        return obj.insight_votes if self.parent is None else obj

class ArticleSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()
    authors = AuthorSerializer(many=True)
    questions = serializers.SerializerMethodField('paginated_questions')
    insight_votes = ArticleInsightVotesSerializer()

    class Meta:
        model = models.Article
        fields = ('pk', 'title', 'url', 'date', 'insight_votes', 'publisher', 'authors', "questions")

    def paginated_questions(self, obj):
        paginator = Paginator(obj.questions.all().order_by('upvotes').reverse(), 10)
        questions = paginator.page(1)

        serializer = PaginatedQuestionSerializer(questions, context=self.context)
        return serializer.data
