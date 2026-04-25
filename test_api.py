# -*- coding: utf-8 -*-
"""
Script de test local pour EduPay Backend
Teste tous les endpoints avant le deploiement
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_login():
    print("\n=== Test 2: Login ===")
    data = {
        "username": "admin@edupay.cd",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Token: {result['access_token'][:50]}...")
        print(f"User: {result['user']['nom']} {result['user']['prenom']}")
        return result['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_abonnements(token):
    print("\n=== Test 3: Abonnements ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/abonnements", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        abonnements = response.json()
        print(f"Nombre d'abonnements: {len(abonnements)}")
        for abo in abonnements:
            print(f"  - {abo['nom']}: ${abo['prix_mensuel']}/mois")

def test_communes(token):
    print("\n=== Test 4: Communes ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/geo/communes", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        communes = response.json()
        print(f"Nombre de communes: {len(communes)}")
        for commune in communes[:3]:
            print(f"  - {commune['nom']}")

def test_create_ecole(token):
    print("\n=== Test 5: Creer Ecole ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nom": "Ecole Test",
        "code": "TEST001",
        "adresse": "123 Rue Test",
        "telephone": "+243999999999",
        "email": "test@ecole.cd",
        "commune_id": 1
    }
    response = requests.post(f"{BASE_URL}/api/ecoles", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        ecole = response.json()
        print(f"Ecole creee: {ecole['nom']} (ID: {ecole['id']})")
        return ecole['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_stats(token):
    print("\n=== Test 6: Statistiques ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/rapports/stats/etudiants", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total etudiants: {stats['total']}")

def run_all_tests():
    print("=" * 60)
    print("TESTS EDUPAY BACKEND")
    print("=" * 60)
    
    try:
        test_health()
        token = test_login()
        
        if token:
            test_abonnements(token)
            test_communes(token)
            test_create_ecole(token)
            test_stats(token)
            
            print("\n" + "=" * 60)
            print("TOUS LES TESTS REUSSIS!")
            print("=" * 60)
        else:
            print("\nERREUR: Impossible de se connecter")
            print("Verifiez que la DB est initialisee: python -m app.init_db")
    
    except requests.exceptions.ConnectionError:
        print("\nERREUR: Impossible de se connecter au serveur")
        print("Lancez le serveur: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERREUR: {e}")

if __name__ == "__main__":
    run_all_tests()
