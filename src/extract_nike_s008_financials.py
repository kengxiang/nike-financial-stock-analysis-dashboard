"""
Extract raw FY2026 Q4 and full-year Nike financial metrics from S008.

This script uses only the official SEC Exhibit 99.1 source recorded as S008 in
data/source_log.csv. It refreshes S008 rows in data/raw/nike_financials_raw.csv
while preserving non-S008 rows.
"""

from __future__ import annotations

import re
import os
import warnings
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError


SOURCE_ID = "S008"
SOURCE_NAME = "NIKE, Inc. Reports Fiscal 2026 Fourth Quarter and Full Year Results"
SOURCE_DATE = "2026-06-30"
SOURCE_LINK = (
    "https://www.sec.gov/Archives/edgar/data/320187/"
    "000032018726000076/q4fy26exhibit991er.htm"
)
LOAD_DATE = "2026-07-01"
OUTPUT_PATH = Path("data/raw/nike_financials_raw.csv")

RAW_COLUMNS = [
    "source_id",
    "period",
    "fiscal_year",
    "fiscal_quarter",
    "period_type",
    "statement_type",
    "metric_name",
    "reported_value",
    "metric_value",
    "unit",
    "currency",
    "source_name",
    "source_date",
    "source_link",
    "load_date",
    "notes",
]


def fetch_s008_html() -> str:
    """Download the official S008 SEC Exhibit 99.1 HTML page."""
    user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        raise RuntimeError(
            'SEC_USER_AGENT environment variable is required. Example: set SEC_USER_AGENT="Your Name your.email@example.com"'
        )

    # SEC EDGAR requests should use a descriptive User-Agent and fair-access-
    # friendly scripting so the request is transparent and rate-limit aware.
    headers = {"User-Agent": user_agent}
    try:
        response = requests.get(SOURCE_LINK, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except SSLError as exc:
        allow_insecure = (
            os.environ.get("ALLOW_INSECURE_SSL_FALLBACK", "").lower() == "true"
        )
        if not allow_insecure:
            raise RuntimeError(
                "SSL certificate verification failed for the official S008 SEC URL. "
                "Set ALLOW_INSECURE_SSL_FALLBACK=true only if this local environment "
                "cannot validate the SEC certificate chain."
            ) from exc

        print(
            "WARNING: SSL verification disabled only for this request to the official S008 SEC URL."
        )
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
        response = requests.get(
            SOURCE_LINK, headers=headers, timeout=30, verify=False
        )
        response.raise_for_status()
        return response.text


def clean_label(value: object) -> str:
    """Normalise table labels while preserving enough meaning for matching."""
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_numeric(value: object) -> str:
    """Convert a source value such as '$', '(8)', or '49.2%' to numeric text."""
    if pd.isna(value):
        return ""

    text = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    text = text.replace("—", "").replace("–", "").strip()
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"
    return text


def make_reported_value(raw_value: object, unit: str) -> str:
    """Format the reported value close to the source presentation."""
    text = str(raw_value).strip()
    if "billion" in text.lower():
        return text

    if unit == "USD millions":
        is_parenthetical = text.startswith("(") and text.endswith(")")
        clean_text = (
            text.replace("$", "")
            .replace(",", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )
        value = float(clean_text)
        formatted = f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}"
        if is_parenthetical:
            return f"$({formatted})"
        return f"${formatted}"

    if unit == "%":
        if text.endswith("%"):
            return text
        return f"{text}%"

    if unit == "basis points":
        if "basis point" in text:
            return text
        return f"{text} basis points"

    if unit == "USD per share":
        if text.startswith("$"):
            return text
        return f"${text}"

    return text


def build_row(
    period: str,
    fiscal_quarter: str,
    period_type: str,
    statement_type: str,
    metric_name: str,
    raw_value: object,
    unit: str,
    currency: str,
    notes: str,
) -> dict[str, str]:
    """Create one raw extraction row using consistent S008 metadata."""
    return {
        "source_id": SOURCE_ID,
        "period": period,
        "fiscal_year": "2026",
        "fiscal_quarter": fiscal_quarter,
        "period_type": period_type,
        "statement_type": statement_type,
        "metric_name": metric_name,
        "reported_value": make_reported_value(raw_value, unit),
        "metric_value": parse_numeric(raw_value),
        "unit": unit,
        "currency": currency,
        "source_name": SOURCE_NAME,
        "source_date": SOURCE_DATE,
        "source_link": SOURCE_LINK,
        "load_date": LOAD_DATE,
        "notes": notes,
    }


def get_row(table: pd.DataFrame, label: str) -> pd.Series:
    """Find a row in a source table by its first-column label."""
    matches = table[table.iloc[:, 0].map(clean_label).str.lower() == label.lower()]
    if matches.empty:
        raise ValueError(f"Could not find source row: {label}")
    return matches.iloc[0]


def table_contains_labels(table: pd.DataFrame, required_labels: list[str]) -> bool:
    """Return True when a table contains all required first-column labels."""
    labels = {clean_label(value).lower() for value in table.iloc[:, 0].tolist()}
    return all(label.lower() in labels for label in required_labels)


def find_table_by_labels(
    tables: list[pd.DataFrame], required_labels: list[str], table_name: str
) -> pd.DataFrame:
    """Find a source table by required row labels instead of fixed index."""
    for table in tables:
        if table.shape[1] > 0 and table_contains_labels(table, required_labels):
            return table
    raise ValueError(
        f"Could not find {table_name} table using required labels: {required_labels}"
    )


def extract_income_statement(table: pd.DataFrame) -> list[dict[str, str]]:
    """Extract Q4 and FY2026 values from the consolidated income statement."""
    mappings = {
        "Revenues": ("total_revenues", "USD millions", "USD"),
        "Cost of sales": ("cost_of_sales", "USD millions", "USD"),
        "Gross profit": ("gross_profit", "USD millions", "USD"),
        "Gross margin": ("gross_margin", "%", "%"),
        "Demand creation expense": (
            "demand_creation_expense",
            "USD millions",
            "USD",
        ),
        "Operating overhead expense": (
            "operating_overhead_expense",
            "USD millions",
            "USD",
        ),
        "Total selling and administrative expense": (
            "total_selling_and_administrative_expense",
            "USD millions",
            "USD",
        ),
        "% of revenues": (
            "selling_and_administrative_expense_percent_of_revenue",
            "%",
            "%",
        ),
        "Interest (income) expense, net": (
            "interest_income_expense_net",
            "USD millions",
            "USD",
        ),
        "Other (income) expense, net": (
            "other_income_expense_net",
            "USD millions",
            "USD",
        ),
        "Income before income taxes": (
            "income_before_income_taxes",
            "USD millions",
            "USD",
        ),
        "Income tax expense": ("income_tax_expense", "USD millions", "USD"),
        "Effective tax rate": ("effective_tax_rate", "%", "%"),
        "NET INCOME": ("net_income", "USD millions", "USD"),
        "Basic": ("basic_eps", "USD per share", "USD"),
        "Diluted": ("diluted_eps", "USD per share", "USD"),
        "Dividends declared per common share": (
            "dividends_declared_per_common_share",
            "USD per share",
            "USD",
        ),
    }

    rows: list[dict[str, str]] = []
    for label, (metric_name, unit, currency) in mappings.items():
        source_row = get_row(table, label)
        q4_value = source_row.iloc[4] if source_row.iloc[3] == "$" else source_row.iloc[3]
        fy_value = source_row.iloc[13] if source_row.iloc[12] == "$" else source_row.iloc[12]
        rows.append(
            build_row(
                "FY2026 Q4",
                "Q4",
                "quarter",
                "income_statement",
                metric_name,
                q4_value,
                unit,
                currency,
                "Q4 value from consolidated statements of income for the three months ended May 31, 2026.",
            )
        )
        rows.append(
            build_row(
                "FY2026",
                "FY",
                "full_year",
                "income_statement",
                metric_name,
                fy_value,
                unit,
                currency,
                "Full-year value from consolidated statements of income for the twelve months ended May 31, 2026.",
            )
        )

    # The table has two Basic/Diluted sections. The EPS rows are above; these
    # rows come from the weighted-average shares section.
    shares_section = table.iloc[30:]
    share_mappings = {
        "Basic": "weighted_average_common_shares_basic",
        "Diluted": "weighted_average_common_shares_diluted",
    }
    for label, metric_name in share_mappings.items():
        source_row = get_row(shares_section, label)
        rows.append(
            build_row(
                "FY2026 Q4",
                "Q4",
                "quarter",
                "income_statement",
                metric_name,
                source_row.iloc[3],
                "shares millions",
                "N/A",
                "Q4 weighted-average common shares from consolidated statements of income.",
            )
        )
        rows.append(
            build_row(
                "FY2026",
                "FY",
                "full_year",
                "income_statement",
                metric_name,
                source_row.iloc[12],
                "shares millions",
                "N/A",
                "Full-year weighted-average common shares from consolidated statements of income.",
            )
        )

    return rows


def extract_balance_sheet(table: pd.DataFrame) -> list[dict[str, str]]:
    """Extract May 31, 2026 balance sheet values."""
    mappings = {
        "Cash and equivalents": "cash_and_equivalents",
        "Short-term investments": "short_term_investments",
        "Accounts receivable, net": "accounts_receivable_net",
        "Inventories": "inventories",
        "Prepaid expenses and other current assets": (
            "prepaid_expenses_and_other_current_assets"
        ),
        "Total current assets": "total_current_assets",
        "Property, plant and equipment, net": "property_plant_and_equipment_net",
        "Operating lease right-of-use assets, net": (
            "operating_lease_right_of_use_assets_net"
        ),
        "Identifiable intangible assets, net": "identifiable_intangible_assets_net",
        "Goodwill": "goodwill",
        "Deferred income taxes and other assets": (
            "deferred_income_taxes_and_other_assets"
        ),
        "TOTAL ASSETS": "total_assets",
        "Current portion of long-term debt": "current_portion_of_long_term_debt",
        "Accounts payable": "accounts_payable",
        "Current portion of operating lease liabilities": (
            "current_portion_of_operating_lease_liabilities"
        ),
        "Accrued liabilities": "accrued_liabilities",
        "Income taxes payable": "income_taxes_payable",
        "Total current liabilities": "total_current_liabilities",
    }

    rows: list[dict[str, str]] = []
    for label, metric_name in mappings.items():
        source_row = get_row(table, label)
        value = source_row.iloc[4] if source_row.iloc[3] == "$" else source_row.iloc[3]
        rows.append(
            build_row(
                "May 31 2026",
                "N/A",
                "balance_sheet_date",
                "balance_sheet",
                metric_name,
                value,
                "USD millions",
                "USD",
                "Balance sheet value as of May 31, 2026.",
            )
        )
    return rows


def extract_divisional_revenue(table: pd.DataFrame) -> list[dict[str, str]]:
    """Extract NIKE Brand, Converse, and total reported/currency-neutral changes."""
    rows: list[dict[str, str]] = []
    mappings = {
        "TOTAL NIKE BRAND REVENUES3": "nike_brand_revenues",
        "Converse": "converse_revenues",
    }
    for label, metric_name in mappings.items():
        source_row = get_row(table, label)
        q4_value = source_row.iloc[4] if source_row.iloc[3] == "$" else source_row.iloc[3]
        fy_value = source_row.iloc[16] if source_row.iloc[15] == "$" else source_row.iloc[15]
        rows.append(
            build_row(
                "FY2026 Q4",
                "Q4",
                "quarter",
                "channel_revenue",
                metric_name,
                q4_value,
                "USD millions",
                "USD",
                "Q4 value from divisional revenues table for the three months ended May 31, 2026.",
            )
        )
        rows.append(
            build_row(
                "FY2026",
                "FY",
                "full_year",
                "channel_revenue",
                metric_name,
                fy_value,
                "USD millions",
                "USD",
                "Full-year value from divisional revenues table for the twelve months ended May 31, 2026.",
            )
        )

    total_row = get_row(table, "TOTAL NIKE, INC. REVENUES")
    change_specs = [
        ("FY2026 Q4", "Q4", "quarter", "reported_revenue_change", total_row.iloc[9]),
        (
            "FY2026 Q4",
            "Q4",
            "quarter",
            "currency_neutral_revenue_change",
            total_row.iloc[12],
        ),
        ("FY2026", "FY", "full_year", "reported_revenue_change", total_row.iloc[21]),
        (
            "FY2026",
            "FY",
            "full_year",
            "currency_neutral_revenue_change",
            total_row.iloc[24],
        ),
    ]
    for period, fiscal_quarter, period_type, metric_name, value in change_specs:
        rows.append(
            build_row(
                period,
                fiscal_quarter,
                period_type,
                "channel_revenue",
                metric_name,
                value,
                "%",
                "%",
                "Reported or currency-neutral total NIKE, Inc. revenue change from divisional revenues table.",
            )
        )

    return rows


def extract_narrative_metrics(text: str) -> list[dict[str, str]]:
    """Extract explicitly stated channel and tariff metrics from release text."""
    rows: list[dict[str, str]] = []

    q4_start = text.find("Fourth Quarter Income Statement Review")
    fy_start = text.find("Fiscal 2026 Income Statement Review")
    bs_start = text.find("May 31, 2026 Balance Sheet Review")
    if q4_start == -1 or fy_start == -1 or bs_start == -1:
        raise ValueError("Could not locate expected narrative review sections.")

    q4_text = text[q4_start:fy_start]
    fy_text = text[fy_start:bs_start]

    narrative_specs = [
        (
            q4_text,
            r"Wholesale revenues were \$(?P<value>[\d.]+) billion, up (?P<reported>-?\d+) percent .*? up (?P<currency>-?\d+) percent on a currency-neutral basis",
            "FY2026 Q4",
            "Q4",
            "quarter",
            "wholesale_revenues",
            "Wholesale revenues Q4 narrative value; notes include reported and currency-neutral changes explicitly stated in S008.",
        ),
        (
            q4_text,
            r"NIKE Direct revenues were \$(?P<value>[\d.]+) billion, down (?P<reported>-?\d+) percent .*? down (?P<currency>-?\d+) percent on a currency-neutral basis",
            "FY2026 Q4",
            "Q4",
            "quarter",
            "nike_direct_revenues",
            "NIKE Direct revenues Q4 narrative value; notes include reported and currency-neutral changes explicitly stated in S008.",
        ),
        (
            fy_text,
            r"Wholesale revenues were \$(?P<value>[\d.]+) billion, up (?P<reported>-?\d+) percent on a reported basis and up (?P<currency>-?\d+) percent on a currency-neutral basis\.",
            "FY2026",
            "FY",
            "full_year",
            "wholesale_revenues",
            "Wholesale revenues full-year narrative value; notes include reported and currency-neutral changes explicitly stated in S008.",
        ),
        (
            fy_text,
            r"NIKE Direct revenues were \$(?P<value>[\d.]+) billion, down (?P<reported>-?\d+) percent on a reported basis and down (?P<currency>-?\d+) percent on a currency-neutral basis",
            "FY2026",
            "FY",
            "full_year",
            "nike_direct_revenues",
            "NIKE Direct revenues full-year narrative value; notes include reported and currency-neutral changes explicitly stated in S008.",
        ),
    ]

    for source_text, pattern, period, fiscal_quarter, period_type, metric_name, note in narrative_specs:
        match = re.search(pattern, source_text)
        if not match:
            continue
        value_billions = match.group("value")
        value_millions = float(value_billions) * 1000
        row = build_row(
            period,
            fiscal_quarter,
            period_type,
            "channel_revenue",
            metric_name,
            f"{value_millions:g}",
            "USD millions",
            "USD",
            f"{note} Reported change: {match.group('reported')}%; currency-neutral change: {match.group('currency')}%.",
        )
        row["reported_value"] = f"${value_billions} billion"
        rows.append(row)

    digital_specs = [
        (
            "FY2026 Q4",
            "Q4",
            "quarter",
            q4_text,
        ),
        (
            "FY2026",
            "FY",
            "full_year",
            fy_text,
        ),
    ]
    digital_pattern = (
        r"due to a (?P<digital>\d+) percent decrease in NIKE Brand Digital "
        r"and a (?P<stores>\d+) percent decrease in NIKE-owned stores"
    )
    for period, fiscal_quarter, period_type, source_text in digital_specs:
        match = re.search(digital_pattern, source_text)
        if not match:
            continue
        for metric_name, group_name in [
            ("nike_brand_digital_revenue_change_reported_or_stated", "digital"),
            ("nike_owned_stores_revenue_change_reported_or_stated", "stores"),
        ]:
            rows.append(
                build_row(
                    period,
                    fiscal_quarter,
                    period_type,
                    "channel_revenue",
                    metric_name,
                    f"-{match.group(group_name)}",
                    "%",
                    "%",
                    "Narrative reported decrease explicitly stated in S008.",
                )
            )

    tariff_patterns = [
        (
            "ieepa_tariff_recovery_amount",
            r"expected recovery of the IEEPA tariffs of \$(?P<value>[\d.]+) million",
            "USD millions",
            "USD",
            "IEEPA tariff recovery amount explicitly stated in Q4 narrative.",
        ),
        (
            "gross_margin_ieepa_tariff_benefit_bps",
            r"approximately (?P<value>\d+) basis point benefit due to the expected recovery",
            "basis points",
            "N/A",
            "IEEPA tariff recovery gross margin benefit explicitly stated in release highlights.",
        ),
        (
            "diluted_eps_ieepa_tariff_benefit",
            r"including a \$(?P<value>[\d.]+) benefit related to the expected recovery of the IEEPA tariffs",
            "USD per share",
            "USD",
            "IEEPA tariff recovery diluted EPS benefit explicitly stated in release highlights.",
        ),
    ]
    for metric_name, pattern, unit, currency, note in tariff_patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        rows.append(
            build_row(
                "FY2026 Q4",
                "Q4",
                "quarter",
                "tariff_recovery",
                metric_name,
                match.group("value"),
                unit,
                currency,
                note,
            )
        )

    return rows


def extract_rows(html: str) -> pd.DataFrame:
    """Extract all requested raw S008 rows from the official SEC HTML."""
    tables = pd.read_html(StringIO(html), flavor="lxml")
    income_statement_table = find_table_by_labels(
        tables,
        ["Revenues", "Gross profit", "NET INCOME", "Diluted"],
        "income statement",
    )
    balance_sheet_table = find_table_by_labels(
        tables,
        [
            "Cash and equivalents",
            "Inventories",
            "TOTAL ASSETS",
            "Total current liabilities",
        ],
        "balance sheet",
    )
    divisional_revenue_table = find_table_by_labels(
        tables,
        ["TOTAL NIKE BRAND REVENUES3", "Converse", "TOTAL NIKE, INC. REVENUES"],
        "divisional revenues",
    )

    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.get_text(" ").split())

    rows = []
    rows.extend(extract_income_statement(income_statement_table))
    rows.extend(extract_balance_sheet(balance_sheet_table))
    rows.extend(extract_divisional_revenue(divisional_revenue_table))
    rows.extend(extract_narrative_metrics(text))

    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def validate_output(df: pd.DataFrame) -> None:
    """Run lightweight validation before saving."""
    missing_columns = [column for column in RAW_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if not (df["source_id"] == SOURCE_ID).all():
        raise ValueError("All extracted rows must have source_id = S008.")

    duplicate_mask = df.duplicated(
        subset=["source_id", "period", "statement_type", "metric_name"],
        keep=False,
    )
    if duplicate_mask.any():
        duplicates = df.loc[
            duplicate_mask, ["period", "statement_type", "metric_name"]
        ]
        raise ValueError(f"Duplicate extracted rows found:\n{duplicates}")

    numeric_units = {
        "USD millions",
        "%",
        "basis points",
        "USD per share",
        "shares millions",
    }
    numeric_rows = df["unit"].isin(numeric_units)
    invalid_numeric = pd.to_numeric(df.loc[numeric_rows, "metric_value"], errors="coerce").isna()
    if invalid_numeric.any():
        bad_rows = df.loc[numeric_rows].loc[
            invalid_numeric, ["period", "metric_name", "metric_value"]
        ]
        raise ValueError(f"Non-numeric metric_value found:\n{bad_rows}")

    rate_units = df[df["metric_name"].isin(["gross_margin", "effective_tax_rate"])]
    if not (rate_units["unit"] == "%").all():
        raise ValueError("gross_margin and effective_tax_rate must use unit = %.") 

    eps_units = df[df["metric_name"].str.contains("eps", na=False)]
    if not (eps_units["unit"] == "USD per share").all():
        raise ValueError("EPS metrics must use unit = USD per share.")

    monetary_statement_rows = df[
        df["statement_type"].isin(["income_statement", "balance_sheet"])
        & (df["currency"] == "USD")
        & ~df["metric_name"].str.contains("eps|dividends_declared", na=False)
    ]
    if not (monetary_statement_rows["unit"] == "USD millions").all():
        raise ValueError(
            "Income statement and balance sheet monetary values must use USD millions."
        )

    required_categories = {
        "income_statement",
        "balance_sheet",
        "channel_revenue",
        "tariff_recovery",
    }
    observed_categories = set(df["statement_type"])
    missing_categories = required_categories - observed_categories
    if missing_categories:
        raise ValueError(
            f"Missing required statement_type categories: {sorted(missing_categories)}"
        )

    required_periods = {"FY2026 Q4", "FY2026", "May 31 2026"}
    observed_periods = set(df["period"])
    missing_periods = required_periods - observed_periods
    if missing_periods:
        raise ValueError(f"Missing required period labels: {sorted(missing_periods)}")


def save_rows(new_rows: pd.DataFrame) -> None:
    """Refresh S008 rows in the raw financial dataset while preserving others."""
    if OUTPUT_PATH.exists():
        existing = pd.read_csv(OUTPUT_PATH, dtype=str)
        for column in RAW_COLUMNS:
            if column not in existing.columns:
                existing[column] = ""
        existing = existing[RAW_COLUMNS]
        existing = existing[existing["source_id"] != SOURCE_ID]
    else:
        existing = pd.DataFrame(columns=RAW_COLUMNS)

    combined = pd.concat([existing, new_rows], ignore_index=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False)


def main() -> None:
    """Run the S008 extraction workflow."""
    try:
        html = fetch_s008_html()
        new_rows = extract_rows(html)
        validate_output(new_rows)
        save_rows(new_rows)
    except Exception as exc:
        raise SystemExit(f"S008 extraction failed: {exc}") from exc

    category_counts = new_rows.groupby("statement_type").size().to_dict()
    period_counts = new_rows.groupby("period").size().to_dict()
    print(f"S008 extraction complete. Total rows extracted: {len(new_rows)}")
    print(f"Rows by statement_type: {category_counts}")
    print(f"Rows by period: {period_counts}")
    print(f"Output path: {OUTPUT_PATH}")
    print(f"Source URL used: {SOURCE_LINK}")


if __name__ == "__main__":
    main()
