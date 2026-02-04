import time
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import lazy_gettext
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError, validate_csrf
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from pluggy import HookimplMarker

from flaskshop.constant import (
    OrderStatusKinds,
    PaymentStatusKinds,
    ReturnStatusKinds,
    ShipStatusKinds,
)
from flaskshop.extensions import csrf_protect
from flaskshop.paypal_client import get_paypal_client

from .models import Order, OrderPayment, OrderReturn, ShippingLabel
from .payment import pay_pal, zhifubao

impl = HookimplMarker("flaskshop")


@login_required
def index():
    return redirect(url_for("account.index"))


@login_required
def show(token):
    order = Order.query.filter_by(token=token).first()
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))
    # If there is an approved/completed return and no return label yet,
    # generate a return shipping label now (for the customer view).
    shipping_label = order.shipping_label
    if (
        order.refund
        and order.refund.status
        in [ReturnStatusKinds.approved.value, ReturnStatusKinds.completed.value]
        and not shipping_label
    ):
        shipping_label = ShippingLabel.generate_for_order(order)
    return render_template(
        "orders/details.html",
        order=order,
        shipping_label=shipping_label,
    )


def create_payment(token, payment_method):
    order = Order.query.filter_by(token=token).first()
    if order.status != OrderStatusKinds.unfulfilled.value:
        abort(403, lazy_gettext("This Order Can Not Pay"))
    payment_no = str(int(time.time())) + str(current_user.id)
    customer_ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    payment = OrderPayment.query.filter_by(order_id=order.id).first()
    if payment:
        payment.update(
            payment_method=payment_method,
            payment_no=payment_no,
            customer_ip_address=customer_ip_address,
        )
    else:
        payment = OrderPayment.create(
            order_id=order.id,
            payment_method=payment_method,
            payment_no=payment_no,
            status=PaymentStatusKinds.waiting.value,
            total=order.total,
            customer_ip_address=customer_ip_address,
        )
    if payment_method == "alipay":
        redirect_url = zhifubao.send_order(order.token, payment_no, order.total)
        payment.redirect_url = redirect_url

    # PAYPAL integration (Swarup)
    if payment_method == "paypal":
        redirect_url, paypal_order_id = pay_pal.send_order(
            order.token, payment_no, order.total
        )

        payment.redirect_url = redirect_url
        payment.paypal_order_id = paypal_order_id  # <-- FIX
        payment.save()

    return payment


@login_required
def ali_pay(token):
    payment = create_payment(token, "alipay")
    return redirect(payment.redirect_url)


# PAYPAL integration (Swarup)
@login_required
def paypal(token):
    payment = create_payment(token, "paypal")
    return redirect(payment.redirect_url)


@csrf_protect.exempt
def ali_notify():
    data = request.form.to_dict()
    success = zhifubao.verify_order(data)
    if success:
        order_payment = OrderPayment.query.filter_by(
            payment_no=data["out_trade_no"]
        ).first()
        order_payment.pay_success(paid_at=data["gmt_payment"])
        return "SUCCESS"
    return "ERROR HAPPEND"


@login_required
def test_pay_flow(token):
    payment = create_payment(token, "testpay")
    payment.pay_success(paid_at=datetime.now())
    return redirect(url_for("order.payment_success"))


@login_required
def payment_success():
    # PAYPAL integration (Swarup)
    payment_no = request.args.get("out_trade_no")
    paypal_order_id = request.args.get("token")
    if paypal_order_id:

        # Get payment for this PayPal order
        order_payment = OrderPayment.query.filter_by(
            paypal_order_id=paypal_order_id
        ).first()
        if not order_payment:
            return "OrderPayment not found", 404

        # Capture payment
        client = get_paypal_client()
        capture_request = OrdersCaptureRequest(paypal_order_id)
        capture_response = client.execute(capture_request)
        # Extract PayPal capture ID safely
        try:
            capture_id = (
                capture_response.result.purchase_units[0].payments.captures[0].id
            )
        except:
            capture_id = None  # Optional — keep record but not required

        paid_at = datetime.now()
        order_payment.pay_success(paid_at=paid_at, paypal_capture_id=capture_id)

    if payment_no:
        res = zhifubao.query_order(payment_no)
        if res["code"] == "10000":
            order_payment = OrderPayment.query.filter_by(
                payment_no=res["out_trade_no"]
            ).first()
            order_payment.pay_success(paid_at=res["send_pay_date"])
        else:
            print(res["msg"])

    return render_template("orders/checkout_success.html")


@login_required
def cancel_order(token):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: cancel_order path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order = Order.query.filter_by(token=token).first_or_404()
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))

    # Allow cancel for unpaid or paid-but-not-shipped orders only
    if order.status not in (
        OrderStatusKinds.unfulfilled.value,
        OrderStatusKinds.fulfilled.value,
    ):
        abort(403, lazy_gettext("This order can no longer be canceled."))
    # If already paid, simulate a refund when canceling
    if order.status == OrderStatusKinds.fulfilled.value:
        payment = OrderPayment.query.filter_by(order_id=order.id).first()
        if payment:
            payment.status = PaymentStatusKinds.refunded.value

            if payment.paypal_capture_id:
                try:
                    order.refundPayPal(payment)
                    print("Refund successful")
                except Exception as e:
                    print(f"Refund failed: {str(e)}")

    order.cancel()

    return redirect(order.get_absolute_url())


@login_required
def receive(token):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    # Validate CSRF token
    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: receive path=%s remote=%s", request.path, request.remote_addr
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order = Order.query.filter_by(token=token).first_or_404()
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))

    order.update(
        status=OrderStatusKinds.completed.value,
        ship_status=ShipStatusKinds.received.value,
    )
    return redirect(order.get_absolute_url())


# Added request return action
# @author: Nebil Müren - cas3322
@login_required
def request_return(token):
    """Customer initiates a return & refund for their own order."""
    order = Order.query.filter_by(token=token).first_or_404()
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))

    # Only allow returns for shipped/completed orders
    if order.status not in (
        OrderStatusKinds.shipped.value,
        OrderStatusKinds.completed.value,
    ):
        abort(403, lazy_gettext("This order cannot be returned."))

    # Check for existing return request to prevent duplicates
    existing = OrderReturn.query.filter_by(
        order_id=order.id, status=ReturnStatusKinds.requested.value
    ).first()
    if existing:
        # silently ignore duplicate requests
        return redirect(order.get_absolute_url())

    reason_raw = request.form.get("reason", "").strip()
    reason = reason_raw[:1000] if reason_raw else "No reason provided"
    refund_amount = order.total

    OrderReturn.create(
        order_id=order.id,
        user_id=current_user.id,
        status=ReturnStatusKinds.requested.value,
        reason=reason,
        refund_amount=refund_amount,
    )

    return redirect(order.get_absolute_url())


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("order", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/<string:token>", view_func=show)
    bp.add_url_rule("/pay/<string:token>/alipay", view_func=ali_pay)
    bp.add_url_rule("/pay/<string:token>/paypal", view_func=paypal)
    bp.add_url_rule("/alipay/notify", view_func=ali_notify, methods=["POST", "HEAD"])
    bp.add_url_rule("/pay/<string:token>/testpay", view_func=test_pay_flow)
    bp.add_url_rule("/payment_success", view_func=payment_success)
    bp.add_url_rule("/cancel/<string:token>", view_func=cancel_order, methods=["POST"])
    bp.add_url_rule("/receive/<string:token>", view_func=receive, methods=["POST"])
    bp.add_url_rule(
        "/return/<string:token>", view_func=request_return, methods=["POST"]
    )
    app.register_blueprint(bp, url_prefix="/orders")
