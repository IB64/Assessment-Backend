"""Tests for the API routes."""

# pylint: skip-file

from unittest.mock import patch
from datetime import date, datetime

import pytest
from psycopg2 import connect


class TestSubjectRoute_Task_1:
    """Tests for the /subject route."""

    def test_returns_200_on_GET(self, test_api):
        """Checks that the route accepts a GET request."""

        res = test_api.get("/subject")

        assert res.status_code == 200

    def test_rejects_non_get_calls(self, test_api):
        """Checks that the route does not accept other types of HTTP request."""

        assert test_api.post("/subject").status_code == 405
        assert test_api.delete("/subject").status_code == 405
        assert test_api.put("/subject").status_code == 405

    def test_returns_list_of_valid_dicts(self, test_api):
        """Checks that the route returns data in the right format."""

        res = test_api.get("/subject")

        required_keys = ["subject_id", "subject_name",
                         "species_name", "date_of_birth"]

        data = res.json

        assert isinstance(data, list), "Not a list"
        assert all(isinstance(d, dict) for d in data), "Not a list of dicts"
        assert all(len(d.keys()) == len(required_keys)
                   for d in data), "Wrong number of keys"
        for k in required_keys:
            assert all(k in d for d in data), f"Key ({k}) not found in data"
    
    def test_returns_data_in_expected_order(self, test_api):
        """Checks that subjects are returned in descending order by DoB."""

        res = test_api.get("/subject")

        data = res.json

        dobs = [datetime.strptime(subject["date_of_birth"], "%Y-%m-%d").date()
                for subject in data]

        for i in range(len(dobs) - 1):
            assert dobs[i] >= dobs[i + 1], "Subjects out of order!"

    def test_returns_data_with_expected_types(self, test_api):
        """Checks that the returned data has the expected types."""

        res = test_api.get("/subject")

        data = res.json

        for subject in data:

            for k, v in subject.items():
                if k != "subject_id":
                    assert isinstance(v, str)
                else:
                    assert isinstance(v, int)

    def test_returns_expected_data(self, test_api, example_subjects):
        """Checks that the expected data is returned."""

        res = test_api.get("/subject")

        data = res.json

        assert len(data) == 5

        for i in range(len(data)):
            assert data[i] == example_subjects[i]

    def test_returns_empty_list_if_no_subjects(self, test_api, test_temp_conn):
        """Checks that the response is an empty list if the database table is empty."""

        with test_temp_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE subject CASCADE;")
            test_temp_conn.commit()

        res = test_api.get("/subject")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == 0

    def test_returns_all_experiments_by_default(self, test_api, test_temp_conn):
        """Checks that the response contains as many items as the database table."""

        with test_temp_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM subject;")
            total = cur.fetchone()["total"]

        res = test_api.get("/subject")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == total

    def test_returns_dates_in_correct_format(self, test_api):
        """Checks that the route returns valid dates in the appropriate format."""

        res = test_api.get("/subject")

        data = res.json

        for subject in data:
           dob = subject["date_of_birth"]
           assert dob.count("-") == 2
           assert datetime.strptime(dob, "%Y-%m-%d")


class TestExperimentGetRoute_Task_2:
    """Tests for the GET /experiment route."""

    def test_returns_200_on_GET(self, test_api):
        """Checks that the route accepts a GET request."""

        res = test_api.get("/experiment")

        assert res.status_code == 200

    def test_rejects_put_delete_calls(self, test_api):
        """Checks that the route does not accept invalid types of HTTP request."""

        assert test_api.delete("/experiment").status_code == 405
        assert test_api.put("/experiment").status_code == 405

    def test_returns_list_of_valid_dicts(self, test_api):
        """Checks that the route returns data in the right format."""

        res = test_api.get("/experiment")

        required_keys = ["experiment_date", "experiment_id",
                         "experiment_type", "score",
                         "species", "subject_id"]

        data = res.json

        assert isinstance(data, list), "Not a list"
        assert all(isinstance(d, dict) for d in data), "Not a list of dicts"
        assert all(len(d.keys()) == len(required_keys)
                   for d in data), "Wrong number of keys"
        for k in required_keys:
            assert all(k in d for d in data), f"Key ({k}) not found in data"

    def test_returns_data_in_expected_order(self, test_api):
        """Checks that subjects are returned in descending order by DoB."""

        res = test_api.get("/experiment")

        data = res.json

        dates = [datetime.strptime(experiment["experiment_date"], "%Y-%m-%d").date()
                for experiment in data]

        for i in range(len(dates) - 1):
            assert dates[i] >= dates[i + 1], "Experiments out of order!"

    def test_returns_data_with_expected_types(self, test_api):
        """Checks that the returned data has the expected types."""

        res = test_api.get("/experiment")

        data = res.json

        for experiment in data:

            for k, v in experiment.items():
                if k not in ("subject_id", "experiment_id"):
                    assert isinstance(v, str)
                else:
                    assert isinstance(v, int)

    def test_returns_correctly_formatted_scores(self, test_api):
        """Checks that scores are returned in the expected format."""

        res = test_api.get("/experiment")

        data = res.json

        scores = [(e["score"], float(e["score"][:-1]))
                  for e in data]
        
        assert all([
            s[0].endswith("%")
            and 0 <= s[1] <= 100
            and round(s[1], 2) == s[1]
            for s in scores
        ])

    def test_returns_expected_data(self, test_api, example_experiments):
        """Checks that the expected data is returned."""

        res = test_api.get("/experiment")

        data = res.json

        assert len(data) == 10

        for i in range(len(data)):
            assert data[i] == example_experiments[i]

    def test_returns_empty_list_if_no_subjects(self, test_api, test_temp_conn):
        """Checks that the response is an empty list if the database table is empty."""

        with test_temp_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE experiment CASCADE;")
            test_temp_conn.commit()

        res = test_api.get("/experiment")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == 0

    def test_returns_all_experiments_by_default(self, test_api, test_temp_conn):
        """Checks that the response contains as many items as the database table."""

        with test_temp_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM experiment;")
            total = cur.fetchone()["total"]

        res = test_api.get("/experiment")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == total

class TestExperimentRoute_Task_3:
    """Tests for the /experiment route with parameters."""

    @pytest.mark.parametrize("filter_type", ("intelligance", "____", 3, True, None, "agression", "threp"))
    def test_rejects_invalid_type_parameter(self, filter_type, test_api):
        """Checks that the route only accepts specific values"""
        res = test_api.get(f"/experiment?type={filter_type}")

        assert res.status_code == 400
        assert res.json == {"error": "Invalid value for 'type' parameter"}

    @pytest.mark.parametrize("filter_score", ("three", -17, 1010, 2.34, -1.2))
    def test_rejects_invalid_score_over_parameter(self, filter_score, test_api):
        """Checks that the route only accepts specific values"""
        res = test_api.get(f"/experiment?score_over={filter_score}")

        assert res.status_code == 400
        assert res.json == {"error": "Invalid value for 'score_over' parameter"}

    @pytest.mark.parametrize("filter_score,output", ((90, 2), (80, 4), (50, 7), (1, 10)))
    def test_returns_expected_data_when_score_is_filtered(self, filter_score, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?score_over={filter_score}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert float(d["score"][:-1]) >= filter_score

    @pytest.mark.parametrize("filter_type,output", (("intelligence", 5), ("obedience", 3), ("aggression", 2)))
    def test_returns_expected_data_when_type_is_filtered(self, filter_type, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?type={filter_type}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type

    @pytest.mark.parametrize("filter_type,output", (("Intelligence", 5), ("oBeDiEnCe", 3), ("aGGressioN", 2)))
    def test_returns_expected_data_when_type_is_filtered_not_case_sensitive(self, filter_type, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?type={filter_type}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type.lower()

    @pytest.mark.parametrize("filter_type, filter_score,output", (("obedience", 90, 0), ("intelligence", 50, 4), ("aggression", 2, 2)))
    def test_returns_expected_data_when_type_and_score_filtered(self, filter_type, filter_score, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(
            f"/experiment?type={filter_type}&score_over={filter_score}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type
            assert float(d["score"][:-1]) >= filter_score


class TestExperimentIDRoute_Task_4:
    """Tests for the /experiment/<id> route."""

    def test_returns_200_on_DELETE(self, test_api):
        """Checks that the route accepts a DELETE request."""

        res = test_api.delete("/experiment/3")

        assert res.status_code == 200

    def test_rejects_put_post_calls(self, test_api):
        """Checks that the route does not accept invalid types of HTTP request."""

        assert test_api.put("/experiment/3").status_code == 405
        assert test_api.post("/experiment/3").status_code == 405

    @pytest.mark.parametrize("id", (3000, 26, 35, 100, 9241))
    def test_rejects_invalid_id(self, id, test_api):
        """Checks that the route rejects an invalid ID."""

        print(f"/experiment/{id}")
        res = test_api.delete(f"/experiment/{id}")

        data = res.json

        assert res.status_code == 404
        assert isinstance(data, dict)

    def test_returns_data_in_expected_format(self, test_api):
        """Checks that the route returns JSON data in the required format."""

        res = test_api.delete("/experiment/3")

        data = res.json

        assert isinstance(data, dict)
        assert "experiment_id" in data
        assert "experiment_date" in data

    def test_returns_expected_data_types(self, test_api):
        """Checks that the route returns data with expected types/format."""

        res = test_api.delete("/experiment/2")

        data = res.json

        assert isinstance(data["experiment_id"], int)
        assert data["experiment_id"] == 2
        assert isinstance(data["experiment_date"], str)
        assert datetime.strptime(data["experiment_date"], "%Y-%m-%d")

    @pytest.mark.parametrize("id, exp_date", ((1, "2024-01-06"), (3, "2024-01-06"), (5, "2024-01-06"),
                                              (2, "2024-01-06"), (8, "2024-02-06")))
    def test_deletes_on_valid_id(self, id, exp_date, test_api, test_temp_conn):
        """Checks that the route deletes valid IDs."""

        res = test_api.delete(f"/experiment/{id}")
        data = res.json

        assert res.status_code == 200
        assert isinstance(data, dict)
        assert "experiment_id" in data
        assert "experiment_date" in data
        assert exp_date == data["experiment_date"]

        with test_temp_conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM experiment WHERE experiment_id = %s", [id])
            data = cur.fetchall()

        assert not data, "Failed to actually delete the row"


class TestExperimentPostRoute_Task_5:
    """Tests for the POST /experiment route."""

    def test_accepts_post_requests(self, test_api):
        """Checks that the route accepts POST requests."""
        
        res = test_api.post("/experiment")

        assert res.status_code != 405

    def test_rejects_requests_without_subject_id(self, new_experiment, test_api):
        """Checks that the route rejects requests without a subject_id in the body."""
        
        del new_experiment["subject_id"]
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Request missing key 'subject_id'."}

    def test_rejects_requests_without_experiment_type(self, new_experiment, test_api):
        """Checks that the route rejects requests without an experiment_type in the body."""
        
        del new_experiment["experiment_type"]
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Request missing key 'experiment_type'."}

    def test_rejects_requests_without_score(self, new_experiment, test_api):
        """Checks that the route rejects requests without a score in the body."""
        
        del new_experiment["score"]
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Request missing key 'score'."}

    @pytest.mark.parametrize("subject_id", ('three', 1.2, -4, 0.37, -34.1, 2.36))
    def test_rejects_invalid_subject_id(self, subject_id,
                                        new_experiment, test_api):
        """Checks that the route rejects invalid subject_id values."""

        new_experiment["subject_id"] = subject_id
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Invalid value for 'subject_id' parameter."}

    @pytest.mark.parametrize("experiment_type", ('intelligance', 34, 900, 'aggre', 'Ob'))
    def test_rejects_invalid_experiment_type(self, experiment_type,
                                             new_experiment, test_api):
        """Checks that the route rejects invalid experiment_type values."""
        
        new_experiment["experiment_type"] = experiment_type
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Invalid value for 'experiment_type' parameter."}

    @pytest.mark.parametrize("experiment_type", ("Intelligence", "oBeDiEnCe", "aGGressioN"))
    def test_accepts_case_insensitive_experiment_types(self, experiment_type,
                                                       new_experiment, test_api):
        """Checks that the route accepts valid experiment_type values regardless of case."""
        
        new_experiment["experiment_type"] = experiment_type
        res = test_api.post("/experiment", json=new_experiment)

        assert res.status_code == 201

    @pytest.mark.parametrize("experiment_type,score", (("Intelligence", 31), ("Obedience", 12),
                                                       ("aggression", 11), ("Aggression", -1),
                                                       ("Intelligence", "three"),
                                                       ("Intelligence", 4.1)))
    def test_rejects_invalid_scores(self, experiment_type, score,
                                    new_experiment, test_api):
        """Checks that the route rejects invalid score values."""
        new_experiment["experiment_type"] = experiment_type
        new_experiment["score"] = score
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Invalid value for 'score' parameter."}

    @pytest.mark.parametrize("experiment_date", ("21-2", "2040-02-30", "1990 06 03",
                                                 "3rd Jan 1817", "three", 17, 2.1))
    def test_rejects_invalid_experiment_date(self, experiment_date,
                                             new_experiment, test_api):
        """Checks that the route rejects invalid experiment_date values."""
        
        new_experiment["experiment_date"] = experiment_date
        res = test_api.post("/experiment", json=new_experiment)

        data = res.json

        assert res.status_code == 400
        assert data == {"error": "Invalid value for 'experiment_date' parameter."}


    def test_returns_201_on_success(self, new_experiment, test_api):
        """Checks that the route returns a 201 code on success."""
        
        res = test_api.post("/experiment", json=new_experiment)

        assert res.status_code == 201

    def test_returns_data_with_expected_keys(self, new_experiment, test_api):
        """Checks that the correct keys are returned in the JSON response."""
        
        new_experiment["subject_id"] = 4
        res = test_api.post("/experiment", json=new_experiment)
        data = res.json

        assert all([k in data for k in ('experiment_id', 'subject_id',
                                        'experiment_type_id', 'experiment_date',
                                        'score')])

    def test_returns_data_with_expected_types_and_format(self, new_experiment, test_api):
        """Checks that the data returned in the JSON response has the correct types/format."""
        
        new_experiment["subject_id"] = 1
        new_experiment["experiment_type"] = "aggression"
        new_experiment["score"] = 7
        res = test_api.post("/experiment", json=new_experiment)
        data = res.json

        for k,v in data.items():
            if k != "experiment_date":
                assert isinstance(v, int)
            else:
                assert isinstance(v, str)
                assert datetime.strptime(v, "%Y-%m-%d")

    def test_returns_expected_data(self, new_experiment, test_api):
        """Checks that the route returns appropriate data on success."""
        
        res = test_api.post("/experiment", json=new_experiment)

        assert res.json == {
        "experiment_id": 11,
        "subject_id": 3,
        "experiment_type_id": 2,
        "experiment_date": "2024-03-01",
        "score": 7
        }

    @pytest.mark.parametrize("experiment_type,score", (("intelligenCe", 15),
                                                       ("intelligenCe", 3),
                                                       ("intelligenCe", 27),
                                                       ("obedience", 8),
                                                       ("obedience", 0),
                                                       ("aggreSSion", 10),
                                                       ("aggression", 9)))
    def test_actually_stores_the_new_experiment(self, experiment_type, score,
                                                new_experiment, test_api, test_temp_conn):
        """Checks that the new experiment is added to the database."""
        
        del new_experiment["experiment_date"]
        new_experiment["experiment_type"] = experiment_type
        new_experiment["score"] = score
        res = test_api.post("/experiment", json=new_experiment)

        res_id = res.json["experiment_id"]

        with test_temp_conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM experiment WHERE experiment_id = %s", [res_id])
            data = cur.fetchall()

        assert data, "Failed to actually create the row"

    def test_defaults_to_current_date(self, new_experiment, test_api):
        """Checks that the experiment_date defaults to the current date if not provided."""
        
        del new_experiment["experiment_date"]
        res = test_api.post("/experiment", json=new_experiment)

        assert res.json == {
        "experiment_id": 11,
        "subject_id": 3,
        "experiment_type_id": 2,
        "experiment_date": datetime.now().strftime("%Y-%m-%d"),
        "score": 7
        }
