from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Comment
from .serializers import CommentSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = self.get_object().post
        return context

    def perform_update(self, serializer):

        comment = self.get_object()

        if comment.user != self.request.user:
            raise PermissionDenied(
                "You can only edit your own comments."
            )

        serializer.save()

    def perform_destroy(self, instance):

        if (
            instance.user != self.request.user
            and instance.post.author != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "You cannot delete this comment."
            )

        instance.delete()
