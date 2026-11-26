import re

from jobs.models import JobCategory


CATEGORY_KEYWORDS = {
    JobCategory.SOFTWARE_DEVELOPER: (
        "software developer",
        "softwareentwickler",
        "software engineer",
        "webentwickler",
        "web developer",
        "frontend developer",
        "backend developer",
        "fullstack developer",
        "full stack developer",
        "python developer",
        "django developer",
        "react developer",
        "entwickler",
        "programmierer",
    ),

    JobCategory.DATA_ANALYST: (
        "data analyst",
        "datenanalyst",
        "data analytics",
        "business intelligence",
        "bi analyst",
        "reporting analyst",
        "power bi",
        "datenanalyse",
    ),

    JobCategory.SOFTWARE_TESTER: (
        "software tester",
        "softwaretester",
        "qa engineer",
        "quality assurance",
        "test engineer",
        "testautomatisierung",
        "test automation",
        "quality engineer",
    ),

    JobCategory.IT_TECHNICIAN: (
        "it-techniker",
        "it techniker",
        "it support",
        "it-support",
        "helpdesk",
        "service desk",
        "systemadministrator",
        "system administrator",
        "fachinformatiker systemintegration",
        "desktop support",
    ),
}


def normalize_text(value: str) -> str:
    """
    Normalisiert Text für einfache Keyword-Vergleiche.
    """

    normalized = value.casefold()

    normalized = re.sub(
        r"[\W_]+",
        " ",
        normalized,
    )

    return re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()


def classify_job(
    title: str,
    body: str = "",
) -> str:
    """
    Ordnet eine Stelle anhand von Titel und Nachrichtentext
    einer JobCategory zu.

    Der Titel wird stärker gewichtet als der Body.
    """

    normalized_title = normalize_text(title)
    normalized_body = normalize_text(body)

    scores = {
        category: 0
        for category in CATEGORY_KEYWORDS
    }

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)

            if normalized_keyword in normalized_title:
                scores[category] += 3

            if normalized_keyword in normalized_body:
                scores[category] += 1

    best_category = max(
        scores,
        key=scores.get,
    )

    if scores[best_category] == 0:
        return JobCategory.OTHER

    return best_category