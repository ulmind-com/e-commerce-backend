from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/comprehensive")
async def get_comprehensive_reports(
    days: int = Query(30, description="Number of days to look back"),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Single comprehensive endpoint that aggregates ALL report data
    from existing MongoDB collections. No dummy data.
    """
    db = get_database()
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    period_start = now - timedelta(days=days)
    month_ago = now - timedelta(days=30)

    # ──────────────────────────────────────────────────────────
    # 1. ORDER-BASED KPIs
    # ──────────────────────────────────────────────────────────

    # Today's stats
    today_pipeline = [
        {"$match": {"created_at": {"$gte": today_start}}},
        {"$group": {
            "_id": None,
            "revenue": {"$sum": "$total_amount"},
            "orders": {"$sum": 1},
            "online_revenue": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "ONLINE"]}, "$total_amount", 0]}},
            "cod_revenue": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "COD"]}, "$total_amount", 0]}},
            "online_orders": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "ONLINE"]}, 1, 0]}},
            "cod_orders": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "COD"]}, 1, 0]}},
        }}
    ]
    today_res = await db["orders"].aggregate(today_pipeline).to_list(1)
    today = today_res[0] if today_res else {"revenue": 0, "orders": 0, "online_revenue": 0, "cod_revenue": 0, "online_orders": 0, "cod_orders": 0}

    # Yesterday's stats (for growth comparison)
    yday_pipeline = [
        {"$match": {"created_at": {"$gte": yesterday_start, "$lt": today_start}}},
        {"$group": {"_id": None, "revenue": {"$sum": "$total_amount"}, "orders": {"$sum": 1}}}
    ]
    yday_res = await db["orders"].aggregate(yday_pipeline).to_list(1)
    yesterday = yday_res[0] if yday_res else {"revenue": 0, "orders": 0}

    # All-time totals
    total_pipeline = [
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$total_amount"},
            "total_orders": {"$sum": 1},
            "avg_order_value": {"$avg": "$total_amount"},
            "total_online": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "ONLINE"]}, "$total_amount", 0]}},
            "total_cod": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "COD"]}, "$total_amount", 0]}},
            "online_count": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "ONLINE"]}, 1, 0]}},
            "cod_count": {"$sum": {"$cond": [{"$eq": ["$payment_mode", "COD"]}, 1, 0]}},
        }}
    ]
    total_res = await db["orders"].aggregate(total_pipeline).to_list(1)
    totals = total_res[0] if total_res else {"total_revenue": 0, "total_orders": 0, "avg_order_value": 0, "total_online": 0, "total_cod": 0, "online_count": 0, "cod_count": 0}

    # Order status counts
    status_pipeline = [
        {"$group": {"_id": "$order_status", "count": {"$sum": 1}, "amount": {"$sum": "$total_amount"}}}
    ]
    status_res = await db["orders"].aggregate(status_pipeline).to_list(20)
    status_map = {r["_id"]: {"count": r["count"], "amount": r["amount"]} for r in status_res}

    pending = status_map.get("Pending", {"count": 0, "amount": 0})["count"] + status_map.get("Order Placed", {"count": 0, "amount": 0})["count"] + status_map.get("Preparing", {"count": 0, "amount": 0})["count"]
    completed = status_map.get("Delivered", {"count": 0, "amount": 0})["count"]
    cancelled = status_map.get("Cancelled", {"count": 0, "amount": 0})["count"]
    returned = status_map.get("Return Requested", {"count": 0, "amount": 0})["count"] + status_map.get("Return Approved", {"count": 0, "amount": 0})["count"]
    refunded_data = status_map.get("Refunded", {"count": 0, "amount": 0})
    refund_count = refunded_data["count"]
    refund_amount = refunded_data["amount"]

    # ──────────────────────────────────────────────────────────
    # 2. CUSTOMER STATS
    # ──────────────────────────────────────────────────────────
    total_customers = await db["users"].count_documents({"role": "user"})
    new_customers = await db["users"].count_documents({"role": "user", "created_at": {"$gte": month_ago}})

    # Top customers
    top_cust_pipeline = [
        {"$match": {"payment_status": {"$ne": "Failed"}}},
        {"$group": {"_id": "$user_id", "total_spent": {"$sum": "$total_amount"}, "order_count": {"$sum": 1}}},
        {"$sort": {"total_spent": -1}},
        {"$limit": 10}
    ]
    top_cust_agg = await db["orders"].aggregate(top_cust_pipeline).to_list(10)
    user_ids = [c["_id"] for c in top_cust_agg]
    users = await db["users"].find({"_id": {"$in": user_ids}}, {"full_name": 1, "email": 1}).to_list(10)
    user_map = {str(u["_id"]): u for u in users}

    top_customers = []
    for c in top_cust_agg:
        u = user_map.get(c["_id"], {})
        top_customers.append({
            "name": u.get("full_name", "Unknown"),
            "email": u.get("email", ""),
            "total_spent": c["total_spent"],
            "orders": c["order_count"]
        })

    # Repeat customers (more than 1 order)
    repeat_pipeline = [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$count": "repeat"}
    ]
    repeat_res = await db["orders"].aggregate(repeat_pipeline).to_list(1)
    repeat_customers = repeat_res[0]["repeat"] if repeat_res else 0

    # ──────────────────────────────────────────────────────────
    # 3. PRODUCT STATS
    # ──────────────────────────────────────────────────────────

    # Best sellers
    best_pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "title": {"$first": "$items.title"},
            "total_sold": {"$sum": "$items.quantity"},
            "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price_at_purchase"]}}
        }},
        {"$sort": {"total_sold": -1}},
        {"$limit": 10}
    ]
    best_sellers = await db["orders"].aggregate(best_pipeline).to_list(10)

    # Worst sellers (least sold, but at least 1)
    worst_pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "title": {"$first": "$items.title"},
            "total_sold": {"$sum": "$items.quantity"},
            "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price_at_purchase"]}}
        }},
        {"$sort": {"total_sold": 1}},
        {"$limit": 10}
    ]
    worst_sellers = await db["orders"].aggregate(worst_pipeline).to_list(10)

    # Inventory
    low_stock = await db["products"].count_documents({"stock_quantity": {"$gt": 0, "$lte": 10}})
    out_of_stock = await db["products"].count_documents({"stock_quantity": {"$lte": 0}})
    total_products = await db["products"].count_documents({})

    inv_pipeline = [
        {"$group": {"_id": None, "inventory_value": {"$sum": {"$multiply": ["$price", "$stock_quantity"]}}}}
    ]
    inv_res = await db["products"].aggregate(inv_pipeline).to_list(1)
    inventory_value = inv_res[0]["inventory_value"] if inv_res else 0

    # Category revenue
    cat_pipeline = [
        {"$unwind": "$items"},
        {"$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product_info"
        }},
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": "$product_info.category_id",
            "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price_at_purchase"]}},
            "orders": {"$sum": 1}
        }},
        {"$sort": {"revenue": -1}},
        {"$limit": 10}
    ]
    cat_rev = await db["orders"].aggregate(cat_pipeline).to_list(10)

    # Enrich with category names
    cat_ids = [c["_id"] for c in cat_rev if c["_id"]]
    categories = await db["categories"].find({"_id": {"$in": cat_ids}}).to_list(20)
    cat_map = {str(c["_id"]): c.get("name", "Unknown") for c in categories}
    for c in cat_rev:
        c["name"] = cat_map.get(str(c["_id"]), "Uncategorized") if c["_id"] else "Uncategorized"

    # ──────────────────────────────────────────────────────────
    # 4. SALES TREND (last N days)
    # ──────────────────────────────────────────────────────────
    trend_pipeline = [
        {"$match": {"created_at": {"$gte": period_start}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "revenue": {"$sum": "$total_amount"},
            "orders": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    trend_data = await db["orders"].aggregate(trend_pipeline).to_list(days + 5)
    sales_trend = [{"date": r["_id"], "revenue": r["revenue"], "orders": r["orders"]} for r in trend_data]

    # ──────────────────────────────────────────────────────────
    # 5. PAYMENT DISTRIBUTION
    # ──────────────────────────────────────────────────────────
    payment_pipeline = [
        {"$group": {
            "_id": "$payment_mode",
            "revenue": {"$sum": "$total_amount"},
            "count": {"$sum": 1}
        }}
    ]
    payment_dist = await db["orders"].aggregate(payment_pipeline).to_list(10)

    payment_status_pipeline = [
        {"$group": {
            "_id": "$payment_status",
            "count": {"$sum": 1},
            "amount": {"$sum": "$total_amount"}
        }}
    ]
    payment_status_dist = await db["orders"].aggregate(payment_status_pipeline).to_list(10)

    # ──────────────────────────────────────────────────────────
    # 6. COUPON STATS
    # ──────────────────────────────────────────────────────────
    total_coupons = await db["coupons"].count_documents({})
    active_coupons = await db["coupons"].count_documents({"status": "Active"})

    coupon_order_pipeline = [
        {"$match": {"coupon_code": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$coupon_code",
            "usage": {"$sum": 1},
            "revenue": {"$sum": "$total_amount"},
            "discount": {"$sum": {"$ifNull": ["$discount_applied", 0]}}
        }},
        {"$sort": {"usage": -1}},
        {"$limit": 10}
    ]
    coupon_usage = await db["orders"].aggregate(coupon_order_pipeline).to_list(10)

    total_coupon_usage_pipeline = [
        {"$match": {"coupon_code": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": None, "total_usage": {"$sum": 1}, "total_discount": {"$sum": {"$ifNull": ["$discount_applied", 0]}}}}
    ]
    coupon_totals_res = await db["orders"].aggregate(total_coupon_usage_pipeline).to_list(1)
    coupon_totals = coupon_totals_res[0] if coupon_totals_res else {"total_usage": 0, "total_discount": 0}

    # ──────────────────────────────────────────────────────────
    # 7. REVIEW STATS
    # ──────────────────────────────────────────────────────────
    review_pipeline = [
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"},
            "star5": {"$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}},
            "star4": {"$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}},
            "star3": {"$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}},
            "star2": {"$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}},
            "star1": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}},
        }}
    ]
    review_res = await db["reviews"].aggregate(review_pipeline).to_list(1)
    reviews = review_res[0] if review_res else {"total": 0, "avg_rating": 0, "star5": 0, "star4": 0, "star3": 0, "star2": 0, "star1": 0}
    reviews.pop("_id", None)

    # ──────────────────────────────────────────────────────────
    # ASSEMBLE RESPONSE
    # ──────────────────────────────────────────────────────────
    return {
        "kpis": {
            "today_revenue": today.get("revenue", 0),
            "today_orders": today.get("orders", 0),
            "today_online": today.get("online_revenue", 0),
            "today_cod": today.get("cod_revenue", 0),
            "yesterday_revenue": yesterday.get("revenue", 0),
            "yesterday_orders": yesterday.get("orders", 0),
            "total_revenue": totals.get("total_revenue", 0),
            "total_orders": totals.get("total_orders", 0),
            "avg_order_value": round(totals.get("avg_order_value", 0), 2),
            "total_online_revenue": totals.get("total_online", 0),
            "total_cod_revenue": totals.get("total_cod", 0),
            "online_order_count": totals.get("online_count", 0),
            "cod_order_count": totals.get("cod_count", 0),
            "pending_orders": pending,
            "completed_orders": completed,
            "cancelled_orders": cancelled,
            "returned_orders": returned,
            "refund_count": refund_count,
            "refund_amount": refund_amount,
            "total_customers": total_customers,
            "new_customers": new_customers,
            "repeat_customers": repeat_customers,
            "total_products": total_products,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "inventory_value": inventory_value,
            "total_coupons": total_coupons,
            "active_coupons": active_coupons,
            "coupon_usage": coupon_totals.get("total_usage", 0),
            "total_discount_given": coupon_totals.get("total_discount", 0),
        },
        "sales_trend": sales_trend,
        "order_status_distribution": [{"status": r["_id"], "count": r["count"], "amount": r["amount"]} for r in status_res],
        "payment_distribution": [{"method": r["_id"], "revenue": r["revenue"], "count": r["count"]} for r in payment_dist],
        "payment_status": [{"status": r["_id"], "count": r["count"], "amount": r["amount"]} for r in payment_status_dist],
        "top_customers": top_customers,
        "best_sellers": best_sellers,
        "worst_sellers": worst_sellers,
        "category_revenue": [{"name": c["name"], "revenue": c["revenue"], "orders": c["orders"]} for c in cat_rev],
        "coupon_details": coupon_usage,
        "reviews": reviews,
    }
