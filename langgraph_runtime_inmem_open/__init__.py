"""
Open Source Alternative to langgraph-runtime-inmem
Compatible with LangGraph CLI inmem functionality

This package provides an open-source implementation of the in-memory runtime
for LangGraph, addressing the supply-chain risks of the closed-source package.
"""

__version__ = "0.1.0"
__author__ = "Abdulmalik Alquwayfili (Open Source Community)"
__description__ = "Open-source alternative to langgraph-runtime-inmem"

from .checkpoint import MemorySaver
from .store import BaseStore, InMemoryStore, Store

__all__ = ["InMemoryStore", "BaseStore", "Store", "MemorySaver"]
