import graphene
import graphene_django_optimizer as gql_optimizer

from apps.banner.models import Banner, BannerGroup
from apps.core import CustomizeFilterConnectionField, CustomizeInterface
from apps.graphene_django_plus.fields import CountableConnection
from django_filters import FilterSet, CharFilter, OrderingFilter
from graphene_django import DjangoObjectType

class BannerGroupFilter(FilterSet):
    item_code = CharFilter(field_name="item_code", lookup_expr="icontains")
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = BannerGroup
        fields = []

    order_by = OrderingFilter(
        fields=(
            {
                "id": "id",
                "name": "name"
            }
        )
    )

class BannerFilter(FilterSet):
    group_id = CharFilter(field_name="group__id", lookup_expr="exact")
    site_id = CharFilter(field_name="group__site_id", lookup_expr="exact")

    class Meta:
        model = Banner
        fields = ["name", "sort_order"]

    order_by = OrderingFilter(
        fields=(
            {
                "id": "id",
                "name": "name",
                "sort_order": "sort_order",
            }
        )
    )


class BannerNode(DjangoObjectType):
    class Meta:
        model = Banner
        fields = ["id",
            "created",
            "name",
            "file",
            "sort_order",
            "description",
            "group",
            "link",
            "file_mobile",
            "animation",
        ]
        interfaces = (CustomizeInterface,)
        connection_class = CountableConnection
        filterset_class = BannerFilter

    def resolve_file(self, info, **kwargs):
        if self.file and hasattr(self.file, "url"):
            if self.file.url.lower().replace('/media/', '').startswith("http"):
                return self.file
            else:
                return info.context.build_absolute_uri(self.file.url)
        return None
    
    def resolve_file_mobile(self, info, **kwargs):
        if self.file_mobile and hasattr(self.file_mobile, "url"):
            if self.file_mobile.url.lower().replace('/media/', '').startswith("http"):
                return self.file_mobile
            else:
                return info.context.build_absolute_uri(self.file_mobile.url)
        return None

    @classmethod
    def get_queryset(cls, queryset, info):
        return gql_optimizer.query(queryset, info)


class BannerGroupNode(DjangoObjectType):
    banner_list = graphene.List(BannerNode)

    class Meta:
        model = BannerGroup
        fields = ["id", "name", "description", "banners", "item_code"]
        interfaces = (CustomizeInterface,)
        connection_class = CountableConnection
        filterset_class = BannerGroupFilter

    def resolve_banner_list(self, info, **kwargs):
        return self.banners.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        return gql_optimizer.query(queryset.prefetch_related("banners"), info)


class Query(graphene.ObjectType):
    banner_group_list = CustomizeFilterConnectionField(BannerGroupNode)
    banner_group = graphene.Field(BannerGroupNode, id=graphene.String(), item_code=graphene.String())

    banner_list = CustomizeFilterConnectionField(BannerNode)
    banner = graphene.Field(BannerNode, id=graphene.String(required=True))

    def resolve_banner_group_list(self, info, **kwargs):
        return BannerGroup.objects.all().order_by("id")

    def resolve_banner_group(self, info, **kwargs):
        if kwargs.get("item_code"):
            return BannerGroup.objects.filter(item_code=kwargs.get("item_code")).first()
        return BannerGroup.objects.filter(id=kwargs.get("id")).first()

    def resolve_banner_list(self, info, **kwargs):
        return Banner.objects.all().order_by("sort_order")

    def resolve_banner(self, info, id, **kwargs):
        return Banner.objects.filter(id=id).first()
