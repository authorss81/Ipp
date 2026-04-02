"""
SMTP module for Ipp language - Email sending support
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailMessage:
    """Email message wrapper for Ipp"""
    
    def __init__(self, subject='', body='', html_body=None, from_addr='', to_addrs=None, cc_addrs=None, bcc_addrs=None):
        self.subject = subject
        self.body = body
        self.html_body = html_body
        self.from_addr = from_addr
        self.to_addrs = to_addrs or []
        self.cc_addrs = cc_addrs or []
        self.bcc_addrs = bcc_addrs or []
        self.attachments = []
    
    def add_attachment(self, filepath, filename=None):
        """Add an attachment to the email"""
        if not os.path.exists(filepath):
            raise RuntimeError(f"Attachment file not found: {filepath}")
        
        if filename is None:
            filename = os.path.basename(filepath)
        
        self.attachments.append({'filepath': filepath, 'filename': filename})
        return True
    
    def _build_message(self):
        """Build the email message object"""
        if self.html_body:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(self.body, 'plain'))
            msg.attach(MIMEText(self.html_body, 'html'))
        else:
            msg = MIMEMultipart()
            msg.attach(MIMEText(self.body, 'plain'))
        
        msg['Subject'] = self.subject
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(self.to_addrs)
        if self.cc_addrs:
            msg['Cc'] = ', '.join(self.cc_addrs)
        
        for attachment in self.attachments:
            with open(attachment['filepath'], 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment["filename"]}"'
                )
                msg.attach(part)
        
        return msg


class SMTPClient:
    """SMTP client wrapper for Ipp"""
    
    def __init__(self, server, port=587, use_tls=True, username=None, password=None):
        self.server = server
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self._smtp = None
        self.connected = False
    
    def connect(self):
        """Connect to the SMTP server"""
        try:
            if self.use_tls:
                self._smtp = smtplib.SMTP(self.server, self.port)
                self._smtp.starttls()
            else:
                self._smtp = smtplib.SMTP(self.server, self.port)
            
            if self.username and self.password:
                self._smtp.login(self.username, self.password)
            
            self.connected = True
            return True
        except Exception as e:
            raise RuntimeError(f"SMTP connection failed: {e}")
    
    def disconnect(self):
        """Disconnect from the SMTP server"""
        if self._smtp and self.connected:
            try:
                self._smtp.quit()
            except Exception:
                pass
            self.connected = False
    
    def send(self, message):
        """Send an email message"""
        if not self.connected:
            raise RuntimeError("Not connected to SMTP server")
        
        if not isinstance(message, EmailMessage):
            raise RuntimeError("Second argument must be an EmailMessage")
        
        try:
            msg = message._build_message()
            all_recipients = list(message.to_addrs) + list(message.cc_addrs) + list(message.bcc_addrs)
            
            self._smtp.sendmail(message.from_addr, all_recipients, msg.as_string())
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")
    
    def send_simple(self, from_addr, to_addrs, subject, body, html_body=None):
        """Send a simple email without attachments"""
        if not self.connected:
            raise RuntimeError("Not connected to SMTP server")
        
        try:
            if isinstance(to_addrs, str):
                to_addrs = [to_addrs]
            
            if html_body:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(body, 'plain'))
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg = MIMEText(body)
            
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = ', '.join(to_addrs)
            
            self._smtp.sendmail(from_addr, to_addrs, msg.as_string())
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")
    
    def __repr__(self):
        return f"<SMTPClient server={self.server} connected={self.connected}>"


def smtp_connect(server, port=587, use_tls=True, username=None, password=None):
    """Create and connect an SMTP client"""
    client = SMTPClient(server, port, use_tls, username, password)
    client.connect()
    return client


def smtp_disconnect(client):
    """Disconnect an SMTP client"""
    if not isinstance(client, SMTPClient):
        raise RuntimeError("First argument must be an SMTPClient")
    client.disconnect()
    return True


def smtp_send(client, message):
    """Send an email via SMTP"""
    if not isinstance(client, SMTPClient):
        raise RuntimeError("First argument must be an SMTPClient")
    return client.send(message)


def smtp_send_simple(client, from_addr, to_addrs, subject, body):
    """Send a simple email via SMTP"""
    if not isinstance(client, SMTPClient):
        raise RuntimeError("First argument must be an SMTPClient")
    return client.send_simple(from_addr, to_addrs, subject, body)


def email_create(subject, body, from_addr, to_addrs, html_body=None):
    """Create an email message"""
    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    return EmailMessage(subject, body, html_body, from_addr, to_addrs)
