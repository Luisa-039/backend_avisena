import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(email: str, token: str) -> bool:
    """
    Envía email con código de 6 dígitos para recuperación de contraseña.
    
    Args:
        email: Email del usuario
        token: Código de 6 dígitos
        
    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Código de Recuperación - AVISENA"
        message["From"] = settings.EMAILS_FROM_EMAIL
        message["To"] = email
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    background-color: #f4f4f4;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #2c5f2d;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #2c5f2d;
                    padding-bottom: 20px;
                }}
                .logo {{
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .code-box {{
                    background: linear-gradient(135deg, #2c5f2d 0%, #234d24 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 30px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .code {{
                    font-size: 48px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                    margin: 10px 0;
                }}
                .footer {{ 
                    margin-top: 30px; 
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px; 
                    color: #666; 
                    text-align: center;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .content {{
                    padding: 20px 0;
                }}
                .info-box {{
                    background-color: #e7f3ff;
                    border-left: 4px solid #2196F3;
                    padding: 12px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🐓 AVISENA</div>
                    <h2 style="margin: 0; color: #2c5f2d;">Recuperación de Contraseña</h2>
                </div>
                
                <div class="content">
                    <p>Hola,</p>
                    <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en AVISENA.</p>
                    
                    <div class="code-box">
                        <p style="margin: 0; font-size: 16px;">Tu código de verificación es:</p>
                        <div class="code">{token}</div>
                        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Ingresa este código en la aplicación</p>
                    </div>
                    
                    <div class="info-box">
                        <strong>📱 Cómo usar tu código:</strong>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Ve a la página de recuperación de contraseña</li>
                            <li>Ingresa el código de 6 dígitos</li>
                            <li>Establece tu nueva contraseña</li>
                        </ol>
                    </div>
                    
                    <div class="warning">
                        <strong>Importante:</strong> Este código expira en 1 hora y solo se puede usar una vez.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>¿No solicitaste este cambio?</strong></p>
                    <p>Si no fuiste tú quien solicitó restablecer la contraseña, puedes ignorar este correo de forma segura. Tu contraseña no se modificará.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">
                    <p><strong>AVISENA</strong> - Sistema de Gestión de Granjas Avícolas</p>
                    <p style="font-size: 11px; color: #999;">Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Enviar email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, email, message.as_string())
        
        logger.info(f"Email de recuperación enviado a: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email a {email}: {e}")
        return False