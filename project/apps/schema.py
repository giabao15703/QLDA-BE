import graphene
import apps.delivery.mutation
import apps.master_data.schema
import apps.users.schema
import apps.authentication.schema
import apps.user_guide.schema
from graphene_file_upload.scalars import Upload
import apps.sale_schema.schema
import apps.payment.schema
import apps.auctions.query
import apps.auctions.mutation
import apps.users.mutation
import apps.manage_data.schema
import apps.rfx.schema
import apps.rfx.mutation
import apps.banner.schema
import apps.banner.mutation
import apps.gallery.schema
import apps.gallery.mutation
import apps.delivery.schema
import apps.order.schema
import apps.order.mutation


class Query(
    apps.order.schema.Query,
    apps.payment.schema.Query,
    apps.master_data.schema.Query,
    apps.users.schema.Query,
    apps.user_guide.schema.Query,
    apps.sale_schema.schema.Query,
    apps.auctions.query.Query,
    apps.rfx.schema.Query,
    apps.banner.schema.Query,
    apps.gallery.schema.Query,
    apps.delivery.schema.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    apps.order.mutation.Mutation,
    apps.payment.schema.Mutation,
    apps.master_data.schema.Mutation,
    apps.authentication.schema.Mutation,
    apps.user_guide.schema.Mutation,
    apps.sale_schema.schema.Mutation,
    apps.users.schema.Mutation,
    apps.auctions.mutation.Mutation,
    apps.users.mutation.Mutation,
    apps.manage_data.schema.Mutation,
    apps.rfx.mutation.Mutation,
    apps.banner.mutation.Mutation,
    apps.gallery.mutation.Mutation,
    apps.delivery.mutation.Mutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, types=[Upload])

