from flask import Blueprint
from utils.logger_config import get_logger

easter_egg_bp = Blueprint('easter_egg', __name__)
logger = get_logger(__name__)

@easter_egg_bp.route("/secret-clue", methods=['GET'])
def easter_egg():
    logger.info("Easter egg route accessed")
    return {"message":"You seem to be expert, ready for a challenge ? Write 753951"}, 200
