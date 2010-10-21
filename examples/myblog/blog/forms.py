from django import forms
from blog.models import BlogPost

class BlogPostForm(forms.ModelForm):
    """Creates/updates a blog post."""
    
    class Meta:
        model = BlogPost
        fields = ('title', 'text')
