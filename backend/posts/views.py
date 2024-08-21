from django.db import connection, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Post, Category, PostView, PostLike, Favorite, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


class CategoryView(views.APIView):
    def get(self, request, category_id=None, *args, **kwargs):

        if category_id:
            category = get_object_or_404(Category, id=category_id)
            data = {
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            }

            return JsonResponse(data)

        else:
            categories = Category.objects.all().values()

            return JsonResponse(
                {
                    'categories': list(categories)
                }
            )


class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly, ]
    pagination_class = MyPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), ]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):

        base_url = request.build_absolute_uri('/')[:-1].strip("/")

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT p.id, p.title, p.image, p.created_at, p.updated_at,
                p.content, p.view_count, p.like_count, a.id, a.username, c.name, pr.photo
                FROM posts_post p
                JOIN auth_user a ON p.author_id = a.id
                JOIN posts_category c ON p.category_id = c.id
                JOIN users_profile pr ON a.id = pr.user_id;
            ''')

            rows = cursor.fetchall()

            if not rows:
                return JsonResponse(
                    {
                        'response': 'Posts not found'
                    }, status=404
                )

            posts = [{
                'id': row[0],
                'title': row[1],
                'post_image': base_url + '/media/' + row[2] if row[2] else 'null',
                'created_at': row[3].strftime('%d.%m.%Y, %H:%M'),
                'updated_at': row[4].strftime('%d.%m.%Y, %H:%M'),
                'content': row[5],
                'view_count': row[6],
                'like_count': row[7],
                'author': {
                    'id': row[8],
                    'name': row[9]
                },
                'category_name': row[10],
                'author_photo': base_url + '/media/' + row[11] if row[11] else 'null'
            } for row in rows]

            page = self.paginate_queryset(posts)

            if page is not None:
                return self.get_paginated_response(page)

            return JsonResponse({'posts': posts})

    @action(detail=True, methods=['get'], url_path='view_count')
    def view_count(self, request, pk=None):
        if request.user.is_authenticated:
            post = get_object_or_404(Post, id=pk)
            user_id = request.user.id
            try:
                with connection.cursor() as cursor:
                    if not PostView.objects.filter(post=post.id, user=user_id).exists():
                        cursor.execute('''
                            UPDATE posts_post
                            SET view_count = view_count + 1
                            WHERE id = %s
                        ''', [post.id])
                        PostView.objects.create(post=post, user=request.user)
                        return JsonResponse({'status': 'OK'}, status=200)
            except IntegrityError:
                return JsonResponse({'error': 'Foreign key constraint failed'}, status=400)
        return JsonResponse({'response': 'Not permission'})

    @action(detail=True, methods=['get'], url_path='like_count')
    def like_count(self, request, pk=None):
        if request.user.is_authenticated:
            post = get_object_or_404(Post, id=pk)

            post_like_exists = PostLike.objects.filter(post=post, user=request.user).exists()

            if post_like_exists:
                post.like_count -= 1
                post.save()
                PostLike.objects.filter(post=post, user=request.user).delete()

                return JsonResponse(
                    {
                        'status': 'Unliked'
                    }, status=200
                )
            else:
                post.like_count += 1
                post.save()
                PostLike.objects.create(post=post, user=request.user)

                return JsonResponse({'status': 'Liked'}, status=200)

        return JsonResponse({'response': 'Not permitted'}, status=403)

    @action(detail=True, methods=['post'], url_path='favorite')
    def toggle_favorite(self, request, pk=None):
        if request.user.is_authenticated:
            post = get_object_or_404(Post, id=pk)
            user = request.user

            favorite = Favorite.objects.filter(post=post, user=user).first()

            if favorite:
                favorite.delete()
                return JsonResponse({'status': 'Removed from favorites'}, status=200)
            else:
                Favorite.objects.create(post=post, user=user)
                return JsonResponse({'status': 'Added to favorites'}, status=200)

        return JsonResponse({'response': 'Not permitted'}, status=403)

    def retrieve(self, request, pk=None, *args, **kwargs):

        base_url = request.build_absolute_uri('/')[:-1].strip("/")

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT p.id, p.title, p.image, p.created_at, p.updated_at, 
                p.content, p.view_count, p.like_count, a.id, a.username, c.name, pr.photo
                FROM posts_post p
                JOIN auth_user a ON p.author_id = a.id
                JOIN posts_category c ON p.category_id = c.id
                JOIN users_profile pr ON a.id = pr.user_id
                WHERE p.id = {pk}
            ''')

            row = cursor.fetchone()

            if not row:
                return JsonResponse(
                    {
                        'response': 'Posts not found'
                    }, status=404
                )

            posts = {
                'id': row[0],
                'title': row[1],
                'post_image': base_url + '/media/' + row[2] if row[2] else 'null',
                'created_at': row[3].strftime('%d.%m.%Y, %H:%M'),
                'updated_at': row[4].strftime('%d.%m.%Y, %H:%M'),
                'content': row[5],
                'view_count': row[6],
                'like_count': row[7],
                'author': {
                    'id': row[8],
                    'name': row[9]
                },
                'category_name': row[10],
                'author_photo': base_url + '/media/' + row[11] if row[11] else 'null'
            }

            return JsonResponse({'posts': posts})

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly, ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post']
    pagination_class = MyPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), ]
        return super().get_permissions()

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)
