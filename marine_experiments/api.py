"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql, extras
from psycopg2.extensions import connection

from database_functions import get_db_connection


app = Flask(__name__)

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

@app.route("/subject", methods=["GET"])
def get_subjects():
    # Sort subjects by date_of_birth in descending order
    subjects = get_all_subjects(conn)
    sorted_subjects = sorted(subjects, key=lambda x: datetime.strptime(x['date_of_birth'], '%Y-%m-%d'), reverse=True)
    return jsonify(sorted_subjects)


@app.route("/experiment", methods=["GET", "POST"])
def get_experiments():
    pass

@app.route("/stories/<int:story_id>", methods=["PATCH", "DELETE"])
def delete_experiment():
    pass

@app.route("/", methods=["GET"])
def index():
    return "Hello World"

if __name__ == "__main__":

    app.run(port=8000, debug=True)
