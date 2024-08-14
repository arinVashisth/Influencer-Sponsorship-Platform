# routes.py
from flask import Blueprint, request, jsonify
from tasks import export_campaigns_to_csv

bp = Blueprint('main', __name__)

@bp.route('/export-csv', methods=['POST'])
def export_csv():
    sponsor_id = request.json.get('sponsor_id')
    export_campaigns_to_csv.delay(sponsor_id)
    return jsonify({"message": "Export started"}), 202
