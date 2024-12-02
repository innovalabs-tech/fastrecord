```pythonBase
# Your application code (e.g., models/user.py)
from fastrecord import FastRecord, Field
from fastrecord.decorators import cached

class User(FastRecord):
    name: str = Field(...)
    email: str = Field(...)
    
    @classmethod
    @cached(ttl=3600)
    def find_by_email(cls, email: str):
        return cls.where(email=email).first()

    @classmethod
    def search(cls, **kwargs):
        return (
            cls.where(**kwargs)
            .cache(ttl=300)  # Cache for 5 minutes
            .all()
        )

    # Or use the cache parameter
    users = User.where(status='active').all(cache=True)
```