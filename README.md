# FastRecord

A Rails-like ORM for FastAPI using SQLModel, bringing Active Record pattern to Python.

## Version Compatibility

| FastRecord | Python | FastAPI  | SQLModel | Redis  |
|------------|--------|----------|----------|--------|
| 0.1.x      | ≥3.13  | ≥0.115.5 | ≥0.0.22  | ≥5.2.0 |

### Requirements

- **Python**: 3.13 or higher required for modern typing features and performance improvements
- **FastAPI**: 0.115.5 or higher for middleware and dependency injection features
- **SQLModel**: 0.0.22 or higher for ORM functionality
- **Redis**: 5.2.0 or higher (with hiredis) for caching support
- **Pydantic Settings**: 2.6.1 or higher for configuration management
- **Inflect**: 7.4.0 or higher for naming conventions

[Previous README content remains the same...]

## Features

- Active Record pattern implementation
- Chainable query interface
- Built-in caching with Redis/memory support
- Callbacks (before/after save, create, update, destroy)
- Validations
- Relationship management (has_many, belongs_to, has_one)
- Soft deletes
- Pagination
- Eager loading

## Installation

```bash
pip install fastrecord
```

## Quick Start

```python
from fastrecord import FastRecord, Field
from typing import Optional, List
from datetime import datetime


class User(FastRecord):
    name: str = Field(...)
    email: str = Field(...)
    posts: List["Post"] = []


class Post(FastRecord):
    title: str = Field(...)
    content: str = Field(...)
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")
    author: Optional[User] = None


# Create
user = User.create(name="John", email="john@example.com")

# Query
user = User.where(name="John").first()
posts = Post.where(author_id=user.id).order("created_at").limit(5).all()

# Update
user.update(name="John Doe")

# Delete
user.delete()  # Soft delete
user.destroy()  # Hard delete
```

## Configuration

```python
from fastrecord import configure

configure(
    DATABASE_URL="postgresql://user:pass@localhost/dbname",
    CACHE_ENABLED=True,
    CACHE_TYPE="redis",
    CACHE_REDIS_URL="redis://localhost:6379/0"
)
```

## FastAPI Integration

```python
from fastapi import FastAPI
from fastrecord import DatabaseMiddleware

app = FastAPI()
app.add_middleware(DatabaseMiddleware)
```

## Validations

```python
from fastrecord.validation import PresenceValidator, FormatValidator


class User(FastRecord):
    name: str = Field(...)
    email: str = Field(...)

    @validates("name", PresenceValidator)
    def validate_name(self):
        pass

    @validates("email", FormatValidator, with_=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    def validate_email(self):
        pass
```

## Relationships

```python
class User(FastRecord):
    posts = has_many("Post")
    profile = has_one("Profile")


class Post(FastRecord):
    author = belongs_to("User")
```

## Caching

```python
class User(FastRecord):
    @cached(ttl=3600)
    def expensive_calculation(self):
        # Complex computation
        pass


# Query caching
users = User.where(active=True).cache(ttl=300).all()
```

## License

MIT License. See [LICENSE](./LICENSE.md) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

Tushar Mangukiya <tushar.m@innovalabs.tech>

# FastRecord Examples

- [Example.md](./Example.md)
- [Cache Example.md](./Cache%20Example.md)
- [Advanced Usage Examples.md](./Advanced%20Usage%20Examples.md)