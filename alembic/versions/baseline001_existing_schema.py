"""Baseline: esquema ya aplicado (scripts SQL). Sin cambios.

Usar `alembic stamp baseline001` en entornos existentes antes de `upgrade head`.
"""

from typing import Sequence, Union

revision: str = "baseline001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
