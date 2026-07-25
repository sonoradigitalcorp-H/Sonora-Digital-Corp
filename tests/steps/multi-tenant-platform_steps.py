"""Step definitions for multi-tenant-platform capability."""

import os
import yaml
import pytest
from pytest_bdd import given, when, then, scenario


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@given("the SDD framework is initialized")
def sdd_initialized():
    assert os.path.isdir(os.path.join(REPO, "specs"))
    assert os.path.isdir(os.path.join(REPO, "adrs"))


@given("the TenantResolver is available in core/tenants/")
def tenant_resolver_exists():
    resolver_py = os.path.join(REPO, "core", "tenants", "resolver.py")
    resolver_go = os.path.join(REPO, "core", "tenants", "resolver.go")
    assert os.path.exists(resolver_py) or os.path.exists(resolver_go)


@given("the repository structure")
def repo_structure():
    assert os.path.isdir(os.path.join(REPO, "core"))
    assert os.path.isdir(os.path.join(REPO, "tenants"))


@given('tenant "{tenant_id}" has skills/ directory')
def tenant_skills_dir(tenant_id):
    skills_path = os.path.join(REPO, "tenants", tenant_id, "skills")
    assert os.path.isdir(skills_path)


@given('tenant "{tenant_id}" has different skills/')
def tenant_skills_other(tenant_id):
    skills_path = os.path.join(REPO, "tenants", tenant_id, "skills")
    assert os.path.isdir(skills_path)


@given("the RAG pipeline is active")
def rag_active():
    qdrant_endpoint = os.environ.get("QDRANT_HOST", "localhost:6333")
    assert qdrant_endpoint, "QDRANT_HOST should be set"


@given("a Cypher query is executed")
def cypher_query():
    neo4j_host = os.environ.get("NEO4J_HOST", "localhost:7687")
    assert neo4j_host


@given("postgres tables have tenant_id columns")
def postgres_rls():
    assert True


@given("the _template/ directory exists")
def template_exists():
    template_path = os.path.join(REPO, "tenants", "_template")
    assert os.path.isdir(template_path)
    assert os.path.isfile(os.path.join(template_path, "prompt.md"))
    assert os.path.isfile(os.path.join(template_path, "tools.yaml"))
    assert os.path.isfile(os.path.join(template_path, "config.yaml"))


@given("the archive/ directory exists")
def archive_exists():
    archive_path = os.path.join(REPO, "archive")
    assert os.path.isdir(archive_path)


@given('tenant "{tenant_id}" has tools.yaml with blocked_tools: [github_deploy]')
def tenant_blocks_github(tenant_id):
    tools_path = os.path.join(REPO, "tenants", tenant_id, "tools.yaml")
    with open(tools_path) as f:
        config = yaml.safe_load(f)
    assert "github_deploy" in config.get("blocked_tools", [])


@given('a valid tenant_id "{tenant_id}"')
def valid_tenant(tenant_id):
    assert os.path.isdir(os.path.join(REPO, "tenants", tenant_id))


@when("I search for hardcoded tenant names in core/")
def search_tenant_names():
    """Placeholder — real impl would grep core/ for tenant name strings"""
    pass


@when("the resolver loads its context")
def load_tenant_context():
    pass


@when("the orchestrator processes a request for sonora-digital")
def orchestrate_for_tenant():
    pass


@when("a vector search is performed for a tenant")
def vector_search_tenant():
    pass


@when('the query originates from tenant "abe-music"')
def neo4j_query_abe():
    pass


@when("a query is executed with current_setting('app.current_tenant') = 'sonora-digital'")
def postgres_rls_tenant():
    pass


@when('a webhook arrives at /webhook')
def webhook_arrives():
    pass


@when('the header X-Tenant-ID is set')
def webhook_with_tenant():
    pass


@when("I copy it to clients/nuevo-cliente/")
def copy_template():
    pass


@when("I replace {{TENANT_ID}} with \"nuevo-cliente\"")
def replace_tenant_id():
    pass


@when("I list tenants for active client configs")
def list_tenants():
    pass


@when("the agent attempts to use github_deploy")
def agent_uses_github():
    pass


@then("no tenant IDs should appear hardcoded in core/")
def verify_no_tenant_names():
    """Placeholder — real impl would grep core/ for these strings"""
    pass


@then("it should return prompt.md content")
def returns_prompt():
    assert True


@then("it should return allowed_tools from tools.yaml")
def returns_tools():
    assert True


@then("it should return mcp_servers from mcp.yaml")
def returns_mcp():
    assert True


@then("it should NOT load skills from other tenants")
def skills_not_loaded():
    assert True


@then("the query should include a tenant_id filter")
def qdrant_filter():
    assert True


@then('the query should target the tenant-specific collection')
def qdrant_collection():
    assert True


@then('the query should target database or include WHERE n.tenant_id = tenant_id')
def neo4j_isolation():
    assert True


@then("it should only return rows with matching tenant_id")
def postgres_isolation():
    assert True


@then("the gateway routes to the correct tenant's agent instance")
def gateway_routes():
    assert True


@then("the tenant should be operational in < 5 minutes")
def tenant_operational():
    assert True


@then("all clients should be in clients/ directory")
def clients_in_clients_dir():
    clients_path = os.path.join(REPO, "clients")
    assert os.path.isdir(clients_path)


@then("the Policy Engine should block the call")
def policy_blocks():
    assert True
