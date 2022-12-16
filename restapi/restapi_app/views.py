from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .renderers import UserRenderer
from .models import UserPost,Images
from .serializers import  UserSerializer,UserChangePasswordSerializer, UserLoginSerializer, UserPostSerializer, UserRegistrationSerializer
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework import parsers
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)



class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)



class UserView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  serializer_class=UserSerializer
  def get(self, request, format=None):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserPostListApiView(APIView):
    # add permission to check if user is authenticated
    
    permission_classes = (permissions.IsAuthenticated,)
    
    # 1. View all
    def get(self, request, *args, **kwargs):
        '''
        List all the posts
        '''
        userpost = UserPost.objects.filter(is_deleted=0).prefetch_related( Prefetch('images' ,queryset=Images.objects.filter(is_deleted=0)))
        serializer = UserPostSerializer(userpost, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the post
        '''
        parser_classes = (parsers.MultiPartParser, parsers.FormParser)
        data = {
            'user_id': request.user.id,
            'username':request.user.username,
            'title': request.data.get('title'), 
            'text': request.data.get('text'),
            'images':request.data.get('images')

        }
        images = request.data.pop('images')
        userpost = UserPost.objects.filter(title=request.data.get('title'),text=request.data.get('text'),user_id=request.user.id,username=request.user.username)
        serializer = UserPostSerializer(data=data)
        print(request.data)
        if serializer.is_valid():
           serializer.save()
           for img in images:
                Images.objects.create(userpost=userpost[0],**img)
           return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class UserPostDetailApiView(APIView):
    #check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, post_id, user_id):
        '''
        Helper method to get the object with given post_id, and user_id
        '''
        try:
            return UserPost.objects.get(id=post_id, user_id = user_id)
        except UserPost.DoesNotExist:
            return None
    # 3. Get post
    def get(self, request, post_id, *args, **kwargs):
        '''
        get the post with given post_id
        '''
        todo_instance = self.get_object(post_id, request.user.id)
        if not todo_instance:
            return Response(
                {"res": "Object with post id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserPostSerializer(todo_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, post_id, *args, **kwargs):
        '''
        Updates the post  with given post_id if exists
        '''
        post_instance = self.get_object(post_id, request.user.id)
        if not post_instance:
            return Response(
                {"res": "Object with post id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'user_id': request.user.id,
            'username': request.user.username, 
            'title': request.data.get('title'), 
            'text': request.data.get('text'), 
            'is_deleted':request.data.get('is_deleted'),
            'images':request.data.get('images')
        }
        serializer = UserPostSerializer(instance = post_instance, data=data, partial = True)
        images = request.data.pop('images')
        userpost = UserPost.objects.filter(title=request.data.get('title'),text=request.data.get('text'),user_id=request.user.id,username=request.user.username)
        Images.objects.filter(userpost = post_id).delete()
        if serializer.is_valid():
            serializer.save()
            for img in images:
                Images.objects.create(userpost=userpost[0],**img)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, post_id, *args, **kwargs):
        '''
        Deletes the post  with given post_id if exists
        '''
        post_instance = self.get_object(post_id, request.user.id)
        if not post_instance:
            return Response(
                {"res": "Object with post id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = { 
            'user_id': request.user.id,
            'username': request.user.username, 
            'title': request.data.get('title'), 
            'text': request.data.get('text'), 
            'is_deleted':True,
            'images':request.data.get('images')
        }

        serializer = UserPostSerializer(instance = post_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            serializer = UserPostSerializer(instance = post_instance, data=data, partial = True)
            images = request.data.pop('images')
            userpost = UserPost.objects.filter(title=request.data.get('title'),text=request.data.get('text'),user_id=request.user.id,username=request.user.username)
            old_images=Images.objects.filter(userpost = post_id).update(is_deleted=True)
            if serializer.is_valid():
              serializer.save()
            return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
