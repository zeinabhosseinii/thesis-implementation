from dataclasses import dataclass
from typing import Dict, Optional


# ======== Data Structures for ERDG ========
@dataclass
class RebecNode:
    """Node representing a rebec instance (N_R)"""
    name: str
    actor_class: str
    arg: str
    priority: Optional[int] = None

@dataclass
class MessageServerNode:
    """Node representing a message server/method (N_M)"""
    rebec_name: str
    method_name: str
    priority: Optional[int] = None

    def __str__(self):
        return f"{self.rebec_name}.{self.method_name}"

@dataclass
class ActivationNode:
    """Node representing a send activation (N_A)"""
    sender_rebec: str
    sender_method: str
    target_rebec: str
    message_name: str
    delay_time: Optional[int] = None

    def __str__(self):
        delay_str = f"@{self.delay_time}" if self.delay_time else ""
        return f"{self.sender_rebec}.{self.sender_method} -> {self.target_rebec}.{self.message_name}{delay_str}"

@dataclass
class TestCase:
    """Represents a generated test case"""
    id: int
    actor_priorities: Dict[str, int]
    method_priorities: Dict[str, Dict[str, int]]

    def __str__(self):
        return f"TestCase_{self.id}"
