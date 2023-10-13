from django.contrib import admin
from .models import Post, PostComment, PostLike, CommentLike

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'caption', 'created_time')
    search_fields = ('id', 'author__usrname', 'caption')


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_time')
    search_fields = ('id', 'author__usrname', 'comment')


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_time')
    search_fields = ('id', 'author__usrname')


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'comment', 'created_time')
    search_fields = ('id', 'author__usrname')
    
    
admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)    
