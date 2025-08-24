from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'slug', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ограничиваем выбор статуса для обычных пользователей
        if self.user and not self.user.has_perm('blog.can_change_blog_status'):
            self.fields['status'].choices = [('draft', 'Черновик')]
            self.fields['status'].initial = 'draft'
