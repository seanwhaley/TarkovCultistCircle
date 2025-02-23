from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from src.core.config import Settings
from src.core.exceptions import AppException

logger = logging.getLogger(__name__)

class EmailTemplate:
    """Email template manager using Jinja2."""

    def __init__(self, templates_dir: Union[str, Path]):
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=True
        )

    def render(
        self,
        template_name: str,
        **context: Any
    ) -> str:
        """Render an email template."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            raise AppException(f"Failed to render email template: {str(e)}")

class EmailManager:
    """Async email manager for sending notifications."""

    def __init__(
        self,
        settings: Settings,
        templates_dir: Union[str, Path]
    ):
        self.settings = settings
        self.templates = EmailTemplate(templates_dir)
        self._smtp = None

    async def _get_smtp(self) -> aiosmtplib.SMTP:
        """Get SMTP connection."""
        if not self._smtp:
            self._smtp = aiosmtplib.SMTP(
                hostname=self.settings.SMTP_HOST,
                port=self.settings.SMTP_PORT,
                use_tls=self.settings.SMTP_TLS,
                username=self.settings.SMTP_USER,
                password=self.settings.SMTP_PASSWORD
            )
        return self._smtp

    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            to_email: Recipient email(s)
            subject: Email subject
            template_name: Name of the template file
            context: Template variables
            cc: CC recipient(s)
            bcc: BCC recipient(s)
        
        Returns:
            True if email was sent successfully
        """
        try:
            # Prepare recipients
            if isinstance(to_email, str):
                to_email = [to_email]
            if isinstance(cc, str):
                cc = [cc]
            if isinstance(bcc, str):
                bcc = [bcc]

            # Render template
            html_content = self.templates.render(template_name, **context)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.settings.SMTP_FROM_EMAIL
            message['To'] = ', '.join(to_email)
            
            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)
                
            # Add HTML content
            message.attach(MIMEText(html_content, 'html'))
            
            # Get all recipients
            all_recipients = to_email.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
                
            # Send email
            smtp = await self._get_smtp()
            await smtp.send_message(message, to_addrs=all_recipients)
            
            logger.info(
                f"Email sent successfully to {len(all_recipients)} recipients"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise AppException(f"Failed to send email: {str(e)}")

    async def send_welcome_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send welcome email to new users."""
        context = {
            "username": username,
            "login_url": f"{self.settings.APP_URL}/auth/login",
            "year": datetime.now().year
        }
        return await self.send_email(
            to_email=to_email,
            subject="Welcome to Tarkov Cultist Circle",
            template_name="welcome.html",
            context=context
        )

    async def send_password_reset(
        self,
        to_email: str,
        reset_token: str,
        expires_in: int
    ) -> bool:
        """Send password reset email."""
        context = {
            "reset_url": (
                f"{self.settings.APP_URL}/auth/reset-password"
                f"?token={reset_token}"
            ),
            "expires_in": expires_in,
            "year": datetime.now().year
        }
        return await self.send_email(
            to_email=to_email,
            subject="Password Reset Request",
            template_name="password_reset.html",
            context=context
        )

    async def send_price_alert(
        self,
        to_email: str,
        item_name: str,
        current_price: float,
        threshold_price: float
    ) -> bool:
        """Send price alert email."""
        context = {
            "item_name": item_name,
            "current_price": current_price,
            "threshold_price": threshold_price,
            "market_url": f"{self.settings.APP_URL}/market",
            "year": datetime.now().year
        }
        return await self.send_email(
            to_email=to_email,
            subject=f"Price Alert: {item_name}",
            template_name="price_alert.html",
            context=context
        )

    async def close(self) -> None:
        """Close SMTP connection."""
        if self._smtp:
            await self._smtp.quit()
            self._smtp = None