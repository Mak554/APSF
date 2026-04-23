"""Quick SMTP connection test to verify credentials."""
import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

print(f"Host: {SMTP_HOST}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password: {'*' * len(SMTP_PASSWORD)} ({len(SMTP_PASSWORD)} chars)")

context = ssl._create_unverified_context()

try:
    print("\n[1] Connecting to SMTP server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    server.ehlo()
    print("[2] Starting TLS...")
    server.starttls(context=context)
    print("[3] Logging in...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("[OK] SMTP authentication successful!")
    
    # Send a quick test email to yourself
    from email.mime.text import MIMEText
    msg = MIMEText("APSF SMTP test - if you see this, email sending works!")
    msg["Subject"] = "APSF SMTP Test"
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_USER
    
    print("[4] Sending test email to self...")
    server.sendmail(SMTP_USER, SMTP_USER, msg.as_string())
    print(f"[OK] Test email sent to {SMTP_USER}")
    
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print(f"\n[FAIL] Authentication error: {e}")
    print("\nPossible fixes:")
    print("  1. Enable 2-Step Verification on the Google account")
    print("  2. Generate an App Password at: https://myaccount.google.com/apppasswords")
    print("  3. Use the App Password (without spaces) in .env SMTP_PASSWORD")
except Exception as e:
    print(f"\n[FAIL] Error: {type(e).__name__}: {e}")
