"""Tests para schema SQL de Sonora OS [FR3, FR9] — valida migración 010_sonora_os.sql."""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
MIGRATIONS = REPO / "infra" / "migrations"
MIGRATION_FILE = MIGRATIONS / "010_sonora_os.sql"

REQUIRED_TABLES = [
    "tenants", "users", "telegram_users", "token_ledger",
    "greetings", "transactions", "quests", "quest_completions",
    "rewards", "schedules", "auto_messages", "notifications",
    "content_generations", "scraped_metrics", "knowledge_bases", "agent_events",
    "artists", "releases", "contracts", "revenue_entries",
]

REQUIRED_ENUMS = [
    "tenant_plan", "user_role", "greeting_status", "transaction_status",
    "transaction_type", "quest_category", "quest_frequency",
    "message_channel", "content_type", "content_status",
]

TENANT_SCOPED_TABLES = [
    "users", "telegram_users", "token_ledger", "greetings", "transactions",
    "quests", "quest_completions", "rewards", "schedules", "auto_messages",
    "notifications", "content_generations", "scraped_metrics", "knowledge_bases",
    "agent_events", "artists", "releases", "contracts", "revenue_entries",
]


class TestSQLMigrationExists:
    """FR3: Migration file must exist and be valid SQL."""

    def test_migration_file_exists(self):
        assert MIGRATION_FILE.exists(), f"Migration file not found: {MIGRATION_FILE}"

    def test_migration_file_not_empty(self):
        content = MIGRATION_FILE.read_text()
        assert len(content) > 1000, "Migration file is too small"

    def test_migration_starts_with_comment(self):
        content = MIGRATION_FILE.read_text()
        assert content.startswith("--"), "Migration should start with SQL comment header"


class TestSQLRequiredTables:
    """FR3: All required tables must be defined in the migration."""

    def _sql_content(self):
        return MIGRATION_FILE.read_text()

    def test_all_required_tables_exist(self):
        sql = self._sql_content()
        for table in REQUIRED_TABLES:
            assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, \
                f"Missing CREATE TABLE for {table}"

    def test_all_required_tables_count(self):
        sql = self._sql_content()
        count = sql.count("CREATE TABLE IF NOT EXISTS")
        assert count == len(REQUIRED_TABLES), \
            f"Expected {len(REQUIRED_TABLES)} tables, found {count}"

    def test_each_table_has_uuid_primary_key(self):
        sql = self._sql_content()
        for table in REQUIRED_TABLES:
            assert f"CREATE TABLE IF NOT EXISTS {table}" in sql
            idx = sql.index(f"CREATE TABLE IF NOT EXISTS {table}")
            end = sql.index(";", idx)
            ddl = sql[idx:end]
            assert "id UUID PRIMARY KEY DEFAULT gen_random_uuid()" in ddl, \
                f"{table}: missing UUID PK with gen_random_uuid()"

    def test_each_table_has_tenant_id(self):
        sql = self._sql_content()
        for table in TENANT_SCOPED_TABLES:
            idx = sql.index(f"CREATE TABLE IF NOT EXISTS {table}")
            end = sql.index(";", idx)
            ddl = sql[idx:end]
            assert "tenant_id UUID NOT NULL REFERENCES tenants(id)" in ddl, \
                f"{table}: missing tenant_id FK to tenants"

    def test_each_table_has_created_at(self):
        sql = self._sql_content()
        for table in REQUIRED_TABLES:
            idx = sql.index(f"CREATE TABLE IF NOT EXISTS {table}")
            end = sql.index(";", idx)
            ddl = sql[idx:end]
            assert "created_at TIMESTAMPTZ NOT NULL DEFAULT now()" in ddl, \
                f"{table}: missing created_at timestamp"


class TestSQLRequiredEnums:
    """FR3: All required enums must be defined."""

    def _sql_content(self):
        return MIGRATION_FILE.read_text()

    def test_all_enums_exist(self):
        sql = self._sql_content()
        for enum_name in REQUIRED_ENUMS:
            assert f"CREATE TYPE {enum_name}" in sql, \
                f"Missing enum: {enum_name}"

    def test_enum_values_are_defined(self):
        sql = self._sql_content()
        assert "tenant_plan AS ENUM ('lanzamiento', 'crecimiento', 'ilimitado', 'enterprise')" in sql
        assert "user_role AS ENUM ('platform_admin', 'client_admin', 'artist', 'fan')" in sql
        assert "greeting_status AS ENUM ('pending_payment', 'paid', 'generating', 'pending_approval', 'approved', 'rejected', 'delivered', 'refunded')" in sql


class TestSQLRLSAndTriggers:
    """FR9: RLS and triggers must be properly configured."""

    def _sql_content(self):
        return MIGRATION_FILE.read_text()

    def test_rls_enabled_on_all_tables(self):
        sql = self._sql_content()
        rls_count = sql.count("ALTER TABLE") - sql.count("ALTER TABLE IF")
        assert rls_count > 0, "No RLS ALTER TABLE statements found"

    def test_each_table_has_rls(self):
        sql = self._sql_content()
        for table in REQUIRED_TABLES:
            assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY" in sql, \
                f"{table}: missing RLS enable"

    def test_updated_at_trigger_function_exists(self):
        sql = self._sql_content()
        assert "CREATE OR REPLACE FUNCTION update_updated_at()" in sql

    def test_seed_data_exists(self):
        sql = self._sql_content()
        assert "abe-music" in sql, "Missing seed data for tenant abe-music"
        assert "beat_supply" in sql, "Missing beat_supply in seed data"


class TestSQLForeignKeyIntegrity:
    """FR3: All Foreign Keys must reference valid tables."""

    def _sql_content(self):
        return MIGRATION_FILE.read_text()

    def test_all_foreign_keys_reference_existing_tables(self):
        sql = self._sql_content()
        import re
        refs = re.findall(r'REFERENCES (\w+)\(', sql)
        for ref in set(refs):
            if ref in ('tenants', 'users', 'quests', 'quest_completions', 'schedules',
                        'artists', 'contracts', 'releases'):
                continue  # expected references
            assert ref in REQUIRED_TABLES, f"FK references unknown table: {ref}"
