"""DTOs agregados para GET/PATCH perfil restaurante (esquema Tabi)."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from Domain.ModeloHorario import Modelo_Horario
from Domain.ModeloRangoPrecioRestaurante import Modelo_RangoPrecioRestaurante


class OwnerContact(BaseModel):
    nombre: str = ""
    apellido: str = ""
    correo: str = ""
    telefono: str = ""


class ProfileSection(BaseModel):
    nombre: str = ""
    razon_social: str = ""
    descripcion: str = ""
    sitio_web: str = ""
    redes_sociales: Dict[str, Any] = Field(default_factory=dict)
    restaurant_type: Optional[str] = None


class LocationSection(BaseModel):
    id_ubicacion: Optional[str] = None
    pais: str = ""
    departamento: str = ""
    ciudad: str = ""
    barrio: str = ""
    direccion: str = ""
    google_maps: str = ""


class ContactSection(BaseModel):
    telefono: str = ""
    owner: Optional[OwnerContact] = None


class OperationsSection(BaseModel):
    horarios_resumen: str = ""
    capacidad_asientos: Optional[int] = None
    numero_mesas: Optional[int] = None
    horarios: List[Modelo_Horario] = Field(default_factory=list)


class FeaturesSection(BaseModel):
    cuisine_types: List[str] = Field(default_factory=list)
    services_offered: List[str] = Field(default_factory=list)
    reservation_types: List[str] = Field(default_factory=list)


class CoverImage(BaseModel):
    id: str
    url: str = ""
    storage_key: str = ""
    orden: int = 0


class DocumentItem(BaseModel):
    id: str
    tipo: str = ""
    url: str = ""
    nombre_archivo: str = ""
    storage_key: str = ""
    mime_type: str = ""
    tamano_bytes: Optional[int] = None
    creado_en: Optional[datetime] = None


class MediaSection(BaseModel):
    logo_url: str = ""
    covers: List[CoverImage] = Field(default_factory=list)
    documents: List[DocumentItem] = Field(default_factory=list)


class SubscriptionSection(BaseModel):
    plan: Optional[str] = None
    ciclo_facturacion: Optional[str] = None
    estado: Optional[str] = None
    inicio_en: Optional[datetime] = None
    expira_en: Optional[datetime] = None


class OnboardingSection(BaseModel):
    paso: Optional[int] = None
    estado: Optional[str] = None
    pct: Optional[int] = None
    enviado_en: Optional[datetime] = None


class MetaSection(BaseModel):
    calificacion_promedio: Optional[float] = None
    calificacion_cantidad: int = 0
    rangos_precio: List[Modelo_RangoPrecioRestaurante] = Field(default_factory=list)
    activo: bool = True
    id_acceso: str = ""


class RestaurantMeResponse(BaseModel):
    id: str
    profile: ProfileSection
    location: LocationSection
    contact: ContactSection
    operations: OperationsSection
    features: FeaturesSection
    media: MediaSection
    subscription: Optional[SubscriptionSection] = None
    onboarding: OnboardingSection
    meta: MetaSection


# --- PATCH bodies (secciones opcionales) ---


class ProfilePatch(BaseModel):
    nombre: Optional[str] = None
    razon_social: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None
    redes_sociales: Optional[Dict[str, Any]] = None
    restaurant_type: Optional[str] = None


class LocationPatch(BaseModel):
    pais: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    barrio: Optional[str] = None
    direccion: Optional[str] = None
    google_maps: Optional[str] = None


class ContactPatch(BaseModel):
    telefono: Optional[str] = None


class OperationsPatch(BaseModel):
    opening_hours: Optional[time] = None
    closing_hours: Optional[time] = None
    horarios_resumen: Optional[str] = None
    capacidad_asientos: Optional[int] = Field(None, ge=0)
    numero_mesas: Optional[int] = Field(None, ge=0)
    horarios: Optional[List[Modelo_Horario]] = None


class FeaturesPatch(BaseModel):
    cuisine_types: Optional[List[str]] = None
    services_offered: Optional[List[str]] = None
    reservation_types: Optional[List[str]] = None


class RestaurantMePatch(BaseModel):
    profile: Optional[ProfilePatch] = None
    location: Optional[LocationPatch] = None
    contact: Optional[ContactPatch] = None
    operations: Optional[OperationsPatch] = None
    features: Optional[FeaturesPatch] = None
