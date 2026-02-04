  # Cancel and Return Process Documentation

### Author: Nebil Müren - cas3322

## Order Cancellation Flow

1. **User Creates Order**
   - Customer adds products to cart → Checkout → Order created
   - Order status: `unfulfilled`

2. **User Makes Payment** (optional)
   - Customer clicks "Pay" on order details → Use test payment: `/orders/pay/<token>/testpay`
   - Order status: `fulfilled`, Payment status: `confirmed`

3. **User Cancels Order**
   - Customer navigates to `/orders/<token>` → Clicks "Cancel Order" (or "Cancel Order & Refund" if paid)
   - Available for orders in `unfulfilled` or `fulfilled` status (before shipping)
   - If paid: Payment status set to `refunded`
   - Order status: `canceled`

## Return and Refund Flow

1. **User Creates Order**
   - Customer adds products to cart → Checkout → Order created
   - Order status: `unfulfilled`

2. **User Makes Payment**
   - Customer clicks "Pay" on order details → Use test payment: `/orders/pay/<token>/testpay`
   - Order status: `fulfilled`, Payment status: `confirmed`

3. **Admin Ships Order**
   - Admin navigates to `/dashboard/orders` → Finds order → Clicks "Send Order"
   - Order status: `shipped`

4. **User Marks Received**
   - Customer navigates to `/orders/<token>` → Clicks "Mark as Received"
   - Order status: `completed`

5. **User Requests Return and Refund**
   - Customer clicks "Return Order & Refund" on order details → Enters reason (optional) → Submits
   - Return status: `requested`

6. **Admin Approves Return**
   - Admin navigates to `/dashboard/orders` → Opens order → Clicks "Approve Return"
   - Return status: `approved`, **Shipping label with QR code generated automatically**

7. **User Ships Package**
   - Customer prints shipping label from order details → Attaches to return package → Ships

8. **Courier Scans and Marks In Transit**
   - Admin navigates to `/dashboard/shipping` → Scans QR code or enters tracking number → Selects "Shipped"
   - Ship status: `in_transit`, **Shipping start time recorded**

9. **Courier Marks Delivered**
   - Admin scans QR code again → Selects "Delivered"
   - Ship status: `delivered`, **Parcel arrival time recorded**, **Process duration calculated**

10. **Admin Processes Refund**
    - Admin navigates to `/dashboard/orders` → Opens order → Clicks "Refund Return"
    - Return status: `completed`, Payment status: `refunded`, Order status: `returned`

11. **User Views Process**
    - Customer navigates to `/orders/<token>` → Views:
      - **Progress stepper** showing all 5 steps with timestamps
      - **Process duration timer** displaying elapsed time (updates in real-time during process)
      - Shipping label with QR code and tracking number

## Key Features

- **Order Cancellation**: Available for `unfulfilled` or `fulfilled` orders (before shipping)
- **Shipping Label with QR Code**: Automatically generated when return is approved
- **Parcel Arrival Time**: Documented when courier marks package as delivered
- **Process Duration Timer**: Calculated and displayed in real-time on order details page
- **Visual Progress Display**: Stepper UI shows all 5 return steps with timestamps

## Key Status Values

- **Order Status**: `unfulfilled` → `fulfilled` → `shipped` → `completed` → `returned` / `canceled`
- **Return Status**: `requested` → `approved` → `completed`
- **Ship Status**: `pending` → `in_transit` → `delivered`
- **Payment Status**: `confirmed` → `refunded`

## Main Endpoints

- Customer order details: `/orders/<token>`
- Cancel order: `/orders/cancel/<token>`
- Admin orders: `/dashboard/orders`
- Shipping management: `/dashboard/shipping`
- Test payment: `/orders/pay/<token>/testpay`
