"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import extras
from psycopg2.extensions import connection

from database_functions import get_db_connection


app = Flask(__name__)

VALID_TYPES = ["intelligence", "obedience", "aggression"]

"""
For testing reasons; please ALWAYS use this connection. 
- Do not make another connection in your code
- Do not close this connection
"""
conn = get_db_connection("marine_experiments")


def get_all_subjects(conn: connection) -> dict:
    """Gets all stories from the database and returns it as a python dict."""
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("""
        SELECT 
            subject_id,
            subject_name,
            species_name,
            TO_CHAR(date_of_birth, 'YYYY-MM-DD') AS date_of_birth
        FROM subject
        INNER JOIN species ON subject.species_id = species.species_id;
    """)
    result = cur.fetchall()
    cur.close()
    return result

def get_experiments(conn, experiment_type=None, score_over=None):
    """Function to retrieve experiments."""
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    base_query = """
        SELECT
            e.experiment_id,
            s.subject_id,
            sp.species_name AS species,
            TO_CHAR(e.experiment_date, 'YYYY-MM-DD') AS experiment_date,
            et.type_name AS experiment_type,
            ROUND((e.score::NUMERIC / et.max_score) * 100, 2) || '%' AS score
        FROM
            experiment e
        INNER JOIN subject s ON e.subject_id = s.subject_id
        INNER JOIN species sp ON s.species_id = sp.species_id
        INNER JOIN experiment_type et ON e.experiment_type_id = et.experiment_type_id
    """

    filters = []
    params = []

    if experiment_type:
        filters.append(f"LOWER(et.type_name) = LOWER('{experiment_type}')")
        params.append(experiment_type)

    if score_over is not None:
        filters.append(f"ROUND((e.score::NUMERIC / et.max_score) * 100, 2) > {score_over}")
        params.append(score_over)

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY e.experiment_date DESC;"

    cur.execute(base_query)
    experiments = cur.fetchall()
    cur.close()
    return experiments


def delete_experiments(conn, experiment_id):
    """Function to delete an experiment."""
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    # Check if the experiment exists
    cur.execute("""
        SELECT
            experiment_id,
            TO_CHAR(experiment_date, 'YYYY-MM-DD') AS experiment_date
        FROM
            experiment
        WHERE
            experiment_id = %s
    """, (experiment_id,))
    experiment = cur.fetchone()

    if not experiment:
        cur.close()
        return jsonify({"error": f"Unable to locate experiment with ID {experiment_id}."}), 404

    # Delete the experiment
    cur.execute("""
        DELETE FROM experiment
        WHERE experiment_id = %s
        RETURNING experiment_id, TO_CHAR(experiment_date, 'YYYY-MM-DD') AS experiment_date
    """, (experiment_id,))
    deleted_experiment = cur.fetchone()
    conn.commit()
    cur.close()
    return deleted_experiment

@app.route("/subject", methods=["GET"])
def get_subjects_endpoint():
    """GET endpoint for subject."""
    # Sort subjects by date_of_birth in descending order
    subjects = get_all_subjects(conn)
    sorted_subjects = sorted(subjects,
                             key=lambda x: datetime.strptime(x['date_of_birth'], '%Y-%m-%d'),
                             reverse=True)
    return jsonify(sorted_subjects)


@app.route("/experiment", methods=["GET"])
def get_experiments_endpoint():
    """GET endpoint for experiment."""
    experiment_type = request.args.get("type")
    score_over = request.args.get("score_over")

    if experiment_type:
        if experiment_type.lower() not in VALID_TYPES:
            return jsonify({"error": "Invalid value for 'type' parameter"}), 400
        experiment_type = experiment_type.lower()

    if score_over:
        try:
            score_over = int(score_over)
            if not 0 <= score_over <= 100:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid value for 'score_over' parameter"}), 400

    experiments = get_experiments(conn, experiment_type, score_over)
    return jsonify(experiments)

@app.route("/experiment/<int:experiment_id>", methods=["DELETE"])
def delete_experiment_endpoint(experiment_id):
    """DELETE endpoint for experiment."""
    deleted_experiment = delete_experiments(conn, experiment_id)

    return deleted_experiment

@app.route("/experiment", methods=["POST"])
def create_experiment():
    """POST endpoint for experiment."""
    data = request.get_json()

    # Validate input data
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    subject_id = data.get("subject_id")
    print(subject_id)
    experiment_type = data.get("experiment_type")
    score = data.get('score')
    experiment_date = data.get("experiment_date", datetime.now().strftime("%Y-%m-%d"))

    if not subject_id:
        return jsonify({"error": "Request missing key 'subject_id'."}), 400
    if not isinstance(subject_id, int):
        return jsonify({"error": "Invalid value for 'subject_id' parameter."}), 400
    if subject_id <= 0:
        return jsonify({"error": "Invalid value for 'subject_id' parameter."}), 400

    if not experiment_type:
        return jsonify({"error": "Request missing key 'experiment_type'."}), 400
    if not isinstance(experiment_type, str):
        return jsonify({"error": "Invalid value for 'experiment_type' parameter."}), 400
    if experiment_type.lower() not in VALID_TYPES:
        return jsonify({"error": "Invalid value for 'experiment_type' parameter."}), 400

    if not score:
        return jsonify({"error": "Request missing key 'score'."}), 400
    if not isinstance(score, int) or score < 0:
        return jsonify({"error": "Invalid value for 'score' parameter."}), 400

    try:
        datetime.strptime(experiment_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid value for 'experiment_date' parameter."}), 400

    # Insert new experiment into the database
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    # Retrieve experiment_type_id from experiment_type
    cur.execute("""
        SELECT experiment_type_id
        FROM experiment_type
        WHERE LOWER(type_name) = LOWER(%s)
    """, (experiment_type,))
    experiment_type_record = cur.fetchone()
    if not experiment_type_record:
        cur.close()
        return jsonify({"error": "Invalid value for 'experiment_type' parameter"}), 400

    experiment_type_id = experiment_type_record['experiment_type_id']

    cur.execute("""
        INSERT INTO experiment (subject_id, experiment_type_id, score, experiment_date)
        VALUES (%s, %s, %s, %s)
        RETURNING experiment_id, subject_id, experiment_type_id, score, TO_CHAR(experiment_date, 'YYYY-MM-DD') AS experiment_date
    """, (subject_id, experiment_type_id, score, experiment_date))
    new_experiment = cur.fetchone()
    conn.commit()
    cur.close()

    return jsonify(new_experiment), 201

if __name__ == "__main__":

    app.run(port=8000, debug=True)
