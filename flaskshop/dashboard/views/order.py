# Added return related model and utils
# @author: Nebil Müren - cas3322

from datetime import datetime

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext
from flask_wtf.csrf import CSRFError, validate_csrf

from flaskshop.constant import OrderStatusKinds, PaymentStatusKinds, ReturnStatusKinds
from flaskshop.database import db
from flaskshop.order.models import Order, OrderPayment, OrderReturn, ShippingLabel


def get_order_detail_context(order):
    shipping_label = order.shipping_label
    order_returns = OrderReturn.query.filter_by(order_id=order.id).all()
    return {
        "order": order,
        "shipping_label": shipping_label,
        "order_returns": order_returns,
    }


def orders():
    page = request.args.get("page", type=int, default=1)
    query = Order.query.order_by(Order.id.desc())

    status = request.args.get("status", type=int)
    if status:
        query = query.filter_by(status=status)
    order_no = request.args.get("order_number", type=str)
    if order_no:
        query = query.filter(Order.token.like(f"%{order_no}%"))
    created_at = request.args.get("created_at", type=str)
    if created_at:
        query = query.filter(Order.created_at >= created_at)
    ended_at = request.args.get("ended_at", type=str)
    if ended_at:
        query = query.filter(Order.created_at <= ended_at)
    pagination = query.paginate(page=page, per_page=10)
    props = {
        "id": lazy_gettext("ID"),
        "identity": lazy_gettext("Identity"),
        "status_human": lazy_gettext("Status"),
        "refund_status_human": lazy_gettext("Refund Status"),
        "total_human": lazy_gettext("Total"),
        "user": lazy_gettext("User"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "order_stats_kinds": OrderStatusKinds,
    }
    return render_template("order/list.html", **context)


def order_detail(id):
    order = Order.get_by_id(id)
    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)


def send_order(id):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: send_order path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order = Order.get_by_id(id)
    # Don't update if order is already completed
    if order.status == OrderStatusKinds.completed.value:
        flash(
            lazy_gettext("Order is already completed and cannot be sent again."),
            "warning",
        )
    else:
        order.delivered()
        flash(lazy_gettext("Order is sent."), "success")

    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)


def draft_order(id):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: draft_order path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order = Order.get_by_id(id)
    order.draft()
    flash(lazy_gettext("Order is draft."), "success")
    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)


# Admin approves the return request and generates a shipping label
def approve_return(id):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: approve_return path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order_return = OrderReturn.get_by_id(id)
    if not order_return:
        flash(lazy_gettext("Return request not found."), "error")
        return redirect(url_for("dashboard.orders"))

    order = Order.get_by_id(order_return.order_id)
    if not order:
        flash(lazy_gettext("Order not found."), "error")
        return redirect(url_for("dashboard.orders"))

    # Only allow approving a freshly requested return
    if order_return.status != ReturnStatusKinds.requested.value:
        flash(
            lazy_gettext("This return request has already been processed."), "warning"
        )
    else:
        try:
            order_return.status = ReturnStatusKinds.approved.value
            order_return.approved_at = datetime.now()
            db.session.add(order_return)
            # Generate shipping label when return is approved
            ShippingLabel.generate_for_order(order)
            db.session.commit()
            flash(lazy_gettext("Return approved."), "success")
        except Exception as e:
            db.session.rollback()
            flash(lazy_gettext("Error approving return. Please try again."), "error")
            current_app.logger.error(f"Error approving return {id}: {e}")

    # Re-render detail with updated data
    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)


# Admin completes the refund for a return (can be requested or approved)
def refund_return(id):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: refund_return path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order_return = OrderReturn.get_by_id(id)
    if not order_return:
        flash(lazy_gettext("Return request not found."), "error")
        return redirect(url_for("dashboard.orders"))

    order = Order.get_by_id(order_return.order_id)
    if not order:
        flash(lazy_gettext("Order not found."), "error")
        return redirect(url_for("dashboard.orders"))

    # Allow refunding when the return is still requested (e.g. lost shipment)
    # or already approved. Other states will be rejected.
    if order_return.status in (
        ReturnStatusKinds.requested.value,
        ReturnStatusKinds.approved.value,
    ):
        try:
            payment = OrderPayment.query.filter_by(order_id=order.id).first()
            if payment:
                payment.status = PaymentStatusKinds.refunded.value
                db.session.add(payment)
                if payment.paypal_capture_id:
                    try:
                        order.refundPayPal(payment)
                        print("Refund successful")
                    except Exception as e:
                        print(f"Refund failed: {str(e)}")

            if not order_return.approved_at:
                order_return.approved_at = datetime.now()
            order_return.status = ReturnStatusKinds.completed.value
            order_return.refund_processed_at = datetime.now()
            db.session.add(order_return)
            # Mark the order itself as returned
            order.status = OrderStatusKinds.returned.value
            db.session.add(order)

            db.session.commit()
            flash(
                lazy_gettext("Return refunded and order marked as returned."), "success"
            )
        except Exception as e:
            db.session.rollback()
            flash(lazy_gettext("Error processing refund. Please try again."), "error")
            current_app.logger.error(f"Error processing refund for return {id}: {e}")
    else:
        flash(
            lazy_gettext("This return cannot be refunded in its current state."),
            "warning",
        )

    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)


# Admin rejects a return request
def reject_return(id):
    # Added CSRF protection
    # @author: Nebil Müren - cas3322
    if request.method != "POST":
        abort(405, lazy_gettext("Method not allowed. Use POST."))

    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        current_app.logger.warning(
            "CSRF blocked: reject_return path=%s remote=%s",
            request.path,
            request.remote_addr,
        )
        abort(400, lazy_gettext("CSRF token missing or invalid"))

    order_return = OrderReturn.get_by_id(id)
    if not order_return:
        flash(lazy_gettext("Return request not found."), "error")
        return redirect(url_for("dashboard.orders"))

    order = Order.get_by_id(order_return.order_id)
    if not order:
        flash(lazy_gettext("Order not found."), "error")
        return redirect(url_for("dashboard.orders"))

    # Allow rejection if status is requested or approved
    if order_return.status not in (
        ReturnStatusKinds.requested.value,
        ReturnStatusKinds.approved.value,
    ):
        flash(
            lazy_gettext("This return request has already been processed."), "warning"
        )
    else:
        try:
            order_return.status = ReturnStatusKinds.rejected.value
            order_return.approved_at = datetime.now()
            db.session.add(order_return)
            db.session.commit()
            flash(lazy_gettext("Return request rejected."), "success")
        except Exception as e:
            db.session.rollback()
            flash(lazy_gettext("Error rejecting return. Please try again."), "error")
            current_app.logger.error(f"Error rejecting return {id}: {e}")

    context = get_order_detail_context(order)
    return render_template("order/detail.html", **context)
