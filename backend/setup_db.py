from database import engine
import models

print("Iniciando a sincronização com o Supabase...")

# Este comando olha para o seu models.py e força a criação de todas as tabelas na nuvem
models.Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso! O banco está pronto.")