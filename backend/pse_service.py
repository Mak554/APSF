# -*- coding: utf-8 -*-
"""
Phishing Simulation Engine (PSE) Service
Handles email template management and sends simulated phishing emails
with embedded tracking pixels (for opens) and one-time tracking links (for clicks).
"""
import uuid
import os
import smtplib
import ssl
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from datetime import datetime
from dotenv import load_dotenv

import upt_service
from models.schemas import CampaignCreate, Campaign, EventType

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
# Email Templates
# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;

TEMPLATES = {
    # &#9472;&#9472; IT Attacks &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
    "tpl-it-easy": {
        "name": "[Easy] IT Password Reset",
        "difficulty": "Easy",
        "subject": ["Your pasword expire!!", "URGENT!! Acount will be DELEATED"],
        "body": """<!DOCTYPE html>
<html>
<body style="font-family: 'Times New Roman', Times, serif; background-color: #ffffff; padding: 15px; color: #000000;">
  <h2 style="color: #FF0000; text-align: center; font-size: 22px;">!! URGANT SECURTY NOTCE !!</h2>
  <hr style="border: 2px solid #FF0000;">
  <p style="font-size: 14px;">Dear Valued Custommer,</p>
  <p style="font-size: 14px; color: #CC0000;"><b>YOUR ACOUNT HAS BEEN SUSPENED!!</b> Our sistem has detcted that your pasword has expiered and your acount will be PERMENANTLY DELEATED in 24 hours if you do not take acton IMMEDITELY.</p>
  <p style="font-size: 14px;">To REACTIVATE your acount and PREVENT DELEATION, you must click the link bellow and verfy your credentals NOW:</p>
  <br>
  <div style="text-align: left; margin-left: 20px;">
    <a href="{tracking_link}" style="background-color: #00CC00; color: #FFFFFF; padding: 14px 30px; text-decoration: none; font-size: 18px; font-weight: bold; font-family: Arial; border: 3px solid #000000;">
      &gt;&gt; CLICK HERE TO VERFY ACOUNT NOW &lt;&lt;
    </a>
  </div>
  <br>
  <p style="font-size: 11px; color: #FF0000;"><b>WARNNING:</b> Faliure to verfy within 24 hours will result in PERMENENT ACOUNT SUSPENCION and lose of all data!!</p>
  <hr style="border: 1px solid #cccccc;">
  <p style="font-size: 10px; color: #666666;">
    Regards,<br>
    IT Helpdesk Suport Team<br>
    WebMail Corperation Inc.<br>
    <i>This is an autmoated mesage. Do NOT reply to this email.</i><br>
    &copy; 1999-2025 WebMail&reg; Corp. All rigths reservd. | <a href="#">Unsubscibe</a> | <a href="#">Privavy Polcy</a>
  </p>
  <img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },
    "tpl-it-medium": {
        "name": "[Medium] IT Password Reset",
        "difficulty": "Medium",
        "subject": ["&#9888;&#65039; Urgent: Your Password Expires in 24 Hours", "Action Required: Password Expiration Notice"],
        "body": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IT Security Alert</title></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);">
      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#1a2340 0%,#1e3a5f 100%);padding:28px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td><span style="display:inline-block;background:#3b82f6;color:#fff;font-weight:900;font-size:18px;width:40px;height:40px;line-height:40px;border-radius:10px;text-align:center;">N</span>
              <span style="color:#fff;font-size:18px;font-weight:700;vertical-align:middle;margin-left:12px;">NexaCore Systems</span>
              <span style="color:#64748b;font-size:13px;vertical-align:middle;margin-left:6px;">&#183; IT Security</span></td>
            <td align="right"><span style="background:rgba(239,68,68,0.15);color:#fca5a5;font-size:11px;font-weight:700;padding:5px 12px;border-radius:20px;border:1px solid rgba(239,68,68,0.3);">&#9888; URGENT NOTICE</span></td>
          </tr>
        </table>
      </td></tr>
      <!-- Alert Banner -->
      <tr><td style="background:#dc2626;padding:12px 36px;text-align:center;">
        <span style="color:#fff;font-size:13px;font-weight:600;">&#128308; &nbsp;Your account password expires in <strong>23 hours 47 minutes</strong> &#8212; Immediate action required</span>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:36px;">
        <p style="margin:0 0 20px;font-size:15px;color:#374151;">{greeting} <strong>{full_name}</strong>,</p>
        <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Our automated security system has flagged that your NexaCore employee password is due to <strong style="color:#dc2626;">expire within 24 hours</strong> in accordance with company policy <strong>NX-SEC-2025</strong>. All employees must reset their password before expiration to maintain uninterrupted access to company systems.</p>
        <!-- Info Box -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;margin-bottom:28px;">
          <tr><td style="padding:18px 22px;">
            <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#991b1b;">&#9888; What happens if you don't act:</p>
            <p style="margin:0;font-size:13px;color:#7f1d1d;line-height:1.8;">&#128274; &nbsp;Your account will be locked automatically<br>&#128231; &nbsp;Email and internal systems access will be suspended<br>&#128203; &nbsp;IT helpdesk ticket required to re-enable (48-72h delay)</p>
          </td></tr>
        </table>
        <!-- CTA Button -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
          <tr><td align="center">
            <a href="{tracking_link}" style="display:inline-block;background:linear-gradient(135deg,#1d4ed8,#3b82f6);color:#fff;text-decoration:none;font-size:15px;font-weight:700;padding:15px 40px;border-radius:10px;box-shadow:0 4px 14px rgba(59,130,246,0.45);">&#128272; &nbsp;Reset My Password Now &#8594;</a>
          </td></tr>
        </table>
        <p style="margin:0 0 8px;font-size:13px;color:#6b7280;text-align:center;">Or copy this link: <span style="color:#3b82f6;font-size:11px;">{tracking_link}</span></p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
        <p style="margin:0 0 6px;font-size:14px;color:#374151;">{sign_off}<br><strong>{sender_name}</strong><br><span style="color:#6b7280;font-size:13px;">IT Security Department &#183; NexaCore Systems</span></p>
        <p style="margin:16px 0 0;font-size:12px;color:#9ca3af;">If you did not request this or believe this is an error, contact IT Support at <strong>ext. 5555</strong> or reply to this email.</p>
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:#f8fafc;border-top:1px solid #e5e7eb;padding:16px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="font-size:11px;color:#9ca3af;">&copy; 2025 NexaCore Systems &#183; Riyadh, Saudi Arabia &#183; <a href="#" style="color:#9ca3af;">Privacy Policy</a> &#183; <a href="#" style="color:#9ca3af;">Terms</a></td>
            <td align="right"><a href="{report_link}" style="font-size:11px;color:#ef4444;text-decoration:underline;">&#128681; Report as Phishing</a></td>
          </tr>
        </table>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body></html>""",
    },
    "tpl-it-hard": {
        "name": "[Hard] IT Security Update",
        "difficulty": "Hard",
        "subject": ["[NexaCore Identity] Action Required: Zero-Trust Re-authentication", "Security Policy NX-SEC-2025: Mandatory Credential Verification"],
        "body": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NexaCore Identity Protection</title>
</head>
<body style="margin:0;padding:0;background-color:#020617;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;color:#e2e8f0;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(160deg,#0f172a 0%,#020617 100%);padding:48px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.07);box-shadow:0 32px 64px rgba(0,0,0,0.6);">
      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#0c1929 0%,#0f2744 100%);padding:28px 40px;border-bottom:1px solid rgba(14,165,233,0.2);">
        <table width="100%"><tr>
          <td>
            <table cellpadding="0" cellspacing="0"><tr>
              <td style="width:36px;height:36px;background:linear-gradient(135deg,#0ea5e9,#2563eb);border-radius:8px;text-align:center;vertical-align:middle;">
                <span style="color:#fff;font-size:16px;font-weight:900;line-height:36px;">N</span>
              </td>
              <td style="padding-left:12px;">
                <div style="font-size:15px;font-weight:700;color:#f8fafc;letter-spacing:0.3px;">NexaCore Systems</div>
                <div style="font-size:11px;color:#64748b;margin-top:1px;">Identity &amp; Access Management</div>
              </td>
            </tr></table>
          </td>
          <td align="right">
            <span style="font-size:10px;color:#475569;font-family:monospace;letter-spacing:0.5px;">REF: SEC-AUDIT-2025-NX</span>
          </td>
        </tr></table>
      </td></tr>
      <!-- Alert Banner -->
      <tr><td style="background:rgba(14,165,233,0.08);padding:14px 40px;border-bottom:1px solid rgba(14,165,233,0.15);">
        <table width="100%"><tr>
          <td><span style="display:inline-block;width:8px;height:8px;background:#0ea5e9;border-radius:50%;box-shadow:0 0 8px #0ea5e9;margin-right:8px;vertical-align:middle;"></span>
            <span style="font-size:12px;color:#7dd3fc;font-weight:600;vertical-align:middle;letter-spacing:0.5px;">ZERO-TRUST SECURITY ALERT &#8212; IMMEDIATE ACTION REQUIRED</span>
          </td>
        </tr></table>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:40px;background:#0a1628;">
        <p style="font-size:15px;color:#cbd5e1;margin:0 0 6px;">{greeting} <strong style="color:#38bdf8;">{full_name}</strong>,</p>
        <p style="font-size:14px;color:#94a3b8;line-height:1.7;margin:0 0 28px;">
          NexaCore's automated compliance engine has flagged your account for <strong style="color:#e2e8f0;">mandatory re-authentication</strong> as required by Security Policy <strong style="color:#e2e8f0;">NX-SEC-2025 (v4.2)</strong>. This is part of our annual Zero-Trust Verification cycle for all staff with elevated system access.
        </p>
        <!-- Session Info Table -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.06);border-radius:10px;margin-bottom:28px;">
          <tr><td style="padding:20px 24px;">
            <p style="font-size:10px;color:#475569;margin:0 0 14px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Verification Session Details</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;">
              <tr><td style="padding:6px 0;color:#64748b;width:50%;">Policy Reference</td><td style="color:#cbd5e1;text-align:right;">NX-SEC-2025 &#183; Clause 7.3.1</td></tr>
              <tr><td style="padding:6px 0;color:#64748b;border-top:1px solid rgba(255,255,255,0.04);">Action Type</td><td style="color:#cbd5e1;text-align:right;border-top:1px solid rgba(255,255,255,0.04);">Zero-Trust Re-authentication</td></tr>
              <tr><td style="padding:6px 0;color:#64748b;border-top:1px solid rgba(255,255,255,0.04);">Severity</td><td style="text-align:right;border-top:1px solid rgba(255,255,255,0.04);"><span style="color:#fbbf24;font-weight:600;">&#9679; High Priority</span></td></tr>
              <tr><td style="padding:6px 0;color:#64748b;border-top:1px solid rgba(255,255,255,0.04);">Session Expires</td><td style="color:#ef4444;text-align:right;border-top:1px solid rgba(255,255,255,0.04);font-weight:600;">Within 4 hours of receipt</td></tr>
            </table>
          </td></tr>
        </table>
        <!-- CTA -->
        <a href="{tracking_link}" style="display:block;text-align:center;background:linear-gradient(135deg,#0284c7,#0ea5e9);color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:16px 32px;border-radius:10px;letter-spacing:0.5px;box-shadow:0 6px 20px rgba(14,165,233,0.35);">
          Authenticate via Identity Vault &rarr;
        </a>
        <p style="font-size:12px;color:#475569;text-align:center;margin:16px 0 0;">If you did not expect this alert, contact IT Security immediately at <strong style="color:#94a3b8;">ext. 5555</strong> or forward this email to <strong style="color:#94a3b8;">security@nexacore.sa</strong></p>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:28px 0;">
        <p style="font-size:13px;color:#475569;margin:0;">{sign_off}<br><strong style="color:#cbd5e1;">{sender_name}</strong><br><span style="font-size:12px;">Information Security Officer &#183; NexaCore Systems</span></p>
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:rgba(0,0,0,0.4);padding:16px 40px;border-top:1px solid rgba(255,255,255,0.04);text-align:center;">
        <p style="margin:0;font-size:10px;color:#334155;letter-spacing:0.5px;">This communication is CONFIDENTIAL and intended solely for {full_name}.<br>&copy; 2025 NexaCore Systems &#183; Riyadh, Saudi Arabia &#183; <a href="#" style="color:#334155;">Privacy Policy</a> &#183; <a href="#" style="color:#334155;">Terms</a> &#183; <a href="{report_link}" style="color:#ef4444;">Report Phishing</a></p>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },

    # &#9472;&#9472; HR Attacks &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
    "tpl-hr-easy": {
        "name": "[Easy] HR Benefits Update",
        "difficulty": "Easy",
        "subject": ["GET FREE MONEY HR UPDATE", "!!! CLAIM UR BENIFITS NOW OR LOSE THEM !!!"],
        "body": """<!DOCTYPE html>
<html>
<body style="font-family: 'Comic Sans MS', cursive, sans-serif; padding: 15px; color: #000000; background: #ffffcc;">
  <table width="100%" style="border: 4px solid #FF0000; background-color: #ffffff;">
    <tr>
      <td style="background-color: #FF6600; padding: 10px; text-align: center;">
        <h1 style="color: #FFFF00; margin: 0; font-size: 24px;">HR DEPARTMANT NOTCE</h1>
        <p style="color: #FFFFFF; margin: 4px 0; font-size: 12px;">Employe Benifits Updaet Sistem v1.0</p>
      </td>
    </tr>
    <tr>
      <td style="padding: 20px;">
        <p style="font-size: 15px;">Hello Dear Employe,</p>
        <p style="font-size: 15px; color: #CC0000;"><b>IMPORATNT NOTCE!!</b> The Human Resourcces Departmant requires you to IMMEDITELY update your employe benifits informaton for the year 2025.</p>
        <p style="font-size: 15px;">If you do NOT update your infomation, your <b style="color: #FF0000;">FREE BENIFITS WILL BE CANCELD</b> and you will loose your helth insurence covrage AND your anual bonus!!</p>
        <br>
        <p style="font-size: 13px; background: #FFFF00; padding: 8px; border: 2px dashed #FF0000;">
          &#9888; You have <b>FREE BENIFITS PONTS</b> wating to be claiemd!! Acess them NOW before they exipre!!
        </p>
        <br>
        <div style="text-align: center;">
          <a href="{tracking_link}" style="display: inline-block; background-color: #FF0000; color: #FFFFFF; padding: 16px 32px; text-decoration: none; font-size: 20px; font-weight: bold; border: 3px solid #000000; font-family: Arial;">
            *** CLIK HERE 2 CLAIM FREE BENIFITS ***
          </a>
        </div>
        <br>
        <p style="font-size: 11px; color: #FF0000;">!! WARNNING: This offfer expiers in 24 hours. Do not ignor this mesage !!</p>
        <hr>
        <p style="font-size: 10px; color: #888;">Best Regads,<br>HR Boss<br>Human Resourcces Departmant<br><i>Do not repley. This is autmated.</i></p>
      </td>
    </tr>
  </table>
  <img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },
    "tpl-hr-medium": {
        "name": "[Medium] HR Benefits Update",
        "difficulty": "Medium",
        "subject": ["Important: Annual Benefits Enrollment Closing Soon", "Action Required: Update Your Benefits Profile"],
        "body": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR Benefits Update</title></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);">
      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#0d2137 0%,#1a3f6b 100%);padding:28px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td><span style="display:inline-block;background:#2563eb;color:#fff;font-weight:900;font-size:18px;width:40px;height:40px;line-height:40px;border-radius:10px;text-align:center;">P</span>
              <span style="color:#fff;font-size:18px;font-weight:700;vertical-align:middle;margin-left:12px;">PeopleFirst</span>
              <span style="color:#64748b;font-size:13px;vertical-align:middle;margin-left:6px;">&#183; Human Resources Portal</span></td>
            <td align="right"><span style="background:rgba(59,130,246,0.15);color:#93c5fd;font-size:11px;font-weight:700;padding:5px 12px;border-radius:20px;border:1px solid rgba(59,130,246,0.3);">&#128203; ACTION REQUIRED</span></td>
          </tr>
        </table>
      </td></tr>
      <!-- Banner -->
      <tr><td style="background:#1d4ed8;padding:12px 36px;text-align:center;">
        <span style="color:#fff;font-size:13px;font-weight:600;">&#128197; &nbsp;Benefits enrollment deadline: <strong>End of this week (Friday, 5:00 PM)</strong> &#8212; Do not miss it</span>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:36px;">
        <p style="margin:0 0 20px;font-size:15px;color:#374151;">{greeting} <strong>{full_name}</strong>,</p>
        <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">As part of our <strong>Annual Benefits Enrollment 2025</strong>, the HR department requires all employees to verify and update their benefits profile before the end of this week. This is mandatory under company policy <strong>HR-BEN-2025</strong>.</p>
        <!-- Benefits Table -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;margin-bottom:24px;">
          <tr><td style="padding:18px 22px;">
            <p style="margin:0 0 12px;font-size:13px;font-weight:700;color:#1e40af;">Benefits awaiting your review:</p>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr><td style="font-size:13px;color:#1e3a8a;padding:4px 0;">&#127973; &nbsp;<strong>Health Insurance</strong> &#8212; Family plan update pending</td></tr>
              <tr><td style="font-size:13px;color:#1e3a8a;padding:4px 0;">&#129463; &nbsp;<strong>Dental & Vision</strong> &#8212; Annual re-enrollment required</td></tr>
              <tr><td style="font-size:13px;color:#1e3a8a;padding:4px 0;">&#128176; &nbsp;<strong>Retirement (GOSI)</strong> &#8212; Contribution rate confirmation needed</td></tr>
              <tr><td style="font-size:13px;color:#1e3a8a;padding:4px 0;">&#128737; &nbsp;<strong>Life Insurance</strong> &#8212; Beneficiary information must be updated</td></tr>
            </table>
          </td></tr>
        </table>
        <!-- Warning Box -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;margin-bottom:28px;">
          <tr><td style="padding:14px 20px;">
            <p style="margin:0;font-size:13px;color:#9a3412;">&#9888; <strong>Failure to update by the deadline</strong> may result in interruption or cancellation of your benefits coverage until the next enrollment period.</p>
          </td></tr>
        </table>
        <!-- CTA -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
          <tr><td align="center">
            <a href="{tracking_link}" style="display:inline-block;background:linear-gradient(135deg,#1565c0,#2980b9);color:#fff;text-decoration:none;font-size:15px;font-weight:700;padding:15px 40px;border-radius:10px;box-shadow:0 4px 14px rgba(41,128,185,0.45);">&#128203; &nbsp;Update My Benefits Now &#8594;</a>
          </td></tr>
        </table>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
        <p style="margin:0 0 6px;font-size:14px;color:#374151;">Thank you for your prompt attention to this matter.<br><br>{sign_off}<br><strong>{sender_name}</strong><br><span style="color:#6b7280;font-size:13px;">Human Resources Department</span></p>
        <p style="margin:16px 0 0;font-size:12px;color:#9ca3af;">Questions? Contact HR at <strong>hr@company.sa</strong> or extension <strong>4400</strong>.</p>
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:#f8fafc;border-top:1px solid #e5e7eb;padding:16px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="font-size:11px;color:#9ca3af;">&copy; 2025 PeopleFirst HR &#183; company.sa &#183; <a href="#" style="color:#9ca3af;">Privacy</a></td>
            <td align="right"><a href="{report_link}" style="font-size:11px;color:#ef4444;text-decoration:underline;">&#128681; Report as Phishing</a></td>
          </tr>
        </table>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body></html>""",
    },
    "tpl-hr-hard": {
        "name": "[Hard] HR Policy GOSI",
        "difficulty": "Hard",
        "subject": ["[PeopleFirst HR] Official Notice: 2025 GOSI & Tawuniya Re-verification Required", "Mandatory Compliance: Saudi Labor Law Article 32.A &#8212; Action Required Today"],
        "body": """<!DOCTYPE html>
<html lang="ar-SA" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HR Compliance Notice</title>
</head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;color:#1e293b;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:40px 0;">
  <tr><td align="center">
    <table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">
      <!-- Gov Header -->
      <tr><td style="background:linear-gradient(135deg,#065f46 0%,#047857 100%);padding:0;">
        <table width="100%" cellpadding="0" cellspacing="0"><tr>
          <td style="padding:22px 36px;">
            <div style="font-size:11px;color:#a7f3d0;letter-spacing:2px;text-transform:uppercase;font-weight:700;margin-bottom:4px;">Kingdom of Saudi Arabia</div>
            <div style="font-size:17px;font-weight:800;color:#ffffff;letter-spacing:0.5px;">Ministry Compliance Portal</div>
            <div style="font-size:12px;color:#6ee7b7;margin-top:2px;">National Labor Law &amp; GOSI Integration &#8212; PeopleFirst HR</div>
          </td>
          <td align="right" style="padding:22px 36px;">
            <div style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:8px;padding:10px 16px;text-align:center;">
              <div style="font-size:9px;color:#a7f3d0;letter-spacing:1px;margin-bottom:3px;">REFERENCE ID</div>
              <div style="font-size:13px;font-family:monospace;color:#ffffff;font-weight:700;">HR-GOSI-2025-{full_name[:4].upper()}</div>
            </div>
          </td>
        </tr></table>
      </td></tr>
      <!-- Status Banner -->
      <tr><td style="background:#fef3c7;padding:12px 36px;border-bottom:1px solid #fde68a;">
        <table width="100%"><tr>
          <td><span style="font-size:13px;color:#92400e;font-weight:700;">&#9888; Action Required Before End of Business Today &#8212; {full_name}</span></td>
          <td align="right"><span style="background:#ef4444;color:#fff;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;">PENDING VERIFICATION</span></td>
        </tr></table>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:36px;">
        <p style="font-size:15px;margin:0 0 8px;">{greeting} <strong>{full_name}</strong>,</p>
        <p style="font-size:14px;color:#475569;line-height:1.75;margin:0 0 24px;">In accordance with the updated <strong>Saudi Labor Law (Article 32.A)</strong> and corporate policy <strong>HR-BEN-V3</strong>, all employees are legally required to verify their Social Insurance (GOSI) records and dependent health insurance coverage for the <strong>2025 fiscal year</strong>.</p>
        <!-- Compliance Table -->
        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:24px;">
          <tr style="background:#f8fafc;"><th style="padding:11px 16px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Verification Module</th><th style="padding:11px 16px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Provider</th><th style="padding:11px 16px;text-align:right;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Status</th></tr>
          <tr style="border-top:1px solid #e2e8f0;"><td style="padding:12px 16px;font-size:13px;">GOSI Basic Wage &amp; Housing Allowance</td><td style="padding:12px 16px;font-size:13px;color:#64748b;">GOSI Portal</td><td style="padding:12px 16px;text-align:right;"><span style="background:#fee2e2;color:#b91c1c;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">Pending</span></td></tr>
          <tr style="border-top:1px solid #e2e8f0;"><td style="padding:12px 16px;font-size:13px;">CCHI Medical Insurance (Tawuniya / Bupa)</td><td style="padding:12px 16px;font-size:13px;color:#64748b;">Tawuniya</td><td style="padding:12px 16px;text-align:right;"><span style="background:#fee2e2;color:#b91c1c;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">Pending</span></td></tr>
          <tr style="border-top:1px solid #e2e8f0;"><td style="padding:12px 16px;font-size:13px;">Dependent Coverage Update (Spouse &amp; Children)</td><td style="padding:12px 16px;font-size:13px;color:#64748b;">MOH Integration</td><td style="padding:12px 16px;text-align:right;"><span style="background:#fef3c7;color:#92400e;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">Incomplete</span></td></tr>
        </table>
        <!-- Warning Box -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;margin-bottom:28px;"><tr><td style="padding:14px 18px;"><p style="margin:0;font-size:13px;color:#991b1b;"><strong>&#9888; Consequence of Non-Compliance:</strong> Failure to verify by end of business today will result in <strong>immediate suspension of medical coverage</strong> and a <strong>delay in the current payroll cycle</strong> pending regulatory review.</p></td></tr></table>
        <!-- CTA -->
        <a href="{tracking_link}" style="display:block;text-align:center;background:#047857;color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;padding:15px 32px;border-radius:8px;letter-spacing:0.3px;box-shadow:0 4px 12px rgba(4,120,87,0.25);">
          Login via Corporate ID (Nafath Integration) &rarr;
        </a>
        <p style="font-size:12px;color:#94a3b8;text-align:center;margin:14px 0 0;">Secure session authenticated via Nafath &#183; ID verification required</p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
        <p style="font-size:13px;color:#374151;margin:0;">{sign_off}<br><strong>{sender_name}</strong><br><span style="color:#6b7280;font-size:12px;">HR Compliance Officer &#183; PeopleFirst HR</span></p>
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:#f8fafc;padding:16px 36px;border-top:1px solid #e5e7eb;text-align:center;">
        <p style="margin:0;font-size:10px;color:#9ca3af;">Confidential &amp; Privileged &#8212; Generated by HR Information Systems v4.1<br>&copy; 2025 PeopleFirst HR &#183; Riyadh, Saudi Arabia &#183; <a href="#" style="color:#9ca3af;">Privacy</a> &#183; <a href="{report_link}" style="color:#ef4444;">Report Phishing</a></p>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },

    # &#9472;&#9472; CEO Attacks &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;



    # &#9472;&#9472; CEO Attacks &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
    "tpl-ceo-easy": {
        "name": "[Easy] CEO Urgent Task",
        "difficulty": "Easy",
        "subject": ["Re: Re: Are you at ur desk??", "URGENT task from CEO pleese respond"],
        "body": """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; padding: 10px; color: #000;">
  <p>Hi,</p>
  <p>I am currntly in a very imporatnt meating and canot talk. I need you to do somthing URGANT and DISCRATE for me right now.</p>
  <p>I need you to buy 5 Apple iTunes gift cads worth SAR 500 each (total SAR 2500) for a very imporatnt client prezentation. Pleese do this <b>IMMEDITELY</b> and do not tell anynoe else about this.</p>
  <p>Once you buy them scach the back and send me the codes by clicking the link bellow. I will pay you back in CASH tommorow.</p>
  <br>
  <p><a href="{tracking_link}" style="color: blue; font-size: 16px;"><b>Click here to upload the gift card codes securly</b></a></p>
  <br>
  <p>This is very URGANT. Pleese do it now and do not reply to this email, just click the link.</p>
  <br>
  <p>Thankyou,</p>
  <p>{sender_name}<br>
  <i>Cheif Exective Officcer</i><br>
  <span style="font-size: 11px; color: #999;">Sent from my iPhome</span></p>
  <img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },
    "tpl-ceo-medium": {
        "name": "[Medium] CEO Wire Transfer",
        "difficulty": "Medium",
        "subject": ["Confidential: Urgent Wire Transfer &#8212; Action Needed Before 3PM", "PRIVATE & CONFIDENTIAL: Executive Request"],
        "body": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Confidential Executive Request</title></head>
<body style="margin:0;padding:0;background:#f0f4f0;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f0;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.12);">
      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#0a1f0a 0%,#1a3a1a 100%);padding:28px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td><span style="display:inline-block;background:#16a34a;color:#fff;font-weight:900;font-size:18px;width:40px;height:40px;line-height:40px;border-radius:10px;text-align:center;">E</span>
              <span style="color:#fff;font-size:18px;font-weight:700;vertical-align:middle;margin-left:12px;">ExecVault</span>
              <span style="color:#4ade80;font-size:13px;vertical-align:middle;margin-left:6px;">&#183; Secure Executive Portal</span></td>
            <td align="right"><span style="background:rgba(22,163,74,0.15);color:#86efac;font-size:11px;font-weight:700;padding:5px 12px;border-radius:20px;border:1px solid rgba(22,163,74,0.4);">&#128274; CONFIDENTIAL</span></td>
          </tr>
        </table>
      </td></tr>
      <!-- Classified Banner -->
      <tr><td style="background:#166534;padding:10px 36px;text-align:center;">
        <span style="color:#bbf7d0;font-size:12px;font-weight:700;letter-spacing:2px;">&#9940; &nbsp; CLASSIFIED &#8212; DO NOT FORWARD OR DISCUSS WITH COLLEAGUES &nbsp; &#9940;</span>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:36px;">
        <p style="margin:0 0 20px;font-size:15px;color:#374151;">{greeting} <strong>{full_name}</strong>,</p>
        <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">I'm reaching out directly because this matter requires your immediate and <strong>discreet</strong> attention. We are in the final stages of closing a <strong>critical strategic acquisition</strong>, and I need a wire transfer processed <strong style="color:#dc2626;">before 3:00 PM today</strong>.</p>
        <!-- Deal Box -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;margin-bottom:24px;">
          <tr><td style="padding:20px 24px;">
            <p style="margin:0 0 14px;font-size:13px;font-weight:700;color:#14532d;">&#128193; Transfer Reference &#8212; CLASSIFIED</p>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="font-size:13px;color:#166534;padding:5px 0;width:160px;">Transaction Ref:</td>
                <td style="font-size:13px;color:#1a2340;font-weight:700;">EV-ACQ-2025-0419</td>
              </tr>
              <tr>
                <td style="font-size:13px;color:#166534;padding:5px 0;">Authorization:</td>
                <td style="font-size:13px;color:#1a2340;font-weight:700;">CEO Direct &#8212; Level 5 Clearance</td>
              </tr>
              <tr>
                <td style="font-size:13px;color:#166534;padding:5px 0;">Deadline:</td>
                <td style="font-size:13px;color:#dc2626;font-weight:700;">Today &#8212; 3:00 PM (Saudi Time)</td>
              </tr>
              <tr>
                <td style="font-size:13px;color:#166534;padding:5px 0;">Priority:</td>
                <td style="font-size:13px;color:#dc2626;font-weight:700;">&#128308; Critical / Urgent</td>
              </tr>
            </table>
          </td></tr>
        </table>
        <!-- Instruction -->
        <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Please access the <strong>Secure Transfer Authorization Portal</strong> using the link below to review the full transfer details and submit your authorization code. <strong>Do not reply to this email</strong> &#8212; use only the secure portal.</p>
        <!-- Warning -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;margin-bottom:28px;">
          <tr><td style="padding:14px 20px;">
            <p style="margin:0;font-size:13px;color:#92400e;">&#9888; <strong>Confidentiality Notice:</strong> This transaction is subject to NDA. Do not discuss this request with colleagues, finance, or any other department. Breach of confidentiality may jeopardize the acquisition.</p>
          </td></tr>
        </table>
        <!-- CTA -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
          <tr><td align="center">
            <a href="{tracking_link}" style="display:inline-block;background:linear-gradient(135deg,#155724,#16a34a);color:#fff;text-decoration:none;font-size:15px;font-weight:700;padding:15px 40px;border-radius:10px;box-shadow:0 4px 14px rgba(22,163,74,0.45);">&#128274; &nbsp;Access Secure Transfer Portal &#8594;</a>
          </td></tr>
        </table>
        <p style="margin:0 0 4px;font-size:13px;color:#6b7280;text-align:center;">Portal access expires in <strong style="color:#dc2626;">2 hours 14 minutes</strong>. Use a private/incognito window.</p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
        <p style="margin:0;font-size:14px;color:#374151;">{sign_off}<br><strong>{sender_name}</strong><br><span style="color:#6b7280;font-size:13px;">Chief Executive Officer</span></p>
        <p style="margin:16px 0 0;font-size:12px;color:#9ca3af;">Sent from a secure mobile device. Replies may be delayed &#8212; use the portal for all communications regarding this matter.</p>
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:#f8fafc;border-top:1px solid #e5e7eb;padding:16px 36px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="font-size:11px;color:#9ca3af;">ExecVault Secure Portal &#183; company.sa &#183; Encrypted &amp; Monitored</td>
            <td align="right"><a href="{report_link}" style="font-size:11px;color:#ef4444;text-decoration:underline;">&#128681; Report as Phishing</a></td>
          </tr>
        </table>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body></html>""",
    },
    "tpl-ceo-hard": {
        "name": "[Hard] CEO Strategic Acquisition",
        "difficulty": "Hard",
        "subject": ["[BOARD DIRECTIVE] Project Falcon: Escrow Authorization &#8212; Strictly Confidential", "PRIVATE & CONFIDENTIAL: Strategic Acquisition Wire Authorization &#8212; {full_name}"],
        "body": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Office of the Chief Executive</title>
</head>
<body style="margin:0;padding:0;background:#020617;font-family:Georgia,'Times New Roman',serif;color:#e2e8f0;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(180deg,#0a0f1a 0%,#020617 100%);padding:48px 0;">
  <tr><td align="center">
    <table width="640" cellpadding="0" cellspacing="0" style="background:#0d1626;border:1px solid #1e3a5f;border-radius:4px;box-shadow:0 0 60px rgba(0,0,0,0.8);">
      <!-- Embossed Header -->
      <tr><td style="padding:0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#0c1929 0%,#132742 100%);border-bottom:3px solid #1d4ed8;">
          <tr><td style="padding:32px 48px;text-align:center;">
            <div style="font-size:10px;letter-spacing:4px;color:#3b82f6;text-transform:uppercase;font-weight:700;margin-bottom:12px;font-family:'Segoe UI',sans-serif;">NexaCore Systems &#183; Riyadh, Kingdom of Saudi Arabia</div>
            <div style="font-size:20px;letter-spacing:5px;color:#f8fafc;text-transform:uppercase;font-weight:400;font-family:Georgia,serif;">Office of the Chief Executive</div>
            <div style="margin-top:10px;height:1px;background:linear-gradient(to right,transparent,#1d4ed8,transparent);"></div>
            <div style="margin-top:10px;font-size:9px;letter-spacing:3px;color:#ef4444;text-transform:uppercase;font-family:'Segoe UI',sans-serif;font-weight:700;">Restricted Access &#8226; Level 5 Board Clearance &#8226; NDA Protected</div>
          </td></tr>
        </table>
      </td></tr>
      <!-- Reference strip -->
      <tr><td style="padding:14px 48px;background:rgba(29,78,216,0.08);border-bottom:1px solid #1e3a5f;">
        <table width="100%"><tr>
          <td style="font-size:11px;color:#64748b;font-family:'Segoe UI',sans-serif;">Reference: <span style="color:#94a3b8;font-family:monospace;">EV-ACQ-2025-FALCON</span></td>
          <td align="right" style="font-size:11px;color:#64748b;font-family:'Segoe UI',sans-serif;">Classification: <span style="color:#ef4444;font-weight:700;">STRICTLY CONFIDENTIAL</span></td>
        </tr></table>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:48px;">
        <p style="font-size:15px;line-height:1.8;margin:0 0 24px;color:#cbd5e1;">{greeting} <strong style="color:#f8fafc;">{full_name}</strong>,</p>
        <p style="font-size:15px;line-height:1.9;margin:0 0 20px;color:#94a3b8;">I am writing to you directly and confidentially regarding the final execution phase of <strong style="color:#e2e8f0;">Project Falcon</strong>, the strategic acquisition approved by the Board of Directors in the closed session held this morning.</p>
        <p style="font-size:15px;line-height:1.9;margin:0 0 28px;color:#94a3b8;">This transaction is governed by a legally binding Non-Disclosure Agreement. You are one of only <strong style="color:#e2e8f0;">three individuals</strong> authorized to act on this directive. I require your immediate electronic authorization to release the escrow transfer to our external legal counsel, Al-Rashidi &amp; Partners Law Firm, Riyadh.</p>
        <!-- Auth Box -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(0,0,0,0.4);border:1px solid #1e3a5f;border-radius:6px;margin-bottom:32px;">
          <tr><td style="padding:24px 32px;">
            <div style="font-size:9px;color:#475569;letter-spacing:2px;text-transform:uppercase;font-family:'Segoe UI',sans-serif;margin-bottom:16px;">Authorization Parameters &#8212; Classified</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;font-family:'Segoe UI',sans-serif;">
              <tr><td style="padding:8px 0;color:#64748b;border-bottom:1px solid #1e293b;width:45%;">Transaction Ref</td><td style="color:#cbd5e1;text-align:right;border-bottom:1px solid #1e293b;font-family:monospace;">EV-ACQ-2025-0419</td></tr>
              <tr><td style="padding:8px 0;color:#64748b;border-bottom:1px solid #1e293b;">Authorization Level</td><td style="color:#cbd5e1;text-align:right;border-bottom:1px solid #1e293b;">CEO Direct &#8212; Board Mandate</td></tr>
              <tr><td style="padding:8px 0;color:#64748b;border-bottom:1px solid #1e293b;">Legal Counsel</td><td style="color:#cbd5e1;text-align:right;border-bottom:1px solid #1e293b;">Al-Rashidi &amp; Partners, Riyadh</td></tr>
              <tr><td style="padding:8px 0;color:#ef4444;font-weight:600;">Action Deadline</td><td style="color:#ef4444;text-align:right;font-weight:700;">15:00 AST &#8212; Today</td></tr>
            </table>
          </td></tr>
        </table>
        <!-- CTA -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
          <tr><td style="padding:24px;text-align:center;background:rgba(0,0,0,0.3);border:1px solid #1e293b;border-radius:4px;">
            <p style="margin:0 0 16px;font-size:11px;letter-spacing:2px;color:#64748b;text-transform:uppercase;font-family:'Segoe UI',sans-serif;">Secure Board Authorization Portal</p>
            <a href="{tracking_link}" style="display:inline-block;background:linear-gradient(135deg,#1d4ed8,#2563eb);color:#ffffff;text-decoration:none;font-size:13px;font-weight:600;padding:14px 36px;border-radius:3px;letter-spacing:1px;font-family:'Segoe UI',sans-serif;box-shadow:0 4px 16px rgba(37,99,235,0.4);">
              AUTHENTICATE &amp; AUTHORIZE TRANSFER
            </a>
          </td></tr>
        </table>
        <p style="font-size:14px;line-height:1.9;margin:0 0 32px;color:#64748b;">Under no circumstances should this communication be forwarded, discussed via internal messaging systems, or disclosed to any party outside this authorization chain. Breach of this directive constitutes a material breach of your NDA and may carry legal consequences.</p>
        <div style="border-top:1px solid #1e3a5f;padding-top:24px;">
          <p style="margin:0;font-size:14px;color:#94a3b8;">{sign_off}</p>
          <p style="margin:6px 0 2px;font-size:15px;font-weight:700;color:#f8fafc;">{sender_name}</p>
          <p style="margin:0;font-size:13px;color:#475569;font-family:'Segoe UI',sans-serif;">Chief Executive Officer &#8226; NexaCore Systems</p>
        </div>
      </td></tr>
      <!-- Legal Footer -->
      <tr><td style="background:rgba(0,0,0,0.5);padding:20px 48px;border-top:1px solid #0f172a;text-align:center;">
        <p style="margin:0;font-size:9px;color:#334155;letter-spacing:0.5px;line-height:1.6;font-family:'Segoe UI',sans-serif;">WARNING: THIS MESSAGE AND ANY ATTACHMENTS ARE STRICTLY CONFIDENTIAL AND LEGALLY PRIVILEGED.<br>UNAUTHORIZED DISCLOSURE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND MAY RESULT IN LEGAL ACTION.<br>&copy; 2025 NexaCore Systems &#183; CR No. 1010XXXXXX &#183; Riyadh, Saudi Arabia</p>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>""",
    },
}

# Add backward compatibility aliases
TEMPLATES["tpl-001"] = TEMPLATES["tpl-it-medium"]
TEMPLATES["tpl-002"] = TEMPLATES["tpl-hr-medium"]
TEMPLATES["tpl-003"] = TEMPLATES["tpl-ceo-medium"]


def get_templates() -> List[dict]:
    """Returns list of all available phishing email templates."""
    # When listing templates, include difficulty and id
    return [
        {
            "id": k,
            "name": v["name"],
            "difficulty": v.get("difficulty", "Medium"),
            "subject": v["subject"][0] if isinstance(v["subject"], list) else v["subject"]
        } 
        for k, v in TEMPLATES.items() 
        if not k.startswith("tpl-00") # Exclude aliases from list to avoid clutter
    ]


# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
# Campaign Creation
# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;

def create_campaign(campaign_data: CampaignCreate) -> Campaign:
    """Creates a new campaign record in Firestore."""
    db_campaign = Campaign(
        campaign_id=str(uuid.uuid4()),
        name=campaign_data.name,
        phishing_type=campaign_data.phishing_type,
        email_template_id=campaign_data.email_template_id,
        sender_name=campaign_data.sender_name,
        sender_email=campaign_data.sender_email,
        subject=campaign_data.subject,
        urgency_level=campaign_data.urgency_level,
        difficulty=campaign_data.difficulty,
        target_count=len(campaign_data.target_user_ids),
        status="draft",
    )
    from firebase_config import get_db
    get_db().collection("campaigns").document(db_campaign.campaign_id).set(
        db_campaign.model_dump()
    )
    return db_campaign


# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;
# Email Sending
# &#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;

def _build_tracking_urls(user_id: str, campaign_id: str) -> dict:
    """Constructs the unique tracking pixel and link URLs for a specific user+campaign."""
    return {
        "pixel_url": f"{APP_BASE_URL}/track/open/{campaign_id}/{user_id}",
        "tracking_link": f"{FRONTEND_URL}/landing/{campaign_id}/{user_id}",
        "report_link": f"{FRONTEND_URL}/report/{campaign_id}/{user_id}",
    }


import random

def _build_email(
    template_id: str,
    user_profile,
    sender_name: str,
    sender_email: str,
    tracking_urls: dict,
) -> MIMEMultipart:
    """Renders an email template and returns the MIME message object."""
    template = TEMPLATES.get(template_id)
    if not template:
        raise ValueError(f"Template '{template_id}' not found.")

    greetings = ["Dear", "Hi", "Hello", "Attention", "To"]
    sign_offs = ["Best regards,", "Thank you,", "Sincerely,", "Regards,", "Best,"]

    html_body = template["body"].format(
        full_name=user_profile.full_name,
        sender_name=sender_name,
        tracking_link=tracking_urls["tracking_link"],
        pixel_url=tracking_urls["pixel_url"],
        report_link=tracking_urls["report_link"],
        greeting=random.choice(greetings),
        sign_off=random.choice(sign_offs)
    )

    msg = MIMEMultipart("alternative")
    
    # If subject is a list (randomized), pick one, else use the string
    subject = random.choice(template["subject"]) if isinstance(template["subject"], list) else template["subject"]
    msg["Subject"] = subject
    
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = user_profile.email
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_campaign_emails(campaign: Campaign, target_user_ids: List[str]) -> dict:
    """
    Sends phishing simulation emails to all target users.
    Logs an Email_Sent event for each user after successful delivery.
    Returns a summary dict.
    """
    sent_count = 0
    failed_count = 0
    errors = []

    # Python 3.14 has stricter SSL validation that rejects some certificate chains.
    # Use an unverified context for dev/testing SMTP connections.
    context = ssl._create_unverified_context()

    try:
        if SMTP_HOST == "localhost":
            print("[PSE] MOCK MODE: Intercepting emails locally instead of sending via SMTP.")
            for user_id in target_user_ids:
                user = upt_service.get_user(user_id)
                if not user:
                    errors.append(f"User {user_id} not found.")
                    failed_count += 1
                    continue
                try:
                    tracking_urls = _build_tracking_urls(user_id, campaign.campaign_id)
                    msg = _build_email(
                        template_id=campaign.email_template_id,
                        user_profile=user,
                        sender_name=campaign.sender_name,
                        sender_email=campaign.sender_email,
                        tracking_urls=tracking_urls,
                    )
                    # MOCK sending
                    print("-" * 50)
                    print(f"To: {user.email}")
                    print(f"Subject: {msg['Subject']}")
                    print(msg.get_payload()[0].get_payload()[:200] + "...\n(body truncated)")
                    print("-" * 50)

                    upt_service.log_event(
                        user_id=user_id,
                        campaign_id=campaign.campaign_id,
                        event_type=EventType.EMAIL_SENT,
                    )
                    upt_service.increment_user_stats(user_id, EventType.EMAIL_SENT, campaign.campaign_id)
                    sent_count += 1
                    print(f"[PSE] Mock Email sent to {user.email}")
                except Exception as e:
                    errors.append(f"Failed to mock send to {user_id}: {str(e)}")
                    failed_count += 1
        else:
            print(f"[PSE] Connecting to SMTP {SMTP_HOST}:{SMTP_PORT} as {SMTP_USER}...")
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASSWORD)
                print("[PSE] SMTP login successful.")
    
                for user_id in target_user_ids:
                    user = upt_service.get_user(user_id)
                    if not user:
                        errors.append(f"User {user_id} not found.")
                        failed_count += 1
                        continue
    
                    try:
                        tracking_urls = _build_tracking_urls(user_id, campaign.campaign_id)
                        msg = _build_email(
                            template_id=campaign.email_template_id,
                            user_profile=user,
                            sender_name=campaign.sender_name,
                            sender_email=campaign.sender_email,
                            tracking_urls=tracking_urls,
                        )
                        server.sendmail(SMTP_USER, user.email, msg.as_string())
                        upt_service.log_event(
                            user_id=user_id,
                            campaign_id=campaign.campaign_id,
                            event_type=EventType.EMAIL_SENT,
                        )
                        upt_service.increment_user_stats(user_id, EventType.EMAIL_SENT, campaign.campaign_id)
                        sent_count += 1
                        print(f"[PSE] Email sent to {user.email}")
                    except Exception as e:
                        errors.append(f"Failed to send to {user_id}: {str(e)}")
                        failed_count += 1

    except smtplib.SMTPAuthenticationError as e:
        print(f"[PSE] SMTP authentication failed: {e}")
        return {"error": "SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD in .env"}
    except Exception as e:
        print(f"[PSE] SMTP connection failed: {type(e).__name__}: {e}")
        return {"error": f"SMTP connection failed: {str(e)}"}

    # Update campaign status
    from firebase_config import get_db
    get_db().collection("campaigns").document(campaign.campaign_id).update({"status": "running"})

    return {
        "campaign_id": campaign.campaign_id,
        "sent": sent_count,
        "failed": failed_count,
        "errors": errors,
    }
