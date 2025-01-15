from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Candidate, Election, Vote
from app import db, login_manager

routes_bp = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@routes_bp.route('/')
def home():
    return jsonify("Hello, Flask!")

@routes_bp.route('/users')
def get_users():
    try:
        users = User.query.all()
        return jsonify({"users": [user.to_dict() for user in users]}), 200
    except Exception as e:
        return jsonify(str(e)), 400

@routes_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    try:
        existing_user = User.query.filter_by(cnp=data['cnp']).first()
        if existing_user:
            return jsonify("CNP already in use"), 400

        new_user = User(
            email=data['email'],
            cnp=data['cnp'],
            hashed_password=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify("User registered successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 400

@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    cnp = data['cnp']
    password = data['password']
    
    try:
        # Find the user
        user = User.query.filter_by(cnp=cnp).first()
        
        # Check if password is correct
        if user and check_password_hash(user.hashed_password, password):
            login_user(user)
            return jsonify("Login successful"), 200
        else:
            return jsonify("Invalid credentials"), 401
    except Exception as e:
        return jsonify(str(e)), 400

@routes_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify("Logout successful"), 200
    except Exception as e:
        return jsonify(str(e)), 400
    

@routes_bp.route('/vote', methods=['POST'])
@login_required
def vote():
    data = request.json
    try:
        election = Election.query.filter_by(id=data['election_id']).first()
        if election is None:
            return jsonify("Inexistent election"), 400

        candidate = Candidate.query.filter_by(id=data['candidate_id']).filter_by(election_id=election.id).first()
        if candidate is None:
            return jsonify("Inexistent candidate"), 400

        existing_vote = Vote.query.filter_by(user_uuid=current_user.uuid).filter_by(election_id=election.id).first()
        if existing_vote:
            return jsonify("User already voted in this election"), 400

        new_vote = Vote(
            user_uuid = current_user.uuid,
            candidate_id = candidate.id,
            election_id = election.id,
            timestamp = data['timestamp']
        )

        db.session.add(new_vote)
        db.session.commit()

        return jsonify("Vote successful"), 201
    except Exception as e:
        return jsonify(str(e)), 400

@routes_bp.route('/vote/status/<int:e_id>', methods=['GET'])
@login_required
def get_voted_status(e_id):
    try:
        election = Election.query.filter_by(id=e_id).first()
        if election is None:
            return jsonify("Inexistent election"), 400
        vote = Vote.query.filter_by(user_uuid=current_user.uuid).filter_by(election_id=e_id).first()
        vote_status = {}
        if vote:
            vote_status['status'] = 'YES'
        else:
            vote_status['status'] = 'NO'
        return jsonify(vote_status), 200
    except Exception as e:
        return jsonify(str(e)), 500    
        

@routes_bp.route('/vote/history', methods=['GET'])
@login_required
def get_vote_history():
    try:
        votes = Vote.query.filter_by(user_uuid=current_user.uuid).all()

        vote_history = []
        for vote in votes:
            election = Election.query.filter_by(id=vote.election_id).first()
            candidate = Candidate.query.filter_by(id=vote.candidate_id).first()
            vote_history_entry = {
                'election_name': election.name,
                'candidate_name': candidate.name,
                'candidate_party': candidate.party,
                'timestamp': vote.timestamp
            }
            vote_history.append(vote_history_entry)
        
        return jsonify(vote_history), 200
    except Exception as e:
        return jsonify(str(e)), 500
    

@routes_bp.route('/election', methods=['GET'])
def get_elections():
    try:
        elections = Election.query.all()
        return jsonify([election.to_dict() for election in elections]), 200
    except Exception as e:
        return jsonify(str(e)), 500
    
@routes_bp.route('/election', methods=['POST'])
@login_required
def add_election():
    if current_user.cnp != "0000000000000":
        return jsonify("User not authorized for this operation"), 401
    
    data = request.json
    try:
        existing_election = Election.query.filter_by(name=data['name']).first()
        if existing_election:
            return jsonify("An election with this name already exists"), 400
        
        new_election = Election(
            name=data['name']
        )

        db.session.add(new_election)
        db.session.commit()
        return jsonify("Election added successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500
    
@routes_bp.route('/election/<int:e_id>', methods=['DELETE'])
@login_required
def delete_election(e_id):
    if current_user.cnp != "0000000000000":
        return jsonify("User not authorized for this operation"), 401
    
    try:
        election = Election.query.filter_by(id=e_id).first()

        if election is None:
            return jsonify("Inexistent election"), 400
        
        db.session.delete(election)
        db.session.commit()
        
        return jsonify("Election deleted successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@routes_bp.route('/candidate/<int:e_id>', methods=['GET'])
def get_candidates_by_election_id(e_id):
    try:
        candidates = Candidate.query.filter_by(election_id=e_id).all()
        return jsonify([candidate.to_dict() for candidate in candidates]), 200
    except Exception as e:
        return jsonify(str(e)), 500
    
@routes_bp.route('/candidate', methods=['POST'])
@login_required
def add_candidate():
    if current_user.cnp != "0000000000000":
        return jsonify("User not authorized for this operation"), 401
    
    data = request.json
    try:
        existing_candidate = Candidate.query.filter_by(name=data['name']).first()
        if existing_candidate:
            return jsonify("A candidate with this name already exists"), 400
        
        new_candidate = Candidate(
            election_id=data['election_id'],
            name=data['name'],
            party=data['party'],
            slogan=data.get('slogan')
        )

        db.session.add(new_candidate)
        db.session.commit()
        
        return jsonify("Candidate added successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500
    
@routes_bp.route('/candidate/<int:c_id>/<int:e_id>', methods=['DELETE'])
@login_required
def delete_candidate(c_id, e_id):
    if current_user.cnp != "0000000000000":
        return jsonify("User not authorized for this operation"), 401
    
    try:
        candidate = Candidate.query.filter_by(id=c_id).filter_by(election_id=e_id)

        if candidate is None:
            return jsonify("Inexistent candidate"), 400
        
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify("Candidate deleted successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500