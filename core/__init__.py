"""
Core module for DianaBot
"""

from .coordinator import coordinador_central
from .transaction_manager import transaction_manager
from .event_bus import event_bus

__all__ = [
    'coordinador_central',
    'transaction_manager', 
    'event_bus'
]