"""Archive management utilities"""

from django.utils import timezone

from bank_statement_app.models import BankStatement
from mater_fundmonitor_app.models import MasterFundMonitoring


def get_archive_years():
    """Return years that have archiveable data in either model."""
    years = {
        int(year)
        for year in MasterFundMonitoring.objects.all_with_archived()
        .filter(date__isnull=False)
        .values_list("date__year", flat=True)
        if year is not None
    }
    years.update(
        int(year)
        for year in BankStatement.objects.all_with_archived()
        .filter(date__isnull=False)
        .values_list("date__year", flat=True)
        if year is not None
    )

    if not years:
        years.add(timezone.now().year)

    return sorted(years, reverse=True)


def get_archive_year_statuses():
    """Return per-year archive and restore availability counts."""
    year_statuses = []

    for year in get_archive_years():
        stats = get_archive_stats(year)
        fund_stats = stats.get("fund_monitoring_year", {})
        bank_stats = stats.get("bank_statements_year", {})

        active_fund_monitoring = int(fund_stats.get("active", 0) or 0)
        archived_fund_monitoring = int(fund_stats.get("archived", 0) or 0)
        active_bank_statements = int(bank_stats.get("active", 0) or 0)
        archived_bank_statements = int(bank_stats.get("archived", 0) or 0)

        active_total = active_fund_monitoring + active_bank_statements
        archived_total = archived_fund_monitoring + archived_bank_statements

        year_statuses.append(
            {
                "year": year,
                "active_fund_monitoring": active_fund_monitoring,
                "archived_fund_monitoring": archived_fund_monitoring,
                "active_bank_statements": active_bank_statements,
                "archived_bank_statements": archived_bank_statements,
                "active_total": active_total,
                "archived_total": archived_total,
                "can_archive": active_total > 0,
                "can_restore": archived_total > 0,
            }
        )

    return year_statuses


def archive_by_year(year, user=None, reason=""):
    """
    Archive all transactions for a given year.

    Args:
        year (int): Year to archive (e.g., 2026)
        user: User performing the archival
        reason (str): Reason for archival

    Returns:
        dict: Statistics about archived records
    """
    from datetime import date

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Archive fund monitoring records
    fund_records = MasterFundMonitoring.objects.all_with_archived().filter(
        date__range=[start_date, end_date], is_archived=False
    )
    fund_count = fund_records.count()

    for record in fund_records:
        record.archive(user=user, reason=reason or f"Archived year {year}")

    # Archive bank statements
    bank_records = BankStatement.objects.all_with_archived().filter(
        date__range=[start_date, end_date], is_archived=False
    )
    bank_count = bank_records.count()

    for record in bank_records:
        record.archive(user=user, reason=reason or f"Archived year {year}")

    return {
        "fund_monitoring_count": fund_count,
        "bank_statement_count": bank_count,
        "total_archived": fund_count + bank_count,
        "year": year,
        "archived_by": user.username if user else "System",
        "archived_at": timezone.now(),
    }


def unarchive_by_year(year):
    """
    Unarchive all transactions for a given year.

    Args:
        year (int): Year to unarchive (e.g., 2026)

    Returns:
        dict: Statistics about unarchived records
    """
    from datetime import date

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Unarchive fund monitoring records
    fund_records = MasterFundMonitoring.objects.all_with_archived().filter(
        date__range=[start_date, end_date], is_archived=True
    )
    fund_count = fund_records.count()

    for record in fund_records:
        record.unarchive()

    # Unarchive bank statements
    bank_records = BankStatement.objects.all_with_archived().filter(
        date__range=[start_date, end_date], is_archived=True
    )
    bank_count = bank_records.count()

    for record in bank_records:
        record.unarchive()

    return {
        "fund_monitoring_count": fund_count,
        "bank_statement_count": bank_count,
        "total_unarchived": fund_count + bank_count,
        "year": year,
    }


def get_archive_stats(year=None):
    """Get archive statistics."""
    from datetime import date

    stats = {
        "active_fund_monitoring": MasterFundMonitoring.objects.filter(
            is_archived=False
        ).count(),
        "archived_fund_monitoring": MasterFundMonitoring.objects.archived().count(),
        "active_bank_statements": BankStatement.objects.filter(
            is_archived=False
        ).count(),
        "archived_bank_statements": BankStatement.objects.archived().count(),
    }

    if year:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        stats["fund_monitoring_year"] = {
            "active": MasterFundMonitoring.objects.filter(
                date__range=[start_date, end_date], is_archived=False
            ).count(),
            "archived": MasterFundMonitoring.objects.all_with_archived()
            .filter(date__range=[start_date, end_date], is_archived=True)
            .count(),
        }

        stats["bank_statements_year"] = {
            "active": BankStatement.objects.filter(
                date__range=[start_date, end_date], is_archived=False
            ).count(),
            "archived": BankStatement.objects.all_with_archived()
            .filter(date__range=[start_date, end_date], is_archived=True)
            .count(),
        }

    return stats
