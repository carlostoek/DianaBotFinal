"""
Módulo de Comercio - Sistema de Tienda y Pagos

Este módulo maneja:
- Catálogo de productos
- Procesamiento de pagos
- Desbloqueos post-compra
- Sistema de arquetipos
- Ofertas personalizadas
"""

from .shop import ShopManager
from .checkout import CheckoutProcessor
from .payments import PaymentProcessor
from .unlocks import PurchaseUnlockEngine
from .archetypes import ArchetypeEngine
from .upselling import UpsellEngine

__all__ = [
    'ShopManager',
    'CheckoutProcessor', 
    'PaymentProcessor',
    'PurchaseUnlockEngine',
    'ArchetypeEngine',
    'UpsellEngine'
]