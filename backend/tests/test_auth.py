from fastapi.testclient import TestClient
# Precisamos voltar uma pasta (..) para importar o app do main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app  

client = TestClient(app)

def test_sincronizar_cadastro_email_invalido():
    payload_invalido = {
        "supabase_user_id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "email_sem_arroba.com", # E-mail propositalmente inválido
        "nome_completo": "Usuário Teste",
        "nome_escritorio": "Escritório Teste"
    }
    
    response = client.post("/api/v1/auth/sincronizar-cadastro", json=payload_invalido)
    
    # O FastAPI/Pydantic deve retornar 422 Unprocessable Entity
    assert response.status_code == 422
    assert "value is not a valid email address" in response.text