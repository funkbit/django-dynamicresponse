# encoding=utf-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson

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

    def testPostDetailAndEdit(self):
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

class ViewJSONTests(TestCase):
    """
    Test all the views with JSON input and ouput.
    """

    def setUp(self):

        # Headers for GET requests
        self.extra_headers = {
            'HTTP_ACCEPT': 'application/json'
        }

        # Create an initial object to test with
        post = BlogPost(title=u'Hello Wørld', text=u'Hello World, this is dynamicresponse. ÆØÅæøå.')
        post.save()

        self.post = post

    def testListPosts(self):
        """
        Test the list_posts view.
        """

        response = self.client.get(reverse('list_posts'), **self.extra_headers)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # Load JSON and check dictionary
        data = simplejson.loads(response.content)
        self.assertTrue('posts' in data)
        self.assertEquals(data['posts'][0]['id'], 1)

    def testCreatePost(self):
        """
        Test the post view, creating a new entry.
        """

        response = self.client.get(reverse('create_post'), **self.extra_headers)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        data_json = u"""
            {
                "title": "Hello Mr. ÆØÅæøå",
                "text": "Lorem ipsum dolor sit amet"
            }
        """

        # Create a new post
        response = self.client.post(reverse('create_post'), data_json, content_type='application/json', **self.extra_headers)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # Check the newly created object
        self.assertTrue(BlogPost.objects.filter(id=2).exists())

        new_post = BlogPost.objects.get(id=2)
        self.assertEquals(new_post.title, u'Hello Mr. ÆØÅæøå')
        self.assertEquals(new_post.text, u'Lorem ipsum dolor sit amet')

    def testPostDetailAndEdit(self):
        """
        Test the post view with existing post, updating it.
        """

        response = self.client.get(reverse('post', kwargs={'post_id': self.post.id}), **self.extra_headers)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # Load JSON and check dictionary
        data = simplejson.loads(response.content)
        self.assertTrue('post' in data)
        self.assertEquals(data['post']['id'], 1)

        # Edit post with invalid data
        data_json_invalid = u"""
            {
                "foo": "bar"
            }
        """

        # Without JSON error output
        response = self.client.post(reverse('post', kwargs={'post_id': self.post.id}), data_json_invalid, content_type='application/json', **self.extra_headers)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # With JSON error output
        settings.DYNAMICRESPONSE_JSON_FORM_ERRORS = True
        response = self.client.post(reverse('post', kwargs={'post_id': self.post.id}), data_json_invalid, content_type='application/json', **self.extra_headers)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # Edit post with valid data
        data_json_valid = u"""
            {
                "title": "Brand new title",
                "text": "This is now edited."
            }
        """

        response = self.client.post(reverse('post', kwargs={'post_id': self.post.id}), data_json_valid, content_type='application/json', **self.extra_headers)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')

        # Check the newly edited object
        new_post = BlogPost.objects.get(id=self.post.id)
        self.assertEquals(new_post.title, u'Brand new title')
        self.assertEquals(new_post.text, u'This is now edited.')

    def testPostDelete(self):
        """
        Test the delete_post view.
        """

        response = self.client.get(reverse('delete_post', kwargs={'post_id': self.post.id}), **self.extra_headers)
        self.assertEquals(response.status_code, 405)

        # Delete the post
        post_id = self.post.id

        response = self.client.post(reverse('delete_post', kwargs={'post_id': post_id}), content_type='application/json', **self.extra_headers)
        self.assertEquals(response.status_code, 204)

        with self.assertRaises(BlogPost.DoesNotExist):
            BlogPost.objects.get(id=post_id)
