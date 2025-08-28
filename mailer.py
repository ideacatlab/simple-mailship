import argparse
import json
import os
import re
import ssl
import sys
import time
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, localtime
from pathlib import Path
from typing import Iterable, List, Dict, Any, Set, Optional, Tuple

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
import html2text
from email_validator import validate_email, EmailNotValidError

EMAIL_KEY_ALIASES = {"email", "e-mail", "mail"}


@dataclass
class Config:
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_name: str
    subject: str
    template_path: Path
    reply_to: Optional[str] = None
    rate_per_minute: Optional[float] = None  # emails/min
    use_ssl: bool = True  # default Gmail SSL 465

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        from_name = os.getenv("FROM_NAME", smtp_username or "")
        subject = os.getenv("SUBJECT", "Servicii Profesionale Coșerit Autorizat - RIGONDA MAROIL SRL")
        template_path_str = os.getenv("TEMPLATE_PATH", "email-template.html")
        reply_to = os.getenv("REPLY_TO", None)
        rate_per_minute_env = os.getenv("RATE_PER_MIN", None)
        rate_per_minute = float(rate_per_minute_env) if rate_per_minute_env else None
        use_ssl = os.getenv("SMTP_USE_SSL", "true").lower() in {"1", "true", "yes", "on"}

        if not smtp_username:
            raise RuntimeError("Missing SMTP_USERNAME in .env")
        if not smtp_password:
            raise RuntimeError("Missing SMTP_PASSWORD in .env (use your Gmail App Password)")

        template_path = Path(template_path_str)
        if not template_path.exists():
            raise RuntimeError(f"TEMPLATE_PATH points to '{template_path}', but the file does not exist.")

        return cls(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            from_name=from_name,
            subject=subject,
            template_path=template_path,
            reply_to=reply_to,
            rate_per_minute=rate_per_minute,
            use_ssl=use_ssl,
        )


def load_json_records(path: Path) -> List[Dict[str, Any]]:
    """Load a JSON file and return a list of dicts (records).
    Supports:
      - Top-level list of objects
      - Top-level dict containing one of: items | results | data -> list of objects
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        # ensure dicts only
        return [x for x in data if isinstance(x, dict)]

    if isinstance(data, dict):
        for key in ("items", "results", "data"):
            val = data.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]

    raise ValueError("Unsupported JSON shape: expected a list of objects or an object with 'items'/'results'/'data' list.")


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def extract_emails(records: Iterable[Dict[str, Any]]) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[Dict[str, Any]]]:
    """Return ([(email, record), ...], [records_without_email]).
    Only first-level keys are considered, case-insensitive, among EMAIL_KEY_ALIASES.
    """
    found: List[Tuple[str, Dict[str, Any]]] = []
    missing: List[Dict[str, Any]] = []

    for rec in records:
        email_val = None
        for k, v in rec.items():
            if k.lower() in EMAIL_KEY_ALIASES and isinstance(v, str) and v.strip():
                email_val = v.strip()
                break

        if not email_val:
            missing.append(rec)
            continue

        # Validate email format (syntax only; deliverability off)
        try:
            valid = validate_email(email_val, check_deliverability=False)
            email_clean = valid.normalized
        except EmailNotValidError:
            # fallback to a simple regex check; if fail, skip
            if not EMAIL_REGEX.match(email_val):
                missing.append(rec)
                continue
            email_clean = email_val

        found.append((email_clean, rec))

    # De-duplicate by email address, keeping the first occurrence
    seen: Set[str] = set()
    unique: List[Tuple[str, Dict[str, Any]]] = []
    for email, rec in found:
        if email.lower() in seen:
            continue
        seen.add(email.lower())
        unique.append((email, rec))

    return unique, missing


def build_jinja_env(template_path: Path) -> Tuple[Environment, str]:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env, template_path.name


def render_template(env: Environment, template_name: str, context: Dict[str, Any]) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


def html_to_plaintext(html: str) -> str:
    # Configure html2text for email-friendly plaintext
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0  # do not hard-wrap
    return h.handle(html).strip()


def make_message(from_name: str, from_email: str, to_email: str, subject: str, html_body: str, reply_to: Optional[str] = None) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to_email
    msg["Date"] = localtime()
    msg["Message-ID"] = make_msgid()
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach both plain and HTML alternatives
    plain = html_to_plaintext(html_body)
    msg.set_content(plain)
    msg.add_alternative(html_body, subtype="html")
    return msg


def send_messages(config: Config, messages: List[EmailMessage], dry_run: bool = False, rate_per_minute: Optional[float] = None) -> None:
    if dry_run:
        print(f"[DRY-RUN] Would send {len(messages)} message(s). No SMTP connection will be made.")
        return

    rate = rate_per_minute if rate_per_minute is not None else config.rate_per_minute
    delay = (60.0 / rate) if rate and rate > 0 else 0.0

    if config.use_ssl:
        context = ssl.create_default_context()
        import smtplib
        with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, context=context) as server:
            server.login(config.smtp_username, config.smtp_password)
            for i, msg in enumerate(messages, start=1):
                server.send_message(msg)
                print(f"[OK] {i}/{len(messages)} -> {msg['To']}")
                if delay and i < len(messages):
                    time.sleep(delay)
    else:
        # STARTTLS path
        import smtplib
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.login(config.smtp_username, config.smtp_password)
            for i, msg in enumerate(messages, start=1):
                server.send_message(msg)
                print(f"[OK] {i}/{len(messages)} -> {msg['To']}")
                if delay and i < len(messages):
                    time.sleep(delay)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Send HTML email via Gmail SMTP using a JSON list of recipients.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", metavar="EMAIL", help="Send a single test email to the specified address.")
    group.add_argument("--list", metavar="JSON_FILE", help="Path to JSON file with contacts (each object may contain an 'email' key).")

    parser.add_argument("--subject", help="Override email subject (otherwise uses SUBJECT from .env).")
    parser.add_argument("--from-name", help="Override From display name (otherwise uses FROM_NAME from .env).")
    parser.add_argument("--reply-to", help="Optional reply-to address (overrides REPLY_TO from .env).")

    parser.add_argument("--rate", type=float, help="Rate limit in emails per minute (overrides RATE_PER_MIN from .env).")
    parser.add_argument("--dry-run", action="store_true", help="Do everything except actually sending emails.")
    parser.add_argument("--save-previews", metavar="DIR", help="Directory to save rendered HTML previews per recipient.")
    parser.add_argument("--verbose", action="store_true", help="More logging.")

    args = parser.parse_args(argv)

    try:
        cfg = Config.from_env()
    except Exception as e:
        print(f"[CONFIG ERROR] {e}", file=sys.stderr)
        return 2

    # Allow CLI overrides
    subject = args.subject or cfg.subject
    from_name = args.from_name or cfg.from_name
    reply_to = args.reply_to or cfg.reply_to

    # Prepare templating environment
    env, template_name = build_jinja_env(cfg.template_path)

    messages: List[EmailMessage] = []

    if args.test:
        # Use minimal context for test; you can extend with placeholders as needed.
        context = {
            "name": "Test Recipient",
            "location": "N/A",
            "county": "N/A",
            "admin": "N/A",
            "address": "N/A",
            "phone": "N/A",
            "email": args.test,
        }
        html = render_template(env, template_name, context)
        if args.save_previews:
            outdir = Path(args.save_previews); outdir.mkdir(parents=True, exist_ok=True)
            (outdir / "preview_test.html").write_text(html, encoding="utf-8")

        msg = make_message(from_name, cfg.smtp_username, args.test, subject, html, reply_to=reply_to)
        messages.append(msg)

    elif args.list:
        json_path = Path(args.list)
        if not json_path.exists():
            print(f"[ERROR] JSON file not found: {json_path}", file=sys.stderr)
            return 2

        records = load_json_records(json_path)
        pairs, missing = extract_emails(records)
        if args.verbose:
            print(f"[INFO] Loaded {len(records)} record(s). {len(pairs)} with emails, {len(missing)} without or invalid.")

        for email_addr, rec in pairs:
            context = {**rec}  # expose the whole record to the template for optional placeholders
            html = render_template(env, template_name, context)

            if args.save_previews:
                outdir = Path(args.save_previews); outdir.mkdir(parents=True, exist_ok=True)
                safe_email = re.sub(r'[^A-Za-z0-9_.+-]+', '_', email_addr)
                (outdir / f"preview_{safe_email}.html").write_text(html, encoding="utf-8")

            msg = make_message(from_name, cfg.smtp_username, email_addr, subject, html, reply_to=reply_to)
            messages.append(msg)

        # Summary
        print(f"[SUMMARY] {len(records)} total; {len(pairs)} to send; {len(missing)} skipped (no/invalid email).")
    else:
        parser.error("Either --test or --list must be provided.")

    # Send
    try:
        send_messages(cfg, messages, dry_run=args.dry_run, rate_per_minute=args.rate)
    except Exception as e:
        print(f"[SEND ERROR] {e}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())