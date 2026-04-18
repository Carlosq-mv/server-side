#!/usr/bin/python3
import json
import os
import sys

JSON_DIR = "/var/www/html/hw-json"


class CellBuilder:
    @staticmethod
    def hubs(company):
        """Build table cell for Hubs data"""
        hubs = company.get("Hubs")
        if hubs and "Hub" in hubs:
            hub_list = ", ".join(hubs["Hub"])
            return f"<td>{hub_list}</td>\n"
        return "<td></td>\n"

    @staticmethod
    def homepage(company):
        """Build table cell for HomePage link"""
        homepage = company.get("HomePage", "")
        if homepage and (
            homepage.startswith("http://") or homepage.startswith("https://")
        ):
            return f'<td><a href="{homepage}" target="_blank">HomePage</a></td>\n'
        return "<td>N/A</td>\n"

    @staticmethod
    def logo(company):
        """Build table cell for Logo"""
        logo = company.get("Logo")
        if logo:
            company_name = company.get("Company", "")
            return f'<td><img src="/hw-json/images/{logo}" alt="{company_name} Logo" width="50" /></td>\n'
        return "<td>No Logo Available</td>\n"

    @staticmethod
    def text(company, field):
        """Build text cell for any field"""
        return f"<td>{company.get(field, '')}</td>\n"


def send_error(message):
    """Send an error response with HTTP 500 status"""
    print("Status: 500")
    print("Content-Type: text/html")
    print()
    print(f"<p>Error: {message}</p>")
    sys.exit()


def send_success(html):
    """Send a success response with HTTP 200 status"""
    print("Content-Type: text/html")
    print()
    print(html)


def get_filename():
    """Get and validate the filename from the query string"""
    filename = os.environ.get("QUERY_STRING", "truckinglist.json")
    if filename != os.path.basename(filename):
        send_error("Invalid filename.")
    return filename


def read_json(filename):
    """Read and parse a JSON file from JSON_DIR"""
    filepath = os.path.join(JSON_DIR, filename)
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        send_error(f"File '{filename}' not found.")
    except json.JSONDecodeError:
        send_error("Invalid JSON format.")
    except Exception as e:
        send_error(str(e))


def validate_json(data):
    """Validate that the JSON has the correct trucking data structure"""
    if "Mainline" not in data or "Table" not in data.get("Mainline", {}):
        send_error("JSON structure is invalid or missing required fields.")

    table = data["Mainline"]["Table"]

    if "Header" not in table:
        send_error("Table header data is missing or invalid.")

    if "Row" not in table or not isinstance(table["Row"], list):
        send_error("Table row data is missing or invalid.")

    if len(table["Row"]) == 0:
        send_error("No trucking companies found in the JSON file.")

    return table


def build_table(table):
    """Build an HTML table from the trucking"""
    headers = table["Header"]["Data"]
    rows = table["Row"]

    html = "<table border='1'>\n"

    # Header row
    html += "<tr>\n"
    for h in headers:
        html += f"<th>{h}</th>\n"
    html += "</tr>\n"

    # Data rows
    for company in rows:
        html += "<tr>\n"
        html += CellBuilder.text(company, "Company")
        html += CellBuilder.text(company, "Services")
        html += CellBuilder.hubs(company)
        html += CellBuilder.text(company, "Revenue")
        html += CellBuilder.homepage(company)
        html += CellBuilder.logo(company)
        html += "</tr>\n"

    html += "</table>"
    return html


def main():
    filename = get_filename()
    data = read_json(filename)
    table = validate_json(data)
    html = build_table(table)
    send_success(html)


main()
