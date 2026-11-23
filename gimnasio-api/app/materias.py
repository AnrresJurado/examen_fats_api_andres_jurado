# app/materias.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import PLANES
from app.esquemas import Plan, PlanActualizar, PlanCrear

router = APIRouter(prefix="/planes", tags=["planes"])


def obtener_plan(codigo: str) -> dict:
    """Devuelve el diccionario de la materia o lanza 404."""
    for materia in PLANES:
        if materia["codigo"] == codigo.upper():
            return materia
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la materia '{codigo}'",
    )


PlanEncontrado = Annotated[dict, Depends(obtener_plan)]

# app/materias.py — segunda parte: el CRUD


@router.get("", response_model=list[Plan])
def listar_planes(
    nivel: Annotated[int | None, Query(ge=1, le=10)] = None,
    incluye_entrenador: bool = False,
) -> list[dict]:
    resultado = PLANES
    if nivel is not None:
        resultado = [m for m in resultado if m["nivel"] == nivel]
    if incluye_entrenador:
        resultado = [m for m in resultado if m["incluye_entrenador"]]
    return resultado


@router.post("", response_model=Plan, status_code=status.HTTP_201_CREATED)
def crear_plan(nueva: PlanCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in PLANES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El plan con el codigo '{nueva.codigo}' ya existe",
        )
    PLANES.append(nueva.model_dump())
    return PLANES[-1]


@router.get("/{codigo}", response_model=Plan)
def ver_plan_codigo(plan: PlanEncontrado) -> dict:
    return plan


@router.put("/{codigo}", response_model=Plan)
def actualizar_materia(cambios: PlanActualizar, plan: PlanEncontrado) -> dict:
    plan.update(cambios.model_dump(exclude_unset=True))
    return plan


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(materia: PlanEncontrado) -> None:
    PLANES.remove(materia)