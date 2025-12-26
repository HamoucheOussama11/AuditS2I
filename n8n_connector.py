import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def send_to_n8n(data_payload, webhook_url=None):
    """
    Sends the data payload to the n8n webhook.

    Args:
        data_payload (dict): The data to send (converted to JSON).
        webhook_url (str, optional): The webhook URL. Defaults to env var N8N_WEBHOOK_URL.

    Returns:
        dict: The JSON response from n8n or an error dictionary.
    """
    url = webhook_url or os.getenv("N8N_WEBHOOK_URL")

    if not url:
        # Mock response for testing when no URL is provided
        return [
            {
                "status": "Critique",
                "risk_score": 12,
                "pillar": "Infrastructure",
                "frequency": 3,
                "gravity": 4,
                "frap_text": "1. CONTEXTE :\nUn audit de sécurité automatisé a été réalisé sur l'infrastructure cloud de production.\n\n2. CONSTAT (Preuves) :\nUn bucket S3 nommé 'prod-data-backup' est actuellement non chiffré. Les logs d'accès montrent des tentatives de lecture anonymes.\n\n3. CONSÉQUENCE :\nRisque élevé de fuite de données confidentielles (PII, secrets industriels), pouvant entraîner des sanctions RGPD et une perte de réputation.\n\n4. RECOMMANDATION :\nActiver le chiffrement côté serveur (SSE-S3 ou SSE-KMS) sur le bucket immédiatement et restreindre les politiques d'accès public.\n\n5. NORME VIOLÉE :\nISO/IEC 27001:2013 - Contrôle A.10.1.1 (Politique de cryptographie)."
            },
            {
                "status": "Majeur",
                "risk_score": 9,
                "pillar": "MLOps",
                "frequency": 5,
                "gravity": 5,
                "frap_text": "1. CONTEXTE :\nSurveillance continue des performances des modèles de machine learning en production.\n\n2. CONSTAT (Preuves) :\nLe modèle 'Fraud_Detection_v2' présente une dérive (drift) significative des données d'entrée par rapport au jeu d'entraînement de référence (Score KS > 0.15).\n\n3. CONSÉQUENCE :\nDégradation de la précision des prédictions, augmentant les faux négatifs dans la détection de fraude.\n\n4. RECOMMANDATION :\nDéclencher un réentraînement immédiat du modèle avec les données des 30 derniers jours et mettre à jour le pipeline de validation.\n\n5. NORME VIOLÉE :\nCOBIT 2019 (EDM04 - Optimisation des Ressources)."
            },
            {
                "status": "Majeur",
                "risk_score": 8,
                "pillar": "Sécurité API",
                "frequency": 2,
                "gravity": 3,
                "frap_text": "1. CONTEXTE :\nAnalyse des configurations d'authentification des endpoints API exposés.\n\n2. CONSTAT (Preuves) :\nL'endpoint '/api/v1/admin' permet l'authentification par simple clé API sans rotation forcée ni MFA.\n\n3. CONSÉQUENCE :\nPotentiel d'accès non autorisé élevé en cas de fuite de la clé API. Manque de traçabilité forte des actions administratives.\n\n4. RECOMMANDATION :\nImplémenter l'authentification OAuth2 avec MFA pour tous les endpoints administratifs.\n\n5. NORME VIOLÉE :\nISO/IEC 25010 (Efficacité de performance - Comportement temporel)."
            }
        ]

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data_payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"⚠ Connection to AI Agent failed: {str(e)}"
        }
    except json.JSONDecodeError:
        return {
            "error": True,
            "message": "⚠ Invalid JSON response from AI Agent."
        }
