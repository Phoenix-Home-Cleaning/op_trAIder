#!/usr/bin/env python3
"""
@fileoverview Freeze Alembic SQL snapshots after each migration revision
@module scripts.freeze_alembic_sql

@description
Generates SQL scripts for each Alembic revision and writes them to
backend/sql/migrations_snapshots/<revision>.sql. This ensures diffs
catch any uncommitted drift between models and migrations.
@performance O(#migrations) SQL generation, offline mode
@risk LOW — Only generates SQL without applying migrations

Usage:
    python scripts/freeze_alembic_sql.py
"""
import os
import subprocess
from alembic.config import Config
from alembic.script import ScriptDirectory

def main():
    repo_root = os.getcwd()
    # Updated paths to reflect monorepo reorganization (ADR-017)
    backend_dir = os.path.join(repo_root, 'apps', 'backend')
    alembic_ini = os.path.join(backend_dir, 'alembic.ini')

    cfg = Config(alembic_ini)
    # Ensure script location (relative to backend_dir)
    cfg.set_main_option('script_location', os.path.join(backend_dir, 'migrations'))
    script_dir = ScriptDirectory.from_config(cfg)

    # Save snapshots alongside other SQL resources inside apps/backend/sql
    snapshots_dir = os.path.join(backend_dir, 'sql', 'migrations_snapshots')
    os.makedirs(snapshots_dir, exist_ok=True)

    # Walk revisions from oldest to newest
    revisions = list(script_dir.walk_revisions(None, 'heads'))
    revisions.reverse()
    for rev in revisions:
        rev_id = rev.revision
        output_path = os.path.join(snapshots_dir, f'{rev_id}.sql')
        print(f'Generating SQL snapshot for revision {rev_id}')
        result = subprocess.run(
            ['alembic', '-c', alembic_ini, 'upgrade', rev_id, '--sql'],
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        if result.returncode != 0:
            print(f'Error generating SQL for {rev_id}:', result.stderr)
            exit(1)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

if __name__ == '__main__':
    main() 