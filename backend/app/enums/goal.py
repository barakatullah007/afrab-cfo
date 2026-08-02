from enum import Enum


class GoalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
