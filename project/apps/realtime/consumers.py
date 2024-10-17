import json
import datetime
import asyncio
from django.utils import timezone
from django.db.models import Max, Min
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.auctions.models import (
    Auction,
    AuctionBid,
    AuctionSupplier,
    AuctionTypeDutch,
    AuctionTypeJapanese,
    AuctionTypePrices,
    AuctionTypeSealedBid,
    AuctionTypeTrafficLight,
    AuctionTypeRanking,
    AuctionItem,
    AuctionItemSupplier,
)
from apps.auctions.serializers import  AuctionBidSerializer
from apps.users.models import User, Token
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import os
from django.contrib.auth.models import AnonymousUser

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from urllib.parse import parse_qs
import dateutil.parser
import operator


@database_sync_to_async
def get_user_name(query_string):
    try:
        token_key = query_string[b'token'][0].decode()
        token = Token.objects.get(key=token_key)
        return token.user

    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)


class TokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        query_string = parse_qs(self.scope['query_string'])
        if b'token' in query_string:
            self.scope['user'] = await get_user_name(query_string)
        inner = self.inner(self.scope)
        return await inner(receive, send)


class RealtimeConsumer(AsyncWebsocketConsumer):

    auctions = {}
    data = {}

    async def auction_add(self, group):
        """
        Adds the channel name to a auction.
        """
        self.auctions[group] = True

    async def auction_discard(self, group):
        del self.auctions[group]

    async def connect(self):

        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_id = 'auction_%s' % self.auction_id

        await self.channel_layer.group_add(self.auction_group_id, self.channel_name)

        asyncio.create_task(self.background_task())
        self.user = self.scope["user"]
        await self.accept()

    async def disconnect(self, close_code):
        server_time = timezone.now()
        await self.channel_layer.group_send(
            self.auction_group_id, {'type': 'check_connection', 'message': {"status": "Disconnect", "username": self.user.username}},
        )
        await self.channel_layer.group_discard(self.auction_group_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data["type"] == "check_connection":
            message = data['message']
            time_send = dateutil.parser.parse(message.get("server_time"))
            server_time = timezone.now()
            delta_time = (server_time - time_send).seconds
            status = None
            if delta_time <= 1:
                status = "Good"
            else:
                status = "Medium"
            message = {"status": status, "username": message.get("username")}
            res_connection = {
                'type': 'check_connection',
                'message': message,
            }
            await self.channel_layer.group_send(self.auction_group_id, res_connection)

        if data['type'] == 'auction_message':

            await self.auction_bid(data)
            data = await self.trigger_time(data)

            # Send message to group
            await self.channel_layer.group_send(self.auction_group_id, data)

    async def auction_message(self, data):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(data))

    async def trigger_time(self, data):
        auction = await sync_to_async(Auction.objects.prefetch_related('bids', 'items').get)(pk=self.auction_id)
        items = auction.items.all()
        end_time = auction.extend_time or auction.end_time
        number_of_times_triggered = auction.number_of_times_triggered
        options = await sync_to_async(get_options)(auction=auction)

        item_id = data['message']['item_id']

        if (
            auction.auction_type1_id != 5
            and auction.auction_type1_id != 6
            and options.auction_extension == 2
            and options.auction_extension_trigger != 3
            and auction.number_of_times_triggered < options.frequency
            and options.trigger_time is not None
        ):

            number_of_bids = await get_number_of_bid(auction=auction, item_id=item_id)
            if options.auction_extension_trigger == 1:
                (end_time, number_of_times_triggered) = await self.extend_time(auction, options.trigger_time, options.prolongation_by)

            elif options.auction_extension_trigger == 2:
                if number_of_bids > options.number_of_rankings:

                    isTrigger = False

                    last_bid = await get_last_bid(auction=auction, item_id=item_id)

                    min_bids = await get_min_bid(auction=auction, item_id=item_id, options=options)
                    for min_bid in min_bids:
                        if min_bid.id == last_bid.id:
                            isTrigger = True

                    if isTrigger:
                        (end_time, number_of_times_triggered) = await self.extend_time(auction, options.trigger_time, options.prolongation_by)

                else:
                    (end_time, number_of_times_triggered) = await self.extend_time(auction, options.trigger_time, options.prolongation_by)

        bids = auction.bids.all()

        rating = await self.rating(auction, options, bids)
        rating_total = await get_rating_total(auction)
        response = {
            **data,
            'end_time': end_time.isoformat(),
            'number_of_times_triggered': number_of_times_triggered,
            'bids': await serializer_bids(auction=auction),
            'rating': rating,
            'rating_total': rating_total,
        }

        return response

    async def extend_time(self, auction, trigger_time, prolongation_by):
        trigger_time_obj = datetime.timedelta(minutes=trigger_time)
        prolongation_by_obj = datetime.timedelta(minutes=prolongation_by)

        end_time = auction.extend_time or auction.end_time
        await check_extend_time(auction=auction, trigger_time_obj=trigger_time_obj, prolongation_by_obj=prolongation_by_obj, end_time=end_time)
        end_time = auction.extend_time or auction.end_time

        return (end_time, auction.number_of_times_triggered)

    async def rating(self, auction, options, bids):
        items = auction.items.all()

        bids = []

        for item in items:
            item_bids = await get_item_bid(auction=auction, item=item)
            result = await add_list_bids(item_bids=item_bids, bids=bids)
        return result

    async def auction_bid(self, data):
        message = data['message']
        if self.auction_id is not None:
            await create_bid(self, message)

    async def background_task(self):
        auction = await sync_to_async(Auction.objects.prefetch_related('bids', 'items').get)(pk=self.auction_id)
        items = auction.items.all()
        end_time = auction.extend_time or auction.end_time
        number_of_times_triggered = auction.number_of_times_triggered
        options = await sync_to_async(get_options)(auction=auction)

        if self.auction_group_id not in self.auctions:
            while True:

                server_time = timezone.now()

                if self.auction_group_id in self.channel_layer.groups:

                    await self.channel_layer.group_send(
                        self.auction_group_id, {'type': 'join_message', 'message': {'server_time': server_time.isoformat()}}
                    )

                    if (
                        auction.auction_type1_id != 5
                        and auction.auction_type1_id != 6
                        and options.auction_extension == 2
                        and options.auction_extension_trigger == 3
                        and auction.number_of_times_triggered < options.frequency
                    ):

                        # get each item
                        for item in items:

                            number_of_bids = await get_number_of_bid(auction=auction, item_id=item.id)

                            print(number_of_bids)

                            if number_of_bids >= 2:

                                # get 2 best bid of item
                                min_bids = await get_2_best_bid_of_item(auction=auction, item=item)

                                # if 2 best bid equal => extend
                                if min_bids[0].price == min_bids[1].price and server_time >= end_time:
                                    (end_time, number_of_times_triggered) = await self.extend_time(auction, 0, options.prolongation_by)

                                    bids = auction.bids.all()

                                    rating = await self.rating(auction, options, bids)

                                    serializer = AuctionBidSerializer(auction.bids.all(), many=True)
                                    rating_total = await get_rating_total(auction)
                                    response = {
                                        'type': 'auction_message',
                                        'end_time': end_time.isoformat(),
                                        'number_of_times_triggered': number_of_times_triggered,
                                        'bids': serializer.data,
                                        'rating': rating,
                                        'rating_total': rating_total,
                                    }
                                    # Send message to group
                                    await self.channel_layer.group_send(self.auction_group_id, response)

                                    break

                    await self.auction_add(self.auction_group_id)
                    await asyncio.sleep(0.997)
                else:
                    print('Break WHILEEEE')
                    await self.auction_discard(self.auction_group_id)
                    break

    async def join_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({'type': 'server_time', 'message': message}))

    async def check_connection(self, data):
        await self.send(text_data=json.dumps(data))


@database_sync_to_async
def serializer_bids(auction):
    return AuctionBidSerializer(auction.bids.all(), many=True).data


@database_sync_to_async
def check_extend_time(auction, trigger_time_obj, prolongation_by_obj, end_time):
    if timezone.now() + trigger_time_obj >= end_time:
        auction.extend_time = end_time + prolongation_by_obj
        auction.number_of_times_triggered += 1
        auction.save()


@database_sync_to_async
def add_list_bids(item_bids, bids):
    for item_bid in item_bids:
        bids.append(item_bid)
    return bids


def get_options(auction):
    options = None
    if auction.auction_type1_id == 1:
        options = AuctionTypeTrafficLight.objects.get(auction_id=auction.id)
    if auction.auction_type1_id == 2:
        options = AuctionTypeSealedBid.objects.get(auction_id=auction.id)
    if auction.auction_type1_id == 3:
        options = AuctionTypeRanking.objects.get(auction_id=auction.id)
    if auction.auction_type1_id == 4:
        options = AuctionTypePrices.objects.get(auction_id=auction.id)
    if auction.auction_type1_id == 5:
        options = AuctionTypeDutch.objects.get(auction_id=auction.id)
    if auction.auction_type1_id == 6:
        options = AuctionTypeJapanese.objects.get(auction_id=auction.id)
    return options


@database_sync_to_async
def create_bid(self, message):
    return AuctionBid.objects.create(
        auction_id=self.auction_id, user_id=message['user_id'], price=message['price'], auction_item_id=message['item_id'],
    )


@database_sync_to_async
def get_number_of_bid(auction, item_id):
    return AuctionBid.objects.filter(auction_id=auction.id, auction_item_id=item_id).distinct('user_id').order_by('user_id', 'price').count()


@database_sync_to_async
def get_last_bid(auction, item_id):
    return AuctionBid.objects.filter(auction_id=auction.id, auction_item_id=item_id).order_by('-id')[0]


@database_sync_to_async
def get_min_bid(auction, item_id, options):
    return AuctionBid.objects.filter(
        id__in=(AuctionBid.objects.filter(auction_id=auction.id, auction_item_id=item_id).distinct('user_id').order_by('user_id', 'price'))
    ).order_by('price', 'id')[0 : options.number_of_rankings]


@database_sync_to_async
def get_item_bid(auction, item):
    return (
        AuctionBid.objects.filter(auction_id=auction.id, auction_item_id=item.id)
        .values('auction_id', 'auction_item_id', 'user_id')
        .annotate(min_price=Min('price'), bid_id=Max('id'), ranking=Window(expression=RowNumber(), order_by=(Min('price'), Max('id'))))
        .order_by('ranking')
    )


@database_sync_to_async
def get_2_best_bid_of_item(auction, item):
    min_bids = AuctionBid.objects.filter(
        id__in=(AuctionBid.objects.filter(auction_id=auction.id, auction_item_id=item.id).distinct('user_id').order_by('user_id', 'price'))
    ).order_by('price', 'id')[0:2]


@database_sync_to_async
def get_rating_total(auction):
    auction_item = AuctionItem.objects.filter(auction=auction)
    auction_supplier = AuctionSupplier.objects.filter(auction=auction, is_accept=True, supplier_status__in=[5, 6, 8, 9, 10]).order_by('id')
    list_total_bid = []
    for supplier in auction_supplier:
        total_bid = 0
        for item in auction_item:
            auction_bids = AuctionBid.objects.filter(user=supplier.user, auction_item=item).order_by('id')
            auction_item_supplier = AuctionItemSupplier.objects.filter(auction_item=item, auction_supplier=supplier).first()
            if auction_bids.exists():
                price = auction_bids.last().price
            else:
                price = auction_item_supplier.confirm_price
            total_bid += price
        list_total_bid.append({"user_id": supplier.user_id, "total_bid": total_bid})
    total_bid_list = []
    for supplier in list_total_bid:
        total_bid_list.append(supplier.get("total_bid"))
    ratings = sorted(list_total_bid, key=operator.itemgetter("total_bid"))

    return ratings


class ConsumerLoginCheck(AsyncWebsocketConsumer):
    users = {}

    async def user_add(self, group):
        self.users[group] = True

    async def user_discard(self, group):
        del self.users[group]

    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.user_group_id = 'username_%s' % self.username

        await self.channel_layer.group_add(self.user_group_id, self.channel_name)
        asyncio.create_task(self.check_user_buyer())

        await self.accept()

    async def disconnect(self, close_code):
        await self.user_discard(self.user_group_id)
        await self.channel_layer.group_discard(self.user_group_id, self.channel_name)

    async def buyer_login_check(self, data):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(data))

    async def check_user_buyer(self):
        user = await get_user(self)
        if user.user_type == 2 and self.user_group_id in self.users:
            response = {'type': 'buyer_login_check', 'message': False}
        else:
            await self.user_add(self.user_group_id)
            response = {'type': 'buyer_login_check', 'message': True}
        await self.channel_layer.group_send(self.user_group_id, response)


@database_sync_to_async
def get_user(self):
    return User.objects.get(username=self.username)

