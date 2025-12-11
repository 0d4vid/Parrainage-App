from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import db
import datetime

# According to specs.md, we should have used ENUM for statut, but it's not standard in all SQL DBs.
# We will use simple booleans and integers instead as described in the MLD.

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False) # e.g., 'B1', 'B2'
    
    etudiants: Mapped[list["Etudiant"]] = relationship(back_populates="promotion")

class Etudiant(db.Model):
    __tablename__ = 'etudiants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matricule: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    
    promo_id: Mapped[int] = mapped_column(ForeignKey('promotions.id'), nullable=False)
    promotion: Mapped["Promotion"] = relationship(back_populates="etudiants")
    
    nb_filleuls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    est_parraine: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship to define the student as a mentor (parrain)
    filleuls: Mapped[list["Binome"]] = relationship(foreign_keys='Binome.parrain_id', back_populates='parrain')

    # Relationship to define the student as a mentee (filleul)
    parrain_rel: Mapped["Binome"] = relationship(foreign_keys='Binome.filleul_id', back_populates='filleul')


class Binome(db.Model):
    __tablename__ = 'binomes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    filleul_id: Mapped[int] = mapped_column(ForeignKey('etudiants.id'), unique=True, nullable=False)
    parrain_id: Mapped[int] = mapped_column(ForeignKey('etudiants.id'), nullable=False)
    
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    filleul: Mapped["Etudiant"] = relationship(foreign_keys=[filleul_id], back_populates='parrain_rel')
    parrain: Mapped["Etudiant"] = relationship(foreign_keys=[parrain_id], back_populates='filleuls')

    def to_dict(self):
        return {
            "filleul": {
                "nom": self.filleul.nom,
                "prenom": self.filleul.prenom,
                "promotion": self.filleul.promotion.code
            },
            "parrain": {
                "nom": self.parrain.nom,
                "prenom": self.parrain.prenom,
                "promotion": self.parrain.promotion.code
            }
        }

