import jwt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers import CommentSerializer
from ..models import Post, Comment
from django.db import transaction, IntegrityError

class CommentAPIView(APIView):
    def get(self, request):
        """
        Return list of comments
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
                {'detail': 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post_id = request.GET.get('post_id', None)
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
        comments = post.comments.filter(post=post_id, is_delete=False)
        serializer = CommentSerializer(comments, many=True)
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
        data = request.data.copy()
        data['user'] = payload['id']
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Comment created'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        comment_id = request.data.get('comment_id', None)
        if comment_id is None:
            return Response(
                {'detail': 'comment_id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if comment.is_delete is True:
            return Response(
                {'detail': 'Comment is deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CommentSerializer(instance=comment, data=request.data, partial=True)
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {'detail': 'Comment editing successfully'},
                        status=status.HTTP_200_OK
                    )
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except IntegrityError:
            return Response(
                {'detail': 'Data integrity violated while editing comment'},
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
                {'detail': 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        comment_id = request.data.get('comment_id', None)
        if comment_id is None:
            return Response(
                {'detail': 'comment_id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if comment.is_delete is True:
            return Response(
                {'detail': 'Comment is deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        comment.is_delete = True
        comment.save()
        return Response(
            {'detail': 'Comment deleted successfully'},
            status=status.HTTP_200_OK
        )

class CommentDetailAPIView(APIView):
    def get(self, request):
        """
        Return comment detail by id
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
                {'detail': 'JWT token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        comment_id = request.GET.get("comment_id", None)
        if comment_id is None:
            return Response(
                {'detail': 'comment_id is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CommentSerializer(comment)
        return Response(serializer.data)