from django.db.models import Q, Count
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .pagination import PostPagination
from .models import Post, Like, Comment, Bookmark
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly


# PAGINATION
class PostPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 24


# POST API
class PostViewSet(viewsets.ModelViewSet):

    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    lookup_field = 'slug'
    pagination_class = PostPagination

    # GET POSTS
    def get_queryset(self):

        user = self.request.user

        if user.is_staff:
            queryset = Post.objects.all()

        elif user.is_authenticated:
            queryset = Post.objects.filter(
                Q(status='Published') |
                Q(author=user)
            )

        else:
            queryset = Post.objects.filter(status='Published')

        # SEARCH
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )

        # CATEGORY FILTER
        category = self.request.query_params.get('category')

        if category:
            queryset = queryset.filter(
                category__name__icontains=category
            )

        # TAG FILTER
        tag = self.request.query_params.get('tag')

        if tag:
            queryset = queryset.filter(
                tags__name__icontains=tag
            )

        # AUTHOR FILTER
        author = self.request.query_params.get('author')

        if author:
            queryset = queryset.filter(
                author__username__icontains=author
            )

        # SORTING
        sort = self.request.query_params.get('sort')

        if sort == 'popular':
            queryset = queryset.annotate(
                like_count=Count('likes')
            ).order_by('-like_count')

        else:
            queryset = queryset.order_by('-created_at')

        return queryset.distinct()

    # CREATE POST
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # LIKE / UNLIKE API
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def like(self, request, slug=None):

        post = self.get_object()

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return Response({
            'liked': liked,
            'like_count': post.likes.count()
        })

    # COMMENTS API
    @action(
        detail=True,
        methods=['get', 'post']
    )
    def comments(self, request, slug=None):

        post = self.get_object()

        if request.method == 'GET':

            comments = Comment.objects.filter(
                post=post,
                parent__isnull=True
            ).order_by('-created_at')

            serializer = CommentSerializer(
                comments,
                many=True
            )

            return Response(serializer.data)

        serializer = CommentSerializer(
            data=request.data,
            context={'post': post}
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user,
                post=post
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # BOOKMARK TOGGLE API
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def bookmark(self, request, slug=None):

        post = self.get_object()

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            bookmark.delete()
            saved = False
        else:
            saved = True

        return Response({
            'bookmarked': saved,
            'message': 'Bookmark updated successfully!'
        })

    # MY SAVED POSTS API
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def saved(self, request):

        posts = Post.objects.filter(
            bookmark__user=request.user
        ).order_by('-created_at')

        serializer = self.get_serializer(
            posts,
            many=True
        )

        return Response(serializer.data)

        # MY POSTS API
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def mine(self, request):

        posts = Post.objects.filter(
            author=request.user
        ).order_by('-created_at')

        serializer = self.get_serializer(
            posts,
            many=True
        )

        return Response(serializer.data)
