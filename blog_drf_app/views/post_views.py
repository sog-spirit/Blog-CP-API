import jwt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers import PostSerializer
from ..models import Post
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

class GetPosts(APIView):
    def get(self, request):
        """
        Return posts with PUBLISH condition
        """
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        posts = Post.objects.filter(status="PUBLISH")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Return posts from a user
        """
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        posts = Post.objects.filter(author=payload['id'])
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class GetPostDetail(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        post_id = request.data.get('post_id', None)
        if post_id is None:
            return Response(
                {'detail': 'Post id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PostSerializer(post)
        return Response(serializer.data)

class PostAPIView(APIView):
    def get(self, request):
        """
        Return posts list contains query string
        """
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        title_query = request.GET.get("query", None)
        if title_query is None:
            return Response(
                {'detail': 'Query is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        posts = Post.objects.filter(title__contains=title_query, status="PUBLISH")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            with transaction.atomic():
                data = request.data.copy()
                data['author'] = payload['id']
                serializer = PostSerializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(
                        {'detail': 'Post created'},
                        status=status.HTTP_201_CREATED
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(
                {'detail': 'Data integrity violated while creating post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post_id = request.data.get("post_id", None)
        if post_id is None:
            return Response(
                {'detail': 'Post id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if (post.author.id != payload['id']):
            return Response(
                {'detail': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = PostSerializer(instance=post, data=request.data, partial=True)
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {'detail': 'Post editing successfully'},
                        status=status.HTTP_200_OK
                    )
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except IntegrityError:
            return Response(
                {'detail': 'Data integrity violated while editing post'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail', 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post_id = request.data.get("post_id", None)
        if post_id is None:
            return Response(
                {'detail': 'post_id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if (post.author.id != payload['id']):
            return Response(
                {'detail': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            with transaction.atomic():
                post.delete()
                return Response(
                    {'detail': 'Post deleted successfully'},
                    status=status.HTTP_200_OK
                )
        except IntegrityError:
            return Response(
                {'detail': 'Data integrity violated while creating post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )