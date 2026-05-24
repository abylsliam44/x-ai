from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import ARRAY as PGArray
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import Float, TypeEngine


def JsonField() -> TypeEngine:
    return JSON().with_variant(JSONB(), "postgresql")


def StringArrayField() -> TypeEngine:
    return JSON().with_variant(PGArray(String), "postgresql")


def FloatArrayField() -> TypeEngine:
    return JSON().with_variant(PGArray(Float), "postgresql")
