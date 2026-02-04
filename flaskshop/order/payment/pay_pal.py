from paypalcheckoutsdk.orders import OrdersCreateRequest
from flaskshop.paypal_client import get_paypal_client
from paypalcheckoutsdk.orders import OrdersGetRequest
from paypalcheckoutsdk.orders import OrdersCreateRequest
from flaskshop.paypal_client import get_paypal_client

#PAYPAL integration (Swarup)
def send_order(token, payment_no, amount):
    order_request = OrdersCreateRequest()
    order_request.prefer("return=representation")
    order_request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "invoice_id": payment_no,  # your internal payment number
            "custom_id": token,        # your order token
            "amount": {
                "currency_code": "USD",
                "value": str(amount)
            }
        }],
        "application_context": {
            "return_url": f"https://localhost/orders/payment_success",
            "cancel_url": f"https://localhost/orders/{token}"
        }
    })

    client = get_paypal_client()
    response = client.execute(order_request)

    redirect_url = None
    for link in response.result.links:
        if link.rel == "approve":
            redirect_url = link.href
            break

    if not redirect_url:
        raise Exception("PayPal approval URL not found")
    paypal_order_id = response.result.id
    return redirect_url,paypal_order_id


def query_order(paypal_order_id):
    """
    Query PayPal for the status of a captured order.
    Returns a dict similar to AliPay's response.
    """
    client = get_paypal_client()
    request = OrdersGetRequest(paypal_order_id)

    response = client.execute(request)

    # Extract relevant info
    order_info = {
        "id": response.result.id,
        "status": response.result.status,
        "amount": response.result.purchase_units[0].amount.value,
        "currency": response.result.purchase_units[0].amount.currency_code,
        "payer": {
            "name": response.result.payer.name.given_name + " " + response.result.payer.name.surname,
            "email": response.result.payer.email_address
        },
        "paid_at": response.result.update_time if response.result.status == "COMPLETED" else None
    }

    return order_info
