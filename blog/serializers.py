from .models import Comment
from rest_framework import serializers
from .models import Post, Tag


class PostSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            return obj.bookmark_set.filter(user=request.user).exists()
        return False

    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    author = serializers.CharField(
        source='author.username',
        read_only=True
    )

    reading_time = serializers.SerializerMethodField()

    def get_reading_time(self, obj):
        import math

        words = len(obj.content.split())
        return max(1, math.ceil(words / 200))

    class Meta:
        model = Post

        fields = [
            'id',
            'author',
            'title',
            'slug',
            'content',
            'cover_image',
            'category',
            'tags',
            'status',
            'created_at',
            'updated_at',
            'reading_time',
            'like_count',
            'is_liked',
            'is_bookmarked',
        ]

        read_only_fields = [
            'id',
            'author',
            'slug',
            'created_at',
            'updated_at'
        ]


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        replies = obj.replies.all().order_by('created_at')

        return CommentSerializer(
            replies,
            many=True,
            context=self.context
        ).data

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment

        fields = [
            'id',
            'post',
            'user',
            'parent',
            'text',
            'created_at',
            'replies',
        ]

        read_only_fields = ['id', 'user', 'post', 'created_at']

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )
        return value

    def validate_parent(self, value):
        if value:
            if value.parent is not None:
                raise serializers.ValidationError(
                    "Replies to replies are not allowed."
                )

            post = self.context.get('post')

            if value.post != post:
                raise serializers.ValidationError(
                    "You cannot reply to a comment from another post."
                )

        return value
