```pythonBase
# Basic Usage Example
from datetime import datetime
from typing import Optional, List
from fastrecord import FastRecord, Field
from fastrecord.validation import PresenceValidator, LengthValidator, FormatValidator
from fastrecord.relationships import belongs_to, has_many, has_one

# Basic Model Definition
class User(FastRecord):
    name: str = Field(index=True)
    email: str = Field(unique=True)
    age: Optional[int] = None
    is_active: bool = Field(default=True)
    
    # Relationships
    posts = has_many("Post", dependent="destroy")
    profile = has_one("Profile")
    
    # Validations
    @validates("name", PresenceValidator)
    def validate_name(self):
        pass
    
    @validates("email", FormatValidator, with_=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    def validate_email(self):
        pass
    
    @validates("age", CustomValidator)
    def validate_age(self, value):
        if value is not None and (value < 0 or value > 120):
            self.add_error("age", "must be between 0 and 120")

class Post(FastRecord):
    title: str
    content: str
    status: str = Field(default="draft")
    view_count: int = Field(default=0)
    published_at: Optional[datetime] = None
    
    # Relationships
    author = belongs_to(User, foreign_key="user_id")
    comments = has_many("Comment")
    
    # Validations
    @validates("title", LengthValidator, minimum=5, maximum=100)
    def validate_title(self):
        pass
    
    @validates("status", CustomValidator)
    def validate_status(self, value):
        if value not in ["draft", "published", "archived"]:
            self.add_error("status", "must be draft, published, or archived")
    
    # Callbacks
    @before_save
    def set_published_at(self):
        if self.status == "published" and not self.published_at:
            self.published_at = datetime.utcnow()

```

# More Advanced Implementation Examples

# Example 1: Custom Query Scopes

```pythonBase
class Article(FastRecord):
    title: str
    content: str
    status: str = Field(default="draft")
    featured: bool = Field(default=False)
    
    @scope("published")
    def published(query):
        return query.where(status="published")
    
    @scope("featured")
    def featured(query):
        return query.where(featured=True)
    
    @default_scope
    def default_scope(query):
        return query.where(deleted_at=None)
```

# Example 2: Caching Implementation

```pythonBase
class CachedPost(FastRecord):
    title: str
    content: str
    view_count: int = Field(default=0)
    
    @classmethod
    def find_cached(cls, id: int):
        cache_key = f"post:{id}"
        
        # Try to get from cache
        cached = cls._cache.fetch(cache_key)
        if cached:
            return cls(**cached)
        
        # Get from database and cache
        post = cls.find(id)
        if post:
            cls._cache.write(cache_key, post.to_dict(), ttl=3600)
        return post
    
    def increment_views(self):
        self.view_count += 1
        self.save()
        # Invalidate cache
        self._cache.delete(f"post:{self.id}")
```

# Example 3: Polymorphic Associations

```pythonBase
class Comment(FastRecord):
    content: str
    commentable = polymorphic(Post, Article, as_="commentable")

class Image(FastRecord):
    url: str
    imageable = polymorphic(User, Post, as_="imageable")
```

# Usage Examples

# Basic CRUD Operations

```pythonBase
def basic_crud_example():
    # Create
    user = User.create(
        name="John Doe",
        email="john@example.com",
        age=30
    )
    
    # Read
    found_user = User.find(user.id)
    all_users = User.all()
    
    # Update
    user.update(name="John Smith")
    
    # Delete
    user.delete()  # Soft delete
    user.destroy()  # Hard delete
```

# Query Examples

```pythonBase
def query_examples():
    # Basic queries
    active_users = User.where(is_active=True).all()
    
    # Complex queries
    recent_posts = Post.where(
        status="published",
        published_at__gt=datetime.utcnow() - timedelta(days=7)
    ).order("-published_at").limit(10).all()
    
    # Using scopes
    featured_articles = Article.featured().published().all()
    
    # Eager loading
    users_with_posts = User.includes("posts", "profile").all()
```

# Relationship Examples

```pythonBase
def relationship_examples():
    user = User.find(1)
    
    # Create associated records
    post = user.posts.create(
        title="My First Post",
        content="Hello World!"
    )
    
    # Query associations
    user_posts = user.posts.where(status="published").all()
    
    # Polymorphic associations
    comment = Comment.create(
        content="Great post!",
        commentable=post
    )
    
    image = Image.create(
        url="/avatar.jpg",
        imageable=user
    )
```

# Validation Examples

```pythonBase
def validation_examples():
    # Valid creation
    try:
        user = User.create_strict(
            name="Jane Doe",
            email="jane@example.com",
            age=25
        )
    except ValidationError as e:
        print(f"Validation failed: {e.errors}")
    
    # Invalid creation
    invalid_user = User(
        name="",  # Will fail presence validation
        email="invalid-email",  # Will fail format validation
        age=150  # Will fail custom validation
    )
    
    if not invalid_user.valid():
        print(f"Validation errors: {invalid_user.errors}")
```

# Cache Usage Examples

```pythonBase
def cache_examples():
    # Find with cache
    post = CachedPost.find_cached(1)
    
    # Increment views with cache invalidation
    post.increment_views()
```