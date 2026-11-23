# app/materias.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import PLANES
from app.esquemas import Plan, PlanActualizar, PlanCrear

router = APIRouter(prefix="/planes", tags=["Planes"])


def obtener_plan(codigo: str) -> dict:
    """Devuelve el diccionario de la materia o lanza 404."""
    for materia in PLANES:
        if materia["codigo"] == codigo.upper():
            return materia
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe el plan con el codigo '{codigo}'",
    )


PlanEncontrado = Annotated[dict, Depends(obtener_plan)]

# app/materias.py — segunda parte: el CRUD


@router.get("")
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


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_plan(nueva: PlanCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in PLANES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El plan con el codigo '{nueva.codigo}' ya existe",
        )
    PLANES.append(nueva.model_dump())
    return PLANES[-1]

@router.get("/facturacion")
def facturacion (
    meses: Annotated[int, Query(ge=1,le=24)],
    nivel: Annotated[int | None, Query(ge=1, le=10)] = None,
) -> dict:
    filtro = (
        [p for p in PLANES if p["nivel"]== nivel]
        if nivel is not None
        else PLANES
    )
    if not filtro: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Error"
        ) 

    planes = len(filtro)
    suma_precios = sum(p["precio_mensual"] for p in filtro)
    precio_promedio = round(suma_precios/planes, 2)

    facturacion_base = suma_precios * meses
    descuento_aplicado = meses >= 12
    facturacion_estimada = round(facturacion_base * 0.15) if descuento_aplicado else facturacion_base

    con_entrenador = sum(1 for p in filtro if p["incluye_entrenador"])
    porcentaje_con_entrenador = round((con_entrenador/precio_promedio)*100, 1) 

    return {
        "planes" : planes,
        "meses": meses,
        "precio_promedio": precio_promedio,
        "facturacion_base": facturacion_base,
        "descuento_aplicado": descuento_aplicado,
        "facturacion_estimada": facturacion_estimada,
        "porcentaje_con_entrenador": porcentaje_con_entrenador
    }


@router.get("/{codigo}")
def ver_plan_codigo(plan: PlanEncontrado) -> dict:
    return plan


@router.put("/{codigo}")
def actualizar_materia(cambios: PlanActualizar, plan: PlanEncontrado) -> dict:
    plan.update(cambios.model_dump(exclude_unset=True))
    return plan


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(materia: PlanEncontrado) -> None:
    PLANES.remove(materia)