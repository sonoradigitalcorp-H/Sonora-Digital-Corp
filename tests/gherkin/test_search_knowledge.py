from pytest_bdd import scenario
from tests.steps.search_knowledge_steps import *


@scenario("search-knowledge.feature", "Basic semantic search")
def test_semantic_search():
    pass


@scenario("search-knowledge.feature", "Empty query rejected")
def test_empty_query():
    pass
