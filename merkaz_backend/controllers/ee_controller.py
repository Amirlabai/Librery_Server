import os
import csv
from flask import Blueprint, jsonify, request, session, send_from_directory
import config.config as config  
from models.user_entity import User 
from datetime import datetime
from utils.logger_config import get_logger
from services.auth_service import AuthService

easter_egg_bp = Blueprint('api', __name__)
logger = get_logger(__name__)
PUZZLES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'merkaz_server', 'puzzles')
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'merkaz_server', 'data')


def get_csv_path(filename):
    return os.path.join(BASE_DATA_DIR, filename)

@easter_egg_bp.route("/secret-clue", methods=["GET"])
def easter_egg():
    return jsonify({
        "message": "You seem to be expert, ready for a challenge ? Write 753951"
    })


@easter_egg_bp.route("/activate-challenge", methods=["POST"])
def activate_challenge():
    """Activate the secret challenge for the currently logged-in user."""
    user_email = session.get('email')
    if not user_email:
        logger.warning("activate_challenge: No user in session")
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    user_code = (data.get("code") or "").strip()

    if not user_code:
        return jsonify({"message": "Missing activation code"}), 400

    if user_code != "753951":
        logger.info(f"activate_challenge: Wrong code attempt by {user_email}")
        return jsonify({"message": "Wrong code. Try harder."}), 400

    try:
        if not os.path.exists(config.AUTH_USER_DATABASE):
            logger.error(f"activate_challenge: Auth DB not found at {config.AUTH_USER_DATABASE}")
            return jsonify({"message": "User database not found"}), 500

        users = []
        fieldnames = None
        user_found = False
        already_activated = False

        # Read all users
        with open(config.AUTH_USER_DATABASE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            # Ensure 'challenge' field exists in header
            if fieldnames is None:
                fieldnames = []
            if 'challenge' not in fieldnames:
                fieldnames.append('challenge')

            for row in reader:
                # Ensure every row has a 'challenge' key (default empty)
                if 'challenge' not in row:
                    row['challenge'] = ''

                if row.get('email') == user_email:
                    user_found = True
                    if row.get('challenge') == 'activated':
                        already_activated = True
                    else:
                        row['challenge'] = 'activated'
                users.append(row)

        if not user_found:
            logger.warning(f"activate_challenge: User {user_email} not found in auth DB")
            return jsonify({"message": "User not found in database"}), 404

        if already_activated:
            logger.info(f"activate_challenge: User {user_email} already activated challenge")
            return jsonify({
                "status": "already_activated",
                "message": "Challenge is already activated."
            }), 200

        # Write updated users back
        # (fieldnames is guaranteed to include 'challenge' and not be None here)
        with open(config.AUTH_USER_DATABASE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)

        # Refresh session so frontend sees updated challenge status
        AuthService.refresh_session()
        logger.info(f"activate_challenge: Challenge activated for {user_email}")
        return jsonify({
            "status": "success",
            "message": "Challenge system activated! Welcome, agent."
        }), 200

    except Exception as e:
        logger.error(f"activate_challenge: Error updating user challenge status: {e}")
        return jsonify({"message": "Internal error while activating challenge"}), 500

@easter_egg_bp.route("/get-puzzle/<puzzle_name>", methods=["GET"])
def get_puzzle(puzzle_name):
    email = session.get('email')
    user = User.find_by_email(email)
    
    if not user or user.challenge != 'activated':
        return jsonify({"error": "Unauthorized"}), 403

    return send_from_directory(PUZZLES_DIR, f"{puzzle_name}.html")

@easter_egg_bp.route('/get-input/<int:puzzle_num>', methods=['GET'])
def get_input(puzzle_num):
    filename = f"input{puzzle_num}.txt"
    return send_from_directory(PUZZLES_DIR, filename)


@easter_egg_bp.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    puzzle_name = data.get('puzzle_name')
    user_answer = str(data.get('answer')).strip()
    user_email = session.get('email')

    if not user_email:
        return jsonify({"message": "Session expired, please login again"}), 401

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

    if user_answer == puzzle_data['correct_answer']:
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
                writer.writerow([user_email, puzzle_name, puzzle_data['points'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        return jsonify({"message": "Correct! Puzzle solved 🎉", "success": True}), 200
    
    return jsonify({"message": "Wrong answer, try again!", "success": False}), 400


@easter_egg_bp.route("/leaderboard-data", methods=["GET"])
def get_leaderboard_data():
    current_user_email = session.get('email')
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