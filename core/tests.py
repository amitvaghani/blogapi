from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import User
from .models import BlogPost,Comment
from .serializers import BlogPostSerializer, ReplySerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateUserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        self.invalid_payload = {
            'username': '',
            'password': 'short'
        }

    def test_create_user_with_valid_data(self):
        response = self.client.post('/api/signup/', data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'User created successfully')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_create_user_with_invalid_data(self):
        response = self.client.post('/api/signup/', data=self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)



class BlogPostListTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.blogpost = BlogPost.objects.create(title="Title", content="Content", author=self.user)
        
    def test_create_blog_post(self):
        data = {'title': 'Test Blog Post', 'content': 'This is a test blog post.'}
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_list_blog_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.blogpost.title)
        self.assertEqual(response.data[0]['content'], self.blogpost.content)
        self.assertEqual(response.data[0]['author'], self.blogpost.author.username)

class BlogPostDetailTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.access_token = str(AccessToken.for_user(self.user))
        self.post = BlogPost.objects.create(title='Test Post', content='Test content', author=self.user)

    def test_retrieve_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        serializer = BlogPostSerializer(instance=self.post, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data = {'title': 'New Title'}
        response = self.client.put(url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'New Title')

    def test_delete_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

class LikeTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = BlogPost.objects.create(
            title='Test Post', content='Test Content', author=self.user)

    def test_like_post(self):
        url = reverse('like-post', kwargs={'pk': self.post.pk})
        self.client.force_authenticate(user=self.user)

        # First, like the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You liked this post.')

        # Check if user is in post likes
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())

        # Then, unlike the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You unliked this post.')

        # Check if user is not in post likes
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())

    def test_like_post_unauthenticated(self):
        url = reverse('like-post', kwargs={'pk': self.post.pk})

        # Try to like the post without authenticating first
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ReplyViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.blog_post = BlogPost.objects.create(title='Test post', content='Test content', author=self.user)
        self.comment = Comment.objects.create(
            post=self.blog_post, content='Test comment', author=self.user)

    def test_create_reply(self):
        url = reverse('reply-list', args=[self.blog_post.id, self.comment.id])
        data = {
            'text': 'Test reply',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'Test reply')
        self.assertEqual(response.data['comment'], self.comment.id)
        self.assertEqual(response.data['author'], self.user.username)

    def test_create_reply_unauthenticated(self):
        url = reverse('reply-list', args=[self.blog_post.id, self.comment.id])
        data = {
            'text': 'Test reply',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
