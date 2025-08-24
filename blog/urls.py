from django.urls import path
from .views import BlogPostListView, BlogPostDetailView, BlogPostCreateView, BlogPostUpdateView, BlogPostDeleteView, \
    BlogPostPublishView, BlogPostChangeStatusView, BlogPostUnpublishView, MyBlogPostsView

app_name = "blog"

urlpatterns = [
    path("", BlogPostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", BlogPostDetailView.as_view(), name="post_detail"),
    path("post/create/", BlogPostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/update/", BlogPostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", BlogPostDeleteView.as_view(), name="post_delete"),
    path('post/<int:pk>/publish/', BlogPostPublishView.as_view(), name='post_publish'),
    path('post/<int:pk>/unpublish/', BlogPostUnpublishView.as_view(), name='post_unpublish'),
    path('post/<int:pk>/change-status/', BlogPostChangeStatusView.as_view(), name='post_change_status'),
    path('my-posts/', MyBlogPostsView.as_view(), name='my_posts'),
]
