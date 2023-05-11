from rest_framework import pagination, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Ad, Comment
from .filters import AdFilter
from .serializers import AdSerializer, AdDetailSerializer, CommentSerializer

from ads.permissions import AdAdminPermission, IsExecutor, IsOwner


class AdPagination(pagination.PageNumberPagination):
    """ Пагинация на страницу не более 4 объектов """
    page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    """ Вьюсет который выводит список всех объектов """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = AdPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdFilter
    # http_method_names = ["patch", "get", "post", "delete"]
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [IsOwner, ]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ["create", "update", "partial_update", "destroy", "me"]:
            self.permission_classes = [IsAuthenticated, AdAdminPermission | IsExecutor]

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        self.queryset = Ad.objects.filter(author=request.user)
        return super().list(self, request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# class AdPagination(pagination.PageNumberPagination):
#     page_size = 4
#
#
#
# class AdViewSet(viewsets.ModelViewSet):
#     queryset = Ad.objects.all()
#     pagination_class = AdPagination
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = AdFilter
#     serializer_class = AdSerializer
#
#     def get_queryset(self):
#         if self.action == 'me':
#             return Ad.objects.filter(author=self.request.user).all()
#         return Ad.objects.all()
#
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve', 'create', 'me']:
#             self.permission_classes = [permissions.IsAuthenticated]
#         else:
#             self.permission_classes = [permissions.IsAdminUser]
#         return super().get_permissions()
#
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return AdDetailSerializer
#         return AdSerializer
#
#
#     @action(detail=False, methods=['get'])
#     def me(self, request, *args, **kwargs):
#         return super().list(self, request, *args, **kwargs)
#


class CommentViewSet(viewsets.ModelViewSet):
    """ Вьюсет который выводит список всех объектов """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = None
    # http_method_names = ["patch", "get", "post", "delete"]

    def perform_create(self, serializer):
        ads_id = self.kwargs.get("ads_pk")
        ad_instance = get_object_or_404(Ad, id=ads_id)
        user = self.request.user
        serializer.save(author=user, ad=ad_instance)

    def get_queryset(self, *args, **kwargs):
        comment = self.kwargs.get('ads_pk')
        return super().get_queryset().filter(ad=comment)

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ["create", "update", "partial_update", "destroy", ]:
            self.permission_classes = [IsAuthenticated, AdAdminPermission | IsExecutor]
        return super().get_permissions()

