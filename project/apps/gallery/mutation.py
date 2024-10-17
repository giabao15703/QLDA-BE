import graphene

from apps.core import errors
from apps.gallery.error_code import GalleryError
from apps.gallery.models import Gallery
from apps.graphene_django_plus.mutations import (
    ModelCreateMutation,
    ModelUpdateMutation,
    ModelDeleteMutation
)
from apps.users.schema import UserNode, GetToken

from django.utils import timezone

class GalleryCreate(ModelCreateMutation):
    class Meta:
        model = Gallery
        only_fields = ["description", "file"]
        allow_unauthenticated = True

    @classmethod
    def mutate(cls, root, info, input):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            return GalleryCreate(errors=errors(GalleryError.GALLERY_02, "GALLERY_02", "id"))

        input._meta.fields.update({"user": graphene.InputField(graphene.Field(UserNode))})
        input._meta.fields.update({"name": graphene.InputField(graphene.String())})
        input["user"] = user
        input["name"] = "{}{}.{}".format(input.file.name.split(".")[0], timezone.now().strftime("_%d%m%Y-%H%M%S%f"), input.file.name.split(".")[-1])
        
        return super().mutate(root, info, input)

class GalleryUpdate(ModelUpdateMutation):
    class Meta:
        model = Gallery
        only_fields = ["description"]
        allow_unauthenticated = True

    @classmethod
    def mutate(cls, root, info, input):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            return GalleryUpdate(errors=errors(GalleryError.GALLERY_02, "GALLERY_02", "id"))

        gallery = Gallery.objects.filter(
            id=input.id,
            user=user
        ).first()
        if not gallery:
            return GalleryUpdate(
                errors=errors(
                    message= GalleryError.GALLERY_01,
                    code = "GALLERY_01",
                    field = "id"
                )
            )

        return super().mutate(root, info, input)

class GalleryDelete(ModelDeleteMutation):
    class Meta:
        model = Gallery
        exclude_fields = ["id"]
        allow_unauthenticated = True

    class Input:
        id = graphene.List(graphene.String, required=True)

    @classmethod
    def mutate(cls, root, info, input):
        error = None
        try:
            user = GetToken.getToken(info).user
        except:
            return GalleryCreate(errors=errors(GalleryError.GALLERY_02, "GALLERY_02", "id"))

        if user.isAdmin():
            if not all(
                Gallery.objects.filter(
                    id=x
                ).exists() for x in input.id
            ):
                return GalleryDelete(errors=errors(GalleryError.GALLERY_01, "GALLERY_01", "id"))

        else:
            if not all(
                Gallery.objects.filter(
                    id=x,
                    user=user
                ).exists() for x in input.id
            ):
                return GalleryDelete(errors=errors(GalleryError.GALLERY_01, "GALLERY_01", "id"))

        Gallery.objects.filter(id__in=input.id).delete()
        return GalleryDelete(status=True)

class Mutation(graphene.ObjectType):
    gallery_create = GalleryCreate.Field()
    gallery_update = GalleryUpdate.Field()
    gallery_delete = GalleryDelete.Field()
