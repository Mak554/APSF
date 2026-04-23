"""
Local in-memory database — a drop-in replacement for firebase_config.py
when running without Firebase credentials.

Set USE_LOCAL_DB=true in .env to use this.
All data is stored in Python dicts (lost on restart — perfect for demos/testing).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


# ─── In-memory store ──────────────────────────────────────────────────────────
_store: Dict[str, Dict[str, Any]] = {
    "users": {},
    "events": {},
    "campaigns": {},
    "training-assignments": {},
}


class _FakeIncrement:
    def __init__(self, n): self.n = n


class _FakeQuery:
    DESCENDING = "desc"
    ASCENDING = "asc"

    def __init__(self, docs): self._docs = docs
    def where(self, field, op, val):
        return _FakeQuery([d for d in self._docs if d.get(field) == val])
    def order_by(self, field, direction="asc"):
        rev = (direction == "desc")
        return _FakeQuery(sorted(self._docs, key=lambda d: d.get(field, ""), reverse=rev))
    def stream(self):
        return [_FakeDoc(d) for d in self._docs]


class _FakeDoc:
    def __init__(self, data): self._data = data
    @property
    def exists(self): return self._data is not None
    def to_dict(self): return dict(self._data)


class _FakeDocRef:
    def __init__(self, collection, doc_id):
        self._col = collection
        self._id = doc_id

    def get(self):
        return _FakeDoc(_store[self._col].get(self._id))

    def set(self, data):
        _store[self._col][self._id] = dict(data)

    def update(self, data):
        existing = _store[self._col].setdefault(self._id, {})
        for k, v in data.items():
            if isinstance(v, _FakeIncrement):
                existing[k] = existing.get(k, 0) + v.n
            else:
                existing[k] = v


class _FakeCollection:
    def __init__(self, name): self._name = name

    def document(self, doc_id): return _FakeDocRef(self._name, doc_id)

    def stream(self):
        return [_FakeDoc(d) for d in _store[self._name].values()]

    def where(self, field, op, val):
        docs = [d for d in _store[self._name].values() if d.get(field) == val]
        return _FakeQuery(docs)

    def order_by(self, field, direction="asc"):
        docs = list(_store[self._name].values())
        rev = (direction == "desc")
        return _FakeQuery(sorted(docs, key=lambda d: d.get(field, ""), reverse=rev))


class _FakeDB:
    def collection(self, name):
        if name not in _store:
            _store[name] = {}
        return _FakeCollection(name)


class Increment:
    """Mimics firestore.Increment for local mode."""
    def __new__(cls, n):
        return _FakeIncrement(n)


class Query:
    DESCENDING = "desc"
    ASCENDING = "asc"


# Singleton
_local_db = _FakeDB()
def get_local_db(): return _local_db
