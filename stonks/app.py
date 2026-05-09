from flask import Flask, jsonify, render_template
import json

import tiingo
import database
import utils
from database import CacheStatus


app = Flask(__name__)

database.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stock/<string:ticker>", methods=["GET"])
def stock(ticker):
    # get data from cache
    status, cache_data = database.get_cache_results(ticker)
    if status == CacheStatus.HIT and cache_data is not None:
        res = jsonify(
            {
                "company": json.loads(cache_data["company_json"]),
                "summary": json.loads(cache_data["stock_json"]),
            }
        )
        res.headers["X-Cache"] = "HIT"
        database.add_search(ticker)
        return res, 200

    # get data from Tiingo if cache MISS or STALE
    try:
        company_data, summary_data = tiingo.fetch_stock(ticker)
    except tiingo.TiingoError as e:
        return jsonify({"error": e.message}), e.status

    # get data ready to be returned
    company_payload = utils.company(company_data)
    summary_payload = utils.summary(summary_data)

    # convert data into json string for caching
    company_json_str = json.dumps(company_payload)
    stock_json_str = json.dumps(summary_payload)

    if status == CacheStatus.STALE:
        database.update_cache(ticker, company_json_str, stock_json_str)
    elif status == CacheStatus.MISS:
        database.insert_cache(ticker, company_json_str, stock_json_str)

    response = jsonify({"company": company_payload, "summary": summary_payload})
    response.headers["X-Cache"] = "MISS"
    database.add_search(ticker)
    return response, 200


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(database.get_recent_searches(10)), 200


if __name__ == "__main__":
    app.run(debug=True, port=8080)
