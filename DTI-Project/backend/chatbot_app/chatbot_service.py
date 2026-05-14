"""
Chatbot service for intent detection and query handling.

This module provides:
- Message cleaning
- Intent detection
- Query handlers for database interactions
- Response formatting
"""

from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta

from mater_fundmonitor_app.models import MasterFundMonitoring
from bank_statement_app.models import BankStatement
from data_management_app.models import Supplier, FundSource, FundSourceBreakdown
from django.contrib.auth.models import User


class ChatbotService:
    """Main chatbot service handling intent detection and query responses."""

    # Intent mapping with keywords
    INTENTS = {
        "total_funds": ["total funds", "balance", "available funds", "total balance"],
        "fund_allocation": ["allocation", "allocated funds", "fund allocation", "budget allocation"],
        "expenses_today": ["expenses today", "spent today", "today expenses", "today's expense"],
        "weekly_expenses": ["weekly expenses", "this week", "week expenses", "expenses this week"],
        "monthly_summary": ["monthly summary", "this month", "month summary", "monthly report"],
        "top_expenses": ["top expenses", "highest expense", "major expenses", "largest expenses"],
        "supplier_list": ["suppliers", "tin list", "supplier list", "all suppliers"],
        "supplier_transactions": [
            "supplier transactions",
            "supplier history",
            "supplier activity",
            "transactions for",
            "transactions from",
        ],
        "top_supplier": ["top supplier", "highest supplier", "major supplier", "top paying supplier"],
        "unreconciled": ["unreconciled", "not matched", "unmatched", "pending reconciliation"],
        "reconciliation_status": ["reconciliation status", "reconciliation", "matched transactions"],
        "financial_summary": ["summary", "financial status", "financial summary", "overall status"],
        "user_activity": ["user activity", "active users", "user activities", "who is active"],
    }

    # Filler words to remove
    FILLER_WORDS = [
        "please",
        "can you",
        "show me",
        "give me",
        "i want",
        "tell me",
        "what is",
        "what are",
        "how many",
        "list",
        "get"
    ]

    @staticmethod
    def clean_message(message: str) -> str:
        """
        Clean the user message.

        Args:
            message: Raw user message

        Returns:
            Cleaned message (lowercase, no filler words, trimmed)
        """
        # Convert to lowercase
        cleaned = message.lower().strip()

        # Remove filler words
        for filler in ChatbotService.FILLER_WORDS:
            # Use word boundaries to avoid partial replacements
            import re
            cleaned = re.sub(r'\b' + re.escape(filler) + r'\b', '', cleaned, flags=re.IGNORECASE)

        # Remove extra spaces
        cleaned = ' '.join(cleaned.split())

        return cleaned

    @staticmethod
    def detect_intent(message: str) -> tuple[str, float]:
        """
        Detect the user's intent from their message.

        Args:
            message: User message

        Returns:
            Tuple of (intent, confidence_score)
        """
        cleaned_message = ChatbotService.clean_message(message)

        # Track intent matches
        intent_matches = {}

        # Check each intent
        for intent, keywords in ChatbotService.INTENTS.items():
            match_count = 0
            for keyword in keywords:
                if keyword in cleaned_message:
                    match_count += 1

            if match_count > 0:
                intent_matches[intent] = match_count

        # If no matches found
        if not intent_matches:
            return "unknown", 0.0

        # Get the best matching intent
        best_intent = max(intent_matches, key=intent_matches.get)

        # Calculate confidence score (number of matches / average keywords per intent)
        avg_keywords = sum(len(keywords) for keywords in ChatbotService.INTENTS.values()) / len(ChatbotService.INTENTS)
        confidence = min(intent_matches[best_intent] / avg_keywords, 1.0)

        return best_intent, round(confidence, 2)

    @staticmethod
    def extract_supplier_name(message: str) -> str:
        """
        Extract supplier name from message.

        Example: "transactions for ABC Corp" -> "ABC Corp"

        Args:
            message: User message

        Returns:
            Extracted supplier name or empty string
        """
        import re

        # Common patterns for supplier queries
        patterns = [
            r'(?:for|from)\s+([A-Za-z0-9\s\-&.]+?)(?:\s+(?:company|corp|supplier|inc|ltd|llc))?(?:\?|$)',
            r'(?:named|called)\s+([A-Za-z0-9\s\-&.]+?)(?:\?|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                supplier_name = match.group(1).strip()
                return supplier_name

        return ""

    @staticmethod
    def format_currency(amount) -> str:
        """Format amount as Philippine Peso."""
        if amount is None:
            amount = 0
        return f"₱{Decimal(str(amount)):,.2f}"

    # ============ Query Handlers ============

    @staticmethod
    def get_total_funds() -> str:
        """
        Get total available funds from all fund sources.

        Returns:
            Formatted response string
        """
        try:
            # Sum of all annual budgets (total allocated)
            total_allocated = FundSource.objects.aggregate(
                total=Sum('annual_budget')
            )['total'] or Decimal('0')

            # Sum of all disbursements/payments made
            total_spent = MasterFundMonitoring.objects.filter(
                payments__isnull=False
            ).aggregate(
                total=Sum('payments')
            )['total'] or Decimal('0')

            # Calculate remaining balance
            remaining_balance = total_allocated - total_spent

            return (
                f"As of today, your total available funds is {ChatbotService.format_currency(remaining_balance)}. "
                f"(Total Allocated: {ChatbotService.format_currency(total_allocated)}, "
                f"Total Spent: {ChatbotService.format_currency(total_spent)})"
            )
        except Exception as e:
            return f"I encountered an error retrieving fund data: {str(e)}"

    @staticmethod
    def get_fund_allocation() -> str:
        """
        Get fund allocation details by source.

        Returns:
            Formatted response string
        """
        try:
            fund_sources = FundSource.objects.all()

            if not fund_sources.exists():
                return "No fund sources are currently configured."

            allocation_details = []
            total_allocation = Decimal('0')

            for fund in fund_sources:
                allocation_details.append(
                    f"• {fund.name}: {ChatbotService.format_currency(fund.annual_budget)}"
                )
                total_allocation += fund.annual_budget

            allocation_text = "\n".join(allocation_details)
            return (
                f"Here's the fund allocation breakdown:\n{allocation_text}\n\n"
                f"Total Allocation: {ChatbotService.format_currency(total_allocation)}"
            )
        except Exception as e:
            return f"I encountered an error retrieving fund allocation: {str(e)}"

    @staticmethod
    def get_expenses_today() -> str:
        """
        Get total expenses for today.

        Returns:
            Formatted response string
        """
        try:
            today = timezone.now().date()

            today_expenses = MasterFundMonitoring.objects.filter(
                date=today,
                payments__isnull=False
            ).aggregate(
                total=Sum('payments')
            )['total'] or Decimal('0')

            transaction_count = MasterFundMonitoring.objects.filter(
                date=today,
                payments__isnull=False
            ).count()

            return (
                f"Today's expenses total {ChatbotService.format_currency(today_expenses)} "
                f"across {transaction_count} transactions."
            )
        except Exception as e:
            return f"I encountered an error retrieving today's expenses: {str(e)}"

    @staticmethod
    def get_weekly_expenses() -> str:
        """
        Get total expenses for the current week.

        Returns:
            Formatted response string
        """
        try:
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())

            weekly_expenses = MasterFundMonitoring.objects.filter(
                date__gte=week_start,
                date__lte=today,
                payments__isnull=False
            ).aggregate(
                total=Sum('payments')
            )['total'] or Decimal('0')

            transaction_count = MasterFundMonitoring.objects.filter(
                date__gte=week_start,
                date__lte=today,
                payments__isnull=False
            ).count()

            return (
                f"This week's expenses total {ChatbotService.format_currency(weekly_expenses)} "
                f"across {transaction_count} transactions "
                f"(from {week_start} to {today})."
            )
        except Exception as e:
            return f"I encountered an error retrieving weekly expenses: {str(e)}"

    @staticmethod
    def get_monthly_summary() -> str:
        """
        Get financial summary for the current month.

        Returns:
            Formatted response string
        """
        try:
            today = timezone.now().date()
            month_start = today.replace(day=1)

            monthly_expenses = MasterFundMonitoring.objects.filter(
                date__gte=month_start,
                date__lte=today,
                payments__isnull=False
            ).aggregate(
                total=Sum('payments')
            )['total'] or Decimal('0')

            monthly_downloads = MasterFundMonitoring.objects.filter(
                date__gte=month_start,
                date__lte=today,
                downloads__isnull=False
            ).aggregate(
                total=Sum('downloads')
            )['total'] or Decimal('0')

            transaction_count = MasterFundMonitoring.objects.filter(
                date__gte=month_start,
                date__lte=today
            ).count()

            total_activity = monthly_expenses + monthly_downloads

            return (
                f"This month's summary ({month_start.strftime('%B %Y')}):\n"
                f"• Expenses: {ChatbotService.format_currency(monthly_expenses)}\n"
                f"• Downloads: {ChatbotService.format_currency(monthly_downloads)}\n"
                f"• Total Activity: {ChatbotService.format_currency(total_activity)}\n"
                f"• Transactions: {transaction_count}"
            )
        except Exception as e:
            return f"I encountered an error retrieving monthly summary: {str(e)}"

    @staticmethod
    def get_top_expenses() -> str:
        """
        Get top 5 highest expenses.

        Returns:
            Formatted response string
        """
        try:
            top_expenses = MasterFundMonitoring.objects.filter(
                payments__isnull=False
            ).order_by('-payments')[:5]

            if not top_expenses.exists():
                return "No expenses found in the system."

            expense_details = []
            for idx, expense in enumerate(top_expenses, 1):
                expense_details.append(
                    f"{idx}. {expense.payee.supplier} - {ChatbotService.format_currency(expense.payments)} "
                    f"({expense.date.strftime('%Y-%m-%d')})"
                )

            expenses_text = "\n".join(expense_details)
            return (
                f"Top 5 highest expenses:\n{expenses_text}"
            )
        except Exception as e:
            return f"I encountered an error retrieving top expenses: {str(e)}"

    @staticmethod
    def get_supplier_list() -> str:
        """
        Get list of all suppliers.

        Returns:
            Formatted response string
        """
        try:
            suppliers = Supplier.objects.all().order_by('supplier')

            if not suppliers.exists():
                return "No suppliers are currently configured."

            supplier_details = []
            for supplier in suppliers:
                tin_info = f" (TIN: {supplier.tin})" if supplier.tin else ""
                supplier_details.append(f"• {supplier.supplier}{tin_info}")

            suppliers_text = "\n".join(supplier_details)
            return (
                f"Total suppliers: {suppliers.count()}\n\n{suppliers_text}"
            )
        except Exception as e:
            return f"I encountered an error retrieving suppliers: {str(e)}"

    @staticmethod
    def get_supplier_transactions(supplier_name: str = "") -> str:
        """
        Get transactions for a specific supplier or all suppliers.

        Args:
            supplier_name: Optional supplier name to filter by

        Returns:
            Formatted response string
        """
        try:
            query = MasterFundMonitoring.objects.filter(
                payments__isnull=False
            ).select_related('payee')

            if supplier_name:
                query = query.filter(payee__supplier__icontains=supplier_name)

            if not query.exists():
                return (
                    f"No transactions found for supplier '{supplier_name}'."
                    if supplier_name
                    else "No transactions found."
                )

            # Group by supplier and get summary
            suppliers_summary = {}
            for transaction in query:
                supplier_key = transaction.payee.supplier
                if supplier_key not in suppliers_summary:
                    suppliers_summary[supplier_key] = {
                        'total': Decimal('0'),
                        'count': 0
                    }
                suppliers_summary[supplier_key]['total'] += transaction.payments or Decimal('0')
                suppliers_summary[supplier_key]['count'] += 1

            supplier_details = []
            for supplier, data in sorted(suppliers_summary.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
                supplier_details.append(
                    f"• {supplier}: {ChatbotService.format_currency(data['total'])} ({data['count']} transactions)"
                )

            suppliers_text = "\n".join(supplier_details)
            header = (
                f"Supplier transactions for '{supplier_name}':\n"
                if supplier_name
                else "Top 10 suppliers by transaction volume:\n"
            )

            return header + suppliers_text
        except Exception as e:
            return f"I encountered an error retrieving supplier transactions: {str(e)}"

    @staticmethod
    def get_top_supplier() -> str:
        """
        Get the supplier with the highest transaction amount.

        Returns:
            Formatted response string
        """
        try:
            top_supplier_query = MasterFundMonitoring.objects.filter(
                payments__isnull=False
            ).values('payee__supplier').annotate(
                total=Sum('payments'),
                count=Count('id')
            ).order_by('-total')[:1]

            if not top_supplier_query.exists():
                return "No supplier transactions found."

            top = top_supplier_query[0]
            return (
                f"The top payee is **{top['payee__supplier']}** with a total of "
                f"{ChatbotService.format_currency(top['total'])} across {top['count']} transactions."
            )
        except Exception as e:
            return f"I encountered an error retrieving top payee: {str(e)}"

    @staticmethod
    def get_unreconciled_transactions() -> str:
        """
        Get unreconciled (unmatched) bank transactions.

        Returns:
            Formatted response string
        """
        try:
            # Bank transactions that haven't been cleared/matched
            unreconciled = BankStatement.objects.filter(
                is_archived=False
            ).exclude(
                debit=0
            ).select_related('account')

            if not unreconciled.exists():
                return "All bank transactions are reconciled. Great job!"

            total_unreconciled = unreconciled.aggregate(
                total=Sum('debit')
            )['total'] or Decimal('0')

            return (
                f"You have {unreconciled.count()} unreconciled transactions totaling "
                f"{ChatbotService.format_currency(total_unreconciled)}. "
                f"Please review and match these transactions."
            )
        except Exception as e:
            return f"I encountered an error retrieving unreconciled transactions: {str(e)}"

    @staticmethod
    def get_reconciliation_status() -> str:
        """
        Get bank reconciliation status.

        Returns:
            Formatted response string
        """
        try:
            total_transactions = BankStatement.objects.filter(
                is_archived=False
            ).count()

            cleared_transactions = BankStatement.objects.filter(
                is_archived=False,
                status="Cleared"
            ).count()

            uncleared = total_transactions - cleared_transactions
            reconciliation_rate = (
                (cleared_transactions / total_transactions * 100)
                if total_transactions > 0
                else 0
            )

            total_amount = BankStatement.objects.filter(
                is_archived=False
            ).aggregate(total=Sum('debit'))['total'] or Decimal('0')

            cleared_amount = BankStatement.objects.filter(
                is_archived=False,
                status="Cleared"
            ).aggregate(total=Sum('debit'))['total'] or Decimal('0')

            return (
                f"Bank Reconciliation Status:\n"
                f"• Total Transactions: {total_transactions}\n"
                f"• Cleared: {cleared_transactions} ({reconciliation_rate:.1f}%)\n"
                f"• Uncleared: {uncleared}\n"
                f"• Total Amount: {ChatbotService.format_currency(total_amount)}\n"
                f"• Cleared Amount: {ChatbotService.format_currency(cleared_amount)}"
            )
        except Exception as e:
            return f"I encountered an error retrieving reconciliation status: {str(e)}"

    @staticmethod
    def get_financial_summary() -> str:
        """
        Get overall financial summary.

        Returns:
            Formatted response string
        """
        try:
            # Fund statistics
            total_funds = FundSource.objects.aggregate(
                total=Sum('annual_budget')
            )['total'] or Decimal('0')

            total_spent = MasterFundMonitoring.objects.filter(
                payments__isnull=False
            ).aggregate(total=Sum('payments'))['total'] or Decimal('0')

            remaining = total_funds - total_spent

            # Transaction count
            transaction_count = MasterFundMonitoring.objects.count()

            # Supplier count
            supplier_count = Supplier.objects.count()

            return (
                f"Financial Summary:\n"
                f"• Total Funds: {ChatbotService.format_currency(total_funds)}\n"
                f"• Total Spent: {ChatbotService.format_currency(total_spent)}\n"
                f"• Remaining Balance: {ChatbotService.format_currency(remaining)}\n"
                f"• Spending Rate: {(total_spent / total_funds * 100 if total_funds > 0 else 0):.1f}%\n"
                f"• Total Transactions: {transaction_count}\n"
            )
        except Exception as e:
            return f"I encountered an error retrieving financial summary: {str(e)}"

    @staticmethod
    def get_user_activity() -> str:
        """
        Get active user statistics.

        Returns:
            Formatted response string
        """
        try:
            from django.utils import timezone as tz
            from datetime import timedelta

            # Users active in the last 7 days
            week_ago = tz.now() - timedelta(days=7)
            active_users = User.objects.filter(
                last_login__gte=week_ago
            ).count()

            total_users = User.objects.filter(is_active=True).count()

            # Get recent activity
            recent_activity = User.objects.filter(
                last_login__isnull=False
            ).order_by('-last_login')[:5]

            activity_details = []
            for user in recent_activity:
                last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never"
                activity_details.append(f"• {user.first_name or user.username} - Last seen: {last_login}")

            activity_text = "\n".join(activity_details) if activity_details else "No recent activity"

            return (
                f"User Activity Summary:\n"
                f"• Active Users (7 days): {active_users} / {total_users}\n"
                f"• Recent Logins:\n{activity_text}"
            )
        except Exception as e:
            return f"I encountered an error retrieving user activity: {str(e)}"

    @staticmethod
    def get_response(intent: str, message: str = "") -> str:
        """
        Get chatbot response based on detected intent.

        Args:
            intent: Detected intent
            message: Original user message (for context)

        Returns:
            Response string
        """
        # Map intents to handler functions
        handlers = {
            "total_funds": ChatbotService.get_total_funds,
            "fund_allocation": ChatbotService.get_fund_allocation,
            "expenses_today": ChatbotService.get_expenses_today,
            "weekly_expenses": ChatbotService.get_weekly_expenses,
            "monthly_summary": ChatbotService.get_monthly_summary,
            "top_expenses": ChatbotService.get_top_expenses,
            "supplier_list": ChatbotService.get_supplier_list,
            "supplier_transactions": lambda: ChatbotService.get_supplier_transactions(
                ChatbotService.extract_supplier_name(message)
            ),
            "top_supplier": ChatbotService.get_top_supplier,
            "top_payee": ChatbotService.get_top_supplier,
            "unreconciled": ChatbotService.get_unreconciled_transactions,
            "reconciliation_status": ChatbotService.get_reconciliation_status,
            "financial_summary": ChatbotService.get_financial_summary,
            "user_activity": ChatbotService.get_user_activity,
        }

        # Get handler function or return default response
        handler = handlers.get(intent)

        if handler:
            return handler()
        else:
            return (
                "Sorry, I couldn't understand your request. Try asking about funds, "
                "expenses, suppliers, transactions, reconciliation, or user activity."
            )

    @staticmethod
    def process_message(message: str, user=None) -> dict:
        """
        Process user message and return chatbot response.

        Args:
            message: User's message
            user: Django user object (optional)

        Returns:
            Dictionary with intent, confidence, response, and other metadata
        """
        # Detect intent
        intent, confidence = ChatbotService.detect_intent(message)

        # Get response
        response = ChatbotService.get_response(intent, message)

        # If intent is unknown, use fallback response
        if intent == "unknown":
            response = (
                "Sorry, I couldn't understand your request. Try asking about funds, "
                "expenses, suppliers, transactions, reconciliation, or user activity."
            )

        return {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "message_cleaned": ChatbotService.clean_message(message),
        }
