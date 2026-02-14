from enum import Enum

class TestLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    NORMAL = "NORMAL"