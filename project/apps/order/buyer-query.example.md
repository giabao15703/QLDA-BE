# Example response expected
{
  "Supplier": {
    "orderCode": "number",
    "status": "string",
    "supplierName": "string",
    "contractPerson": "string",
    "address": "string",
    "phone": "number",
    "deliveryInfo": "string",
    "taxCode": "number",
    "deliveryTimeline": [
      {
        "orderDate": "string",
        "date": "string",
        "time": "string"
      },
      {
        "orderConfirmation": "string",
        "date": "string",
        "time": "string"
      },
      {
        "transport": "string",
        "date": "string",
        "time": "string"
      },
      {
        "deleveryDate": "string",
        "date": "string"
      }
    ],
    "deliveryAddress": "string",
    "city": "string",
    "country": "string",
    "productServiceInfo": [
      {
        "productName": "string",
        "image": "string",
        "specifications": "string",
        "quantity": "number",
        "unitPrice": "number",
        "taxGTGT": "number",
        "buyerClub": "number",
        "refund": "number",
        "price": "number"
      }
    ],
    "deliveryFee": "number",
    "totalPrice": "number",
    "currency": "string",
    "paymentMethod": "string"
  },
  "Transporter": {
    "orderCode": "number",
    "status": "string",
    "supplierName": "string",
    "deliveryAddress": "string",
    "phone": "number",
    "city": "number",
    "deliveryBrand": "string",
    "country": "string",
    "deliveryTimeline": [
      {
        "orderDate": "string",
        "date": "string",
        "time": "string"
      },
      {
        "orderConfirmation": "string",
        "date": "string",
        "time": "string"
      },
      {
        "transport": "string",
        "date": "string",
        "time": "string"
      },
      {
        "deleveryDate": "string",
        "date": "string"
      }
    ],
    "consigneeInformation": {
      "fullName": "string",
      "address": "string",
      "phone": "number",
      "city": "string",
      "email": "string",
      "country": "string"
    },
    "productServiceInfo": [
      {
        "productName": "string",
        "image": "string",
        "specifications": "string",
        "quantity": "number",
        "unitPrice": "number",
        "taxGTGT": "number",
        "buyerClub": "number",
        "refund": "number",
        "price": "number"
      }
    ],
    "deliveryFee": "number",
    "totalPrice": "number",
    "currency": "string",
    "paymentMethod": "string"
  },
  "Buyer": {
    "orderCode": "number",
    "status": "string",
    "supplierName": "string",
    "contractPerson": "string",
    "address": "string",
    "phone": "number",
    "deliveryInfo": "string",
    "taxCode": "number",
    "deliveryTimeline": [
      {
        "orderDate": "string",
        "date": "string",
        "time": "string"
      },
      {
        "orderConfirmation": "string",
        "date": "string",
        "time": "string"
      },
      {
        "transport": "string",
        "date": "string",
        "time": "string"
      },
      {
        "deleveryDate": "string",
        "date": "string"
      }
    ],
    "deliveryAddress": "string",
    "city": "string",
    "country": "string",
    "productServiceInfo": [
      {
        "productName": "string",
        "quantity": "number",
        "taxGTGT": "number",
        "image": "string",
        "specifications": "string",
        "unitPrice": "number"
        "buyerClub": "number",
        "refund": "number",
        "price": "number"
      }
    ],
    "deliveryFee": "number",
    "totalPrice": "number",
    "currency": "string",
    "paymentMethod": "string"
  }
}


# ======= BUYER ======
Query: query Orders {
    orders {
        edges {
            node {
                id
                orderCode
                orderStatus
                deliveryFee
                orderType
                discount
                guaranteedDeliveryDate
                taxCode
                createdAt
                updatedAt
                supplierName
                currency
                orderDeliveryTimelines {
                    time
                    orderDate
                    date
                }
                orderPaymentDetails {
                    id
                    paymentMethod
                    paymentStatus
                    amountPaid
                }
                orderItems {
                    taxGTGT
                    quantity
                    productName
                    images
                    specification
                    buyerClub
                    refund
                    flashSaleInitialPrice
                    flashSaleDiscountedPrice
                    wholesalePrice 
                }
            }
            cursor
        }
        totalCount
        pageInfo {
            hasNextPage
        }
    }
}

Response: {
    "data": {
        "orders": {
            "edges": [
                {
                    "node": {
                        "id": "1",
                        "orderCode": "W000001",
                        "orderStatus": "INITIATED",
                        "deliveryFee": 12000,
                        "orderType": "KCS",
                        "discount": 0.055,
                        "guaranteedDeliveryDate": "2017-02-11T02:39:14+00:00",
                        "taxCode": "FDJQ2",
                        "createdAt": "2003-02-23T12:01:46+00:00",
                        "updatedAt": "2008-03-29T01:19:48+00:00",
                        "supplierName": "CÔNG TY TNHH THƯƠNG MẠI TUẤN HƯNG PHÁT",
                        "currency": "VND-Vietnamese dong",
                        "orderDeliveryTimelines": [
                            {
                                "time": "15:00:45",
                                "orderDate": "2022-09-09T14:20:00+00:00",
                                "date": "2019-08-12T21:31:11+00:00"
                            },
                            {
                                "time": "17:57:17",
                                "orderDate": "2020-10-06T03:32:25+00:00",
                                "date": "2016-02-04T11:58:10+00:00"
                            },
                            {
                                "time": "11:50:06",
                                "orderDate": "2016-02-20T06:07:54+00:00",
                                "date": "2014-02-11T14:48:12+00:00"
                            }
                        ],
                        "orderPaymentDetails": {
                            "id": "1",
                            "paymentMethod": "Wallet",
                            "paymentStatus": "Confirmed",
                            "amountPaid": 20000
                        },
                        "orderItems": [
                            {
                                "taxGTGT": 5.7465,
                                "quantity": 15,
                                "productName": "Vữa chống thấm",
                                "images": [
                                    "597/product_image_vat-lieu-chong-tham_7bc5a153-fd35-468d-a99a-7bf3e8e75854.png"
                                ],
                                "specification": "",
                                "buyerClub": "Not yet",
                                "refund": null,
                                "flashSaleInitialPrice": null,
                                "flashSaleDiscountedPrice": null,
                                "wholesalePrice": 165000
                            },
                            {
                                "taxGTGT": 0.6655,
                                "quantity": 1,
                                "productName": "Dầu nhớt bánh răng",
                                "images": [
                                    "547/product_image_dau-nhot-banh-rang_3b89a708-dbc1-4b72-b1b5-c715156f6a10.png"
                                ],
                                "specification": "",
                                "buyerClub": "Not yet",
                                "refund": null,
                                "flashSaleInitialPrice": null,
                                "flashSaleDiscountedPrice": null,
                                "wholesalePrice": null
                            },
                            {
                                "taxGTGT": 3.0098000000000003,
                                "quantity": 8,
                                "productName": "Vữa khô trộn sẵn xây gạch nhẹ",
                                "images": [
                                    "597/product_image_vua-kho-tron-san-xay-gach-nhe_4d6d0678-aae7-4796-a013-349e10b74cbd.jpg"
                                ],
                                "specification": "",
                                "buyerClub": "Not yet",
                                "refund": null,
                                "flashSaleInitialPrice": null,
                                "flashSaleDiscountedPrice": null,
                                "wholesalePrice": 830000
                            }
                        ]
                    },
                    "cursor": "0"
                }
            ],
            "totalCount": 1,
            "pageInfo": {
                "hasNextPage": false
            }
        }
    }
}