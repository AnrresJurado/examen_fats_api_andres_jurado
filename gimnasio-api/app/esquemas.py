# app/esquemas.py
from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    precio_mensual: int = Field(ge=1, le=10)
    nivel: int = Field(ge=1, le=10)
    incluye_entrenador: bool = True


class PlanCrear(PlanBase):
    # Tres letras mayúsculas + tres dígitos: MAT101, PRG201...
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class PlanActualizar(BaseModel):
    # Todos opcionales: en un PUT parcial, lo que no se envía no se toca.
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    precio_mensual: int | None = Field(default=None, ge=1, le=10)
    nivel: int | None = Field(default=None, ge=1, le=10)
    incluye_entrenador: bool | None = None


class Plan(PlanCrear):
    """Lo que la API devuelve: los cinco campos completos."""