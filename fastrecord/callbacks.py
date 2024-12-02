from enum import Enum
from typing import List, Dict, Any


class CallbackType(Enum):
    BEFORE_VALIDATION = "before_validation"
    AFTER_VALIDATION = "after_validation"
    BEFORE_SAVE = "before_save"
    AFTER_SAVE = "after_save"
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create"
    BEFORE_UPDATE = "before_update"
    AFTER_UPDATE = "after_update"
    BEFORE_DESTROY = "before_destroy"
    AFTER_DESTROY = "after_destroy"


class CallbackHandler:
    def __init__(self):
        self._callbacks: Dict[CallbackType, List[str]] = {
            callback_type: [] for callback_type in CallbackType
        }

    def register(self, callback_type: CallbackType, method_name: str):
        self._callbacks[callback_type].append(method_name)

    def run_callbacks(self, instance: Any, callback_type: CallbackType) -> bool:
        """Run callbacks for a given type. Returns False if any callback returns False."""
        for method_name in self._callbacks[callback_type]:
            method = getattr(instance, method_name)
            if method() is False:  # Explicit false return halts the callback chain
                return False
        return True


class CallbackMixin:
    _callback_handler = CallbackHandler()

    @classmethod
    def before_validation(cls, method_name: str):
        cls._callback_handler.register(CallbackType.BEFORE_VALIDATION, method_name)
        return method_name

    @classmethod
    def after_validation(cls, method_name: str):
        cls._callback_handler.register(CallbackType.AFTER_VALIDATION, method_name)
        return method_name

    @classmethod
    def before_save(cls, method_name: str):
        cls._callback_handler.register(CallbackType.BEFORE_SAVE, method_name)
        return method_name

    @classmethod
    def after_save(cls, method_name: str):
        cls._callback_handler.register(CallbackType.AFTER_SAVE, method_name)
        return method_name

    @classmethod
    def before_create(cls, method_name: str):
        cls._callback_handler.register(CallbackType.BEFORE_CREATE, method_name)
        return method_name

    @classmethod
    def after_create(cls, method_name: str):
        cls._callback_handler.register(CallbackType.AFTER_CREATE, method_name)
        return method_name

    @classmethod
    def before_update(cls, method_name: str):
        cls._callback_handler.register(CallbackType.BEFORE_UPDATE, method_name)
        return method_name

    @classmethod
    def after_update(cls, method_name: str):
        cls._callback_handler.register(CallbackType.AFTER_UPDATE, method_name)
        return method_name

    @classmethod
    def before_destroy(cls, method_name: str):
        cls._callback_handler.register(CallbackType.BEFORE_DESTROY, method_name)
        return method_name

    @classmethod
    def after_destroy(cls, method_name: str):
        cls._callback_handler.register(CallbackType.AFTER_DESTROY, method_name)
        return method_name
