"""Initial migration - create tasks table

Revision ID: 001
Revises: 
Create Date: 2024-12-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task status and priority enums using raw SQL
    conn = op.get_bind()
    
    # Create enums with IF NOT EXISTS
    conn.execute(sa.text(
        "DO $$ BEGIN "
        "CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'done'); "
        "EXCEPTION WHEN duplicate_object THEN null; "
        "END $$;"
    ))
    
    conn.execute(sa.text(
        "DO $$ BEGIN "
        "CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high'); "
        "EXCEPTION WHEN duplicate_object THEN null; "
        "END $$;"
    ))
    
    # Create tasks table using raw SQL to avoid SQLAlchemy's enum auto-creation
    conn.execute(sa.text(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status taskstatus NOT NULL DEFAULT 'todo',
            priority taskpriority NOT NULL DEFAULT 'medium',
            is_completed BOOLEAN NOT NULL DEFAULT false,
            due_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            owner_id INTEGER NOT NULL
        )
        """
    ))
    
    # Create indexes
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_tasks_id ON tasks(id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_tasks_owner_id ON tasks(owner_id)"))


def downgrade() -> None:
    conn = op.get_bind()
    
    # Drop indexes
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_tasks_owner_id"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_tasks_id"))
    
    # Drop table
    conn.execute(sa.text("DROP TABLE IF EXISTS tasks"))
    
    # Drop enums
    conn.execute(sa.text("DROP TYPE IF EXISTS taskstatus"))
    conn.execute(sa.text("DROP TYPE IF EXISTS taskpriority"))

