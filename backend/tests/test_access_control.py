import os
import sys

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from access_control import has_management_access, require_management_access
from comentarios import CommentCreate


def test_admin_e_gerente_possuem_acesso_de_gestao():
    assert has_management_access({"role": "admin"}) is True
    assert has_management_access({"role": "gerente"}) is True
    assert has_management_access({"role": "colaborador"}) is False


def test_colaborador_nao_recebe_permissao_de_gestao():
    with pytest.raises(HTTPException) as error:
        require_management_access({"role": "colaborador"})

    assert error.value.status_code == 403


def test_comentario_remove_espacos_e_rejeita_conteudo_vazio():
    from uuid import uuid4

    payload = CommentCreate(client_id=uuid4(), content="  Observação interna  ")
    assert payload.content == "Observação interna"

    with pytest.raises(ValidationError):
        CommentCreate(client_id=uuid4(), content="   ")
