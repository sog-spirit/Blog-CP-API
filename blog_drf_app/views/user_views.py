from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import jwt
from datetime import datetime, timedelta

class UserRegister(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if username is None or password is None:
            return Response(
                {'detail': 'Username or password is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(username=username).first()
        if user is not None:
            return Response(
                {'detail': 'Username is existed!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create_user(
            username=username,
            password=password
        )
        return Response(
            {'detail': 'User registered successfully'},
            status=status.HTTP_201_CREATED
        )

class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if username is None or password is None:
            return Response(
                {'detail': 'Username or password is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(
                {'detail': 'User or password is invalid'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'User or password is invalid'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token)
        response.data = {
            'detail': 'Login successfully',
            'jwt': token
        }
        return response

class UserLogout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'detail': 'Logout successfully'
        }
        return response

class UserStatus(APIView):
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
        
        return Response(
            {'detail': 'User is authenticated'},
            status=status.HTTP_202_ACCEPTED
        )
