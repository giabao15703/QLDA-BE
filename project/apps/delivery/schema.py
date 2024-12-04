import graphene
import graphene_django_optimizer as gql_optimizer
import django_filters

from apps.core import CustomNode, CustomizeFilterConnectionField, Error
from django_filters import FilterSet
from graphene_django import DjangoObjectType
 
from apps.delivery.models import (
    Notification,
    ShippingFee,
    TransporterList,
    DeliveryResponsible,
    DeTai,
    User,
    GroupQLDA,
    JoinRequest,
    JoinGroup,
    KeHoachDoAn,
    Admin
)
from apps.users.models import Token
from graphene import relay, ObjectType, Connection
from graphql import GraphQLError

class GetToken:
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            return token
        except:
            raise GraphQLError("DELIVERY_01")

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

class ShippingFeeFilter(FilterSet):
    pick_up_city_code = django_filters.NumberFilter(field_name='pick_up_city_id', lookup_expr="exact")
    pick_up_city_name = django_filters.CharFilter(field_name='pick_up_city__name', lookup_expr="icontains")
    destination_city_code = django_filters.NumberFilter(field_name='destination_city_id', lookup_expr="exact")
    destination_city_name = django_filters.CharFilter(field_name='destination_city__name', lookup_expr="icontains")
    weight = django_filters.NumberFilter(field_name='weight', lookup_expr="exact")
    fee = django_filters.NumberFilter(field_name='fee', lookup_expr="exact")
    status = django_filters.BooleanFilter(field_name='status', lookup_expr="exact")
    class Meta:
        model = ShippingFee
        fields = []

class ShippingFeeNode(DjangoObjectType):
    class Meta:
        model = ShippingFee
        filterset_class = ShippingFeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class TransporterListFilter(FilterSet):
    short_name = django_filters.CharFilter(field_name="short_name", lookup_expr="icontains")
    long_name = django_filters.CharFilter(field_name="long_name", lookup_expr="icontains")
    code = django_filters.CharFilter(field_name='code', lookup_expr="exact")
    tax = django_filters.CharFilter(field_name='tax', lookup_expr="exact")
    phone = django_filters.CharFilter(field_name='phone', lookup_expr="exact")
    address = django_filters.CharFilter(field_name='address', lookup_expr="icontains")
    email = django_filters.CharFilter(field_name='email', lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name='status', lookup_expr="exact")

    class Meta:
        model = TransporterList
        fields = []

class TransporterListNode(DjangoObjectType):
    class Meta:
        model = TransporterList
        filterset_class = TransporterListFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class DeliveryResponsibleFilter(FilterSet):
    transporter_code = django_filters.CharFilter(field_name="transporter_code_id", lookup_expr="exact")
    transporter_short_name = django_filters.CharFilter(field_name="transporter_code__short_name", lookup_expr="icontains")
    city_code = django_filters.CharFilter(field_name='city_code_id', lookup_expr="exact")
    city_name = django_filters.CharFilter(field_name='city_code__name', lookup_expr="icontains")

    class Meta:
        model = DeliveryResponsible
        fields = []

class DeliveryResponsibleNode(DjangoObjectType):
    class Meta:
        model = DeliveryResponsible
        filterset_class = DeliveryResponsibleFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class DeTaiFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id', lookup_expr="exact")
    idgvhuongdan = django_filters.CharFilter(field_name='idgvhuongdan__full_name', lookup_expr="icontains")  # Lọc theo tên giảng viên hướng dẫn
    idgvphanbien = django_filters.CharFilter(field_name='idgvphanbien__full_name', lookup_expr="icontains")  # Lọc theo tên giảng viên phản biện
    idnhom = django_filters.CharFilter(field_name='idnhom', lookup_expr="exact")  # Lọc theo ID nhóm
    madoan = django_filters.CharFilter(field_name='madoan', lookup_expr="exact")  # Lọc theo mã đồ án
    chuyennganh = django_filters.CharFilter(field_name='chuyennganh', lookup_expr="icontains")  # Lọc theo chuyên ngành
    tendoan = django_filters.CharFilter(field_name='tendoan', lookup_expr="icontains")  # Lọc theo tên đồ án
    trangthai = django_filters.CharFilter(field_name='trangthai', lookup_expr="exact")  # Lọc theo trạng thái
    idkehoach = django_filters.CharFilter(field_name='idkehoach__id', lookup_expr="exact")

    @property
    def qs(self):
        parent = super().qs
        key = self.request.headers['Authorization'].split(" ")
        key = key[-1]
        token = Token.objects.get(key=key)
        user = token.user
        if user.isAdmin():
            user_admin = Admin.objects.filter(user=user).first()
            if user_admin:
                role = user_admin.role
                if role == 1:
                    return parent
                elif role == 3:
                    return parent.filter(idgvhuongdan=user_admin)
        return parent

    class Meta:
        model = DeTai
        fields = []

class DeTaiNode(DjangoObjectType):
    giang_vien_long_name = graphene.String()
    ke_hoach_do_an_id = graphene.ID()
    giang_vien_phan_bien_long_name = graphene.String()

    class Meta:
        model = DeTai
        filterset_class = DeTaiFilter
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection

    def resolve_giang_vien_long_name(self, info):
        # Lấy long_name của giảng viên hướng dẫn
        return self.idgvhuongdan.long_name if self.idgvhuongdan else None

    def resolve_giang_vien_phan_bien_long_name(self, info):
        # Lấy long_name của giảng viên phản biện nếu có
        return self.idgvphanbien.long_name if self.idgvphanbien else None

    def resolve_ke_hoach_do_an_id(self, info):
        # Trả về ID của kế hoạch đồ án
        return self.idkehoach.id if self.idkehoach else None





class GroupQLDAFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="status")
    idgvhuongdan = django_filters.CharFilter(field_name='de_tai__idgvhuongdan__id', lookup_expr="exact")  # Lọc theo id giảng viên hướng dẫn
    idgvphanbien = django_filters.CharFilter(field_name='de_tai__idgvphanbien__id', lookup_expr="exact") 

    def filter_members_count(self, queryset, name, value):
        return queryset.annotate(num_members=models.Count('members')).filter(num_members=value)


    class Meta:
        model = GroupQLDA
        fields = []


class GroupQLDANode(DjangoObjectType):
    creator_short_name = graphene.String()

    class Meta:
        model = GroupQLDA
        filterset_class = GroupQLDAFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_creator_short_name(self, info):
        return self.leader_user.short_name if self.leader_user else None


class JoinGroupFilter(FilterSet):
    user_id = django_filters.NumberFilter(field_name="user_id", lookup_expr="exact")
    group_id = django_filters.NumberFilter(field_name="group_id", lookup_expr="exact")
    role = django_filters.CharFilter(field_name="role", lookup_expr="icontains")

class JoinGroupNode(DjangoObjectType):
    class Meta:
        model = JoinGroup
        filterset_class = JoinGroupFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class JoinRequestFilter(FilterSet):
    user_id = django_filters.NumberFilter(field_name="user_id", lookup_expr="exact")
    group_id = django_filters.NumberFilter(field_name="group_id", lookup_expr="exact")
    is_approved = django_filters.BooleanFilter(field_name="is_approved", lookup_expr="exact")

    class Meta:
        model = JoinRequest
        fields = []
class JoinRequestNode(DjangoObjectType):
    members_count = graphene.Int()
    leader_notification = graphene.String()  # Thêm trường để chứa thông báo dành riêng cho leader

    class Meta:
        model = JoinRequest
        filterset_class = JoinRequestFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_leader_notification(self, info):
        # Lấy thông tin người dùng hiện tại
        current_user = info.context.user

        # Kiểm tra nếu người dùng hiện tại là leader của nhóm bằng cách so sánh với leader_user_id
        if current_user.id == self.leader_user_id:
            return f"Thông báo: User {self.user.id} đã gửi yêu cầu tham gia nhóm {self.group.id}."
        else:
            return None  # Không hiện thông báo cho người không phải leader

class KeHoachDoAnFilter(FilterSet):
    ma_ke_hoach = django_filters.CharFilter(field_name="ma_ke_hoach", lookup_expr="icontains")
    sl_sinh_vien = django_filters.NumberFilter(field_name="sl_sinh_vien", lookup_expr="exact")
    sl_do_an = django_filters.NumberFilter(field_name="sl_do_an", lookup_expr="exact")
    ky_mo = django_filters.CharFilter(field_name="ky_mo", lookup_expr="icontains")

    class Meta:
        model = KeHoachDoAn
        fields = []

class KeHoachDoAnNode(DjangoObjectType):
    class Meta:
        model = KeHoachDoAn
        filterset_class = KeHoachDoAnFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class NotificationFilter(FilterSet):
    created_date = django_filters.DateTimeFilter(field_name="created_date", lookup_expr="exact")
    status = django_filters.BooleanFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Notification
        fields = []
        
class NotificationNode(DjangoObjectType):
    class Meta:
        model = Notification
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        


class Query(object):
    shipping_fee = CustomNode.Field(ShippingFeeNode)
    shipping_fees = CustomizeFilterConnectionField(ShippingFeeNode)
    
    transporter_list = CustomNode.Field(TransporterListNode)
    transporter_lists = CustomizeFilterConnectionField(TransporterListNode)

    delivery_responsible = CustomNode.Field(DeliveryResponsibleNode)
    delivery_responsibles = CustomizeFilterConnectionField(DeliveryResponsibleNode)

    de_tai = CustomNode.Field(DeTaiNode)
    de_tais = CustomizeFilterConnectionField(DeTaiNode)

    group_qlda = CustomNode.Field(GroupQLDANode)
    group_qldas = CustomizeFilterConnectionField(GroupQLDANode, filterset_class=GroupQLDAFilter)

    join_group = CustomNode.Field(JoinGroupNode)
    join_groups = CustomizeFilterConnectionField(JoinGroupNode, filterset_class=JoinGroupFilter)
    join_request= CustomNode.Field(JoinRequestNode)
    
    join_requests = CustomizeFilterConnectionField(JoinRequestNode, filterset_class=JoinRequestFilter)

    ke_hoach_do_an = CustomNode.Field(KeHoachDoAnNode)
    ke_hoach_do_ans = CustomizeFilterConnectionField(KeHoachDoAnNode, filterset_class=KeHoachDoAnFilter)
    
    notifications = CustomizeFilterConnectionField(NotificationNode, filterset_class=NotificationFilter)
    notification = CustomNode.Field(NotificationNode)

