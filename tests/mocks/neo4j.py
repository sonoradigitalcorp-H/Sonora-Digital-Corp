"""Mock Neo4j driver for testing."""


class MockRecord:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data.get(key)

    def get(self, key, default=None):
        return self._data.get(key, default)


class MockResult:
    def __init__(self, records=None):
        self._records = records or []

    def single(self):
        return self._records[0] if self._records else None

    def __iter__(self):
        return iter(self._records)


class MockSession:
    def __init__(self, records=None):
        self._records = records or []

    def run(self, query, **params):
        return MockResult(self._records)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def close(self):
        pass


class MockDriver:
    def __init__(self, available=True, records=None):
        self._available = available
        self._records = records or []

    def session(self):
        return MockSession(self._records)

    def close(self):
        pass


class MockNeo4jStore:
    def __init__(self, available=True):
        self.available = available
        self._driver = MockDriver(available=available)

    def get_driver(self):
        return self._driver if self.available else None

    def is_available(self):
        return self.available

    def test_connection(self):
        return self.available

    def create_session(self, session_id=None, title="", project=None, tags=None):
        return {"id": session_id or "test-session", "title": title, "project": project, "tags": tags or []}

    def get_session(self, session_id):
        return {"id": session_id, "title": "Test", "messages": []}

    def list_sessions(self, **kwargs):
        return [{"id": "test-1", "title": "Test Session"}]

    def add_message(self, session_id, role, content, tokens=0):
        return {"id": "msg-1", "role": role, "content": content, "tokens": tokens}

    def search_sessions(self, query):
        return [{"id": "test-1", "title": "Test Session"}]

    def toggle_pin(self, session_id):
        return True

    def delete_session(self, session_id):
        return True

    def init_schema(self):
        return True
