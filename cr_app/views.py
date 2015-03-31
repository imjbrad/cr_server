from django import http
from django.core import mail, exceptions as django_exceptions
from rest_framework import views, generics, status, response, mixins, permissions as rest_permissions
from rest_framework import exceptions as rest_exceptions
from cr_app.article_service.article import ArticleHelper
from cr_app import models, serializers, permissions, codes
from app_user.models import User
from rest_framework_jwt.utils import jwt_decode_handler
import json

class GetUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            data = jwt_decode_handler(self.request.auth)
            return response.Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise rest_exceptions.APIException(e)


class GetArticle(generics.RetrieveAPIView):
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    permission_classes = ()

    def get_object(self):
        request = self.request
        article_url = None
        article_id = None
        article = None

        if "url" in request.GET:
            article_url = request.GET.get("url")

        if "pk" in self.kwargs:
            article_id = self.kwargs["pk"]

        if article_id is not None:
            article = ArticleHelper.find_article_with(article_id=article_id)

        elif article_url is not None:
            article = ArticleHelper.find_article_with(article_url=article_url)

        if article:
            return article

        raise http.Http404

class GetArticleQuestions(generics.ListAPIView):
    model = models.Question
    serializer_class = serializers.QuestionSerializer
    paginate_by = 6
    paginate_by_param = 'size'
    pagination_serializer_class = serializers.PaginatedQuestionSerializer

    def get_queryset(self):
        queryset = models.Question.objects.filter(article__pk=self.kwargs['pk']).order_by('upvotes').reverse()
        filter = self.request.QUERY_PARAMS.get('filter', None)

        if filter is not None:
            if filter == "me":
                queryset = queryset.filter(user=self.request.user)
            if filter == "answered":
                queryset = queryset.filter(answered=True)

        if queryset.count():
            return queryset
        else:
            raise http.Http404

class GetOrUpdateArticleQuestion(generics.RetrieveUpdateDestroyAPIView):
    model = models.Question
    serializer_class = serializers.QuestionSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)

    def get_object(self):
        try:
            question = models.Question.objects.get(article__pk=self.kwargs['article_pk'], pk=self.kwargs['question_pk'])
            return question
        except:
            raise http.Http404

class PostArticleQuestionFollow(generics.CreateAPIView):
    model = models.QuestionFollow
    serializer_class = serializers.QuestionFollowSerializer

    def post(self, request, *args, **kwargs):

        user = self.request.user
        question = models.Question.objects.get(pk=self.kwargs['question_pk'])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        follow = self.model(question=question, user=user, **serializer.validated_data)

        try:
            follow.clean()
            follow.save()
            return response.Response(self.serializer_class(follow).data, status=status.HTTP_201_CREATED)

        except django_exceptions.ValidationError as e:
            raise rest_exceptions.ValidationError(e.message)

class FindArticleQuestionFollow(generics.RetrieveAPIView):
    model = models.QuestionFollow
    serializer_class = serializers.QuestionFollowSerializer

    def get_object(self):
        user = self.request.user
        follow = None
        try:
            follow = self.model.objects.get(
                question=models.Question.objects.get(pk=self.kwargs["question_pk"]),
                user=self.request.user
            )
        except:
            raise http.Http404

        self.check_object_permissions(self.request, follow)

        return follow

class DeleteArticleQuestionFollow(generics.DestroyAPIView):
    model = models.QuestionFollow
    serializer_class = serializers.QuestionFollowSerializer
    permission_classes = (permissions.IsOwnerOrNoPermissions,)

    def get_object(self):
        user = self.request.user
        follow = None
        try:
            follow = self.model.objects.get(
                pk=self.kwargs["follow_pk"],
                question=models.Question.objects.get(pk=self.kwargs["question_pk"]),
                user=self.request.user
            )
        except:
            raise http.Http404

        self.check_object_permissions(self.request, follow)

        return follow

class PostArticleQuestionUpvote(generics.CreateAPIView):
    model = models.UpVote
    serializer_class = serializers.QuestionUpVoteSerializer

    def get_object(self):
        try:
            question = models.Question.objects.get(article__pk=self.kwargs['article_pk'], pk=self.kwargs['question_pk'])
            return question
        except:
            raise http.Http404

    def post(self, request, *args, **kwargs):
        question = self.get_object()

        try:
            upvote = question.upvote(request.user)
            return response.Response(self.serializer_class(upvote).data, status=status.HTTP_201_CREATED)

        #catch an exception from cleaning the upvote, and pass that to the serializer
        except django_exceptions.ValidationError as e:
            if e.code == codes.ALREADY_UPVOTED:
                raise rest_exceptions.ValidationError({"pk": e.params["pk"], "message": e.message})

            raise rest_exceptions.ValidationError(e.message)

class FindArticleQuestionUpvote(generics.RetrieveAPIView):
    model = models.UpVote
    serializer_class = serializers.QuestionUpVoteSerializer
    permission_classes = (permissions.IsOwnerOrNoPermissions,)

    def get_object(self):
        user = self.request.user
        upvote = None

        try:
            upvote = models.UpVote.objects.get(
                question=models.Question.objects.get(pk=self.kwargs["question_pk"]),
                user=self.request.user
            )
        except:
            raise http.Http404

        self.check_object_permissions(self.request, upvote)

        return upvote


class GetOrDeleteArticleQuestionUpvote(generics.RetrieveDestroyAPIView):
    model = models.UpVote
    serializer_class = serializers.QuestionUpVoteSerializer
    permission_classes = (permissions.IsOwnerOrNoPermissions,)

    def get_object(self):
        upvote = None

        try:
            upvote = models.UpVote.objects.get(pk=self.kwargs['upvote_pk'], question=self.kwargs['question_pk'])
            self.check_object_permissions(self.request, upvote)
            return upvote
        except:
            raise http.Http404


    def delete(self, request, *args, **kwargs):
        upvote = self.get_object()
        question = upvote.question

        try:
            question.downvote(request.user, upvote)
            return response.Response(self.serializer_class(question).data, status=status.HTTP_204_NO_CONTENT)

        #catch an exception from cleaning the upvote, and pass that to the serializer
        except Exception as e:
            raise rest_exceptions.ValidationError(e.message)

class PostArticleQuestion(generics.CreateAPIView):
    model = models.Question
    serializer_class = serializers.QuestionSerializer

    def perform_create(self, serializer):
        try:
            article = models.Article.objects.get(pk=self.kwargs['article_pk'])
            serializer.save(user=self.request.user, article=article)
        except:
            raise rest_exceptions.ValidationError("Something went wrong")

class PostArticleVote(generics.CreateAPIView):
    model = models.Vote
    serializer_class = serializers.VoteSerializer


    def post(self, request, *args, **kwargs):
        user = self.request.user

        try:
            article = models.Article.objects.get(pk=self.kwargs['article_pk'])
            insight = models.CRInsight.objects.get(pk=self.kwargs['insight_pk'])
        except:
            raise rest_exceptions.ValidationError("Something went wrong with your contribution")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = self.model(article=article, user=user, insight=insight, **serializer.validated_data)

        try:
            vote.clean()
            vote.save()
            return response.Response(self.serializer_class(vote).data, status=status.HTTP_201_CREATED)

        except django_exceptions.ValidationError as e:
            raise rest_exceptions.ValidationError(e.message)


        # serializer.save()

class GetPostUpdateOrDeleteArticleVote(generics.RetrieveUpdateDestroyAPIView):
    model = models.Vote
    serializer_class = serializers.VoteSerializer
    queryset = models.Vote.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated, permissions.IsOwnerOrNoPermissions,)

    def get_object(self):
        user = self.request.user
        if ("vote_pk" in self.kwargs) and (self.kwargs["vote_pk"] != None):
            vote = generics.get_object_or_404(self.queryset, pk=self.kwargs["vote_pk"])
        else:
            try:
                vote = models.Vote.objects.get(
                    article=models.Article.objects.get(pk=self.kwargs["article_pk"]),
                    insight=models.CRInsight.objects.get(pk=self.kwargs["insight_pk"]),
                    user=self.request.user
                )
            except:
                raise http.Http404

        self.check_object_permissions(self.request, vote)

        return vote

    def post(self, request, *args, **kwargs):
        user = self.request.user

        try:
            article = models.Article.objects.get(pk=self.kwargs['article_pk'])
            insight = models.CRInsight.objects.get(pk=self.kwargs['insight_pk'])
        except:
            raise rest_exceptions.ValidationError("Something went wrong with your contribution")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = self.model(article=article, user=user, insight=insight, **serializer.validated_data)

        try:
            vote.clean()
            vote.save()
            return response.Response(self.serializer_class(vote).data, status=status.HTTP_201_CREATED)

        except django_exceptions.ValidationError as e:
            raise rest_exceptions.ValidationError(e.message)


class GetArticleInsightVotes(generics.RetrieveAPIView):
    model = models.Article
    serializer_class = serializers.ArticleInsightVotesSerializer

    def get_object(self):
        try:
            return models.Article.objects.get(pk=self.kwargs['pk'])
        except:
            raise http.Http404


class PostArticleSuggestion(views.APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        if "message" in request.data:
            mail.send_mail('CR Suggestion',
                           request.data["message"],
                           'suggestions@cr.net',
                           ['jbradley@mica.edu'],
                           fail_silently=False,
                           html_message='<h3>'+request.data[u'url']+'</h3><br><div>'+request.data[u'message']+'</div>')
            return response.Response(status=status.HTTP_201_CREATED)
        return rest_exceptions.APIException("Message Not Sent")

