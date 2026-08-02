from app.enums.category import CategoryType

DEFAULT_INCOME_CATEGORIES = [
    {
        "name": "Salary",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-wallet",
        "color": "#22C55E",
    },
    {
        "name": "Freelancing",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-laptop-code",
        "color": "#3B82F6",
    },
    {
        "name": "Business",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-briefcase",
        "color": "#8B5CF6",
    },
    {
        "name": "Investment",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-chart-line",
        "color": "#10B981",
    },
    {
        "name": "Bonus",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-gift",
        "color": "#F59E0B",
    },
    {
        "name": "Interest",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-piggy-bank",
        "color": "#16A34A",
    },
    {
        "name": "Rental Income",
        "type": CategoryType.INCOME,
        "icon": "fa-solid fa-building",
        "color": "#0EA5E9",
    },
]


DEFAULT_EXPENSE_CATEGORIES = [
    {
        "name": "Food",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-utensils",
        "color": "#EF4444",
    },
    {
        "name": "Transport",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-car",
        "color": "#3B82F6",
    },
    {
        "name": "Rent",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-house",
        "color": "#6366F1",
    },
    {
        "name": "Shopping",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-cart-shopping",
        "color": "#EC4899",
    },
    {
        "name": "Health",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-heart-pulse",
        "color": "#DC2626",
    },
    {
        "name": "Bills",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-file-invoice-dollar",
        "color": "#F97316",
    },
    {
        "name": "Entertainment",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-film",
        "color": "#8B5CF6",
    },
    {
        "name": "Education",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-graduation-cap",
        "color": "#14B8A6",
    },
    {
        "name": "Travel",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-plane",
        "color": "#0EA5E9",
    },
    {
        "name": "Groceries",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-basket-shopping",
        "color": "#84CC16",
    },
    {
        "name": "Fuel",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-gas-pump",
        "color": "#F59E0B",
    },
    {
        "name": "Insurance",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-shield-heart",
        "color": "#2563EB",
    },
    {
        "name": "Personal Care",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-soap",
        "color": "#D946EF",
    },
    {
        "name": "Subscriptions",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-repeat",
        "color": "#7C3AED",
    },
    {
        "name": "Charity",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-hand-holding-heart",
        "color": "#059669",
    },
    {
        "name": "Other",
        "type": CategoryType.EXPENSE,
        "icon": "fa-solid fa-box",
        "color": "#6B7280",
    },
]


DEFAULT_CATEGORIES = (
    DEFAULT_INCOME_CATEGORIES
    + DEFAULT_EXPENSE_CATEGORIES
)