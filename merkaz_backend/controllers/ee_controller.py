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
    user_email = session.get('email') 
    if not user_email:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    user_code = data.get("code")

    if user_code == "753951":
        users = []
        updated = False
        
        with open(config.AUTH_USER_DATABASE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['email'] == user_email:
                    row['challenge'] = 'activated'
                    updated = True
                users.append(row)

        if updated:
            with open(config.AUTH_USER_DATABASE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)
            

            AuthService.refresh_session()
            return jsonify({
                "status": "success",
                "message": "Challenge system activated! Welcome, agent."
            }), 200
        
        return jsonify({"message": "User not found in database"}), 404

    return jsonify({"message": "Wrong code. Try harder."}), 400

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