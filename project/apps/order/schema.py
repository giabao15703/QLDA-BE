import graphene
import graphene_django_optimizer as gql_optimizer
from apps.core import CustomizeFilterConnectionField, CustomizeInterface
from apps.graphene_django_plus.fields import CountableConnection
from apps.order.models import (
    Order, 
    OrderDeliveryTimelines, 
    # OrderPaymentDetails, 
    OrderItems
)
from graphene_django import DjangoObjectType
from django_filters import FilterSet, CharFilter, NumberFilter
from apps.users.models import SupplierProductImage, SupplierProductFlashSale, SupplierProductWholesalePrice
from apps.order.models import Login
from django.contrib.auth.hashers import make_password


# ----------------- Order Filter -----------------


class OrderFilter(FilterSet):
    id = NumberFilter(field_name="id", lookup_expr="exact")
    order_status = CharFilter(field_name="order_status", lookup_expr="exact")
    buyer_name = CharFilter(field_name="buyer__company_full_name", lookup_expr="exact")
    supplier_name = CharFilter(field_name="supplier__company_full_name", lookup_expr="exact")
    city_pick_up_id = NumberFilter(field_name="order_delivery_shipping_fee__delivery_shipping_fee__pick_up_city_id", lookup_expr="exact")
    destination_city_id = NumberFilter(field_name="order_delivery_shipping_fee__delivery_shipping_fee__destination_city", lookup_expr="exact")
    class Meta:
        model = Order
        fields = [
            "id", 
        ]
class LoginFilter(FilterSet):
    id = NumberFilter(field_name="id", lookup_expr="exact")
    username = CharFilter(field_name="username", lookup_expr="exact")
    role = CharFilter(field_name="role", lookup_expr="exact")
    class Meta:
        model = Login
        fields = [
            "id", 
        ]
# ----------------- Order Delivery Node -----------------
class OrderDeliveryTimelineNode(DjangoObjectType):
    class Meta:
        model = OrderDeliveryTimelines
        fields = ["order_date", "date", "time"]
        interfaces = (CustomizeInterface,)

# ----------------- Order Payment Node -----------------
# class OrderPaymentDetailsNode(DjangoObjectType):
#     payment_method = graphene.String()
#     payment_status = graphene.String()

#     class Meta:
#         model = OrderPaymentDetails
#         fields = ["payment_method", "payment_status", "amount_paid"]
#         interfaces = (CustomizeInterface,)

#     def resolve_payment_method(self, info):
#         return self.get_payment_method_display()
    
#     def resolve_payment_status(self, info):
#         return self.get_payment_status_display()

# ----------------- Product Supplier Image -----------------
class OrderItemSupplierProductImageNode(DjangoObjectType):
    class Meta: 
        model = SupplierProductImage
        fields = [
            "id",
            "image"
        ]
        interfaces = (CustomizeInterface,)

# ----------------- Product Supplier Flash Sale -----------------
class OrderItemSupplierProductFlashSaleNode(DjangoObjectType):
    class Meta: 
        model = SupplierProductFlashSale
        fields = [
            "id",
            "initial_price",
            "discounted_price"
        ]
        interfaces = (CustomizeInterface,)

# ----------------- Product Supplier Wholesale Price -----------------
class OrderItemSupplierProductWholesalePriceNode(DjangoObjectType):
    class Meta: 
        model = SupplierProductWholesalePrice
        fields = [
            "id",
            "quality_from",
            "quality_to",
            "price_bracket",
            "delivery_days"
        ]
        interfaces = (CustomizeInterface,)

# ----------------- Order Items -----------------
class OrderItemsNode(DjangoObjectType):
    taxGTGT = graphene.Float()
    #buyerClub = graphene.String()
    refund = graphene.Float()
    # rating_product_quality = graphene.Float() 
    # rating_delivery_time = graphene.Float()
    
    class Meta:
        model = OrderItems
        interfaces = (CustomizeInterface,)
   
    def resolve_refund(self, info):
        return None # TODO: Fix this later

    #def resolve_buyerClub(self, info):
     #  return 'Not yet' # TODO: Fix this later

    def resolve_taxGTGT(self, info):
        return float(self.taxGTGT) / 100

    # def resolve_rating_product_quality(self, info):
    #     return float(self.product_quality)

    # def resolve_rating_delivery_time(self, info):
    #     return float(self.delivery_time)
class LoginNode(DjangoObjectType):
    class Meta:
        model = Login
        fields = ("id", "username","password", "role", "is_active")
        interfaces = (CustomizeInterface,)
        connection_class = CountableConnection
        filterset_class = LoginFilter
# ----------------- Order Node -----------------
class OrderNode(DjangoObjectType):
    order_delivery_timelines = graphene.List(OrderDeliveryTimelineNode)
    order_items = graphene.List(OrderItemsNode)
    # order_payment_details = graphene.Field(OrderPaymentDetailsNode)
    #weight = graphene.Int()
    # rating_product_quality = graphene.Float() 
    # rating_delivery_time = graphene.Float()
    class Meta:
        model = Order
        interfaces = (CustomizeInterface,)
        connection_class = CountableConnection
        filterset_class = OrderFilter

    # def resolve_rating_product_quality(self, info):
    #     items = self.order_items.all()
    #     if items.exists():
    #         return sum([item.product_quality for item in items]) / items.count()
    #     return 0.0

    # def resolve_rating_delivery_time(self, info):
    #     items = self.order_items.all()
    #     if items.exists():
    #         return sum([item.delivery_time for item in items]) / items.count()
    #     return 0.0

  # def resolve_country(self, info):
  #     return self.order_addresses.state.country.name

  #def resolve_weight(self, info):
  #   return self.order_delivery_shipping_fee.delivery_shipping_fee.weight
  
  # def resolve_delivery_fee(self, info):
  #     return self.order_delivery_shipping_fee.delivery_shipping_fee.fee

  # def resolve_contract_person(self, info):
  #     return self.buyer.user.full_name

    #def resolve_order_payment_details(self, info):
      #  return self.order_payment_details

    def resolve_order_delivery_timelines(self, info):
        return self.order_delivery_timelines.all()

    def resolve_order_items(self, info):
        return self.order_items.all().order_by('-amount')

  # def resolve_product_service_info(self, info):
  #     return self.order_items.all()

  # def resolve_discount(self, info):
  #     return float(self.discount) / 100

    @classmethod
    def get_queryset(cls, queryset, info):
        return gql_optimizer.query(queryset,info)
                                   
# ----------------- Order Query -----------------
class Query(graphene.ObjectType):
    order = graphene.Field(OrderNode) # TODO: Fix this later
    orders = CustomizeFilterConnectionField(OrderNode)
    login = graphene.Field(LoginNode)
    logins = CustomizeFilterConnectionField(LoginNode)


