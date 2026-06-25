"""Servicio del wizard de onboarding."""

from __future__ import annotations

from typing import Any

from Application.schemas_onboarding import (
    STEP_MODELS,
    FullOnboardingDataResponse,
    OnboardingStartResponse,
    OnboardingStatusResponse,
    OnboardingStepResponse,
    StepBody,
)
from Infraestructure.InfraestructuraRestaurantePerfil import Infraestructura_RestaurantePerfil


class OnboardingService:
    def __init__(self) -> None:
        self._infra = Infraestructura_RestaurantePerfil()

    def start(self) -> OnboardingStartResponse:
        rid = self._infra.crear_restaurante_stub()
        return OnboardingStartResponse(restaurant_id=str(rid), status="draft")

    def parse_step_body(self, step: int, body: dict[str, Any]) -> StepBody:
        model = STEP_MODELS.get(step)
        if model is None:
            raise ValueError(f"Paso inválido: {step}")
        return model.model_validate(body)

    def persist_step(self, step: int, body: StepBody, restaurant_id: int) -> OnboardingStepResponse:
        handlers = {
            1: self._infra.aplicar_paso_1,
            2: self._infra.aplicar_paso_2,
            3: self._infra.aplicar_paso_3,
            4: self._infra.aplicar_paso_4,
            5: self._infra.aplicar_paso_5,
            6: self._infra.aplicar_paso_6,
            7: self._infra.aplicar_paso_7,
        }
        handler = handlers.get(step)
        if handler is None:
            raise ValueError(f"Paso inválido: {step}")
        handler(restaurant_id, body)
        status = self._infra.obtener_estado_onboarding(restaurant_id)
        return OnboardingStepResponse(
            restaurant_id=str(restaurant_id),
            step=status["step"],
            status=status["status"],
            pct=status["pct"],
        )

    def get_status(self, restaurant_id: int) -> OnboardingStatusResponse:
        status = self._infra.obtener_estado_onboarding(restaurant_id)
        return OnboardingStatusResponse(**status)

    def submit(self, restaurant_id: int) -> OnboardingStatusResponse:
        self._infra.submit_onboarding(restaurant_id)
        return self.get_status(restaurant_id)

    def get_full_admin(self, restaurant_id: int) -> FullOnboardingDataResponse:
        return self._infra.obtener_perfil_completo(restaurant_id)


onboarding_service = OnboardingService()
