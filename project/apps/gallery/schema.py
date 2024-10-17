import graphene
import graphene_django_optimizer as gql_optimizer

from apps.core import CustomizeFilterConnectionField, CustomizeInterface
from apps.gallery.models import Gallery
from apps.graphene_django_plus.fields import CountableConnection
from apps.users.schema import GetToken

from django_filters import FilterSet, CharFilter, OrderingFilter

from graphene_django import DjangoObjectType

class GalleryFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    file = CharFilter(field_name="file", lookup_expr="icontains")
    user_id = CharFilter(field_name="user_id", lookup_expr="exact")

    class Meta:
        model = Gallery
        fields = ["name", "user_id"]

    order_by = OrderingFilter(
        fields = (
            {
                "id": "id",
                "name": "name",
                "user_id": "user"
            }
        )
    )

class GalleryNode(DjangoObjectType):
    class Meta:
        model = Gallery
        fields = ["id", "user", "name", "file", "description"]
        interfaces = (CustomizeInterface,)
        connection_class = CountableConnection
        filterset_class = GalleryFilter

    def resolve_file(self, info, **kwargs):
        if self.file and hasattr(self.file, "url"):
            return info.context.build_absolute_uri(self.file.url)
        return None

    @classmethod
    def get_queryset(cls, queryset, info):
        return gql_optimizer.query(queryset, info)


class Query(graphene.ObjectType):
    galleries = CustomizeFilterConnectionField(GalleryNode)
    gallery = graphene.Field(GalleryNode, id=graphene.String(required=True))

    def resolve_galleries(self, info, **kwargs):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            return Gallery.objects.none()

        return Gallery.objects.all()

    def resolve_gallery(self, info, id, **kwargs):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            return []

        if info.context.user.isAdmin():
            return Gallery.objects.filter(id=id).first()
        return Gallery.objects.filter(id=id, user=user).first()
