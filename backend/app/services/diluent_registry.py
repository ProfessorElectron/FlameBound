"""Server-controlled diluent lookup boundary; no trusted catalogue is loaded yet."""

from __future__ import annotations

from typing import Protocol

from modelling.atmospheric import BinaryDiluent


class DiluentRegistry(Protocol):
    def resolve(self, diluent_id: str) -> BinaryDiluent | None:
        """Return a catalogue-backed diluent or ``None`` when it is unavailable."""


class UnavailableDiluentRegistry:
    """Default registry until reviewed source-backed diluent records exist."""

    def resolve(self, diluent_id: str) -> BinaryDiluent | None:
        return None


def get_diluent_registry() -> DiluentRegistry:
    """FastAPI dependency for the currently unavailable trusted catalogue."""
    return UnavailableDiluentRegistry()
