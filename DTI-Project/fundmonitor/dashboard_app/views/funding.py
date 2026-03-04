"""
Funding Module - Main entry point for all funding and transaction related views

This module organizes views into separate functional modules:
- fund_source: FundSource CRUD and breakdown management
- tax_table: TaxTable CRUD operations
- bank_statement: BankStatement CRUD and transaction management
- master_fund_monitoring: MasterFundMonitoring CRUD operations
- api: API endpoints and helper functions
"""

# Fund Source Views
from .fund_source import (
    fund_sources_view,
    fund_source_create,
    fund_source_update,
    fund_source_delete,
    fund_source_detail,
    fund_source_breakdown_add,
    fund_source_breakdown_edit,
    fund_source_breakdown_delete,
)

# Tax Table Views
from .tax_table import (
    tax_table_list,
    tax_table_create,
    tax_table_update,
    tax_table_delete,
)

# Bank Statement Views
from .bank_statement import (
    bank_statement_list,
    bank_statement_create,
    bank_statement_update,
    bank_statement_delete,
)

# Master Fund Monitoring Views
from .master_fund_monitoring import (
    master_fund_monitoring_list,
    master_fund_monitoring_create,
    master_fund_monitoring_update,
    master_fund_monitoring_delete,
)

# API Views
from .api import (
    get_supplier_data,
    get_tax_rates,
)

__all__ = [
    # Fund Source
    'fund_sources_view',
    'fund_source_create',
    'fund_source_update',
    'fund_source_delete',
    'fund_source_detail',
    'fund_source_breakdown_add',
    'fund_source_breakdown_edit',
    'fund_source_breakdown_delete',
    # Tax Table
    'tax_table_list',
    'tax_table_create',
    'tax_table_update',
    'tax_table_delete',
    # Bank Statement
    'bank_statement_list',
    'bank_statement_create',
    'bank_statement_update',
    'bank_statement_delete',
    # Master Fund Monitoring
    'master_fund_monitoring_list',
    'master_fund_monitoring_create',
    'master_fund_monitoring_update',
    'master_fund_monitoring_delete',
    # API
    'get_supplier_data',
    'get_tax_rates',
]
