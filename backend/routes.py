import os
import random
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

@api_bp.route('/draw', methods=['GET'])
def draw_pair():
    """
    Selects a random mentee and mentor pair based on the rules.
    """
    try:
        rules = get_sponsorship_rules()
        filleul_promo_codes = list(rules.values())

        # 1. Select a random Filleul
        potential_filleuls = db.session.query(Etudiant).join(Promotion).filter(
            Promotion.code.in_(filleul_promo_codes),
            Etudiant.est_parraine == False
        ).all()

        if not potential_filleuls:
            return jsonify({"message": "Tous les filleuls ont été parrainés !"}), 404

        filleul = random.choice(potential_filleuls)
        filleul_promo_code = filleul.promotion.code

        # 2. Determine the corresponding Parrain promotion
        parrain_promo_code = None
        for parrain_code, sponsored_code in rules.items():
            if sponsored_code == filleul_promo_code:
                parrain_promo_code = parrain_code
                break
        
        if not parrain_promo_code:
            return jsonify({"error": f"Aucune promotion de parrain correspondante trouvée pour {filleul_promo_code}"}), 500

        # 3. Select a Parrain from the corresponding promotion
        # Priority 1: Parrains with 0 filleuls
        potential_parrains_prio1 = db.session.query(Etudiant).join(Promotion).filter(
            Promotion.code == parrain_promo_code,
            Etudiant.nb_filleuls == 0
        ).all()
        
        parrain = None
        if potential_parrains_prio1:
            parrain = random.choice(potential_parrains_prio1)
        else:
            # Priority 2: Parrains who already have filleuls (imbalance case)
            potential_parrains_prio2 = db.session.query(Etudiant).join(Promotion).filter(
                Promotion.code == parrain_promo_code
            ).all()
            if potential_parrains_prio2:
                # In a more complex scenario, we might want to choose the one with the fewest filleuls
                parrain = random.choice(potential_parrains_prio2)

        if not parrain:
            return jsonify({"error": f"Aucun parrain disponible dans la promotion {parrain_promo_code}"}), 404
            
        # 4. Create the pairing
        new_binome = Binome(filleul_id=filleul.id, parrain_id=parrain.id)
        
        # 5. Update student statuses
        filleul.est_parraine = True
        parrain.nb_filleuls += 1
        
        db.session.add(new_binome)
        db.session.commit()
        
        # 6. Return the result
        return jsonify(new_binome.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/import', methods=['POST'])
def import_students():
    """
    Imports students from the default CSV file.
    This will clear all existing students and pairings before importing.
    """
    try:
        # Clear existing data by cascading deletes (or manually)
        Binome.query.delete()
        Etudiant.query.delete()
        
        # Reset autoincrement counters if using SQLite by deleting and recreating tables
        # For simplicity, we just delete content. A more robust solution might be needed.
        db.session.commit() # Commit deletions before adding new data
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(project_dir, 'data', 'students.csv')

        if not os.path.exists(csv_path):
            return jsonify({"error": "students.csv not found"}), 404

        df = pd.read_csv(csv_path)
        required_columns = ['nom', 'prenom', 'promotion']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"CSV must contain the columns: {required_columns}"}), 400

        students_added = 0
        for _, row in df.iterrows():
            promo = Promotion.query.filter_by(code=row['promotion']).first()
            if not promo:
                continue
            
            student = Etudiant(
                nom=row['nom'],
                prenom=row['prenom'],
                matricule=row.get('matricule'),
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
    """
    try:
        Binome.query.delete()
        
        Etudiant.query.update({
            'est_parraine': False,
            'nb_filleuls': 0
        })
        
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
    filleul_promos = list(rules.values())
    
    # We need to count students in sponsoring promos that are not fully "used up" if we want to be precise,
    # but for a general counter, counting all potential sponsors is fine.
    parrain_promos = list(rules.keys())

    remaining_filleuls = db.session.query(Etudiant).join(Promotion).filter(
        Promotion.code.in_(filleul_promos),
        Etudiant.est_parraine == False
    ).count()

    available_parrains = db.session.query(Etudiant).join(Promotion).filter(
        Promotion.code.in_(parrain_promos)
    ).count()

    return jsonify({
        "remaining_filleuls": remaining_filleuls,
        "available_parrains": available_parrains
    }), 200

@api_bp.route('/undo', methods=['POST'])
def undo_last_pairing():
    """
    Finds and deletes the most recent pairing.
    """
    try:
        last_binome = Binome.query.order_by(Binome.timestamp.desc()).first()

        if not last_binome:
            return jsonify({"message": "Aucun parrainage à annuler."}), 404

        filleul = last_binome.filleul
        parrain = last_binome.parrain

        # Revert student states
        filleul.est_parraine = False
        if parrain.nb_filleuls > 0:
            parrain.nb_filleuls -= 1
        
        db.session.delete(last_binome)
        db.session.commit()

        return jsonify({"message": f"Le parrainage entre {parrain.prenom} et {filleul.prenom} a été annulé."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500