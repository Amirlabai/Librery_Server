from flask import Blueprint, jsonify
from utils.logger_config import get_logger

easter_egg_bp = Blueprint('api', __name__)
logger = get_logger(__name__)

@easter_egg_bp.route("/secret-clue", methods=["GET"])
def easter_egg():
    return jsonify({
        "message": "You seem to be expert, ready for a challenge ? Write 753951"
    })

