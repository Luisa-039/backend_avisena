from typing import Annotated
from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.router.dependencies import authenticate_user
from app.schemas.auth import ResponseLoggin
from core.security import create_access_token
from core.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.crud import users as crud_users
from core.email import send_password_reset_email
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/token", response_model=ResponseLoggin)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Datos Incorrectos en email o password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data={"sub": str(user.id_usuario), "rol":user.id_rol}
    access_token = create_access_token(data)   

    return ResponseLoggin(
        user=user,
        access_token=access_token
    )

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita recuperación de contraseña.
    Genera un código de 6 dígitos y lo envía por email.
    """
    try:
        # Verificar si el usuario existe
        user = crud_users.get_user_by_email(db, request.email)
        
        # Por seguridad, siempre retornamos el mismo mensaje
        if user:
            # Generar y guardar código
            reset_token = crud_users.save_reset_token(db, request.email)
            
            if reset_token:
                # Enviar email con el código
                email_sent = send_password_reset_email(request.email, reset_token)
                
                if email_sent:
                    logger.info(f"Código de recuperación enviado a: {request.email}")
                else:
                    logger.warning(f"No se pudo enviar email a: {request.email}")
        return {
            "message": "Si el correo existe, recibirás un código de 6 dígitos para recuperar tu contraseña"
        }
    except Exception as e:
        logger.error(f"Error en forgot_password: {e}")
        raise HTTPException(status_code=500,detail="Error al procesar la solicitud")

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Restablece la contraseña usando el código de 6 dígitos recibido.
    """
    try:
        # Validar que el token sea de 6 dígitos
        if not request.token.isdigit() or len(request.token) != 6:
            raise HTTPException(
                status_code=400,
                detail="El código debe tener exactamente 6 dígitos"
            )
        
        # Validar longitud mínima de contraseña
        if len(request.new_password) < 9:
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe tener al menos 9 caracteres"
            )
        
        # Actualizar contraseña con el token
        success = crud_users.update_password_with_token(
            db, 
            request.token, 
            request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Código inválido o expirado"
            )
        
        return {
            "message": "Contraseña actualizada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset_password: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al restablecer la contraseña"
        )

