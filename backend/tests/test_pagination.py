import inspect
from types import SimpleNamespace

import clientes
import documentos
import membros
import obrigacoes
import pytest
from main import app
from pagination import paginate


class FakeQuery:
    def __init__(self, items):
        self.items = items
        self.applied_offset = None
        self.applied_limit = None

    def count(self):
        return len(self.items)

    def order_by(self, *_values):
        return self

    def offset(self, value):
        self.applied_offset = value
        return self

    def limit(self, value):
        self.applied_limit = value
        return self

    def all(self):
        start = self.applied_offset or 0
        end = start + (self.applied_limit or len(self.items))
        return self.items[start:end]


def test_paginate_retorna_metadados_e_somente_a_pagina_solicitada():
    query = FakeQuery([SimpleNamespace(id=index) for index in range(45)])

    result = paginate(query, page=2, page_size=20)

    assert [item.id for item in result["items"]] == list(range(20, 40))
    assert result == {
        "items": result["items"],
        "page": 2,
        "page_size": 20,
        "total": 45,
        "pages": 3,
        "summary": None,
    }


def test_paginate_retorna_zero_paginas_quando_nao_ha_resultados():
    result = paginate(FakeQuery([]), page=1, page_size=20)

    assert result == {
        "items": [],
        "page": 1,
        "page_size": 20,
        "total": 0,
        "pages": 0,
        "summary": None,
    }


def test_paginate_inclui_resumo_calculado_no_escopo_autorizado():
    result = paginate(
        FakeQuery([SimpleNamespace(id=1)]),
        page=1,
        page_size=20,
        summary={"total": 8, "concluidas": 3},
    )

    assert result["summary"] == {"total": 8, "concluidas": 3}


@pytest.mark.parametrize(
    "list_endpoint",
    [
        clientes.listar_clientes,
        documentos.listar_documentos,
        obrigacoes.listar_obrigacoes,
        membros.listar_membros,
    ],
)
def test_listagens_principais_exigem_paginacao_limitada(list_endpoint):
    parameters = inspect.signature(list_endpoint).parameters

    assert "page" in parameters
    assert "page_size" in parameters


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/clientes",
        "/api/v1/documentos",
        "/api/v1/obrigacoes",
        "/api/v1/membros",
    ],
)
def test_openapi_documenta_limite_maximo_e_resposta_paginada(path):
    operation = app.openapi()["paths"][path]["get"]
    parameters = {item["name"]: item["schema"] for item in operation["parameters"]}
    response_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]

    assert parameters["page"]["minimum"] == 1
    assert parameters["page_size"]["maximum"] == 100
    assert response_schema["$ref"].startswith(
        "#/components/schemas/PaginatedResponse_"
    )


@pytest.mark.parametrize(
    ("path", "filters"),
    [
        ("/api/v1/clientes", {"search", "natureza", "responsible_profile_id", "unassigned"}),
        ("/api/v1/documentos", {"search", "client_id", "categoria"}),
        ("/api/v1/obrigacoes", {"search", "client_id", "assigned_to", "task_status"}),
        ("/api/v1/membros", {"search", "role"}),
    ],
)
def test_openapi_documenta_filtros_das_listagens(path, filters):
    operation = app.openapi()["paths"][path]["get"]
    parameter_names = {item["name"] for item in operation["parameters"]}

    assert filters <= parameter_names
