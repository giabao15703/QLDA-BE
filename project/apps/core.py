import graphene

from django.db.models.query import QuerySet
from django.db import models

from graphene import relay
from graphene_django.converter import convert_django_field
from graphene_django.utils import maybe_queryset
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField, DjangoListField
from graphene.relay import PageInfo
from graphql_relay.connection.connectiontypes import Connection, Edge

class CustomNode(relay.Node):
    @classmethod
    def node_resolver(cls, only_type, root, info, id):
        get_node = getattr(only_type, "get_node", None)
        if get_node:
            return get_node(info, id)

    @classmethod
    def to_global_id(cls, type, id):
        return id

def connection_from_list_slice(list_slice, args=None, connection_type=None, edge_type=None, pageinfo_type=None, slice_start=0, list_length=0, list_slice_length=None):
    connection_type = connection_type or Connection
    edge_type = edge_type or Edge
    pageinfo_type = pageinfo_type or PageInfo

    args = args or {}

    before = args.get("before")
    after = args.get("after")
    first = args.get("first")
    last = args.get("last")
    if list_slice_length is None:
        list_slice_length = len(list_slice)
    slice_end = slice_start + list_slice_length
    before_offset = get_offset_with_default(before, list_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(slice_start - 1, after_offset, -1) + 1
    end_offset = min(slice_end, before_offset, list_length)
    if isinstance(first, int):
        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        start_offset = max(start_offset, end_offset - last)

    _slice = list_slice[max(start_offset - slice_start, 0) : list_slice_length - (slice_end - end_offset)]
    edges = [edge_type(node=node, cursor=start_offset + i) for i, node in enumerate(_slice)]

    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None
    lower_bound = after_offset + 1 if after else 0
    upper_bound = before_offset if before else list_length

    return connection_type(
        edges=edges,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=isinstance(last, int) and start_offset > lower_bound,
            has_next_page=isinstance(first, int) and end_offset < upper_bound,
        ),
    )

def get_offset_with_default(cursor=None, default_offset=0):
    if not isinstance(cursor, str):
        return default_offset

    offset = cursor
    try:
        return int(offset)
    except Exception:
        return default_offset

class CustomizeFilterConnectionField(DjangoFilterConnectionField):
    class Meta:
        name = "CustomizeFilterConnectionField"

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
            list_slice_length = min(max_limit, list_length) if max_limit is not None else list_length
        else:
            list_length = len(iterable)
            list_slice_length = min(max_limit, list_length) if max_limit is not None else list_length

        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        if max_limit is not None and "first" not in args:
            args["first"] = max_limit

        connection = connection_from_list_slice(
            iterable[after:],
            args,
            slice_start=after,
            list_length=list_length,
            list_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length

        return connection


class CustomizeDjangoConnectionField(DjangoConnectionField):
    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
            list_slice_length = min(max_limit, list_length) if max_limit is not None else list_length
        else:
            list_length = len(iterable)
            list_slice_length = min(max_limit, list_length) if max_limit is not None else list_length

        # If after is higher than list_length, connection_from_list_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        if max_limit is not None and "first" not in args:
            args["first"] = max_limit

        connection = connection_from_list_slice(
            iterable[after:],
            args,
            slice_start=after,
            list_length=list_length,
            list_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field, registry=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        description = field.help_text if isinstance(field, models.ManyToManyField) else field.field.help_text

        # If there is a connection, we should transform the field
        # into a DjangoConnectionField
        if _type._meta.connection:
            # Use a DjangoFilterConnectionField if there are
            # defined filter_fields or a filterset_class in the
            # DjangoObjectType Meta
            if _type._meta.filter_fields or _type._meta.filterset_class:

                return CustomizeFilterConnectionField(_type, required=True, description=description)

            return CustomizeDjangoConnectionField(_type, required=True, description=description)

        return DjangoListField(_type, required=True, description=description,)  # A Set is always returned, never None.

    return graphene.Dynamic(dynamic_type)

class CustomizeInterface(graphene.relay.Node):
    class Meta:
        name = "CustomizeInterface"

    @classmethod
    def to_global_id(cls, type, id):
        return id

class Error(graphene.ObjectType):
    code = graphene.String()
    message = graphene.String()
    field = graphene.String()

def errors(message, code, field=None):
    return [
        {
            "message": message,
            "field": field,
            "code": code,
        }
    ]

def get_full_company_address(company_address=None, company_city=None, company_country_name=None):
    full_company_address_list = []
    if company_address:
        full_company_address_list.append(company_address)
    if company_city:
        full_company_address_list.append(company_city)
    if company_country_name:
        full_company_address_list.append(company_country_name)
    return ", ".join(full_company_address_list)
