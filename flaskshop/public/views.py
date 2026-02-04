# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, current_app, render_template, request, send_from_directory
from pluggy import HookimplMarker

from flaskshop.account.models import User
from flaskshop.extensions import login_manager, db
from flaskshop.product.models import Product, ProductAttribute, AttributeChoiceValue

from .models import Page
from .search import Item

impl = HookimplMarker("flaskshop")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


def home():
    products = Product.get_featured_product()
    return render_template("public/home.html", products=products)


def style():
    return render_template("public/style_guide.html")


def favicon():
    return send_from_directory("static", "favicon-32x32.png")

# author: Wassim Alkhalil
def search():
    print("invoke search()")
    query = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    per_page = 16
    
    if current_app.config["USE_ES"]:
        pagination = Item.new_search(query, page)
        attribute_filters = {}
    else:
        # Replaced raw SQL with sqlalchemy to prevent SQLi
        # @author: Nebil Müren - cas3322

        # Get paginated results with product images
        products_query = Product.query.filter(Product.title.like(f"%{query}%")).order_by(Product.id)
        
        # Keep a copy of the original query for collecting all available attribute values
        original_query = products_query
        
        # Get price range filter values (None if not provided or invalid)
        price_from = request.args.get("price_from", None, type=int)
        price_to = request.args.get("price_to", None, type=int)
        
        # Auto-swap if from > to (handle 0 values correctly)
        if price_from is not None and price_to is not None and price_from > price_to:
            price_from, price_to = price_to, price_from
        
        # product.price is a computed property (includes discounts) and
        # cannot be filtered in SQL. We filter by actual displayed price.
        
        # Attribute-based filtering (Brand, Color, Collar)
        # Collect all selected filters first
        filter_attributes = ["Brand", "Color", "Collar"]
        selected_filters = {}
        
        for attr_name in filter_attributes:
            attr_values = request.args.getlist(attr_name.lower())
            if attr_values:
                selected_filters[attr_name] = attr_values
        
        # Apply all attribute filters together using AND logic
        if selected_filters:
            filtered_products = None
            
            for attr_name, attr_values in selected_filters.items():
                # Filter products that have the specified attribute value
                matching_products = set()
                for product in products_query.all():
                    if product.attributes:
                        for attr_id, value_id in product.attributes.items():
                            attr_obj = ProductAttribute.get_by_id(int(attr_id))
                            if attr_obj and attr_obj.title == attr_name:
                                value_obj = AttributeChoiceValue.get_by_id(int(value_id))
                                if value_obj and value_obj.title in attr_values:
                                    matching_products.add(product.id)
                
                # Intersect with previous filters
                if filtered_products is None:
                    filtered_products = matching_products
                else:
                    filtered_products = filtered_products.intersection(matching_products)
            
            if filtered_products:
                products_query = products_query.filter(Product.id.in_(filtered_products))
            else:
                # No products match all filters
                products_query = products_query.filter(Product.id.in_([]))
        
        # Collect available values for each attribute for display
        # Use original_query (before attribute filters) so all options are always shown
        attribute_filters = {}
        for attr_name in filter_attributes:
            available_values = set()
            for product in original_query.all():
                if product.attributes:
                    for attr_id, value_id in product.attributes.items():
                        attr_obj = ProductAttribute.get_by_id(int(attr_id))
                        if attr_obj and attr_obj.title == attr_name:
                            value_obj = AttributeChoiceValue.get_by_id(int(value_id))
                            if value_obj:
                                available_values.add(value_obj.title)
            
            attr_values = request.args.getlist(attr_name.lower())
            attribute_filters[attr_name.lower()] = {
                "selected": attr_values,
                "available": sorted(list(available_values))
            }
        
        pagination = products_query.paginate(page=page, per_page=per_page)
        
        # Convert to template format and apply price filter on actual price (includes discounts)
        pagei = []
        for product in pagination.items:
            # Filter by actual displayed price (computed property that includes discounts)
            actual_price = float(product.price)
            if price_from is not None and actual_price < price_from:
                continue
            if price_to is not None and actual_price > price_to:
                continue
            
            item = {
                'id': product.id,
                'title': product.title,
                'basic_price': product.basic_price,
                'first_img': product.first_img,
                'price': product.price,
                'is_discounted': product.is_discounted
            }
            pagei.append(item)
        
        pagination.items = pagei
    
    return render_template(
        "public/search_result.html",
        products=pagination.items,
        query=query,
        pagination=pagination,
        attribute_filters=attribute_filters if not current_app.config["USE_ES"] else {},
        price_from=request.args.get("price_from", ""),
        price_to=request.args.get("price_to", ""),
    )

def show_page(identity):
    page = Page.get_by_identity(identity)
    return render_template("public/page.html", page=page)


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("public", __name__)
    bp.add_url_rule("/", view_func=home)
    bp.add_url_rule("/style", view_func=style)
    bp.add_url_rule("/favicon.ico", view_func=favicon)
    bp.add_url_rule("/search", view_func=search)
    bp.add_url_rule("/page/<identity>", view_func=show_page)
    app.register_blueprint(bp)
