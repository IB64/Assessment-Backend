"""Fixtures used by multiple tests."""

# pylint: skip-file

import pytest

from api import app
from database_functions import get_db_connection


@pytest.fixture
def test_api():
    return app.test_client()

# The fixtures below this comment are used by the existing tests; to avoid unexpected complications, your own tests should NOT
# interact with them.

@pytest.fixture(autouse=True)
def setup_test_db():
    """Sets up a test database with the same structure as the real one."""

    conn = get_db_connection("postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP DATABASE IF EXISTS test_marine_experiments;")
        cur.execute("CREATE DATABASE test_marine_experiments;")
    conn.close()
    conn = get_db_connection("test_marine_experiments")
    with conn.cursor() as cur:
        with open("setup-db.sql", 'r') as f:
            for q in f.read().split("\n\n"):
                cur.execute(q)
    conn.commit()
    conn.close()
    yield
    conn = get_db_connection("postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP DATABASE test_marine_experiments WITH (FORCE);")
    conn.close()


@pytest.fixture(autouse=True)
def test_db_conn(monkeypatch):
    """Ensures that all tests use the test database."""
    mock_conn = get_db_connection("test_marine_experiments")
    monkeypatch.setattr("api.conn", mock_conn)


@pytest.fixture
def example_subjects():
    return [
        {
            "date_of_birth": "2023-01-15",
            "species_name": "Tuna",
            "subject_id": 1,
            "subject_name": "Flounder"
        },
        {
            "date_of_birth": "2022-06-12",
            "species_name": "Orca",
            "subject_id": 2,
            "subject_name": "Triton"
        },
        {
            "date_of_birth": "2021-08-08",
            "species_name": "Tiger shark",
            "subject_id": 5,
            "subject_name": "Poseidon"
        },
        {
            "date_of_birth": "2018-11-10",
            "species_name": "Tiger shark",
            "subject_id": 3,
            "subject_name": "Moana"
        },
        {
            "date_of_birth": "2014-02-03",
            "species_name": "Orca",
            "subject_id": 4,
            "subject_name": "Cindi"
        }
    ]


@pytest.fixture
def example_experiments():
    return [
        {
            "experiment_date": "2024-02-12",
            "experiment_id": 10,
            "experiment_type": "obedience",
            "score": "60.00%",
            "species": "Tiger shark",
            "subject_id": 5
        },
        {
            "experiment_date": "2024-02-10",
            "experiment_id": 9,
            "experiment_type": "aggression",
            "score": "100.00%",
            "species": "Orca",
            "subject_id": 4
        },
        {
            "experiment_date": "2024-02-08",
            "experiment_id": 7,
            "experiment_type": "obedience",
            "score": "80.00%",
            "species": "Orca",
            "subject_id": 2
        },
        {
            "experiment_date": "2024-02-06",
            "experiment_id": 8,
            "experiment_type": "aggression",
            "score": "10.00%",
            "species": "Orca",
            "subject_id": 2
        },
        {
            "experiment_date": "2024-02-02",
            "experiment_id": 6,
            "experiment_type": "obedience",
            "score": "20.00%",
            "species": "Orca",
            "subject_id": 4
        },
        {
            "experiment_date": "2024-01-06",
            "experiment_id": 1,
            "experiment_type": "intelligence",
            "score": "23.33%",
            "species": "Tuna",
            "subject_id": 1
        },
        {
            "experiment_date": "2024-01-06",
            "experiment_id": 5,
            "experiment_type": "intelligence",
            "score": "56.67%",
            "species": "Tiger shark",
            "subject_id": 5
        },
        {
            "experiment_date": "2024-01-06",
            "experiment_id": 4,
            "experiment_type": "intelligence",
            "score": "96.67%",
            "species": "Orca",
            "subject_id": 4
        },
        {
            "experiment_date": "2024-01-06",
            "experiment_id": 3,
            "experiment_type": "intelligence",
            "score": "86.67%",
            "species": "Tiger shark",
            "subject_id": 3
        },
        {
            "experiment_date": "2024-01-06",
            "experiment_id": 2,
            "experiment_type": "intelligence",
            "score": "90.00%",
            "species": "Orca",
            "subject_id": 2
        }
    ]


@pytest.fixture
def test_temp_conn():
    return get_db_connection("test_marine_experiments")

@pytest.fixture
def new_experiment():
    return {
        "subject_id": 3,
        "experiment_type": "obedience",
        "experiment_date": "2024-03-01",
        "score": 7
    }
