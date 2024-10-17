import django_filters
import graphene
from apps.core import CustomNode, CustomizeFilterConnectionField
from apps.user_guide.models import Modules, Courses, CoursesProfileFeaturesBuyer,CoursesProfileFeaturesSupplier
from apps.users.models import Token
from django_filters import FilterSet, OrderingFilter
from django.contrib.auth import get_user_model
from graphene import Connection
from graphene_django.types import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

User = get_user_model()

class ExtendedConnection(Connection):
    class Meta:
        abstract = True
    total_count = graphene.Int()
    def resolve_total_count(root, info, **kwargs):
        return root.length

#----------modules---------
class GetToken():
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key  = key[-1]
            token  = Token.objects.get(key =key)
            return token
        except: 
            raise GraphQLError("Invalid token")

class ModulesFilter(FilterSet):
    class Meta:
        model = Modules
        fields= {
            'id': ['exact'],
            'name': ['icontains'],
            'role': ['exact'],
        }
    order_by = OrderingFilter(fields=('name','status')) 


class ModulesNode(DjangoObjectType):
    class Meta:
        model = Modules
        filterset_class = ModulesFilter
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection
    @classmethod
    def get_queryset (cls, queryset,  info):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            queryset = queryset.filter().order_by('id')
        if token.user.isBuyer():
            queryset = queryset.filter(role=2,status=True).order_by('id')
        if token.user.isSupplier():
            queryset = queryset.filter(role=3,status =True).order_by('id')
        return queryset

class ModulesInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    status = graphene.Boolean(required =True)
    role = graphene.Int(required =True)
    
class ModulesCreate(graphene.Mutation):
    class Arguments:
        modules = ModulesInput(required=True)

    status = graphene.Boolean()
    modules = graphene.Field(ModulesNode)
    def mutate(root, info, modules=None):
        token   = GetToken.getToken(info)
        if token.user.isAdmin():
            modules_instance = Modules(name=modules.name,status = modules.status,role = modules.role)
            modules_instance.save()
            return ModulesCreate(status=True, modules=modules_instance)
        else:
            raise GraphQLError('No permisson')
class ModulesUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        modules = ModulesInput(required=True)

    status = graphene.Boolean()
    modules = graphene.Field(ModulesNode)
    def mutate(root, info, id, modules=None):
        token   = GetToken.getToken(info)
        if token.user.isAdmin():
            modules_instance = Modules.objects.get(pk = id)
            modules_instance.name = modules.name
            modules_instance.status = modules.status
            modules_instance.role = modules.role
            modules_instance.save()
            status = True
            return ModulesUpdate(status=status, modules=modules_instance)
        else:
            raise GraphQLError('No permisson')

class ModulesDelete(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        id = graphene.String(required=True)
    def mutate(root, info,id):
        modules_instance = Modules.objects.get(pk=id)
        modules_instance.delete()
        return ModulesDelete(status=True)

class ModulesStatusInput(graphene.InputObjectType):
    modules_id = graphene.String(required= True)
    status = graphene.Boolean(required =True)

class MoudulesUpdatesStatus(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        list_status = graphene.List(ModulesStatusInput,required = True)
    def mutate(root, info,list_status):
        token   = GetToken.getToken(info)
        if token.user.isAdmin():
            for modules_status in list_status:
                modules = Modules.objects.get(id = modules_status.modules_id)
                modules.status = modules_status.status
                modules.save()
            return MoudulesUpdatesStatus(status= True)
        else:
            raise GraphQLError('No permisson')


#-----------Courses-----------
class CoursesFilter(FilterSet):
    modules_name = django_filters.CharFilter(field_name='modules__name',lookup_expr='icontains')
    profile_features_buyer = django_filters.CharFilter(method='profile_features_buyer_filter')
    profile_features_supplier = django_filters.CharFilter(method='profile_features_supplier_filter')

    class Meta:
        model = Courses
        fields= {
            'id': ['exact'],
            'name': ['icontains'],
            'role': ['exact'],
        }
    order_by = OrderingFilter(fields=('name','modules__name','video','status'))
    def profile_features_buyer_filter(self,queryset,name,value):
        value = value.split(',')
        list_id = map(lambda x: int(x),value)
        courses_profile_features_buyer = list(
            map(lambda x : CoursesProfileFeaturesBuyer.objects.filter(profile_features_id=x).values('courses_id'), list_id))
        courses_ids = courses_profile_features_buyer[0].intersection(*courses_profile_features_buyer[1:])
        queryset = queryset.filter(id__in = courses_ids)
        return queryset

    def profile_features_supplier_filter(self,queryset,name,value):
        value = value.split(',')
        list_id = map(lambda x: int(x),value)
        courses_profile_features_suppliers = list(
            map(lambda x : CoursesProfileFeaturesSupplier.objects.filter(profile_features_id=x).values('courses_id'), list_id))
        courses_ids = courses_profile_features_suppliers[0].intersection(*courses_profile_features_suppliers[1:])
        queryset = queryset.filter(id__in = courses_ids)
        return queryset

class CoursesNode(DjangoObjectType):
    class Meta:
        model = Courses
        filterset_class = CoursesFilter
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection
   
    def resolve_video(self,info):
        if self.video !="":
            return info.context.build_absolute_uri(self.video.url)
        else:
            return ''
            
    @classmethod
    def get_queryset (cls, queryset,  info):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            queryset = queryset.filter().order_by('id')
        if token.user.isBuyer():
            queryset = queryset.filter(role=2,status = True).order_by('id')
        if token.user.isSupplier():
            queryset = queryset.filter(role=3,status = True).order_by('id')
        return queryset

class CoursesInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    modules = graphene.String(required =True)
    profile_level_type = graphene.String(required =True)
    profile_level = graphene.List(graphene.String,required = True)
    status = graphene.Boolean(required =True)
    role = graphene.Int(required =True)
    video = Upload()

class CoursesCreate(graphene.Mutation):
    class Arguments:
        courses = CoursesInput(required=True)
    status = graphene.Boolean()
    courses = graphene.Field(CoursesNode)
    def mutate(root, info, courses=None):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            courses_instance = Courses(name = courses.name,video= courses.video,role = courses.role, modules_id =courses.modules,status = courses.status)
            courses_instance.save()
            for id in courses.profile_level:
                pk = id
                if  courses.profile_level_type == "buyer":
                    profile_features = CoursesProfileFeaturesBuyer(courses = courses_instance,profile_features_id = pk)
                if  courses.profile_level_type == "supplier":
                    profile_features = CoursesProfileFeaturesSupplier(courses = courses_instance,profile_features_id = pk)
                profile_features.save()
            return CoursesCreate(status=True, courses=courses_instance)
        else:
            raise GraphQLError('No permisson')

class CoursesUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        is_delete = graphene.Boolean(required = True)
        courses = CoursesInput(required=True)
    status = graphene.Boolean()
    courses = graphene.Field(CoursesNode)
    def mutate(root, info, id,is_delete, courses=None):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            courses_instance = Courses.objects.get(pk = id)
            if courses.video is None and not is_delete:
                video = courses_instance.video
            else:
                video = courses.video
            courses_instance.name = courses.name
            courses_instance.role = courses.role
            courses_instance.modules_id = courses.modules
            courses_instance.video = video
            courses_instance.status = courses.status
            courses_instance.save()

            list_id = (map(lambda x: int(x),courses.profile_level))

            if  courses.profile_level_type == "buyer":
                profile_featuress = CoursesProfileFeaturesBuyer.objects.filter(courses_id = courses_instance.id)
                list_id_mapping =[]
                for profile_features  in profile_featuress:
                    list_id_mapping.append(profile_features.profile_features_id)

                list_id_mapping=set(list_id_mapping)
                list_id= set(list_id)
                list_create = list_id.difference(list_id_mapping)
                list_delete = list_id_mapping.difference(list_id)

                CoursesProfileFeaturesBuyer.objects.filter(profile_features_id__in = list_delete).delete()
                for profile_features_id in list_create:
                    profile_features = CoursesProfileFeaturesBuyer(courses_id = courses_instance.id, profile_features_id  = profile_features_id)
                    profile_features.save()

            if  courses.profile_level_type == "supplier":
                profile_featuress = CoursesProfileFeaturesSupplier.objects.filter(courses_id = courses_instance.id)
                list_id_mapping =[]
                for profile_features  in profile_featuress:
                    list_id_mapping.append(profile_features.profile_features_id)
                list_id_mapping=set(list_id_mapping)
                list_id= set(list_id)
                
                list_create = list_id.difference(list_id_mapping)
                list_delete = list_id_mapping.difference(list_id)
                CoursesProfileFeaturesSupplier.objects.filter(profile_features_id__in = list_delete).delete()
                for profile_features_id in list_create:
                    profile_features = CoursesProfileFeaturesSupplier(courses_id = courses_instance.id, profile_features_id  = profile_features_id)
                    profile_features.save()
            return CoursesUpdate(status=True, courses=courses_instance)
        else:
            raise GraphQLError('No permisson')

class CoursesDelete(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        id = graphene.String(required=True)
    def mutate(root, info, id):
        courses_instance = Courses.objects.get(pk=id)
        courses_instance.delete()
        return CoursesDelete(status=True)

class CoursesStatusInput(graphene.InputObjectType):
    courses_id = graphene.String(required= True)
    status = graphene.Boolean(required =True)

class CoursesUpdatesStatus(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        list_status = graphene.List(CoursesStatusInput,required = True)
    def mutate(root, info,list_status):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            for courses_status in list_status:
                courses = Courses.objects.get(id = courses_status.courses_id)
                courses.status = courses_status.status
                courses.save()
            return CoursesUpdatesStatus(status= True)
        else:
            raise GraphQLError('No permisson')


class CoursesProfileFeaturesBuyerNode(DjangoObjectType):
    class Meta:
        model = CoursesProfileFeaturesBuyer
        filter_fields = ['id']
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection

class CoursesProfileFeaturesSupplierNode(DjangoObjectType):
    class Meta:
        model = CoursesProfileFeaturesSupplier
        filter_fields = ['id']
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection


class Mutation(graphene.ObjectType):
    modules_create = ModulesCreate.Field()
    modules_update = ModulesUpdate.Field()
    modules_delete = ModulesDelete.Field()
    modules_update_status = MoudulesUpdatesStatus.Field()

    courses_create = CoursesCreate.Field()
    courses_update = CoursesUpdate.Field()
    courses_delete = CoursesDelete.Field()
    courses_update_status = CoursesUpdatesStatus.Field()


class Query(object):
    module = CustomNode.Field(ModulesNode)
    modules = CustomizeFilterConnectionField(ModulesNode)

    course = CustomNode.Field(CoursesNode)
    courses = CustomizeFilterConnectionField(CoursesNode)

    courses_profilefeature_buyer = CustomNode.Field(CoursesProfileFeaturesBuyerNode)
    courses_profilefeature_buyers = CustomizeFilterConnectionField(CoursesProfileFeaturesBuyerNode)

    courses_profilefeature_supplier = CustomNode.Field(CoursesProfileFeaturesSupplierNode)
    courses_profilefeature_suppliers = CustomizeFilterConnectionField(CoursesProfileFeaturesSupplierNode)
