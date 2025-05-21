from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import ChangePasswordSerializer, UserRegistrationSerializers, UserLoginSerializers, UserProfileSerializers, ChangePasswordSerializer,PostSerializers,CommentSerializers,VideoSerializers,VideoCommentSerializers,UserSerializers,ExpenseSerializers,ProductSerializer,CartItemSerializers,NotificationSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from api.models import Post,Comment,VideoComment,Video,MyUser,Expense,Product,CartItem,Mychats,Notification

from rest_framework import generics
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }

class UserRegistrationView(APIView):
    
    def post(self, request):
        serializer = UserRegistrationSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_token_for_user(user)
            return Response({"Token": token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializers = UserLoginSerializers(data=request.data)
        if serializers.is_valid(raise_exception=True):
            email = serializers.validated_data.get('email')
            password = serializers.validated_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_token_for_user(user)
                return Response({"Token": token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializers = UserProfileSerializers(request.user)
        return Response(serializers.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Successfully changed'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def post(self, request):
        serializers = PostSerializers(data=request.data)
        if serializers.is_valid(raise_exception=True):
            serializers.save(author=request.user)
            return Response({'msg': 'You have successfully posted'}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(commented_on=post).order_by('created_at')
        serializers = CommentSerializers(comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializers = CommentSerializers(data=request.data)
        if serializers.is_valid(raise_exception=True):
            serializers.save(author=request.user, commented_on=post)
            return Response({'msg': 'You have successfully posted a comment'}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostAllView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Post.objects.all().order_by('-created_at')
        serializers = PostSerializers(queryset, many=True)  # Correct context as dictionary
        return Response(serializers.data, status=status.HTTP_200_OK)
    
class VideoView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializers=VideoSerializers(data=request.data)
        if (serializers.is_valid(raise_exception=True)):
            return Response({'msg':'You have successfully added a video',},status=status.HTTP_200_OK)
        else:
            return Response({'msg':'Unable to add a video'},status=status.HTTP_400_BAD_REQUEST)
        
class VideoCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video_content = get_object_or_404(Video, id=video_id)
        serializers = VideoCommentSerializers(data=request.data)
        if serializers.is_valid(raise_exception=True):
            serializers.save(author=request.user, commented_on=video_content)
            return Response({'msg': 'You have successfully added a comment on a video'}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, video_id):
        video_content = get_object_or_404(Video, id=video_id)
        comments = VideoComment.objects.filter(commented_on=video_content).order_by('-created_at')
        serializers = VideoCommentSerializers(comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
        
class VideoAll(APIView):
  permission_classes=[IsAuthenticated]
  def get(self,request):
    queryset=Video.objects.all().order_by('-uploaded_at')
    serializers=VideoSerializers(queryset,many=True)
    return Response(serializers.data,status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        
        queryset = MyUser.objects.exclude(id=request.user.id)
        serializers = UserSerializers(queryset, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from api.models import Mychats, MyUser

# class ChatHistoryView(APIView):
#     def get(self, request, me_id, frnd_id):
#         try:
#             me = MyUser.objects.get(id=me_id)
#             frnd = MyUser.objects.get(id=frnd_id)
#             chat = Mychats.objects.filter(me=me, frnd=frnd).first()

#             if chat:
#                 return Response(chat.chats)  # Return the list of messages
#             else:
#                 return Response([])  # Return empty list if no chat history found
#         except MyUser.DoesNotExist:
#             return Response({"error": "User does not exist"}, status=400)
class ChatHistoryView(APIView):
    def get(self, request, me_id, frnd_id):
        try:
            # Sort the IDs to ensure consistency
            sorted_ids = sorted([me_id, frnd_id])

            me = MyUser.objects.get(id=sorted_ids[0])
            frnd = MyUser.objects.get(id=sorted_ids[1])

            chat = Mychats.objects.filter(me=me, frnd=frnd).first()

            if chat:
                return Response(chat.chats)  # Return the list of messages
            else:
                return Response([])  # Return empty list if no chat history found
        except MyUser.DoesNotExist:
            return Response({"error": "User does not exists"}, status=400)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from api.models import MyUser, Mychats

# class ChatHistoryView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, me_id, frnd_id):
#         # Ensure the IDs are ordered consistently
#         me_id, frnd_id = sorted([me_id, frnd_id])

#         try:
#             # Query for the chat history using the ordered IDs
#             me = MyUser.objects.get(id=me_id)
#             frnd = MyUser.objects.get(id=frnd_id)
#             mychats = Mychats.objects.get(me=me, frnd=frnd)

#             # Return the chat history
#             return Response({
#                 'chats': mychats.chats,
#                 'me': me_id,
#                 'frnd': frnd_id
#             })
#         except Mychats.DoesNotExist:
#             return Response({'error': 'No chat history found'}, status=404)
#         except MyUser.DoesNotExist:
#             return Response({'error': 'User not found'}, status=404),

        
class ExpenseListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializers(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpenseSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Expense, pk=pk, user=user)

    def get(self, request, pk):
        expense = self.get_object(pk, request.user)
        serializer = ExpenseSerializers(expense)
        return Response(serializer.data)

    def put(self, request, pk):
        expense = self.get_object(pk, request.user)
        serializer = ExpenseSerializers(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk, request.user)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CitizenshipVerification
from .serializers import CitizenshipVerificationSerializer

class SubmitCitizenshipVerification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            verification = CitizenshipVerification.objects.get(user=user)
            if verification.is_verified:
                return Response({
                    "detail": "Your citizenship has already been verified.",
                    "is_verified": True,
                    "verification_request_sent": verification.verification_request_sent
                }, status=status.HTTP_202_ACCEPTED)
            
            return Response({
                "detail": "Verification request already submitted.",
                "is_verified": False,
                "verification_request_sent": verification.verification_request_sent
            }, status=status.HTTP_102_PROCESSING)
            
        except CitizenshipVerification.DoesNotExist:
            data = request.data
            data['user'] = user.id
            serializer = CitizenshipVerificationSerializer(data=data)

            if serializer.is_valid():
                serializer.save(verification_request_sent=True)
                return Response({
                    "detail": "Verification request submitted successfully.",
                    "is_verified": False,
                    "verification_request_sent": True
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Role
from .serializers import RoleSerializer

class SelectRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        role = request.data.get('role')

        if role not in dict(Role.ROLE_CHOICES).keys():
            return Response({"detail": "Invalid role selected."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role_instance, created = Role.objects.update_or_create(
                user=user,
                defaults={'role': role}
            )
            if created:
                return Response({"status": "success", "detail": "Role selected successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "success", "detail": "Role updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FarmerProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Product.objects.filter(farmer=request.user)
        serializer = ProductSerializer(queryset, many=True) 
        return Response(serializer.data, status=status.HTTP_200_OK)

class FarmerProductAddView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializers=ProductSerializer(request.data,farmer=request.user)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors)
        


class FarmerProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        product = get_object_or_404(Product, id=id, farmer=request.user)  
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        product = get_object_or_404(Product, id=id, farmer=request.user)  
        serializer = ProductSerializer(product, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        product = get_object_or_404(Product, id=id, farmer=request.user)  
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class BuyerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()  
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BuyerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        product = get_object_or_404(Product, id=id)  
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetCartItemView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        cartitem=CartItem.objects.filter(user=request.user)
        serializers=CartItemSerializers(cartitem,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
class PostCartItemView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        product_id=request.data.get('id')
        product=Product.objects.get(id=product_id)
        cart_item,created=CartItem.objects.get_or_create(
            user=request.user,
            item=product,
            quantity=1
        )
        if not created:
            cart_item.quantity+=1
            cart_item.save()
        serializer=CartItemSerializers(cart_item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class NotificationPost(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,id):
        buyer=request.user
        product=get_object_or_404(Product,id=id)
        farmer=product.farmer
        message=f"{buyer.username} is interested in buying {product.name}."
        Notification.objects.create(
            product=product,
            farmer=farmer,
            buyer=buyer,
            message=message
        )
        return Response({"message":"Notification sent to the farmer"},status=status.HTTP_201_CREATED)

class NotificationGet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        farmer = request.user  # Get the farmer (logged-in user)
        notifications = Notification.objects.filter(farmer=farmer)  # Farmer's notifications

        # Use the serializer to serialize the notification data
        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
        

        
        

    

    
        
            
        
        
  
  
  
  
  
  
  
  
  
  
  
    
