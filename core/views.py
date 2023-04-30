from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login
from .serializers import UserSerializer
from .permissions import IsAuthorOrReadOnly
from .models import BlogPost, Comment
from django.shortcuts import get_object_or_404
from .serializers import BlogPostSerializer, CommentSerializer,ReplySerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

class BlogPostList(APIView):
    permission_classes = (IsAuthenticated,IsAuthorOrReadOnly)

    def get(self, request, format=None):
        posts = BlogPost.objects.all()
        search_query = request.query_params.get('search', None)
        if search_query is not None:
            posts = posts.filter(title__icontains=search_query)
        serializer = BlogPostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogPostDetail(APIView):
    permission_classes = (IsAuthenticated,IsAuthorOrReadOnly)

    def get_object(self, pk):
        return get_object_or_404(BlogPost, pk=pk)

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = BlogPostSerializer(post, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        data = request.data
        if 'title' not in data and 'content' not in data:
            return Response({'error': 'You must provide either a title or content to update.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BlogPostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    permission_classes = (IsAuthenticated,IsAuthorOrReadOnly)

    def get_object(self, post_pk):
        return get_object_or_404(BlogPost, pk=post_pk)

    # def get(self, request, post_pk, format=None):
    #     post = self.get_object(post_pk)
    #     comments = post.comments.all()
    #     serializer = CommentSerializer(comments, many=True)
    #     return Response(serializer.data)

    def post(self, request, post_pk, format=None):
        post = self.get_object(post_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Like(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(BlogPost, pk=pk)

    def post(self, request, pk, format=None):
        post = self.get_object(pk)
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            message = 'You unliked this post.'
        else:
            post.likes.add(user)
            message = 'You liked this post.'
        return Response({'message': message})

class ReplyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, post_pk, comment_pk):
        post = get_object_or_404(BlogPost, pk=post_pk)
        comment = get_object_or_404(post.comments.all(), pk=comment_pk)
        return comment

    # def get(self, request, post_pk, comment_pk, format=None):
    #     comment = self.get_object(post_pk, comment_pk)
    #     replies = comment.replies.all()
    #     serializer = ReplySerializer(replies, many=True)
    #     return Response(serializer.data)

    def post(self, request, post_pk, comment_pk, format=None):
        comment = self.get_object(post_pk, comment_pk)
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(comment=comment, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
