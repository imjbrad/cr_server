from django import http
from django.core import exceptions as django_exceptions
from rest_framework import generics, status, response, mixins
from rest_framework import exceptions as rest_exceptions
from cr_app.article_service.article import ArticleHelper
from cr_app import models, serializers, permissions, errors

class GetArticle(generics.RetrieveAPIView):
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer

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
    paginate_by = 10
    paginate_by_param = 'size'

    def get_queryset(self):

        self.queryset = models.Question.objects.filter(article__pk=self.kwargs['pk']).order_by('upvotes').reverse()
        if self.queryset.count():
            return self.queryset
        else:
            raise http.Http404

class GetOrUpdateArticleQuestion(generics.RetrieveUpdateAPIView):
    model = models.Question
    serializer_class = serializers.QuestionSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)

    def get_object(self):
        try:
            question = models.Question.objects.get(article__pk=self.kwargs['article_pk'], pk=self.kwargs['question_pk'])
            return question
        except:
            raise http.Http404

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
            if e.code == errors.ALREADY_UPVOTED:
                raise rest_exceptions.ValidationError({"pk": e.params["pk"], "message": e.message})

            raise rest_exceptions.ValidationError(e.message)

class DeleteArticleQuestionUpvote(generics.DestroyAPIView):
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
    serializer_class = serializers.AskQuestionSerializer

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

class GetUpdateOrDeleteArticleVote(generics.RetrieveUpdateDestroyAPIView):
    model = models.Vote
    serializer_class = serializers.VoteSerializer
    queryset = models.Vote.objects.all()
    permission_classes = (permissions.IsOwnerOrNoPermissions,)

    def get_object(self):
        user = self.request.user
        vote = generics.get_object_or_404(self.queryset, pk=self.kwargs["vote_pk"])
        self.check_object_permissions(self.request, vote)

        return vote

class GetArticleInsightVotes(generics.RetrieveAPIView):
    model = models.Article
    serializer_class = serializers.ArticleInsightVotesSerializer

    def get_object(self):
        try:
            return models.Article.objects.get(pk=self.kwargs['pk'])
        except:
            raise http.Http404