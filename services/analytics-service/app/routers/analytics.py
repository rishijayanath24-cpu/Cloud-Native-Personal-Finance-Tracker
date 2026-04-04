from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional
import httpx
import json
import redis.asyncio as aioredis
from datetime import datetime, date
from collections import defaultdict

from app.config import settings
from app.schemas import (
    SummaryResponse, CategoryBreakdownResponse, CategoryBreakdown,
    BudgetStatusResponse, BudgetStatusItem, MonthlyTrendResponse, MonthlyTrendItem,
)

router = APIRouter()


# ─── Redis cache helpers ──────────────────────────────────────────────────────

async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def cache_get(key: str):
    try:
        r = await get_redis()
        data = await r.get(key)
        await r.aclose()
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(key: str, value: dict):
    try:
        r = await get_redis()
        await r.setex(key, settings.CACHE_TTL_SECONDS, json.dumps(value))
        await r.aclose()
    except Exception:
        pass


# ─── Service fetch helpers ────────────────────────────────────────────────────

async def fetch_transactions(user_id: int, authorization: str) -> list:
    headers = {"Authorization": authorization} if authorization else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.TRANSACTION_SERVICE_URL}/api/transactions",
            params={"user_id": user_id},
            headers=headers,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch transactions")
        return resp.json()


async def fetch_budgets(user_id: int, authorization: str) -> list:
    headers = {"Authorization": authorization} if authorization else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.BUDGET_SERVICE_URL}/api/budgets",
            params={"user_id": user_id},
            headers=headers,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch budgets")
        return resp.json()


# ─── Filter helpers ───────────────────────────────────────────────────────────

def parse_txn_date(txn: dict) -> Optional[date]:
    raw = txn.get("date") or txn.get("created_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def filter_by_month(transactions: list, month: Optional[str]) -> list:
    if not month:
        return transactions
    try:
        year, mon = map(int, month.split("-"))
    except ValueError:
        raise HTTPException(status_code=400, detail="month must be YYYY-MM")
    result = []
    for t in transactions:
        d = parse_txn_date(t)
        if d and d.year == year and d.month == mon:
            result.append(t)
    return result


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    user_id: int = Query(..., description="User ID"),
    month: Optional[str] = Query(None, description="Filter by month YYYY-MM"),
    authorization: Optional[str] = Header(None),
):
    cache_key = f"analytics:summary:{user_id}:{month or 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    transactions = await fetch_transactions(user_id, authorization or "")
    transactions = filter_by_month(transactions, month)

    income   = sum(t["amount"] for t in transactions if t.get("transaction_type") == "income")
    expenses = sum(t["amount"] for t in transactions if t.get("transaction_type") == "expense")

    result = SummaryResponse(
        user_id=user_id,
        period=month or "all-time",
        total_income=round(income, 2),
        total_expenses=round(expenses, 2),
        net_balance=round(income - expenses, 2),
        transaction_count=len(transactions),
    ).model_dump()

    await cache_set(cache_key, result)
    return result


@router.get("/by-category", response_model=CategoryBreakdownResponse)
async def get_by_category(
    user_id: int = Query(..., description="User ID"),
    month: Optional[str] = Query(None, description="Filter by month YYYY-MM"),
    authorization: Optional[str] = Header(None),
):
    cache_key = f"analytics:by-category:{user_id}:{month or 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    transactions = await fetch_transactions(user_id, authorization or "")
    expenses = [t for t in filter_by_month(transactions, month) if t.get("transaction_type") == "expense"]

    totals: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    grand_total = sum(t["amount"] for t in expenses)

    for t in expenses:
        cat = t.get("category", "Other")
        totals[cat]["total"] += t["amount"]
        totals[cat]["count"] += 1

    breakdown = [
        CategoryBreakdown(
            category=cat,
            total=round(vals["total"], 2),
            count=vals["count"],
            percentage=round((vals["total"] / grand_total * 100) if grand_total else 0, 1),
        )
        for cat, vals in sorted(totals.items(), key=lambda x: -x[1]["total"])
    ]

    result = CategoryBreakdownResponse(
        user_id=user_id,
        period=month or "all-time",
        breakdown=breakdown,
    ).model_dump()

    await cache_set(cache_key, result)
    return result


@router.get("/budget-status", response_model=BudgetStatusResponse)
async def get_budget_status(
    user_id: int = Query(..., description="User ID"),
    month: Optional[str] = Query(None, description="Month YYYY-MM (defaults to current month)"),
    authorization: Optional[str] = Header(None),
):
    current_month = month or date.today().strftime("%Y-%m")
    cache_key = f"analytics:budget-status:{user_id}:{current_month}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    transactions, budgets = await asyncio_gather(
        fetch_transactions(user_id, authorization or ""),
        fetch_budgets(user_id, authorization or ""),
    )

    month_expenses = [
        t for t in filter_by_month(transactions, current_month)
        if t.get("transaction_type") == "expense"
    ]

    spent_by_cat: dict[str, float] = defaultdict(float)
    for t in month_expenses:
        spent_by_cat[t.get("category", "Other")] += t["amount"]

    items = []
    for b in budgets:
        cat   = b.get("category", "Other")
        limit = float(b.get("monthly_limit") or b.get("limit") or 0)
        spent = round(spent_by_cat.get(cat, 0.0), 2)
        util  = round((spent / limit * 100) if limit else 0, 1)
        items.append(BudgetStatusItem(
            category=cat,
            limit=limit,
            spent=spent,
            remaining=round(limit - spent, 2),
            utilization_pct=util,
            exceeded=spent > limit,
        ))

    result = BudgetStatusResponse(
        user_id=user_id,
        period=current_month,
        items=items,
    ).model_dump()

    await cache_set(cache_key, result)
    return result


@router.get("/monthly-trend", response_model=MonthlyTrendResponse)
async def get_monthly_trend(
    user_id: int = Query(..., description="User ID"),
    months: int = Query(6, ge=1, le=24, description="Number of past months to include"),
    authorization: Optional[str] = Header(None),
):
    cache_key = f"analytics:monthly-trend:{user_id}:{months}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    transactions = await fetch_transactions(user_id, authorization or "")

    monthly: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
    for t in transactions:
        d = parse_txn_date(t)
        if not d:
            continue
        key = d.strftime("%Y-%m")
        if t.get("transaction_type") == "income":
            monthly[key]["income"] += t["amount"]
        elif t.get("transaction_type") == "expense":
            monthly[key]["expenses"] += t["amount"]

    trend = [
        MonthlyTrendItem(
            month=k,
            income=round(v["income"], 2),
            expenses=round(v["expenses"], 2),
            net=round(v["income"] - v["expenses"], 2),
        )
        for k, v in sorted(monthly.items())[-months:]
    ]

    result = MonthlyTrendResponse(user_id=user_id, trend=trend).model_dump()
    await cache_set(cache_key, result)
    return result


# asyncio.gather alias (avoids import at top level)
from asyncio import gather as asyncio_gather
