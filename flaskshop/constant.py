import enum

from flask_babel import lazy_gettext

# Introduced new status and status kinds for cancel and return process
# @author: Nebil Müren - cas3322
ShipStatusKinds = enum.Enum(
    value="ShipStatus", names="pending delivered received in_transit"
)
PaymentStatusKinds = enum.Enum(
    value="PaymentStatus", names="waiting preauth confirmed rejected refunded"
)
# draft: admin drafted the order
# unfulfilled: order created but not paid
# fulfilled: order paid
# canceled: order paid and canceled before shipped
# completed: order shipped and received
# shipped: order shipped
# returned: order has been refunded after a return process
OrderStatusKinds = enum.Enum(
    value="OrderStatus",
    names="draft unfulfilled fulfilled canceled completed shipped returned",
)
OrderEvents = enum.Enum(
    value="OrderEvents",
    names="draft_created payment_captured payment_failed order_canceled order_delivered order_completed",
)

# requested: customer requested a return
# approved: admin approved the return and generated a return shipping label
# rejected: admin rejected the return
# completed: return process completed
ReturnStatusKinds = enum.Enum(
    value="ReturnStatus", names="requested approved rejected completed"
)
DiscountValueTypeKinds = enum.Enum(value="DiscountValueType", names="fixed percent")
VoucherTypeKinds = enum.Enum(
    value="VoucherType", names="product category shipping value"
)

SettingValueType = enum.Enum(
    value="SettingValueType", names="string integer float boolean select selectmultiple"
)


class Permission:
    LOGIN = 0x01
    EDITOR = 0x02
    OPERATOR = 0x04
    ADMINISTER = 0xFF

    PERMISSION_MAP = {
        LOGIN: ("login", lazy_gettext("Login user")),
        EDITOR: ("editor", lazy_gettext("Editor")),
        OPERATOR: ("op", lazy_gettext("Operator")),
        ADMINISTER: ("admin", lazy_gettext("Super administrator")),
    }


SiteDefaultSettings = {
    "project_title": {
        "value": "FlaskShop",
        "value_type": SettingValueType.string,
        "name": "Project title",
        "description": "The title of the project.",
    },
    "project_subtitle": {
        "value": "A lightweight e-commerce software in Flask",
        "value_type": SettingValueType.string,
        "name": "Project subtitle",
        "description": "A short description of the project.",
    },
    "project_copyright": {
        "value": "",
        "value_type": SettingValueType.string,
        "name": "Project Copyright",
        "description": "Copyright notice of the Project like '&copy; 2019 FlaskShop'. ",
    },
}
