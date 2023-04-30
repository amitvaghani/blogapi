from django.contrib.auth.models import User
from rest_framework import serializers
from .models import BlogPost, Comment, Reply


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.ReadOnlyField(source='post.id')
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_likes_post = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'comments', 'likes_count', 'user_likes_post']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_likes_post(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class ReplySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comment = serializers.ReadOnlyField(source='comment.id')
    class Meta:
        model = Reply
        fields = '__all__'
