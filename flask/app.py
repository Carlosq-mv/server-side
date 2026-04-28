import json
import os

from flask import Flask, abort, jsonify, request

app = Flask(__name__)

JSON_DIR = "/var/www/html/hw-json"
REQUIRED_FIELDS = {"Company", "Services", "Hubs", "Revenue", "HomePage", "Logo"}


class TruckCRUD:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_file(self):
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            abort(500, description="JSON file missing")
        except json.JSONDecodeError:
            abort(500, description="Corrupted JSON data")

    def write_to_file(self, data):
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=2)
        except FileNotFoundError:
            abort(500, description="JSON file missing")
        except Exception:
            abort(500, description="Failed to save data")

    def get_rows(self, data):
        try:
            return data["Mainline"]["Table"]["Row"]
        except (KeyError, TypeError):
            abort(500, description="Corrupted JSON data")

    def is_duplicate(self, rows, company_name):
        for row in rows:
            if row.get("Company") == company_name:
                return True
        return False


crud = TruckCRUD(os.path.join(JSON_DIR, "truckinglist.json"))


# Root route with helpful description
@app.route("/")
def index():
    return """
        <h2>Trucking Company API</h2>
        <p>This is a RESTful API for managing trucking company data.</p>
        <p>Available endpoints:</p>
        <ul>
            <li>GET /companies</li>
            <li>GET /companies/&lt;name&gt;</li>
            <li>POST /companies</li>
            <li>PUT /companies/&lt;name&gt;</li>
            <li>DELETE /companies/&lt;name&gt;</li>
        </ul>
    """


# GET all trucking companies
@app.route("/companies", methods=["GET"])
def get_all_companies():
    # Load JSON file from disk
    # Get data from JSON file
    data = crud.read_file()
    rows = crud.get_rows(data)

    companies = []
    for row in rows:
        companies.append(row.get("Company"))

    return jsonify(companies), 200


# GET a specific company by name
@app.route("/companies/<string:name>", methods=["GET"])
def get_company(name):
    # Load JSON and return data for the company if it exists
    # If not found, return 404 error
    data = crud.read_file()
    rows = crud.get_rows(data)
    for row in rows:
        if row.get("Company") == name:
            return jsonify(row), 200

    abort(404, description="Company not found")


# POST a new trucking company
@app.route("/companies", methods=["POST"])
def add_company():
    # Read JSON from request body
    # Validate required fields
    # Add the new company to the JSON data
    # Save the updated data back to the file
    new_company = request.get_json(silent=True)
    if not new_company:
        abort(400, description="Request body must be valid JSON")

    # make sure payload is dictionary so it won't crash on .keys()
    if not isinstance(new_company, dict):
        abort(400, description="Request body must be a JSON object")

    # make sure no extra fields are added
    extra_fields = new_company.keys() - REQUIRED_FIELDS
    if extra_fields:
        abort(400, description="Extra fields present")

    # make sure all required fields are present
    missing_fields = REQUIRED_FIELDS - new_company.keys()
    if missing_fields:
        abort(400, description="Invalid or missing fields")

    # make sure none of the fields are empty:
    for field in new_company.keys():
        if new_company[field] in [[], {}, None, ""]:
            abort(400, description="One or more empty fields")

    # make sure that "Hubs" is a dictionary
    if not isinstance(new_company.get("Hubs"), dict):
        abort(400, description="Invalid JSON structure")

    data = crud.read_file()
    rows = crud.get_rows(data)

    if crud.is_duplicate(rows, new_company.get("Company")):
        abort(400, description="Company already exists")

    rows.append(new_company)
    crud.write_to_file(data)

    return jsonify(new_company), 201


# PUT to update an existing company
@app.route("/companies/<string:name>", methods=["PUT"])
def update_company(name):
    # Read update data from request
    # Find and update the specified company
    # Save the updated data back to the file
    updated_company = request.get_json(silent=True)
    if not updated_company:
        abort(400, description="Request body must be valid JSON")

    if not isinstance(updated_company, dict):
        abort(400, description="Request body must be a JSON object")

    # make sure that provided fields can't be empty
    for key in updated_company:
        if updated_company[key] in (None, "", [], {}):
            abort(400, description="Empty fields present")

    # make sure that if "Hubs" is provided, it must be a dict
    if "Hubs" in updated_company and not isinstance(updated_company["Hubs"], dict):
        abort(400, description="'Hubs' must be a JSON object")

    data = crud.read_file()
    rows = crud.get_rows(data)

    for row in rows:
        if row.get("Company", "N/A") == name:
            row.update(updated_company)
            crud.write_to_file(data)

            return jsonify(row), 200

    abort(404, description="Company not found")


# DELETE a trucking company
@app.route("/companies/<string:name>", methods=["DELETE"])
def delete_company(name):
    # Locate and delete the specified company
    # Save the updated data back to the file
    data = crud.read_file()
    rows = crud.get_rows(data)

    for company in rows:
        if company.get("Company") == name:
            rows.remove(company)
            crud.write_to_file(data)
            return jsonify({"message": f"{name} deleted"}), 200

    abort(404, description="Company not found")


# Error handlers (optional to implement in their section)
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": error.description}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": error.description}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
