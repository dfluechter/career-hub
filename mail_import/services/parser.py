import re
from dataclasses import dataclass
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Final
from urllib.parse import urlparse

from .classifier import classify_job


URL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)

HTML_TAG_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"<[^>]+>",
)


@dataclass(frozen=True, slots=True)
class ParsedJobEmail:
    message_id: str
    mailbox: str
    sender: str
    subject: str
    title: str
    company: str
    location: str
    body: str
    job_url: str
    received_at: datetime
    category: str


def clean_text(value: str) -> str:
    """
    Entfernt überflüssige Whitespaces.
    """

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def html_to_text(value: str) -> str:
    """
    Konvertiert einfaches HTML in strukturierten Text.

    Blockelemente werden vor dem Entfernen der Tags durch
    Zeilenumbrüche getrennt.
    """

    value = re.sub(
        r"<\s*br\s*/?\s*>",
        "\n",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"</\s*(?:p|div|li|tr|h[1-6])\s*>",
        "\n",
        value,
        flags=re.IGNORECASE,
    )

    without_tags = HTML_TAG_PATTERN.sub(
        " ",
        value,
    )

    decoded = unescape(
        without_tags
    )

    lines = [
        clean_text(line)
        for line in decoded.splitlines()
        if clean_text(line)
    ]

    return "\n".join(lines)


def extract_text_body(
    message: EmailMessage,
) -> str:
    """
    Extrahiert bevorzugt text/plain.

    Zeilenumbrüche bleiben erhalten, damit strukturierte Felder
    wie "Unternehmen:" und "Standort:" zuverlässig gelesen
    werden können.

    Anhänge werden ignoriert.
    """

    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in message.walk():
        if part.is_multipart():
            continue

        disposition = part.get_content_disposition()

        if disposition == "attachment":
            continue

        content_type = part.get_content_type()

        try:
            content = part.get_content()

        except (
            LookupError,
            UnicodeDecodeError,
        ):
            payload = part.get_payload(
                decode=True,
            )

            if payload is None:
                continue

            charset = (
                part.get_content_charset()
                or "utf-8"
            )

            content = payload.decode(
                charset,
                errors="replace",
            )

        if not isinstance(
            content,
            str,
        ):
            continue

        if content_type == "text/plain":
            plain_parts.append(
                content.strip()
            )

        elif content_type == "text/html":
            html_parts.append(
                content
            )

    if plain_parts:
        return "\n".join(
            plain_parts
        ).strip()

    if html_parts:
        return html_to_text(
            "\n".join(
                html_parts
            )
        )

    return ""


def extract_first_url(
    body: str,
) -> str:
    """
    Liefert die erste plausible HTTP(S)-URL.
    """

    for match in URL_PATTERN.findall(body):
        candidate = match.rstrip(
            ".,);]}"
        )

        parsed = urlparse(candidate)

        if (
            parsed.scheme in {"http", "https"}
            and parsed.netloc
        ):
            return candidate

    return ""


def parse_received_at(
    date_header: str | None,
) -> datetime:
    """
    Konvertiert den Date-Header zu datetime.

    Fehlt der Header, wird ein Fehler ausgelöst, damit keine
    erfundene Empfangszeit in JobOffer gespeichert wird.
    """

    if not date_header:
        raise ValueError(
            "Die E-Mail enthält keinen Date-Header."
        )

    parsed = parsedate_to_datetime(
        date_header,
    )

    if parsed is None:
        raise ValueError(
            "Der Date-Header konnte nicht gelesen werden."
        )

    return parsed


def extract_labeled_value(
    body: str,
    labels: tuple[str, ...],
) -> str:
    """
    Liest beschriftete Werte aus dem Nachrichtentext.

    Beispiele:
        Stellenbezeichnung: Python Developer
        Unternehmen: Beispiel GmbH
        Standort: Lippstadt
    """

    for line in body.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        for label in labels:
            prefix = f"{label}:"

            if cleaned_line.casefold().startswith(
                prefix.casefold()
            ):
                value = cleaned_line[
                    len(prefix):
                ]

                return clean_text(value)

    return ""


def derive_title(
    subject: str,
    body: str,
) -> str:
    """
    Ermittelt den Jobtitel zunächst aus einem beschrifteten
    Body-Feld und anschließend aus dem Betreff.
    """

    title = extract_labeled_value(
        body,
        (
            "Stellenbezeichnung",
            "Jobtitel",
            "Position",
            "Job title",
        ),
    )

    if title:
        return title

    cleaned_subject = re.sub(
        r"^(?:job|stellenangebot|jobangebot|vacancy)"
        r"\s*[:\-]\s*",
        "",
        subject,
        flags=re.IGNORECASE,
    )

    return clean_text(cleaned_subject)


def parse_email_bytes(
    raw_message: bytes,
    *,
    mailbox: str,
) -> ParsedJobEmail:
    """
    Parst eine vollständige RFC-/MIME-E-Mail aus Bytes.
    """

    message = BytesParser(
        policy=policy.default,
    ).parsebytes(raw_message)

    message_id = clean_text(
        str(message.get("Message-ID", ""))
    )

    subject = clean_text(
        str(message.get("Subject", ""))
    )

    sender = clean_text(
        str(message.get("From", ""))
    )

    if not message_id:
        raise ValueError(
            "Die E-Mail enthält keine Message-ID."
        )

    if not subject:
        raise ValueError(
            "Die E-Mail enthält keinen Betreff."
        )

    body = extract_text_body(message)

    title = derive_title(
        subject,
        body,
    )

    if not title:
        raise ValueError(
            "Es konnte kein Jobtitel ermittelt werden."
        )

    company = extract_labeled_value(
        body,
        (
            "Unternehmen",
            "Firma",
            "Arbeitgeber",
            "Company",
        ),
    )

    location = extract_labeled_value(
        body,
        (
            "Standort",
            "Arbeitsort",
            "Location",
        ),
    )

    received_at = parse_received_at(
        message.get("Date"),
    )

    job_url = extract_first_url(
        body,
    )

    category = classify_job(
        title=title,
        body=body,
    )

    return ParsedJobEmail(
        message_id=message_id,
        mailbox=mailbox,
        sender=sender,
        subject=subject,
        title=title,
        company=company,
        location=location,
        body=body,
        job_url=job_url,
        received_at=received_at,
        category=category,
    )