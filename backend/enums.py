from enum import Enum


class TaskStatus(str, Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_CLIENTE = "aguardando_cliente"
    CONCLUIDA = "concluida"
