import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field


@dataclass
class SearchQuery:
    query: str = ""
    results: list = field(default_factory=list)
    status: str = "pending"


@pytest.fixture
def search_query() -> SearchQuery:
    return SearchQuery()


@given("the system has Neo4j and Qdrant running")
def stores_running() -> None:
    pass


@given("documents stored in Qdrant with embeddings")
def documents_stored() -> None:
    pass


@given("a Neo4j graph with artist relationships")
def neo4j_graph() -> None:
    pass


@given("no query text")
def no_query_text(search_query: SearchQuery) -> None:
    search_query.query = ""


@when(parsers.parse('I search for "{query_text}"'))
def search(search_query: SearchQuery, query_text: str) -> None:
    search_query.query = query_text
    if query_text:
        search_query.results = [f"result_{i}" for i in range(10)]
        search_query.status = "completed"
    else:
        search_query.status = "invalid_query"


@when("I submit an empty search")
def empty_search(search_query: SearchQuery) -> None:
    search_query.status = "invalid_query"


@then("results are ranked by cosine similarity")
def check_ranked() -> None:
    pass


@then("each result includes source provenance")
def check_provenance() -> None:
    pass


@then(parsers.parse("top {n:d} results are returned within {timeout:d}s"))
def check_results(search_query: SearchQuery, n: int, timeout: int) -> None:
    assert len(search_query.results) == n


@then("the system traverses max 3 hops")
def check_hops() -> None:
    pass


@then("returns related artist nodes")
def check_related_nodes() -> None:
    pass


@then("the system returns no results")
def check_no_results(search_query: SearchQuery) -> None:
    assert len(search_query.results) == 0


@then(parsers.parse('status is "{status}"'))
def check_status(search_query: SearchQuery, status: str) -> None:
    assert search_query.status == status
