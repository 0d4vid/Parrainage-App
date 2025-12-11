import os
import random
import pandas as pd
from flask import Blueprint, jsonify, request, Response
from .database import db
from .models import Promotion, Etudiant, Binome
import io

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

@api_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    Exports the current list of pairings to a CSV file.
    """
    try:
        pairings = Binome.query.all()
        if not pairings:
            return jsonify({"message": "Aucun parrainage à exporter."}), 404

        # Prepare data for DataFrame
        data = []
        for p in pairings:
            data.append({
                'Parrain_Nom': p.parrain.nom,
                'Parrain_Prenom': p.parrain.prenom,
                'Parrain_Promotion': p.parrain.promotion.code,
                'Filleul_Nom': p.filleul.nom,
                'Filleul_Prenom': p.filleul.prenom,
                'Filleul_Promotion': p.filleul.promotion.code,
                'Date_Parrainage': p.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        
        # Create an in-memory CSV file
        output = io.StringIO()
        df.to_csv(output, index=False, sep=';') # Use semicolon for better Excel compatibility
        csv_data = output.getvalue()
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=parrainages.csv"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/draw', methods=['GET'])
def draw_pair():
    """
    Selects a random mentee and mentor pair based on the rules.
    """
    try:
        rules = get_sponsorship_rules()
        filleul_promo_codes = list(rules.values())

        potential_filleuls = db.session.query(Etudiant).join(Promotion).filter(
            Promotion.code.in_(filleul_promo_codes),
            Etudiant.est_parraine == False
        ).all()

        if not potential_filleuls:
            return jsonify({"message": "Tous les filleuls ont été parrainés !"}), 404

        filleul = random.choice(potential_filleuls)
        filleul_promo_code = filleul.promotion.code

        parrain_promo_code = next((p_code for p_code, f_code in rules.items() if f_code == filleul_promo_code), None)
        
        if not parrain_promo_code:
            return jsonify({"error": f"Aucune promotion de parrain correspondante trouvée pour {filleul_promo_code}"}), 500

        potential_parrains_prio1 = db.session.query(Etudiant).join(Promotion).filter(
            Promotion.code == parrain_promo_code,
            Etudiant.nb_filleuls == 0
        ).all()
        
        parrain = None
        if potential_parrains_prio1:
            parrain = random.choice(potential_parrains_prio1)
        else:
            potential_parrains_prio2 = db.session.query(Etudiant).join(Promotion).filter(
                Promotion.code == parrain_promo_code
            ).all()
            if potential_parrains_prio2:
                parrain = random.choice(potential_parrains_prio2)

        if not parrain:
            return jsonify({"error": f"Aucun parrain disponible dans la promotion {parrain_promo_code}"}), 404
            
        new_binome = Binome(filleul_id=filleul.id, parrain_id=parrain.id)
        
        filleul.est_parraine = True
        parrain.nb_filleuls += 1
        
        db.session.add(new_binome)
        db.session.commit()
        
        return jsonify(new_binome.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/import', methods=['POST'])
def import_students():
    try:
        Binome.query.delete()
        Etudiant.query.delete()
        db.session.commit()
        
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
            if not promo: continue
            
            student = Etudiant(
                nom=row['nom'],
                prenom=row['prenom'],
                matricule=row.get('matricule'),
                promo_id=promo.id
            )
            db.session.add(student)
            students_added += 1

        db.session.commit()
        
        return jsonify({ "message": f"Successfully imported {students_added} students." }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/reset', methods=['POST'])
def reset_sponsorship():
    try:
        Binome.query.delete()
        Etudiant.query.update({'est_parraine': False, 'nb_filleuls': 0})
        db.session.commit()
        return jsonify({"message": "Sponsorship reset successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    rules = get_sponsorship_rules()
    filleul_promos = list(rules.values())
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
    try:
        last_binome = Binome.query.order_by(Binome.timestamp.desc()).first()
        if not last_binome:
            return jsonify({"message": "Aucun parrainage à annuler."}), 404

        filleul = last_binome.filleul
        parrain = last_binome.parrain

        filleul.est_parraine = False
        if parrain.nb_filleuls > 0:
            parrain.nb_filleuls -= 1
        
        db.session.delete(last_binome)
        db.session.commit()

        return jsonify({"message": f"Le parrainage entre {parrain.prenom} et {filleul.prenom} a été annulé."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
