"""
Microtransactions system for 3D Ludo.
This module handles in-game purchases, virtual currency, and shop features.
"""

import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

class CurrencyType(Enum):
    COINS = "coins"
    GEMS = "gems"
    DIAMONDS = "diamonds"
    RENOWN = "renown"
    XP = "xp"
class PurchaseType(Enum):
    SINGLE_USE = "single_use"
    CONSUMABLE = "consumable"
    USAGE_BASED = "usage_based"
    SUBSCRIPTION = "subscription"
    BUNDLE = "bundle"
class ProductCategory(Enum):
    COSMETIC = "cosmetic"
    CHARACTER = "character"
    BOARD = "board"
    Dice = "dice"
    BOOST = "boost"
    PREMIUM = "premium"
    EVENT = "event"
class PaymentProvider(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CRYPTO = "crypto"
@dataclass
class Product:
    """Product in the shop."""

    product_id: str
    name: str
    description: str
    price: Dict[str, float]
    category: ProductCategory
    purchase_type: PurchaseType
    is_purchasable: bool = True
    is_new: bool = False
    is_limited: bool = False
    stock_count: int = 0
    max_purchase_count: int = 1
    unlock_level: int = 0
    images: List[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    effects: Dict[str, Any] = None
    custom_data: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category.value,
            'purchase_type': self.purchase_type.value,
            'is_purchasable': self.is_purchasable,
            'is_new': self.is_new,
            'is_limited': self.is_limited,
            'stock_count': self.stock_count,
            'max_purchase_count': self.max_purchase_count,
            'unlock_level': self.unlock_level,
            'images': self.images or [],
            'video_url': self.video_url,
            'audio_url': self.audio_url,
            'effects': self.effects or {},
            'custom_data': self.custom_data or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        return cls(
            product_id=data['product_id'],
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=ProductCategory(data['category']),
            purchase_type=PurchaseType(data['purchase_type']),
            is_purchasable=data.get('is_purchasable', True),
            is_new=data.get('is_new', False),
            is_limited=data.get('is_limited', False),
            stock_count=data.get('stock_count', 0),
            max_purchase_count=data.get('max_purchase_count', 1),
            unlock_level=data.get('unlock_level', 0),
            images=data.get('images'),
            video_url=data.get('video_url'),
            audio_url=data.get('audio_url'),
            effects=data.get('effects'),
            custom_data=data.get('custom_data')
        )
@dataclass
class Purchase:
    """Purchase record."""

    purchase_id: str
    user_id: str
    product_id: str
    currency_type: CurrencyType
    amount: float
    price_paid: Dict[str, float]
    timestamp: str
    transaction_id: Optional[str] = None
    status: str = "completed"
    receipt_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'purchase_id': self.purchase_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'currency_type': self.currency_type.value,
            'amount': self.amount,
            'price_paid': self.price_paid,
            'timestamp': self.timestamp,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'receipt_data': self.receipt_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Purchase':
        return cls(
            purchase_id=data['purchase_id'],
            user_id=data['user_id'],
            product_id=data['product_id'],
            currency_type=CurrencyType(data['currency_type']),
            amount=data['amount'],
            price_paid=data['price_paid'],
            timestamp=data['timestamp'],
            transaction_id=data.get('transaction_id'),
            status=data.get('status', 'completed'),
            receipt_data=data.get('receipt_data')
        )
@dataclass
class CurrencyBalance:
    """User currency balance."""

    user_id: str
    coins: float = 0.0
    gems: float = 0.0
    diamonds: float = 0.0
    renown: float = 0.0
    xp: float = 0.0
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'coins': self.coins,
            'gems': self.gems,
            'diamonds': self.diamonds,
            'renown': self.renown,
            'xp': self.xp,
            'last_updated': self.last_updated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurrencyBalance':
        return cls(
            user_id=data['user_id'],
            coins=data.get('coins', 0.0),
            gems=data.get('gems', 0.0),
            diamonds=data.get('diamonds', 0.0),
            renown=data.get('renown', 0.0),
            xp=data.get('xp', 0.0),
            last_updated=data.get('last_updated', datetime.now().isoformat())
        )
class Microtransactions:
    """
    Microtransactions system for 3D Ludo.
    Handles in-game purchases, virtual currency, and shop features.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the microtransactions system with configuration.

        Args:
            config: Microtransactions configuration dictionary
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.payment_provider = PaymentProvider(config.get('payment_provider', 'stripe'))
        self.currencies_enabled = config.get('currencies_enabled', ['coins', 'gems', 'diamonds', 'renown'])
        self.taxes_enabled = config.get('taxes_enabled', True)
        self.tax_rate = config.get('tax_rate', 0.1)

        # Product data
        self.products: Dict[str, Product] = {}
        self.categories: Dict[ProductCategory, List[str]] = {}

        # User data
        self.user_balances: Dict[str, CurrencyBalance] = {}
        self.purchase_history: Dict[str, List[Purchase]] = {}

        # Load data
        self._load_product_data()
        self._load_currency_data()

    def _load_product_data(self) -> None:
        """Load product data from configuration."""
        products_config = self.config.get('products', {})

        for category, product_configs in products_config.items():
            try:
                product_category = ProductCategory(category)
                self.categories[product_category] = []

                for product_config in product_configs:
                    product = Product.from_dict(product_config)
                    self.products[product.product_id] = product
                    self.categories[product_category].append(product.product_id)

            except ValueError:
                pass

    def _load_currency_data(self) -> None:
        """Load initial currency data."""
        currencies_config = self.config.get('initial_currencies', {})

        # Create default currency balances for new users
        default_currencies = {
            'coins': currencies_config.get('coins', 0),
            'gems': currencies_config.get('gems', 0),
            'diamonds': currencies_config.get('diamonds', 0),
            'renown': currencies_config.get('renown', 0),
            'xp': currencies_config.get('xp', 0)
        }

    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product or None
        """
        return self.products.get(product_id)

    def get_products_by_category(self, category: ProductCategory) -> List[Product]:
        """
        Get products by category.

        Args:
            category: Product category

        Returns:
            List of products
        """
        product_ids = self.categories.get(category, [])
        return [self.products[pid] for pid in product_ids if pid in self.products]

    def get_all_products(self) -> List[Product]:
        """Get all products."""
        return list(self.products.values())

    def purchase_product(self, user_id: str, product_id: str, quantity: int = 1,
                         payment_method: Optional[str] = None) -> Tuple[bool, str, Optional[Purchase]]:
        """
        Purchase a product.

        Args:
            user_id: User ID
            product_id: Product ID
            quantity: Quantity to purchase
            payment_method: Payment method

        Returns:
            Tuple of (success, message, purchase)
        """
        if not self.is_enabled:
            return False, "Microtransactions system is disabled", None

        # Check if product exists
        product = self.products.get(product_id)
        if not product:
            return False, "Product not found", None

        # Check if product is purchasable
        if not product.is_purchasable:
            return False, "Product is not available for purchase", None

        # Check stock
        if product.is_limited and product.stock_count < quantity:
            return False, "Not enough stock available", None

        # Check purchase limits
        user_purchase_count = self._get_user_purchase_count(user_id, product_id)
        if user_purchase_count >= product.max_purchase_count:
            return False, "Purchase limit exceeded", None

        # Get user currency balance
        balance = self._get_user_balance(user_id)
        if not balance:
            # Create new balance if not exists
            balance = CurrencyBalance(user_id=user_id)
            self.user_balances[user_id] = balance

        # Check if user has enough of each currency
        for currency in self.currencies_enabled:
            if currency in product.price:
                currency_balance = getattr(balance, currency)
                required = product.price[currency] * quantity

                if currency_balance < required:
                    return False, f"Not enough {currency}", None

        # Process payment
        if payment_method:
            payment_success, transaction_id = self._process_payment(
                user_id, product.price, currency_type=product.price.keys().__iter__().__next__()
            )
            if not payment_success:
                return False, "Payment failed", None
        else:
            transaction_id = None

        # Deduct currency from balance
        self._deduct_currency(balance, product.price, quantity)

        # Update product stock
        if product.is_limited:
            product.stock_count -= quantity

        # Create purchase record
        purchase_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Calculate total amount
        total_amount = 0
        currency_type = list(product.price.keys())[0]  # Assume single currency for simplicity
        if currency_type in CurrencyType.__members__:
            total_amount = product.price[currency_type] * quantity

        purchase = Purchase(
            purchase_id=purchase_id,
            user_id=user_id,
            product_id=product_id,
            currency_type=CurrencyType(currency_type),
            amount=total_amount,
            price_paid=product.price.copy(),
            timestamp=timestamp,
            transaction_id=transaction_id
        )

        # Save purchase
        if user_id not in self.purchase_history:
            self.purchase_history[user_id] = []
        self.purchase_history[user_id].append(purchase)

        # Save data
        self._save_data()

        return True, "Purchase successful", purchase

    def add_currency(self, user_id: str, currency_type: CurrencyType, amount: float) -> bool:
        """
        Add currency to user balance.

        Args:
            user_id: User ID
            currency_type: Currency type
            amount: Amount to add

        Returns:
            True if successful, False otherwise
        """
        balance = self._get_user_balance(user_id)
        if not balance:
            balance = CurrencyBalance(user_id=user_id)
            self.user_balances[user_id] = balance

        setattr(balance, currency_type.value, getattr(balance, currency_type.value) + amount)
        balance.last_updated = datetime.now().isoformat()

        self._save_data()
        return True

    def get_currency_balance(self, user_id: str) -> Optional[CurrencyBalance]:
        """
        Get user currency balance.

        Args:
            user_id: User ID

        Returns:
            Currency balance or None
        """
        return self.user_balances.get(user_id)

    def get_purchase_history(self, user_id: str) -> List[Purchase]:
        """
        Get user purchase history.

        Args:
            user_id: User ID

        Returns:
            List of purchases
        """
        return self.purchase_history.get(user_id, [])

    def _get_user_balance(self, user_id: str) -> Optional[CurrencyBalance]:
        """Get user balance."""
        return self.user_balances.get(user_id)

    def _get_user_purchase_count(self, user_id: str, product_id: str) -> int:
        """Get number of times user has purchased a product."""
        purchases = self.purchase_history.get(user_id, [])
        return sum(1 for p in purchases if p.product_id == product_id)

    def _deduct_currency(self, balance: CurrencyBalance, prices: Dict[str, float], quantity: int) -> None:
        """Deduct currency from balance."""
        for currency, price in prices.items():
            if hasattr(balance, currency):
                setattr(balance, currency, getattr(balance, currency) - price * quantity)

        balance.last_updated = datetime.now().isoformat()

    def _process_payment(self, user_id: str, prices: Dict[str, float], currency_type: str) -> Tuple[bool, Optional[str]]:
        """
        Process payment.

        Args:
            user_id: User ID
            prices: Product prices
            currency_type: Currency type

        Returns:
            Tuple of (success, transaction_id)
        """
        # This would integrate with actual payment processor
        # For now, just return success
        transaction_id = str(uuid.uuid4())
        return True, transaction_id

    def _save_data(self) -> None:
        """Save data to files."""
        import os

        data_dir = self.config.get('data_directory', 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Save products
        products_data = [product.to_dict() for product in self.products.values()]
        with open(os.path.join(data_dir, 'products.json'), 'w') as f:
            json.dump(products_data, f, indent=2)

        # Save user balances
        balances_data = [balance.to_dict() for balance in self.user_balances.values()]
        with open(os.path.join(data_dir, 'currency_balances.json'), 'w') as f:
            json.dump(balances_data, f, indent=2)

        # Save purchase history
        history_data = {}
        for user_id, purchases in self.purchase_history.items():
            history_data[user_id] = [purchase.to_dict() for purchase in purchases]

        with open(os.path.join(data_dir, 'purchase_history.json'), 'w') as f:
            json.dump(history_data, f, indent=2)

    def _load_currency_data(self) -> None:
        """Load currency data."""
        import os

        data_dir = self.config.get('data_directory', 'data')

        # Load user balances
        balances_file = os.path.join(data_dir, 'currency_balances.json')
        if os.path.exists(balances_file):
            try:
                with open(balances_file, 'r') as f:
                    balances_data = json.load(f)
                    for balance_data in balances_data:
                        balance = CurrencyBalance.from_dict(balance_data)
                        self.user_balances[balance.user_id] = balance
            except Exception as e:
                print(f"Error loading currency balances: {e}")

        # Load purchase history
        history_file = os.path.join(data_dir, 'purchase_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)

                    for user_id, purchases_data in history_data.items():
                        purchases = [Purchase.from_dict(data) for data in purchases_data]
                        self.purchase_history[user_id] = purchases

            except Exception as e:
                print(f"Error loading purchase history: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert microtransactions system to dictionary for saving.

        Returns:
            Dictionary representation of microtransactions
        """
        return {
            'is_enabled': self.is_enabled,
            'payment_provider': self.payment_provider.value,
            'currencies_enabled': self.currencies_enabled,
            'taxes_enabled': self.taxes_enabled,
            'tax_rate': self.tax_rate,
            'products_count': len(self.products),
            'users_count': len(self.user_balances),
            'total_purchases': sum(len(purchases) for purchases in self.purchase_history.values())
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load microtransactions system from dictionary.

        Args:
            data: Dictionary representation of microtransactions
        """
        self.is_enabled = data['is_enabled']
        self.payment_provider = PaymentProvider(data['payment_provider'])
        self.currencies_enabled = data['currencies_enabled']
        self.taxes_enabled = data['taxes_enabled']
        self.tax_rate = data['tax_rate']

    def update(self) -> None:
        """Update microtransactions system."""
        # Update currency balances, check for expired items, etc.
        pass

    def cleanup(self) -> None:
        """Cleanup microtransactions system."""
        # Save all data
        self._save_data()