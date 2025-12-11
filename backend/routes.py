import os
import pandas as pd
from flask import Blueprint, jsonify, request
from .database import db
from .models import Promotion, Etudiant, Binome

# Create a Blueprint for API routes
api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

# --- Helper Functions ---
def get_sponsorship_rules():
    """Returns the sponsorship hierarchy."""
    return {
        'B2': 'B1',
        'B3': 'B2',
        'M1': 'B3',
        'M2': 'M1',
    }

# --- API Routes ---

@api_bp.route('/import', methods=['POST'])
def import_students():
    """
    Imports students from the default CSV file.
    This will clear all existing students and pairings before importing.
    """
    try:
        # Clear existing data
        Binome.query.delete()
        Etudiant.query.delete()
        db.session.commit()
        
        # Get the path to the CSV file
        project_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(project_dir, 'data', 'students.csv')

        if not os.path.exists(csv_path):
            return jsonify({"error": "students.csv not found"}), 404

        df = pd.read_csv(csv_path)
        
        # Basic validation
        required_columns = ['nom', 'prenom', 'promotion']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"CSV must contain the columns: {required_columns}"}), 400

        students_added = 0
        for _, row in df.iterrows():
            promo = Promotion.query.filter_by(code=row['promotion']).first()
            if not promo:
                # Optional: Handle students with unknown promotions, for now we skip them
                continue
            
            student = Etudiant(
                nom=row['nom'],
                prenom=row['prenom'],
                matricule=row.get('matricule'), # Use .get() for optional field
                promo_id=promo.id
            )
            db.session.add(student)
            students_added += 1

        db.session.commit()
        
        return jsonify({
            "message": f"Successfully imported {students_added} students.",
            "status": "success"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/reset', methods=['POST'])
def reset_sponsorship():
    """
    Resets the sponsorship by clearing all pairings and student states.
    This does NOT delete the students themselves, just their sponsorship status.
    """
    try:
        Binome.query.delete()
        
        # Reset all students to their initial state
        students = Etudiant.query.all()
        for student in students:
            student.est_parraine = False
            student.nb_filleuls = 0
        
        db.session.commit()
        
        return jsonify({"message": "Sponsorship reset successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Returns statistics about the remaining students.
    """
    rules = get_sponsorship_rules()
    
    # Promotions that are sponsored (filleuls)
    filleul_promos = list(rules.values())
    
    # Promotions that are sponsors (parrains)
    parrain_promos = list(rules.keys())

    remaining_filleuls = db.session.query(Etudiant).join(Promotion).filter(
        Promotion.code.in_(filleul_promos),
        Etudiant.est_parraine == False
    ).count()

    # A parrain is available if they are in a sponsoring promotion.
    # The algorithm will later decide if they can be picked based on nb_filleuls.
    available_parrains = db.session.query(Etudiant).join(Promotion).filter(
        Promotion.code.in_(parrain_promos)
    ).count()

    return jsonify({
        "remaining_filleuls": remaining_filleuls,
        "available_parrains": available_parrains, # This is the total pool of parrains
    }), 200
