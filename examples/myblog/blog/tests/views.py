# encoding=utf-8
from django.core.urlresolvers import reverse
from django.test import TestCase

from blog.models import BlogPost

class ViewTests(TestCase):
    """
    Test the views as regular Django views.
    """
    
    def setUp(self):
        
        # Create an initial object to test with
        post = BlogPost(title=u'Hello Wørld', text=u'Hello World, this is dynamicresponse. ÆØÅæøå.')
        post.save()
        
        self.post = post
    
    def testListPosts(self):
        """
        Test the list_posts view.
        """
        
        response = self.client.get(reverse('list_posts'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/list_posts.html')
        self.assertTrue(self.post in response.context['posts'])
    
    def testCreatePost(self):
        """
        Test the post view, creating a new entry.
        """
        
        response = self.client.get(reverse('create_post'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post.html')
        self.assertTrue('form' in response.context)
        
        # Create a new post
        response = self.client.post(reverse('create_post'), {
            'title': u'Hello Mr. ÆØÅæøå',
            'text': u'How nice to finally meet you.',
        })
        
        self.assertRedirects(response, reverse('list_posts'))
        
        # Check the newly created object
        self.assertTrue(BlogPost.objects.filter(id=2).exists())
        
        new_post = BlogPost.objects.get(id=2)
        self.assertEquals(new_post.title, u'Hello Mr. ÆØÅæøå')
        self.assertEquals(new_post.text, u'How nice to finally meet you.')
        
    def testPostDetail(self):
        """
        Test the post view with existing post, updating it.
        """
        
        response = self.client.get(reverse('post', kwargs={'post_id': self.post.id}))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post.html')
        self.assertEquals(self.post, response.context['post'])
        self.assertTrue('form' in response.context)
        
        # Edit post with invalid data
        response = self.client.post(reverse('post', kwargs={'post_id': self.post.id}), {})
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertFalse(response.context['form'].is_valid())
        
        # Edit post with valid data
        response = self.client.post(reverse('post', kwargs={'post_id': self.post.id}), {
            'title': u'Brand new title',
            'text': u'Now with more swag. Før real.',
        })
        
        self.assertRedirects(response, reverse('list_posts'))
        
        # Check the newly edited object
        new_post = BlogPost.objects.get(id=self.post.id)
        self.assertEquals(new_post.title, u'Brand new title')
        self.assertEquals(new_post.text, u'Now with more swag. Før real.')
    
    def testPostDelete(self):
        """
        Test the delete_post view.
        """
        
        response = self.client.get(reverse('delete_post', kwargs={'post_id': self.post.id}))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/delete_post.html')
        self.assertEquals(self.post, response.context['post'])
        
        # Delete the post
        post_id = self.post.id
        
        response = self.client.post(reverse('delete_post', kwargs={'post_id': post_id}))
        self.assertRedirects(response, reverse('list_posts'))
        
        with self.assertRaises(BlogPost.DoesNotExist):
            BlogPost.objects.get(id=post_id)
