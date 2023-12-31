from django.shortcuts import render
from .serializers import PostSerializer, PostLikeSerializer, CommentLikeSerializer, CommentSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .models import Post, PostComment, PostLike, CommentLike
from shared.cutom_pagination import CustomPagination


class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Post.objects.all() 
    

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]
    
    def perform_create(self, serializer):
        serializer.save(author = self.request.user)
    
    
class PostRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    
    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serilizer = self.serializer_class(post, data=request.data)
        serilizer.is_valid(raise_exception= True)
        serilizer.save()
        return Response(
            {
                'success': True,
                'code': status.HTTP_200_OK,
                'message': "post o'zgardi",
                'data': serilizer.data
            }
        )
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                'success': True,
                'code': status.HTTP_200_OK,
                'message': "post o'chirildi",
            }
        )
        
        
class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id = post_id)
        return queryset
    
class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]
    
    def get_queryset(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author = self.request.user, post_id = post_id)
        
        
        
class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id = post_id)
    
    