# -*- coding: utf-8 -*-
"""Product views."""
import bleach
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from pluggy import HookimplMarker

from flaskshop.checkout.models import Cart

PRODUCT_SHOW_ENDPOINT = "product.show"

from .forms import AddCartForm, ProductFeedbackForm
from .models import (
    Category,
    Product,
    ProductCollection,
    ProductFeedback,
    ProductVariant,
)

impl = HookimplMarker("flaskshop")


# Add customer feedback feature
# @author: Nebil Müren - cas3322
def show(id, form=None, feedback_form=None):
    product = Product.get_or_404(id)
    if not form:
        form = AddCartForm(request.form, product=product)
    if not feedback_form:
        feedback_form = ProductFeedbackForm()
    if current_user.is_authenticated and not feedback_form.nickname.data:
        feedback_form.nickname.data = current_user.nick_name or current_user.username

    existing_feedback = None
    already_submitted = False
    if current_user.is_authenticated:
        existing_feedback = ProductFeedback.query.filter_by(
            product_id=product.id, user_id=current_user.id
        ).first()
        already_submitted = existing_feedback is not None
        if existing_feedback:
            feedback_form.nickname.data = existing_feedback.nickname
            feedback_form.packaging_rating.data = existing_feedback.packaging_rating
            feedback_form.delivery_rating.data = existing_feedback.delivery_rating
            feedback_form.item_rating.data = existing_feedback.item_rating
            feedback_form.comment.data = existing_feedback.comment
        elif not feedback_form.nickname.data:
            feedback_form.nickname.data = (
                current_user.nick_name or current_user.username
            )

    recent_feedbacks = (
        ProductFeedback.query.filter_by(product_id=product.id)
        .order_by(ProductFeedback.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "products/details.html",
        product=product,
        form=form,
        feedback_form=feedback_form,
        feedbacks=recent_feedbacks,
        already_submitted=already_submitted,
    )


@login_required
def product_add_to_cart(id):
    """this method return to the show method and use a form instance for display validater errors"""
    product = Product.get_by_id(id)
    form = AddCartForm(request.form, product=product)

    if form.validate_on_submit():
        Cart.add_to_currentuser_cart(form.quantity.data, form.variant.data)
    return redirect(url_for(PRODUCT_SHOW_ENDPOINT, id=id))


# Add customer feedback feature
# @author: Nebil Müren - cas3322
@login_required
def product_feedback(id):
    product = Product.get_or_404(id)
    form = ProductFeedbackForm(request.form)

    if not form.validate_on_submit():
        return show(id, feedback_form=form)

    nickname = (
        bleach.clean(form.nickname.data or "", tags=[], strip=True).strip()
        or "Anonymous"
    )
    comments = bleach.clean(form.comment.data or "", tags=[], strip=True).strip()
    comment_value = comments or None
    existing_feedback = ProductFeedback.query.filter_by(
        product_id=product.id, user_id=current_user.id
    ).first()
    if existing_feedback:
        flash("You have already submitted feedback for this product.", "warning")
        return redirect(url_for(PRODUCT_SHOW_ENDPOINT, id=id))
    ProductFeedback.create(
        product_id=product.id,
        user_id=current_user.id,
        nickname=nickname,
        packaging_rating=form.packaging_rating.data,
        delivery_rating=form.delivery_rating.data,
        item_rating=form.item_rating.data,
        comment=comment_value,
    )
    return redirect(url_for(PRODUCT_SHOW_ENDPOINT, id=id))


def variant_price(id):
    variant = ProductVariant.get_by_id(id)
    return jsonify({"price": float(variant.price), "stock": variant.stock})


def show_category(id):
    page = request.args.get("page", 1, type=int)
    ctx = Category.get_product_by_category(id, page)
    return render_template("category/index.html", **ctx)


def show_collection(id):
    page = request.args.get("page", 1, type=int)
    ctx = ProductCollection.get_product_by_collection(id, page)
    return render_template("category/index.html", **ctx)


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("product", __name__)
    bp.add_url_rule("/<int:id>", view_func=show)
    bp.add_url_rule("/api/variant_price/<int:id>", view_func=variant_price)
    bp.add_url_rule("/<int:id>/add", view_func=product_add_to_cart, methods=["POST"])
    bp.add_url_rule("/<int:id>/feedback", view_func=product_feedback, methods=["POST"])
    bp.add_url_rule("/category/<int:id>", view_func=show_category)
    bp.add_url_rule("/collection/<int:id>", view_func=show_collection)

    app.register_blueprint(bp, url_prefix="/products")
