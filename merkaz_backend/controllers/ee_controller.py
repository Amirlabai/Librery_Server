import os
import re
import csv
from flask import Blueprint, jsonify, request, send_from_directory
import config.config as config
from models.user_entity import User
from datetime import datetime
from utils.logger_config import get_logger
from services.auth_service import AuthService
from repositories.user_repository import UserRepository

easter_egg_bp = Blueprint('api', __name__)
logger = get_logger(__name__)
PUZZLES_DIR = config.PUZZLES_DIR
BASE_DATA_DIR = config.BASE_DATA_DIR
_PUZZLE_NAME_RE = re.compile(r'^puzzle\d+$', re.IGNORECASE)


def get_csv_path(filename):
    return os.path.join(BASE_DATA_DIR, filename)


def _require_activated_challenge():
    email = AuthService.get_current_email()
    if not email:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    user = User.find_by_email(email)
    if not user or user.challenge != 'activated':
        return None, (jsonify({"error": "Unauthorized"}), 403)
    return user, None


@easter_egg_bp.route("/secret-clue", methods=["GET"])
def easter_egg():
    return jsonify({
        "message": "You seem to be expert, ready for a challenge ? Write the activation code."
    })


@easter_egg_bp.route("/activate-challenge", methods=["POST"])
def activate_challenge():
    """Activate the secret challenge for the currently logged-in user."""
    user_email = AuthService.get_current_email()
    if not user_email:
        logger.warning("activate_challenge: No user in session")
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    user_code = (data.get("code") or "").strip()
    expected = getattr(config, "CHALLENGE_ACTIVATION_CODE", "753951")

    if not user_code:
        return jsonify({"message": "Missing activation code"}), 400

    if user_code != expected:
        logger.info(f"activate_challenge: Wrong code attempt by {user_email}")
        return jsonify({"message": "Wrong code. Try harder."}), 400

    try:
        status, err = UserRepository.set_challenge(user_email, 'activated')
        if status == 'not_found':
            return jsonify({"message": "User not found in database"}), 404
        if status == 'already_activated':
            return jsonify({
                "status": "already_activated",
                "message": "Challenge is already activated."
            }), 200

        user_data, refresh_err = AuthService.refresh_session()
        if refresh_err:
            logger.error(f"activate_challenge: Error refreshing session: {refresh_err}")
            return jsonify({"message": "Error refreshing session"}), 500

        logger.info(f"activate_challenge: Challenge activated for {user_email}")
        return jsonify({
            "status": "success",
            "message": "Challenge system activated! Welcome, agent.",
            "challenge": user_data.get("challenge") if user_data else "activated",
        }), 200

    except Exception as e:
        logger.error(f"activate_challenge: Error updating user challenge status: {e}")
        return jsonify({"message": "Internal error while activating challenge"}), 500


@easter_egg_bp.route("/get-puzzle/<puzzle_name>", methods=["GET"])
def get_puzzle(puzzle_name):
    if not _PUZZLE_NAME_RE.fullmatch(puzzle_name or ''):
        return jsonify({"error": "Invalid puzzle name"}), 400
    user, err_resp = _require_activated_challenge()
    if err_resp:
        return err_resp
    logger.info(f"get_puzzle: Serving puzzle {puzzle_name} to user {user.email}")
    return send_from_directory(PUZZLES_DIR, f"{puzzle_name}.html")


@easter_egg_bp.route('/get-input/<int:puzzle_num>', methods=['GET'])
def get_input(puzzle_num):
    user, err_resp = _require_activated_challenge()
    if err_resp:
        return err_resp
    if puzzle_num < 1 or puzzle_num > 99:
        return jsonify({"error": "Invalid puzzle number"}), 400
    filename = f"input{puzzle_num}.txt"
    return send_from_directory(PUZZLES_DIR, filename)


@easter_egg_bp.route('/submit-answer', methods=['POST'])
def submit_answer():
    # UX-only: not a security boundary (spoofable User-Agent).
    if is_mobile_request():
        return jsonify({"error": "Mobile devices not supported"}), 403

    try:
        data = request.get_json(silent=True) or {}
        puzzle_name = data.get('puzzle_name')
        if puzzle_name is None:
            return jsonify({"message": "error"}), 400
        user_answer = data.get('answer')
        if user_answer is None:
            return jsonify({"message": "Answer is required"}), 400
        if not isinstance(user_answer, str):
            user_answer = str(user_answer)
        user_answer = user_answer.strip().casefold()

        user, err_resp = _require_activated_challenge()
        if err_resp:
            return err_resp
        user_email = user.email

        puzzle_data = None
        puzzles_path = get_csv_path('puzzles.csv')

        with open(puzzles_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            for row in reader:
                if row['name'] == puzzle_name:
                    puzzle_data = row
                    break

        if not puzzle_data:
            return jsonify({"message": "Puzzle not found"}), 404

        correct = (puzzle_data.get('correct_answer') or '').strip().casefold()
        if user_answer == correct:
            solutions_path = get_csv_path('user_solutions.csv')

            if not os.path.exists(solutions_path):
                with open(solutions_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['email', 'puzzle_name', 'points', 'timestamp'])

            already_solved = False
            with open(solutions_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['email'] == user_email and row['puzzle_name'] == puzzle_name:
                        already_solved = True
                        break

            if not already_solved:
                with open(solutions_path, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        user_email, puzzle_name, puzzle_data['points'],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])

            return jsonify({"message": "Correct! Puzzle solved", "success": True}), 200

        return jsonify({"message": "Wrong answer, try again!", "success": False}), 400
    except Exception as e:
        logger.error(f"submit_answer: Error submitting answer: {e}")
        return jsonify({"message": "Internal error while submitting answer"}), 500


@easter_egg_bp.route("/leaderboard-data", methods=["GET"])
def get_leaderboard_data():
    if is_mobile_request():
        return jsonify({"error": "Mobile devices not supported"}), 403

    current_user_email = AuthService.get_current_email()
    if not current_user_email:
        return jsonify({"error": "Unauthorized"}), 401

    solutions_path = get_csv_path('user_solutions.csv')
    user_points = {}
    solved_puzzles = []

    try:
        with open(solutions_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email')
                points_raw = row.get('points')
                if not points_raw:
                    continue
                try:
                    points = int(points_raw)
                except ValueError:
                    continue
                user_points[email] = user_points.get(email, 0) + points
                if email == current_user_email:
                    solved_puzzles.append(row['puzzle_name'].strip().lower())
    except FileNotFoundError:
        pass

    sorted_leaderboard = sorted(
        [{"name": email.split('@')[0], "points": pts} for email, pts in user_points.items()],
        key=lambda x: x['points'],
        reverse=True
    )
    for i, entry in enumerate(sorted_leaderboard):
        entry['rank'] = i + 1

    return jsonify({
        "leaderboard": sorted_leaderboard,
        "user_solved": solved_puzzles
    }), 200


def is_mobile_request():
    ua = request.headers.get('User-Agent', '').lower()
    mobile_indicators = [
        'android', 'iphone', 'ipad', 'ipod',
        'mobile', 'opera mini', 'windows phone'
    ]
    return any(m in ua for m in mobile_indicators)
