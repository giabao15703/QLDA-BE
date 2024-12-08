import graphene
import graphene_django_optimizer as gql_optimizer
import django_filters

from apps.core import CustomNode, CustomizeFilterConnectionField, Error
from django_filters import FilterSet
from graphene_django import DjangoObjectType
 
from apps.delivery.models import (
    Grading,
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
from apps.users.schema import UserNode
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
    idgvhuongdan = django_filters.CharFilter(field_name='idgvhuongdan__id', lookup_expr="icontains")  # Lọc theo tên giảng viên hướng dẫn
    idgvphanbien = django_filters.CharFilter(field_name='idgvphanbien__id', lookup_expr="icontains")  # Lọc theo tên giảng viên phản biện
    idnhom = django_filters.CharFilter(field_name='idnhom', lookup_expr="exact")  # Lọc theo ID nhóm
    madoan = django_filters.CharFilter(field_name='madoan', lookup_expr="exact")  # Lọc theo mã đồ án
    chuyennganh = django_filters.CharFilter(field_name='chuyennganh', lookup_expr="icontains")  # Lọc theo chuyên ngành
    tendoan = django_filters.CharFilter(field_name='tendoan', lookup_expr="icontains")  # Lọc theo tên đồ án
    mota = django_filters.CharFilter(field_name='mota', lookup_expr="icontains")  # Lọc theo mô tả
    trangthai = django_filters.CharFilter(field_name='trangthai', lookup_expr="exact")  # Lọc theo trạng thái
    idkehoach = django_filters.CharFilter(field_name='idkehoach__id', lookup_expr="exact")
    gvhd_LongName = django_filters.CharFilter(field_name='idgvhuongdan__long_name', lookup_expr="icontains")
    

    #@property
    #def qs(self):
    #    parent = super().qs
    #    key = self.request.headers['Authorization'].split(" ")
    #    key = key[-1]
    #    token = Token.objects.get(key=key)
    #    user = token.user
    #    if user.isAdmin():
    #        user_admin = Admin.objects.filter(user=user).first()
    #        if user_admin:
    #            role = user_admin.role
    #            if role == 1:
    #                return parent
    #            elif role == 3:
    #                return parent.filter(idgvhuongdan=user_admin)
    #    return parent

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

class GroupQLDAFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="status")
    idgvhuongdan = django_filters.CharFilter(field_name='de_tai__idgvhuongdan__id', lookup_expr="exact") 
    idgvphanbien = django_filters.CharFilter(field_name='de_tai__idgvphanbien__id', lookup_expr="exact") 

    def filter_members_count(self, queryset, name, value):
        return queryset.annotate(num_members=Count('join_groups')).filter(num_members=value)

    user_id = django_filters.CharFilter(field_name='join_groups__user__id', lookup_expr="exact")  # Lọc theo ID người dùng
    group_id = django_filters.CharFilter(field_name='join_groups__group__id', lookup_expr="exact")  # Lọc theo ID nhóm
    mssv = django_filters.CharFilter(field_name='join_groups__user__mssv', lookup_expr="icontains")  # Lọc theo mã sinh viên (mssv)

    def filter_by_group_and_user(self, queryset, name, value):
        if self.request.GET.get('group_id') and self.request.GET.get('user_id'):
            return queryset.filter(
                join_groups__group__id=self.request.GET.get('group_id'),
                join_groups__user__id=self.request.GET.get('user_id')
            )
        return queryset

    class Meta:
        model = GroupQLDA
        fields = ['name', 'status', 'idgvhuongdan', 'idgvphanbien', 'user_id', 'group_id', 'mssv']


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
    leader_user_id = django_filters.NumberFilter(field_name="leader_user_id", lookup_expr="exact")
    request_type = django_filters.CharFilter(field_name="request_type", lookup_expr="exact")
    is_approved = django_filters.BooleanFilter(field_name="is_approved", lookup_expr="exact")

    class Meta:
        model = JoinRequest
        fields = []
class JoinRequestNode(DjangoObjectType):
    members_count = graphene.Int()
    leader_notification = graphene.String()
    request_type = graphene.String()  # Đảm bảo khai báo kiểu trả về là String

    class Meta:
        model = JoinRequest
        filterset_class = JoinRequestFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_request_type(self, info):
        # Chuyển đổi giá trị số trong DB sang chuỗi
        if self.request_type == '1':
            return "invite"
        elif self.request_type == '2':
            return "joinRequest"
        return None

    def resolve_leader_notification(self, info):
        current_user = info.context.user
        if current_user.id == self.leader_user_id:
            return f"Thông báo: User {self.user.id} đã gửi yêu cầu tham gia nhóm {self.group.id}."
        return None


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
        
class GradingFilter(FilterSet):
    detai = django_filters.CharFilter(field_name="detai", lookup_expr="exact")
    diem_huongdan = django_filters.NumberFilter(field_name="diem_huongdan", lookup_expr="exact")
    diem_phanbien = django_filters.NumberFilter(field_name="diem_phanbien", lookup_expr="exact")
    type = django_filters.CharFilter(method='filter_by_type')  # Custom field for filtering

    class Meta:
        model = Grading
        fields = []

    def filter_by_type(self, queryset, name, value):
        """
        Custom filter method to handle `type` field for classification.
        """
        if value == 'huongdan':
            return queryset.filter(diem_huongdan__isnull=False)  # Filter for huongdan
        elif value == 'phanbien':
            return queryset.filter(diem_phanbien__isnull=False)  # Filter for phanbien
        return queryset

    @property
    def qs(self):
        parent = super().qs
        key = self.request.headers.get('Authorization', '').split(" ")
        key = key[-1] if len(key) > 1 else None

        # Ensure token exists
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            return parent.none()  # Return empty queryset if token is invalid

        user = token.user

        # Check if user is admin
        if user.isAdmin():
            user_admin = Admin.objects.filter(user=user).first()
            if user_admin:
                role = user_admin.role
                print(role)
                if role in [1, 3]:  # Apply filtering logic based on type
                    filter_type = self.data.get('type')
                    print(user_admin.id)
                    if filter_type == 'PHAN_BIEN':
                        print("PHAN_BIEN")
                        return parent.filter(detai__idgvphanbien=user_admin)
                    elif filter_type == 'HUONG_DAN':
                        print("HUONG_DAN")
                        return parent.filter(detai__idgvhuongdan=user_admin)
        return parent

        
class GradingNode(DjangoObjectType):
    class Meta:
        model = Grading
        filterset_class = GradingFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        
class StudentWithGroupNode(graphene.ObjectType):
    joinGroup = graphene.Field(JoinGroupNode)        


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
    
    gradings = CustomizeFilterConnectionField(GradingNode, filterset_class=GradingFilter)
    grading = CustomNode.Field(GradingNode)

    get_students_in_group = graphene.Field(
        graphene.List(StudentWithGroupNode),  # Đảm bảo trả về danh sách kiểu StudentWithGroupNode
        description="Lấy danh sách sinh viên trong nhóm"
    )
    def resolve_get_students_in_group(self, info):
        try:
            token = GetToken.getToken(info)
            user = token.user  # Lấy thông tin user từ token

            # Lấy tất cả các nhóm mà người dùng tham gia
            join_groups = JoinGroup.objects.filter(user_id=user.id)

            if not join_groups:
                raise GraphQLError("Người dùng không tham gia bất kỳ nhóm nào.")

            # Lấy tất cả các group_id mà người dùng tham gia
            group_ids = [join_group.group_id for join_group in join_groups]

            # Lấy thông tin tất cả các thành viên trong các nhóm mà người dùng tham gia
            join_groups = JoinGroup.objects.filter(group_id__in=group_ids)

            # Lấy thông tin sinh viên và thông tin nhóm (role) từ JoinGroup và trả về danh sách
            students = [
                StudentWithGroupNode(joinGroup=join_group)  # Đảm bảo joinGroup được truyền đúng
                for join_group in join_groups
            ]


            return students

        except Exception as e:
            raise GraphQLError(f"Lỗi: {str(e)}")