# Created to simulate return shipment flow
# @author: Nebil Müren - cas3322
from datetime import datetime

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext
from flask_wtf.csrf import CSRFError, validate_csrf

from flaskshop.constant import ShipStatusKinds
from flaskshop.database import db
from flaskshop.order.models import Order, ShippingLabel


def shipping_list():
    """List all return shipments for courier processing"""
    page = request.args.get("page", type=int, default=1)

    # Query return shipping labels
    query = ShippingLabel.query.order_by(ShippingLabel.id.desc())

    # Filter by tracking number
    tracking_number = request.args.get("tracking_number", type=str)
    if tracking_number:
        query = query.filter(ShippingLabel.tracking_number.like(f"%{tracking_number}%"))

    # Filter by order status
    order_status = request.args.get("order_status", type=str)
    if order_status:
        query = query.join(Order).filter(Order.status == int(order_status))

    # Filter by shipping status (return shipment status on label)
    ship_status = request.args.get("ship_status", type=int)
    if ship_status:
        query = query.filter(ShippingLabel.ship_status == ship_status)

    pagination = query.paginate(page=page, per_page=10)

    # Get orders and return data for each label
    items = []
    for label in pagination.items:
        order = Order.get_by_id(label.order_id)
        # Get the return request for this order
        order_return = order.refund
        items.append(
            {
                "label": label,
                "order": order,
                "return": order_return,
            }
        )

    context = {
        "items": items,
        "pagination": pagination,
        "ship_status_kinds": ShipStatusKinds,
    }
    return render_template("shipping/list.html", **context)


def scan_tracking():
    """Simulate courier scanning a QR code/tracking number"""
    if request.method == "POST":
        try:
            validate_csrf(request.form.get("csrf_token"))
        except CSRFError:
            current_app.logger.warning(
                "CSRF blocked: scan_tracking path=%s remote=%s",
                request.path,
                request.remote_addr,
            )
            abort(400, lazy_gettext("CSRF token missing or invalid"))

        tracking_number = request.form.get("tracking_number", "").strip()
        action = request.form.get("action", "").strip()

        if not tracking_number:
            flash(lazy_gettext("Tracking number is required."), "error")
            return redirect(url_for("dashboard.shipping_list"))

        if not action:
            flash(lazy_gettext("Action is required."), "error")
            return redirect(url_for("dashboard.shipping_list"))

        # Validate action against allowed values
        allowed_actions = ["shipped", "delivered"]
        if action not in allowed_actions:
            flash(lazy_gettext("Invalid action."), "error")
            return redirect(url_for("dashboard.shipping_list"))

        # Find the shipping label
        label = ShippingLabel.query.filter_by(tracking_number=tracking_number).first()

        if not label:
            flash(lazy_gettext("Tracking number not found."), "error")
            return redirect(url_for("dashboard.shipping_list"))

        # Determine next status based on action
        try:
            if action == "shipped":
                # Mark as shipped (package has left and is on the way)
                label.ship_status = ShipStatusKinds.in_transit.value
                # Clear delivered time and duration if they exist (package is being re-shipped)
                if label.parcel_arrival_time:
                    label.parcel_arrival_time = None
                if label.process_duration_seconds:
                    label.process_duration_seconds = None
                # Record the time when package was shipped
                if not label.shipping_start_time:
                    label.shipping_start_time = datetime.now()
                db.session.add(label)
                flash(lazy_gettext("Package marked as shipped."), "success")
            elif action == "delivered":
                # Mark as delivered
                label.ship_status = ShipStatusKinds.delivered.value
                label.parcel_arrival_time = datetime.now()

                # If no shipping_start_time set, set it now (package was shipped and delivered in same action)
                if not label.shipping_start_time:
                    label.shipping_start_time = datetime.now()

                # Calculate process duration
                if label.shipping_start_time:
                    duration = (
                        label.parcel_arrival_time - label.shipping_start_time
                    ).total_seconds()
                    label.process_duration_seconds = int(duration)

                db.session.add(label)
                flash(lazy_gettext("Package marked as delivered."), "success")

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(
                lazy_gettext("Error updating shipping status. Please try again."),
                "error",
            )
            current_app.logger.error(f"Error updating shipping status: {e}")

        return redirect(url_for("dashboard.shipping_list"))

    # GET request - show scan form
    tracking_number = request.args.get("tracking_number", "")
    return render_template("shipping/scan.html", tracking_number=tracking_number)


def shipping_detail(label_id):
    """Show details of a specific shipping label"""
    label = ShippingLabel.get_by_id(label_id)
    if not label:
        flash(lazy_gettext("Shipping label not found."), "error")
        return redirect(url_for("dashboard.shipping_list"))

    order = Order.get_by_id(label.order_id)
    # Get the return request for this order (using order.refund property)
    order_return = order.refund

    context = {
        "label": label,
        "order": order,
        "return": order_return,
        "ship_status_kinds": ShipStatusKinds,
    }
    return render_template("shipping/detail.html", **context)
