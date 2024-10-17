import graphene

from apps.core import Error
from apps.banner.error_code import BannerError
from apps.banner.models import Banner, BannerGroup
from apps.graphene_django_plus.mutations import ModelCreateMutation, ModelUpdateMutation
from apps.master_data.schema import GetToken
from django.db import transaction
from graphene_file_upload.scalars import Upload

class BannerGroupBannerInput(graphene.InputObjectType):
    name = graphene.String()
    file = Upload()
    file_mobile = Upload()
    sort_order = graphene.Int()
    description = graphene.String()
    link = graphene.String()
    animation = graphene.String()

class BannerGroupItemUpdateInput(graphene.InputObjectType):
    id = graphene.String()
    name = graphene.String()
    file = Upload()
    file_mobile = Upload(required=False)
    sort_order = graphene.Int()
    description = graphene.String()
    link = graphene.String()
    animation = graphene.String()

class BannerGroupBannerCreate(ModelCreateMutation):
    status = graphene.Boolean(default_value=False)
    errors = graphene.List(Error)

    class Meta:
        model = BannerGroup
        only_fields = ["name", "description", "item_code"]
        allow_unauthenticated = True

    class Input:
        banners = graphene.List(BannerGroupBannerInput)
    
    @classmethod
    def mutate(cls, root, info, input):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            error = Error(code = "BANNER_02", message = BannerError.BANNER_02)
            return BannerGroupBannerCreate(status = False, errors = [error])
        if not user.isAdmin():
            error = Error(code = "BANNER_02", message = BannerError.BANNER_02)
            return BannerGroupBannerCreate(status = False, errors = [error])
        if BannerGroup.objects.filter(item_code=input["item_code"]).exists():
            error = Error(code = "BANNER_03", message = BannerError.BANNER_03)
            return BannerGroupBannerCreate(status = False, errors = [error])
        if input.get("banners") and len(input["banners"]) > 0:
            seen = set()
            uniq = [x for x in input.get("banners") if x.get("sort_order") not in seen and not seen.add(x.get("sort_order"))]
            if len(seen) < len(input.get("banners")):
                error = Error(code="BANNER_04", message=BannerError.BANNER_04)
                return BannerGroupBannerCreate(status = False, errors = [error])
        return super().mutate(root, info, input)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            payload = super().perform_mutation(root, info, **data)
            if data.get("banners") and len(data["banners"]) > 0:
                banner_list = []
                for banner in data["banners"]:
                    banner_list.append(
                        Banner(
                            name=banner.name,
                            file=banner.file,
                            file_mobile=banner.file_mobile,
                            link=banner.link,
                            sort_order=banner.sort_order if banner.sort_order is not None else 0,
                            description=banner.description,
                            group=payload.bannerGroup
                        )
                    )
                Banner.objects.bulk_create(banner_list)
            return BannerGroupBannerCreate(status=True, bannerGroup=payload.bannerGroup)
        except Exception as error:
            transaction.set_rollback(True)
            return BannerGroupBannerCreate(error)

class BannerGroupBannerUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    errors = graphene.List(Error)

    class Meta:
        model = BannerGroup
        only_fields = ["name", "description", "item_code", "richtext", "animation"]
        allow_unauthenticated = True

    class Input:
        banner_list = graphene.List(BannerGroupItemUpdateInput)
        banners_remove = graphene.List(graphene.String)    

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            user = GetToken.getToken(info).user
        except:
            error = Error(code = "BANNER_02", message = BannerError.BANNER_02)
            return BannerGroupBannerUpdate(status = False, errors = [error])
        if not user.isAdmin():
            error = Error(code = "BANNER_02", message = BannerError.BANNER_02)
            return BannerGroupBannerUpdate(status = False, errors = [error])
        try:
            if not BannerGroup.objects.filter(id=data.get("id")).exists():
                error = Error(code="BANNER_06", message=BannerError.BANNER_06)
                return BannerGroupBannerUpdate(status=False, errors = [error])
            
            if "item_code" in data and BannerGroup.objects.filter(item_code=data["item_code"]).exclude(id=data.get("id")).exists():
                error = Error(code="BANNER_05", message=BannerError.BANNER_05)
                return BannerGroupBannerUpdate(status=False, errors = [error])

            payload = super().perform_mutation(root, info, **data)

            bannerGroup = payload.bannerGroup
            if data.get("banner_list") and not all(Banner.objects.filter(id=x.get("id"), group_id=data.get("id")).exists() for x in data.get("banner_list") if x.get("id") is not None):
                error = Error(code="BANNER_01", message=BannerError.BANNER_01)
                return BannerGroupBannerUpdate(status=False, errors = [error])

            if data.get("banners_remove") and not all(Banner.objects.filter(id=x,group_id=data.get("id")).exists() for x in data.get("banners_remove")):
                error = Error(code="BANNER_01", message=BannerError.BANNER_01)
                return BannerGroupBannerUpdate(status=False, errors = [error])
            #Check sort order
            seen = set()
            lenght = 0
            if data.get("banner_list") and len(data["banner_list"]) > 0:
                uniq = [x for x in data.get("banner_list") if x.get("sort_order") not in seen and not seen.add(x.get("sort_order"))]
                lenght += len(data["banner_list"])
            
            if len(seen) < lenght:
                error = Error(code="BANNER_04", message=BannerError.BANNER_04)
                return BannerGroupBannerUpdate(status=False, errors = [error])
            if data.get("banner_list") and len(data["banner_list"]) > 0:
                banner_create_list = []
                for banner in data["banner_list"]:
                    if banner.get("id") is None:
                        if banner.get("file") is not None or banner.get("file_mobile") is not None:
                            if banner.sort_order is not None:
                                sort_order = banner.sort_order
                            else:
                                sort_order = 0
                            banner_create_list.append(
                                Banner(
                                    name = banner.name,
                                    file = banner.file,
                                    file_mobile = banner.file_mobile,
                                    link = banner.link,
                                    sort_order = sort_order,
                                    description = banner.description,
                                    group = bannerGroup
                                )
                            )
                    else:
                        new_banner = Banner.objects.get(id=banner.id)
                        if "name" in banner:
                            new_banner.name = banner.name
                        if "file" in banner:
                            new_banner.file = banner.file
                        if "file_mobile" in banner:
                            new_banner.file_mobile = banner.file_mobile
                        if "link" in banner:
                            new_banner.link = banner.link
                        if "sort_order" in banner:
                            new_banner.sort_order = banner.sort_order
                        if "description" in banner:
                            new_banner.description = banner.description
                        new_banner.save()
                Banner.objects.bulk_create(banner_create_list)
                
            if data.get("banners_remove") and len(data["banners_remove"]) > 0:
                Banner.objects.filter(id__in=data.get("banners_remove")).delete()
            return BannerGroupBannerUpdate(status = True, bannerGroup = bannerGroup)
        except Exception as error:
            print(error)
            transaction.set_rollback(True)
            return BannerGroupBannerUpdate(status = False, errors = [error])

class Mutation(graphene.ObjectType):
    banner_group_banner_create = BannerGroupBannerCreate.Field()
    banner_group_banner_update = BannerGroupBannerUpdate.Field()
