"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql, extras
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
    print(base_query)

    cur.execute(base_query)
    experiments = cur.fetchall()
    cur.close()
    return experiments

@app.route("/subject", methods=["GET"])
def get_subjects_endpoint():
    # Sort subjects by date_of_birth in descending order
    subjects = get_all_subjects(conn)
    sorted_subjects = sorted(subjects, key=lambda x: datetime.strptime(x['date_of_birth'], '%Y-%m-%d'), reverse=True)
    return jsonify(sorted_subjects)


@app.route("/experiment", methods=["GET", "POST"])
def get_experiments_endpoint():
    experiment_type = request.args.get('type')
    score_over = request.args.get('score_over')

    if experiment_type:
        if experiment_type.lower() not in VALID_TYPES:
            return jsonify({"error": "Invalid value for 'type' parameter"}), 400
        experiment_type = experiment_type.lower()

    if score_over:
        try:
            score_over = int(score_over)
            if not (0 <= score_over <= 100):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid value for 'score_over' parameter"}), 400

    experiments = get_experiments(conn, experiment_type, score_over)
    return jsonify(experiments)

@app.route("/stories/<int:story_id>", methods=["PATCH", "DELETE"])
def delete_experiments_endpoint():
    pass

@app.route("/", methods=["GET"])
def index():
    return "Hello World"

if __name__ == "__main__":

    app.run(port=8000, debug=True)
