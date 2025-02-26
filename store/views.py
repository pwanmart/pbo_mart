from django.shortcuts import render
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

PAYSTACK_SECRET_KEY = "your-paystack-secret-key"


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"])
    def initiate_payment(self, request, pk=None):
        """Initiate Paystack payment for an order"""
        order = self.get_object()

        payment_data = {
            "email": request.user.email,
            "amount": int(order.total_amount * 100),  # Convert to kobo
            "reference": f"ORDER_{order.id}",
            "callback_url": "https://yourdomain.com/payment/callback/",
        }

        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payment_data,
            headers=headers,
        )

        if response.status_code == 200:
            order.paystack_payment_reference = payment_data["reference"]
            order.save()
            return Response(response.json(), status=status.HTTP_200_OK)

        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="paystack-webhook")
    def paystack_webhook(self, request):
        """Handle Paystack webhook for payment status updates"""
        payload = request.data
        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference")
            order = Order.objects.filter(paystack_payment_reference=reference).first()

            if order:
                order.status = Order.STATUS_COMPLETED
                order.save()
                return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid event"}, status=status.HTTP_400_BAD_REQUEST)

