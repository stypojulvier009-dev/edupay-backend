from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .middleware import InternetCheckMiddleware
from .routers import (
    auth, abonnements, geolocalisation, ecoles, classes,
    parents, etudiants, frais, echeanciers, paiements,
    notifications, rapports, audit,
    admin_utilisateurs, presences, journal_cours, examens, admin_cahier
)

app = FastAPI(
    title="EduPay API - Oasis des Juniors",
    description="API complete de gestion scolaire et paiements - Complexe Scolaire Oasis des Juniors",
    version="2.0.0",
)

@app.on_event("startup")
def startup():
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"DB init warning: {e}")

# Middleware verification Internet (OBLIGATOIRE)
app.add_middleware(InternetCheckMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers de base
app.include_router(auth.router)
app.include_router(abonnements.router)
app.include_router(geolocalisation.router)
app.include_router(ecoles.router)
app.include_router(classes.router)
app.include_router(parents.router)
app.include_router(etudiants.router)
app.include_router(frais.router)
app.include_router(echeanciers.router)
app.include_router(paiements.router)
app.include_router(notifications.router)
app.include_router(rapports.router)
app.include_router(audit.router)

# Routers admin (fonctionnalites avancees)
app.include_router(admin_utilisateurs.router)
app.include_router(presences.router)
app.include_router(journal_cours.router)
app.include_router(examens.router)
app.include_router(admin_cahier.router)

@app.get("/")
def root():
    return {
        "message": "EduPay API - Oasis des Juniors",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "20+ moyens de paiement RDC",
            "Gestion utilisateurs",
            "Presences et absences",
            "Journal de classe",
            "Cours et emploi du temps",
            "Examens et notes",
            "Cahier de paiements",
            "Exports CSV",
            "Verification Internet obligatoire"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
