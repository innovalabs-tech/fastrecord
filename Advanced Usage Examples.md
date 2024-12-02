# Advanced Scoping Examples
```pythonBase
from datetime import datetime, timedelta
from typing import Optional, List
from fastrecord import FastRecord, Field
from fastrecord.validation import CustomValidator
from fastrecord.callbacks import before_save, after_save
from fastrecord.relationships import belongs_to, has_many

class Product(FastRecord):
    name: str
    price: float
    stock: int
    category: str
    status: str = Field(default="active")
    featured: bool = Field(default=False)
    sale_starts_at: Optional[datetime] = None
    sale_ends_at: Optional[datetime] = None

    # Dynamic scope with parameters
    @scope("price_range")
    def price_range(query, min_price: float, max_price: float):
        return query.where(price__gte=min_price, price__lte=max_price)

    # Composite scope combining conditions
    @scope("available")
    def available(query):
        return query.where(
            status="active",
            stock__gt=0
        )

    # Time-based scope
    @scope("on_sale")
    def on_sale(query):
        now = datetime.utcnow()
        return query.where(
            sale_starts_at__lte=now,
            sale_ends_at__gte=now
        )

    # Chainable scopes
    @scope("featured")
    def featured(query):
        return query.where(featured=True)

    @scope("by_category")
    def by_category(query, category: str):
        return query.where(category=category)

    # Example usage:
    # Product.available().on_sale().price_range(10, 100).all()
    # Product.featured().by_category("electronics").all()
```

# Advanced Validation Examples
class Order(FastRecord):
    user_id: int
    total_amount: float
    items: List[dict]  # JSON field storing order items
    status: str = Field(default="pending")
    shipping_address: dict
    payment_method: str
    coupon_code: Optional[str] = None
    
    user = belongs_to("User")
    
    # Complex validation with custom logic
    @validates("items", CustomValidator)
    def validate_items(self, value):
        if not value or len(value) == 0:
            self.add_error("items", "Order must contain at least one item")
            return

        for item in value:
            if not all(k in item for k in ["product_id", "quantity", "price"]):
                self.add_error("items", "Invalid item format")
                return

            if item["quantity"] <= 0:
                self.add_error("items", "Quantity must be positive")
                return

            # Check if product exists and has enough stock
            product = Product.find(item["product_id"])
            if not product:
                self.add_error("items", f"Product {item['product_id']} not found")
            elif product.stock < item["quantity"]:
                self.add_error("items", f"Insufficient stock for product {item['product_id']}")

    @validates("shipping_address", CustomValidator)
    def validate_shipping_address(self, value):
        required_fields = ["street", "city", "state", "zip", "country"]
        if not value or not all(field in value for field in required_fields):
            self.add_error("shipping_address", "Missing required address fields")

    @validates("payment_method", CustomValidator)
    def validate_payment_method(self, value):
        valid_methods = ["credit_card", "paypal", "bank_transfer"]
        if value not in valid_methods:
            self.add_error("payment_method", f"Must be one of: {', '.join(valid_methods)}")

    @validates("coupon_code", CustomValidator)
    def validate_coupon_code(self, value):
        if value:
            coupon = Coupon.where(code=value, status="active").first()
            if not coupon:
                self.add_error("coupon_code", "Invalid or expired coupon code")
            elif coupon.minimum_order_amount and self.total_amount < coupon.minimum_order_amount:
                self.add_error("coupon_code", f"Order total must be at least ${coupon.minimum_order_amount}")


# Advanced Caching Patterns
```pythonBase
class BlogPost(FastRecord):
    title: str
    content: str
    author_id: int
    category: str
    tags: List[str]
    view_count: int = Field(default=0)
    
    author = belongs_to("User")
    comments = has_many("Comment")

    def cache_key(self, suffix: str = "") -> str:
        """Generate a cache key with version and optional suffix"""
        version = getattr(self, 'version', 1)
        return f"blog_post:{self.id}:v{version}{suffix}"

    @classmethod
    def find_with_cache(cls, id: int):
        """Find a blog post with caching"""
        cache_key = f"blog_post:{id}"
        
        # Try to get from cache
        cached = cls._cache.fetch(cache_key)
        if cached:
            return cls(**cached)
        
        # Get from database and cache
        post = cls.find(id)
        if post:
            cls._cache.write(cache_key, post.to_dict(), ttl=3600)
        return post

    def cached_comment_count(self) -> int:
        """Get cached comment count"""
        cache_key = self.cache_key(":comment_count")
        
        count = self._cache.fetch(cache_key)
        if count is None:
            count = self.comments.count()
            self._cache.write(cache_key, count, ttl=300)  # Cache for 5 minutes
        
        return count

    @classmethod
    def trending(cls, limit: int = 10):
        """Get trending posts with caching"""
        cache_key = f"trending_posts:limit:{limit}"
        
        posts = cls._cache.fetch(cache_key)
        if posts is None:
            posts = cls.where(
                published=True
            ).order(
                "-view_count", "-created_at"
            ).limit(limit).all()
            
            posts_data = [post.to_dict() for post in posts]
            cls._cache.write(cache_key, posts_data, ttl=900)  # Cache for 15 minutes
            return posts
        
        return [cls(**post_data) for post_data in posts]

    def increment_views(self):
        """Increment view count with cache invalidation"""
        self.view_count += 1
        self.save()
        
        # Invalidate caches
        self._cache.delete(self.cache_key())
        self._cache.delete("trending_posts:limit:10")  # Invalidate trending cache

    @before_save
    def invalidate_caches(self):
        """Invalidate all related caches before save"""
        self._cache.delete(self.cache_key())
        self._cache.delete(self.cache_key(":comment_count"))
        self._cache.delete("trending_posts:limit:10")

    @classmethod
    def bulk_cache_comment_counts(cls, post_ids: List[int]):
        """Bulk cache comment counts for multiple posts"""
        posts = cls.where(id__in=post_ids).includes("comments").all()
        
        for post in posts:
            cache_key = post.cache_key(":comment_count")
            count = len(post.comments)
            cls._cache.write(cache_key, count, ttl=300)
```

# Example Usage
```pythonBase
def scope_examples():
    # Find products on sale in a specific price range
    affordable_sale_items = Product.available().on_sale().price_range(10, 50).all()
    
    # Find featured products by category
    featured_electronics = Product.featured().by_category("electronics").all()
    
    # Complex chaining
    holiday_deals = (
        Product.available()
        .on_sale()
        .featured()
        .price_range(20, 200)
        .by_category("toys")
        .order("-price")
        .limit(20)
        .all()
    )
```

```pythonBase
def validation_examples():
    # Create an order with validation
    order = Order(
        user_id=1,
        total_amount=99.99,
        items=[
            {"product_id": 1, "quantity": 2, "price": 49.99},
            {"product_id": 2, "quantity": 1, "price": 0.01}
        ],
        shipping_address={
            "street": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "zip": "02108",
            "country": "USA"
        },
        payment_method="credit_card",
        coupon_code="SUMMER20"
    )
    
    if not order.valid():
        print("Validation errors:", order.errors)
    else:
        order.save()
```

```pythonBase
def caching_examples():
    # Find post with caching
    post = BlogPost.find_with_cache(1)
    
    # Get cached comment count
    comment_count = post.cached_comment_count()
    
    # Get trending posts
    trending_posts = BlogPost.trending(limit=5)
    
    # Increment views with cache invalidation
    post.increment_views()
    
    # Bulk cache comment counts
    BlogPost.bulk_cache_comment_counts([1, 2, 3, 4, 5])
```