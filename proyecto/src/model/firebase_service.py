import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH
import uuid  # Para generar un ID único por sesión

# Inicialización Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_tuning_data(session_id, tuning_data):
    doc_ref = db.collection("tunings").document(session_id)
    doc_ref.set(tuning_data)

def get_tuning_data(user_id):
    db = firestore.client()
    tuning_ref = db.collection('tunings').where('user_id', '==', user_id)
    tuning_docs = tuning_ref.stream()

    tuning_data = []
    for doc in tuning_docs:
        doc_data = doc.to_dict()
        doc_data["id"] = doc.id  
        print(f"ID: {doc.id}, Data: {doc_data}") 
        tuning_data.append(doc_data)

    return tuning_data

def update_tuning_data(doc_id, new_data):
    db = firestore.client()
    doc_ref = db.collection("tunings").document(doc_id)

    # Verificar si el documento existe antes de actualizar
    if doc_ref.get().exists:
        doc_ref.update(new_data)
        print(f"Afinación con ID {doc_id} actualizada.")
    else:
        print(f"No se encontró ninguna afinación con ID {doc_id}.")


def delete_tuning_data(doc_id):
    """Elimina un documento en Firestore usando su ID."""
    db = firestore.client()
    doc_ref = db.collection("tunings").document(doc_id)

    # Verificar si el documento existe antes de eliminar
    if doc_ref.get().exists:
        doc_ref.delete()
        print(f"Afinación con ID {doc_id} eliminada.")
    else:
        print(f"No se encontró ninguna afinación con ID {doc_id}.")