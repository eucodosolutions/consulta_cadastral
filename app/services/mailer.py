import smtplib
import os
import logging
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import BytesIO

log = logging.getLogger(__name__)

def enviar_email_resultado(email_destino: str, df: pd.DataFrame, resumo: dict) -> bool:
    """Envia um e-mail via SMTP Gmail contendo os resultados e a planilha em anexo."""
    
    mail_sender = os.getenv("MAIL_SENDER")
    mail_password = os.getenv("MAIL_PASSWORD")
    
    if not mail_sender or not mail_password:
        log.error("Credenciais de e-mail (MAIL_SENDER, MAIL_PASSWORD) não configuradas no .env")
        return False
        
    try:
        # 1. Configurar Mensagem
        msg = MIMEMultipart()
        msg['From'] = mail_sender
        msg['To'] = email_destino
        msg['Subject'] = "Resultados da Colsulta Cadastral"
        
        # 2. Corpo do E-mail em HTML
        sucessos = resumo.get('sucessos', 0)
        erros = resumo.get('erros', 0)
        total = sucessos + erros
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2 style="color: #4a4eb8;">Processamento Concluído!</h2>
            <p>Olá,</p>
            <p>O processamento em lote dos CNPJs que você solicitou foi finalizado. Segue o resumo da operação:</p>
            <ul>
                <li><b>Total processado:</b> {total}</li>
                <li><span style="color: green;"><b>Sucessos:</b> {sucessos}</span></li>
                <li><span style="color: red;"><b>Erros:</b> {erros}</span></li>
            </ul>
            <p>A planilha contendo os dados e a situação cadastral detalhada encontra-se em anexo.</p>
            <br>
            <p>Atenciosamente,<br>Assistente de Consulta Cadastral</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        
        # 3. Anexo CSV (em memória)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_buffer.seek(0)
        
        anexo = MIMEApplication(csv_buffer.read(), _subtype="csv")
        anexo.add_header('Content-Disposition', 'attachment', filename="resultados_processamento.csv")
        msg.attach(anexo)
        
        # 4. Enviar via SMTP (Gmail)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_sender, mail_password)
            server.send_message(msg)
            
        log.info(f"E-mail enviado com sucesso para {email_destino}")
        return True
        
    except Exception as e:
        log.error(f"Erro ao enviar e-mail para {email_destino}: {str(e)}")
        return False
