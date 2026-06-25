from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field, model_validator

from Application.auth_context import permissions_for_principal, resolve_role_name_for_user
from Application.deps import Principal, get_principal, role_for_principal
from Application.rate_limit import limiter
from Application.role_permissions import default_roles_permission_matrix, is_restaurant_admin

from Application.jwt_tokens import create_access_token
from Application.passwords import prepare_password_for_store, verify_password
from Domain.ModeloRestaurante import Modelo_Restaurante
from Domain.ModeloUsuario import Modelo_Usuario
from Infraestructure.InfraestructuraRestaurante import Infraestructura_Restaurante
from Infraestructure.InfraestructuraRestaurantePerfil import Infraestructura_RestaurantePerfil
from Infraestructure.InfraestructuraRol import Infraestructura_Rol
from Infraestructure.InfraestructuraSuperUsuario import Infraestructura_Super_Usuario
from Infraestructure.InfraestructuraUsuario import Infraestructura_Usuario

router = APIRouter()


class LoginRequest(BaseModel):
    correo: str = Field(..., min_length=1)
    contrasena: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    kind: Literal["user", "super"]
    restaurant_id: Optional[str] = None


class AuthMeResponse(BaseModel):
    user_id: str
    email: str
    kind: Literal["user", "super"]
    restaurant_id: Optional[str] = None
    nombre: str = ""
    apellido: str = ""
    rol: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    is_admin: bool = False


def _token_for_user(user: Modelo_Usuario, restaurant_id: Optional[str]) -> str:
    rol_nombre = resolve_role_name_for_user(user.Correo, str(user.ID_Key))
    return create_access_token(
        {
            "sub": str(user.ID_Key),
            "email": user.Correo,
            "kind": "user",
            "restaurant_id": restaurant_id,
            "rol": rol_nombre,
        }
    )


@router.get("/me", response_model=AuthMeResponse, summary="Sesión actual")
async def auth_me(p: Principal = Depends(get_principal)) -> AuthMeResponse:
    if p.kind == "super":
        rows = Infraestructura_Super_Usuario().consultar_super_usuario_id(p.user_id)
        if not rows or "Fallido" in (rows[0].resultado or ""):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Superusuario no encontrado",
            )
        sup = rows[0]
        return AuthMeResponse(
            user_id=p.user_id,
            email=p.email,
            kind="super",
            restaurant_id=None,
            nombre=sup.Nombre,
            apellido=sup.Apellido,
            rol="super",
            permissions=permissions_for_principal("super", "super"),
            is_admin=True,
        )

    user = Infraestructura_Usuario().buscar_por_correo(p.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    rol_nombre: Optional[str] = None
    if (user.ID_Rol or "").strip():
        rol_rows = Infraestructura_Rol().consultar_rol_id(user.ID_Rol)
        if rol_rows and "Fallido" not in (rol_rows[0].resultado or ""):
            rol_nombre = rol_rows[0].Nombre
    rol_nombre = role_for_principal(p) or rol_nombre
    return AuthMeResponse(
        user_id=p.user_id,
        email=p.email,
        kind="user",
        restaurant_id=p.restaurant_id,
        nombre=user.Nombre,
        apellido=user.Apellido,
        rol=rol_nombre,
        permissions=permissions_for_principal("user", rol_nombre),
        is_admin=is_restaurant_admin(rol_nombre),
    )


@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión")
@limiter.limit("30/minute")
async def login(request: Request, body: LoginRequest) -> LoginResponse:
    correo = body.correo.strip()
    infra_u = Infraestructura_Usuario()
    user = infra_u.buscar_por_correo(correo)
    if user is not None and verify_password(body.contrasena, user.Contrasena):
        rid = (user.ID_Restaurante or "").strip() or None
        token = _token_for_user(user, rid)
        return LoginResponse(access_token=token, kind="user", restaurant_id=rid)

    infra_s = Infraestructura_Super_Usuario()
    sup = infra_s.buscar_por_correo(correo)
    if sup is not None and verify_password(body.contrasena, sup.Contrasena):
        token = create_access_token(
            {
                "sub": str(sup.ID_Key),
                "email": sup.Correo,
                "kind": "super",
                "restaurant_id": None,
            }
        )
        return LoginResponse(access_token=token, kind="super", restaurant_id=None)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
    )


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    owner_name: str = Field(..., min_length=1)
    phone: str = ""
    restaurant_id: Optional[str] = None


@router.post(
    "/register",
    response_model=LoginResponse,
    summary="Registro del dueño tras onboarding (auto-login)",
    description=(
        "Crea el usuario Propietario enlazado a un restaurante en borrador. "
        "Puede enviar `restaurant_id` en el body o el header `X-Restaurant-Id`."
    ),
)
@limiter.limit("15/minute")
async def register_owner(
    request: Request,
    body: RegisterRequest,
    x_restaurant_id: Optional[str] = Header(None, alias="X-Restaurant-Id"),
) -> LoginResponse:
    rid_str = (body.restaurant_id or x_restaurant_id or "").strip()
    if not rid_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indica restaurant_id en el body o header X-Restaurant-Id",
        )
    try:
        rid = int(rid_str)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="restaurant_id inválido",
        )

    infra_perfil = Infraestructura_RestaurantePerfil()
    if not infra_perfil.restaurante_en_borrador(rid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurante no encontrado o no está en borrador",
        )

    correo = body.email.strip()
    infra_u = Infraestructura_Usuario()
    if infra_u.buscar_por_correo(correo) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo",
        )

    infra_rol = Infraestructura_Rol()
    id_rol = infra_rol.obtener_id_por_nombre("Propietario") or ""
    if not id_rol:
        id_rol = infra_rol.obtener_id_por_nombre("Administrador") or ""
    if not id_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontró rol Propietario ni Administrador en BD",
        )

    parts = body.owner_name.strip().split(None, 1)
    nombre = parts[0]
    apellido = parts[1] if len(parts) > 1 else ""

    modelo_usuario = Modelo_Usuario(
        ID_Key="",
        Nombre=nombre,
        Apellido=apellido,
        Telefono=body.phone.strip(),
        Correo=correo,
        Contrasena=prepare_password_for_store(body.password),
        Tipo_Documento="",
        Numero_Documento="",
        ID_Rol=id_rol,
        ID_Restaurante=str(rid),
        resultado="",
    )
    out_u = infra_u.ingresar_usuario(modelo_usuario)
    if "Fallido" in (out_u.resultado or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=out_u.resultado)

    token = _token_for_user(out_u, str(rid))
    return LoginResponse(access_token=token, kind="user", restaurant_id=str(rid))


class RolesPermissionMatrixResponse(BaseModel):
    roles: dict[str, list[str]]


@router.get(
    "/roles/permissions",
    response_model=RolesPermissionMatrixResponse,
    summary="Matriz de permisos por rol (referencia para el front)",
)
async def roles_permission_matrix() -> RolesPermissionMatrixResponse:
    return RolesPermissionMatrixResponse(roles=default_roles_permission_matrix())


class EmpleadoRegistroRequest(BaseModel):
    """Datos del primer empleado (administrador del local)."""

    Nombre: str = Field(..., min_length=1)
    Apellido: str = ""
    Telefono: str = ""
    Correo: str = Field(..., min_length=3)
    Contrasena: str = Field(..., min_length=1)
    Tipo_Documento: str = ""
    Numero_Documento: str = ""
    ID_Rol: str = Field(
        "",
        description="ID del rol en BD; si está vacío se usa el rol 'Administrador'.",
    )


class RegistroRestauranteRequest(BaseModel):
    """Alta pública: restaurante y, opcionalmente, primer empleado."""

    id_acceso: str = ""
    Nombre: str = Field(..., min_length=1, description="Nombre del restaurante")
    Direccion: str = ""
    Telefono: str = ""
    Calificacion: int = 0
    Horarios: str = ""
    Imagen_destacada: str = ""
    Google_maps: str = ""
    Rango_de_precios: int = Field(1, ge=1, le=4, description="1=$ … 4=$$$$")
    ID_Ubicacion: str = ""
    ID_categorias: str = ""
    ID_Etiqueta: str = ""
    empleado: Optional[EmpleadoRegistroRequest] = Field(
        None,
        description="Si se envía, se crea el usuario enlazado al restaurante (requiere id_acceso único).",
    )

    @model_validator(mode="after")
    def _empleado_requiere_id_acceso(self) -> "RegistroRestauranteRequest":
        if self.empleado is not None and not (self.id_acceso or "").strip():
            raise ValueError("id_acceso es obligatorio al registrar un empleado")
        return self


class RegistroRestauranteResponse(BaseModel):
    restaurante: Modelo_Restaurante
    empleado: Optional[Modelo_Usuario] = None


def _modelo_restaurante_desde_registro(body: RegistroRestauranteRequest) -> Modelo_Restaurante:
    return Modelo_Restaurante(
        ID_Key="",
        id_acceso=body.id_acceso.strip(),
        Nombre=body.Nombre.strip(),
        Direccion=body.Direccion.strip(),
        Telefono=body.Telefono.strip(),
        Calificacion=body.Calificacion,
        Horarios=body.Horarios.strip(),
        Imagen_destacada=body.Imagen_destacada.strip(),
        Google_maps=body.Google_maps.strip(),
        Rango_de_precios=body.Rango_de_precios,
        ID_Ubicacion=body.ID_Ubicacion.strip(),
        ID_categorias=body.ID_categorias.strip(),
        ID_Etiqueta=body.ID_Etiqueta.strip(),
        resultado="",
    )


def _dummy_restaurante() -> Modelo_Restaurante:
    return Modelo_Restaurante(
        ID_Key="",
        id_acceso="",
        Nombre="",
        Direccion="",
        Telefono="",
        Calificacion=0,
        Horarios="",
        Imagen_destacada="",
        Google_maps="",
        Rango_de_precios=0,
        ID_Ubicacion="",
        ID_categorias="",
        ID_Etiqueta="",
        resultado="",
    )


@router.post(
    "/registro/restaurante",
    response_model=RegistroRestauranteResponse,
    summary="Registro público de restaurante (y empleado opcional)",
    description=(
        "No requiere token. Crea el restaurante; si el cuerpo incluye `empleado`, "
        "crea el usuario con `id_restaurante` asignado. Requiere `id_acceso` único cuando hay empleado."
    ),
)
@limiter.limit("15/minute")
async def registro_restaurante(
    request: Request, body: RegistroRestauranteRequest
) -> RegistroRestauranteResponse:
    infra_r = Infraestructura_Restaurante()
    infra_u = Infraestructura_Usuario()
    infra_rol = Infraestructura_Rol()

    if body.empleado is not None:
        correo = body.empleado.Correo.strip()
        if infra_u.buscar_por_correo(correo) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo",
            )

    modelo = _modelo_restaurante_desde_registro(body)
    out = infra_r.ingresar_restaurante(modelo)
    if "Fallido" in (out.resultado or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=out.resultado)

    if body.empleado is None:
        return RegistroRestauranteResponse(restaurante=out, empleado=None)

    rid_str = infra_r.obtener_id_por_id_acceso(body.id_acceso.strip())
    if not rid_str:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Restaurante creado pero no se pudo obtener su id; revisa id_acceso en BD",
        )

    emp = body.empleado
    id_rol = (emp.ID_Rol or "").strip()
    if not id_rol:
        id_rol = infra_rol.obtener_id_por_nombre("Administrador") or ""
    if not id_rol:
        infra_r.retirar_restaurante(rid_str, _dummy_restaurante())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontró el rol 'Administrador' en la base de datos",
        )

    modelo_usuario = Modelo_Usuario(
        ID_Key="",
        Nombre=emp.Nombre.strip(),
        Apellido=emp.Apellido.strip(),
        Telefono=emp.Telefono.strip(),
        Correo=emp.Correo.strip(),
        Contrasena=emp.Contrasena,
        Tipo_Documento=emp.Tipo_Documento.strip(),
        Numero_Documento=emp.Numero_Documento.strip(),
        ID_Rol=id_rol,
        ID_Restaurante=rid_str,
        resultado="",
    )
    out_u = infra_u.ingresar_usuario(modelo_usuario)
    if "Fallido" in (out_u.resultado or ""):
        infra_r.retirar_restaurante(rid_str, _dummy_restaurante())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=out_u.resultado)

    return RegistroRestauranteResponse(restaurante=out, empleado=out_u)
