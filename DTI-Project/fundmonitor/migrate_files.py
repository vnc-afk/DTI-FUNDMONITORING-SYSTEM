#!/usr/bin/env python
"""
Migration script to reorganize project files
This script moves templates and static files to their new organized locations
"""

import os
import shutil
from pathlib import Path

# Get the base path
BASE_DIR = Path(__file__).parent.resolve()

# Define file mappings: (source_path, destination_path)
TEMPLATE_MOVES = [
    # Staff templates
    ('templates/staff_list.html', 'templates/staff/list.html'),
    ('templates/staff_form.html', 'templates/staff/form.html'),
    ('templates/staff_confirm_delete.html', 'templates/staff/confirm_delete.html'),
    
    # Supplier templates
    ('templates/supplier_list.html', 'templates/supplier/list.html'),
    ('templates/supplier_form.html', 'templates/supplier/form.html'),
    ('templates/supplier_confirm_delete.html', 'templates/supplier/confirm_delete.html'),
    
    # Funding templates
    ('templates/fund_sources.html', 'templates/funding/fund_sources.html'),
    ('templates/fund_source_form.html', 'templates/funding/fund_source_form.html'),
    ('templates/bank_statement.html', 'templates/funding/bank_statement.html'),
    ('templates/bank_statement_form.html', 'templates/funding/bank_statement_form.html'),
    
    # Report templates
    ('templates/expenses_report.html', 'templates/reports/expenses_report.html'),
    ('templates/mooe_report.html', 'templates/reports/mooe_report.html'),
    ('templates/fund_report.html', 'templates/reports/fund_report.html'),
    ('templates/negosyo_center_report.html', 'templates/reports/negosyo_center_report.html'),
    
    # Allocation/Disbursement templates
    ('templates/disbursement_table.html', 'templates/reports/allocations/disbursement_table.html'),
    ('templates/downloads_table.html', 'templates/reports/allocations/downloads_table.html'),
    ('templates/fund_disbursement_table.html', 'templates/reports/allocations/fund_disbursement_table.html'),
    ('templates/fund_downloads_table.html', 'templates/reports/allocations/fund_downloads_table.html'),
    ('templates/nc_district1_table.html', 'templates/reports/allocations/nc_district1_table.html'),
    ('templates/nc_district2_table.html', 'templates/reports/allocations/nc_district2_table.html'),
    ('templates/nc_district3_table.html', 'templates/reports/allocations/nc_district3_table.html'),
    ('templates/tin.html', 'templates/reports/allocations/tin.html'),
]

STATIC_MOVES = [
    # CSS files
    ('static/dashboard_app/css/base.css', 'static/dashboard_app/css/layouts/base.css'),
    ('static/dashboard_app/css/sidebar.css', 'static/dashboard_app/css/layouts/sidebar.css'),
    ('static/dashboard_app/css/form.css', 'static/dashboard_app/css/components/form.css'),
    ('static/dashboard_app/css/table.css', 'static/dashboard_app/css/components/table.css'),
    ('static/dashboard_app/css/report.css', 'static/dashboard_app/css/pages/report.css'),
    
    # JS files
    ('static/dashboard_app/js/app.js', 'static/dashboard_app/js/modules/app.js'),
    ('static/dashboard_app/js/expenses.js', 'static/dashboard_app/js/modules/expenses.js'),
    ('static/dashboard_app/js/table.js', 'static/dashboard_app/js/modules/table.js'),
]


def move_files(mappings, base_path):
    """Move files from old locations to new locations"""
    moved = 0
    failed = 0
    
    for old_path, new_path in mappings:
        source = base_path / 'dashboard_app' / old_path
        dest = base_path / 'dashboard_app' / new_path
        
        if source.exists():
            try:
                # Create destination directory if it doesn't exist
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(source), str(dest))
                print(f"✓ Moved: {old_path} → {new_path}")
                moved += 1
            except Exception as e:
                print(f"✗ Failed to move {old_path}: {e}")
                failed += 1
        else:
            print(f"⚠ Source not found: {old_path}")
            failed += 1
    
    return moved, failed


def main():
    """Run the migration"""
    print("=" * 70)
    print("DTI Fund Monitoring System - File Migration Script")
    print("=" * 70)
    print()
    
    app_path = BASE_DIR / 'dashboard_app'
    if not app_path.exists():
        print(f"Error: dashboard_app directory not found at {app_path}")
        return False
    
    print("Starting file migration...\n")
    
    # Move templates
    print("Moving template files...")
    t_moved, t_failed = move_files(TEMPLATE_MOVES, BASE_DIR)
    print(f"Templates: {t_moved} moved, {t_failed} failed\n")
    
    # Move static files
    print("Moving static files...")
    s_moved, s_failed = move_files(STATIC_MOVES, BASE_DIR)
    print(f"Static files: {s_moved} moved, {s_failed} failed\n")
    
    print("=" * 70)
    print("Migration complete!")
    print(f"Total: {t_moved + s_moved} files moved, {t_failed + s_failed} failed")
    print("=" * 70)
    
    return t_failed + s_failed == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
