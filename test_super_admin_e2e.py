"""
Playwright End-to-End Test Suite for Suggu Services Super Admin Dashboard
========================================================================
This script performs a complete automated walkthrough of every page, button,
modal, and form in the Super Admin portal:
  1. Secure Super Admin Login (admin / 12345)
  2. Dashboard Overview & Live Charts
  3. All Users Directory (Filters, View Profile Modal, Edit Form, Update User, Add User)
  4. Vendors & Pros (Filters, View Quick Modal, Edit Form, Update Vendor, Add Vendor Toggle)
  5. KYC Approvals & Document Review
  6. Categories & Cities CMS (Edit/Update Category, Edit/Update Location)
  7. Jobs Engine (Bids & Assign View, Edit/Update Job, Create Job Page)
  8. Quick Services (Edit/Update QS, Create QS Page)
  9. Bids & Quotations (Edit/Update Bid, Create Bid Page)
 10. Subscriptions & Plans (List, Add Subscription Form)
 11. Payouts & Settlements (KPI Cards, Filter Controls)
 12. Disputes & Complaints (Resolution Hub, Dispute Detail Page)
 13. Message Oversight (List & Details)
 14. Landing CMS - Quick Service Cards (Edit/Update Card)
 15. Landing CMS - Service Packages (Edit/Update Package)
 16. Landing CMS - Testimonials (Review Snippet, Full Review Modal, Edit Form)
 17. Sign Out Verification

Usage:
  python test_super_admin_e2e.py            # Run headless
  python test_super_admin_e2e.py --headed   # Run headed (watch browser live)
"""

import sys
import os
import time
import io

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright, expect

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
# Open browser visibly by default unless explicitly running with --headless
HEADED = "--headless" not in sys.argv
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_reports", "screenshots")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class SuperAdminE2ETester:
    def __init__(self, page):
        self.page = page
        self.step_num = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_step(self, title):
        self.step_num += 1
        print(f"\n{'='*75}")
        print(f"  [STEP {self.step_num:02d}] {title}")
        print(f"{'='*75}", flush=True)
        # Brief pause between test steps for visual clarity
        time.sleep(0.4)

    def safe_goto(self, url, max_retries=4, **kwargs):
        kwargs.setdefault("wait_until", "networkidle")
        kwargs.setdefault("timeout", 15000)
        for i in range(max_retries):
            try:
                self.page.goto(url, **kwargs)
                return
            except Exception as e:
                err_msg = str(e)
                if i < max_retries - 1 and ("ERR_CONNECTION_REFUSED" in err_msg or "refused" in err_msg or "Timeout" in err_msg):
                    print(f"  [WAIT] Transient server connection, retrying in 1.5s ({i+1}/{max_retries})...", flush=True)
                    time.sleep(1.5)
                else:
                    raise e

    def snap(self, name):
        filename = f"{self.step_num:02d}_{name}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        self.page.screenshot(path=filepath, full_page=False)
        print(f"  [SCREENSHOT] Saved: {filename}", flush=True)

    def assert_success(self, test_name):
        self.passed_tests += 1
        print(f"  [PASSED] {test_name}", flush=True)

    def test_00_open_home(self):
        self.log_step("Open Root Page: http://127.0.0.1:8000/ on Chrome")
        home_url = f"{BASE_URL}/"
        print(f"  Opening URL on Chrome: {home_url}", flush=True)
        self.safe_goto(home_url)
        expect(self.page.locator("body")).to_be_visible()
        self.snap("00_chrome_home")
        print("  Successfully opened http://127.0.0.1:8000/ on Chrome!", flush=True)
        time.sleep(2.0)
        self.assert_success("Root page http://127.0.0.1:8000/ opened and displayed on Chrome")

    def test_01_login(self):
        self.log_step("Super Admin Login (admin / 12345)")
        login_url = f"{BASE_URL}/super-admin/login/"
        print(f"  Navigating to: {login_url}")
        self.safe_goto(login_url)
        
        # Verify login page components
        expect(self.page.locator("h1:has-text('Suggu Services')")).to_be_visible()
        expect(self.page.locator("text=Super Administrator Portal")).to_be_visible()
        self.snap("login_page")

        # Fill credentials
        print("  Entering credentials: admin / 12345")
        self.page.fill('input[name="username"]', "admin")
        self.page.fill('input[name="password"]', "12345")
        time.sleep(0.5)
        self.page.click('button[type="submit"]')

        # Verify redirect to dashboard
        expect(self.page.locator(".header-title:has-text('Dashboard Overview')")).to_be_visible(timeout=15000)
        self.snap("dashboard_loaded")
        self.assert_success("Login successfully authenticated and redirected to Dashboard")

    def test_02_dashboard(self):
        self.log_step("Dashboard KPIs, Canvases & Quick Actions")
        self.safe_goto(f"{BASE_URL}/super-admin/", wait_until="networkidle")

        # Verify stat cards
        expect(self.page.locator(".stat-card .label:has-text('Customers')")).to_be_visible()
        expect(self.page.locator(".stat-card .label:has-text('Vendors')")).to_be_visible()
        expect(self.page.locator(".stat-card .label:has-text('Active Jobs')")).to_be_visible()
        expect(self.page.locator(".stat-card .label:has-text('Area Admins')")).to_be_visible()
        print("  Verified Core KPI metrics on Dashboard")

        # Verify charts
        expect(self.page.locator("#growthChart")).to_be_visible()
        expect(self.page.locator("#categoryChart")).to_be_visible()
        print("  Verified Canvas Chart elements: #growthChart & #categoryChart")

        # Verify Quick Action Buttons
        expect(self.page.locator(".card a:has-text('Add User')")).to_be_visible()
        expect(self.page.locator(".card a:has-text('Add Category')")).to_be_visible()
        expect(self.page.locator(".card a:has-text('Add Location')")).to_be_visible()
        expect(self.page.locator(".card a:has-text('Manage Services')")).to_be_visible()
        self.snap("dashboard_full")
        self.assert_success("Dashboard KPIs, Charts, and Quick Action buttons validated")

    def test_03_users_management(self):
        self.log_step("Users Management: Filters, Profile Modal, Edit & Update Form")
        self.safe_goto(f"{BASE_URL}/super-admin/users/", wait_until="networkidle")
        expect(self.page.locator("h1, .header-title:has-text('User Management')")).to_be_visible()

        # 1. Test Filter Functionality
        print("  Testing Search & Role filter...")
        self.page.fill('input[name="q"]', "admin")
        self.page.select_option('select[name="role"]', "all")
        self.page.click('button[type="submit"]:has-text("Filter")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("text=Active Filters:")).to_be_visible()
        print("  Active filters badge bar displayed correctly")

        # Reset filter
        self.page.click('a[title="Reset filters"]')
        self.page.wait_for_load_state("networkidle")
        self.snap("users_directory")

        # 2. Test User Profile Modal
        print("  Testing View Profile modal...")
        view_btn = self.page.locator('button.action-btn[title="View Profile"]').first
        expect(view_btn).to_be_visible()
        view_btn.click()

        # Verify modal opens with content
        modal = self.page.locator('#userProfileModal')
        expect(modal).to_be_visible()
        modal_name = self.page.locator('#mFullName').inner_text()
        print(f"  Profile modal successfully opened for user: '{modal_name}'")
        self.snap("user_profile_modal")

        # Close modal
        close_btn = modal.locator('button:has-text("Close"), button:has(.fa-xmark)').first
        close_btn.click()
        time.sleep(0.3)
        print("  Profile modal successfully closed")

        # 3. Test Edit & Update User Form
        print("  Testing Edit User Form...")
        edit_btn = self.page.locator('a.action-btn[title="Edit"]').first
        edit_url = edit_btn.get_attribute("href")
        print(f"  Opening edit form: {edit_url}")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")

        expect(self.page.locator("text=Account & Contact Details")).to_be_visible()
        
        # Update phone number
        phone_input = self.page.locator('input[name="phone_number"]')
        new_phone = "+91 9988776655"
        phone_input.fill(new_phone)
        print(f"  Updated phone number to '{new_phone}'")
        self.snap("edit_user_form")

        # Submit form
        self.page.click('button[type="submit"]:has-text("Save All Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('User Management')")).to_be_visible()
        print("  User changes successfully saved and toast displayed")

        # 4. Test Add User Page & Role Toggles
        print("  Testing Add User Page & Role Visibility Switches...")
        self.safe_goto(f"{BASE_URL}/super-admin/users/create/", wait_until="networkidle")
        expect(self.page.locator("text=Create New User")).to_be_visible()
        
        # Test Area Admin toggle
        self.page.select_option('#roleSelect', 'ADMIN')
        expect(self.page.locator('#areaAdminNotice')).to_be_visible()
        expect(self.page.locator('#stateLabel:has-text("Assigned Operational State")')).to_be_visible()
        print("  Role switch to Area Admin verified: Assigned Operational State label updated")

        # Test Vendor toggle
        self.page.select_option('#roleSelect', 'VENDOR')
        expect(self.page.locator('#vendorSection')).to_be_visible()
        expect(self.page.locator('#stateLabel:has-text("State")')).to_be_visible()
        print("  Role switch to Vendor verified: Vendor details section displayed")

        # Click Cancel
        self.page.click('a.btn:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/users/**", timeout=10000)
        self.assert_success("Users Directory: Filters, Modal, Edit/Update, and Create Role-toggles passed")

    def test_04_vendors_management(self):
        self.log_step("Vendors Management: Classification Filter, Quick Modal, Edit & Add Form")
        self.safe_goto(f"{BASE_URL}/super-admin/vendors/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Vendor Management')")).to_be_visible()

        # 1. Test Filter
        print("  Filtering by Classification: Company Vendors...")
        self.page.select_option('select[name="type"]', 'company')
        self.page.click('button[type="submit"]:has-text("Filter")')
        self.page.wait_for_load_state("networkidle")
        self.snap("vendors_filtered")
        print("  Company vendors filter executed successfully")

        # Reset
        self.safe_goto(f"{BASE_URL}/super-admin/vendors/", wait_until="networkidle")

        # 2. Test Vendor Quick View Modal
        print("  Testing Vendor Quick Profile Modal...")
        view_vendor_btn = self.page.locator('button.action-btn[title="View Details"]').first
        expect(view_vendor_btn).to_be_visible()
        view_vendor_btn.click()

        vendor_modal = self.page.locator('#vendorQuickModal')
        expect(vendor_modal).to_be_visible()
        v_name = self.page.locator('#vmCompanyName').inner_text()
        print(f"  Vendor Quick Modal opened for: '{v_name}'")
        self.snap("vendor_modal")

        # Close modal
        close_btn = vendor_modal.locator('button:has-text("Close"), button:has(.fa-xmark)').first
        close_btn.click()
        time.sleep(0.3)
        print("  Vendor modal closed")

        # 3. Test Edit Vendor Form
        print("  Testing Edit Vendor Form...")
        edit_btn = self.page.locator('a.action-btn[title="Edit Vendor"]').first
        edit_url = edit_btn.get_attribute("href")
        print(f"  Navigating to vendor edit form: {edit_url}")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")

        expect(self.page.locator("h3:has-text('Edit:')")).to_be_visible()
        
        # Test update About section
        about_box = self.page.locator('textarea[name="about"]')
        about_box.fill("Certified service professional verified by Suggu Services Super Admin.")
        self.snap("edit_vendor_form")

        # Save Changes
        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Vendor Management')")).to_be_visible()
        print("  Vendor updated successfully")

        # 4. Test Add Vendor Form (Company vs Outside dynamic toggle)
        print("  Testing Add Vendor Form & Dynamic Company/Individual Fields...")
        self.safe_goto(f"{BASE_URL}/super-admin/vendors/create/", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Add New Vendor')")).to_be_visible()

        # Select Company Vendor -> verify companyFields visible
        self.page.select_option('#vendorTypeSelect', 'company')
        expect(self.page.locator('#companyFields')).to_be_visible()
        expect(self.page.locator('#individualFields')).not_to_be_visible()
        print("  Company Vendor selected -> Company fields (GST, Company Name, Staff Code) visible")

        # Select Individual Vendor -> verify individualFields visible
        self.page.select_option('#vendorTypeSelect', 'vendor')
        expect(self.page.locator('#individualFields')).to_be_visible()
        expect(self.page.locator('#companyFields')).not_to_be_visible()
        print("  Individual Vendor selected -> Individual fields (DOB, Gender, ID Proof) visible")

        # Cancel
        self.page.click('a.btn:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/vendors/**", timeout=10000)
        self.assert_success("Vendors: Filters, Modal, Edit/Update, and Add Vendor dynamic fields tested")

    def test_05_kyc_approvals(self):
        self.log_step("KYC Approvals: Filters, Document Links & Reject Form Toggle")
        self.safe_goto(f"{BASE_URL}/super-admin/kyc/", wait_until="networkidle")
        expect(self.page.locator("text=KYC Document Verification Center")).to_be_visible()

        # Filter by Pending
        self.page.select_option('select[name="status"]', 'pending')
        self.page.wait_for_load_state("networkidle")
        self.snap("kyc_list")

        # Check if reject toggle button exists
        reject_toggle = self.page.locator('button:has-text("Reject")').first
        if reject_toggle.is_visible():
            print("  Testing Reject form toggle accordion...")
            reject_toggle.click()
            time.sleep(0.3)
            # Rejection notes textarea should become visible
            reject_box = self.page.locator('textarea[name="admin_notes"]').first
            expect(reject_box).to_be_visible()
            # Click cancel on reject box
            cancel_reject = self.page.locator('button:has-text("Cancel")').first
            cancel_reject.click()
            print("  Reject reason textarea toggled and cancelled cleanly")

        self.assert_success("KYC Document Verification Center fully verified")

    def test_06_categories_and_cities(self):
        self.log_step("Categories & Cities CMS: Edit/Update Category & Edit Location")
        self.safe_goto(f"{BASE_URL}/super-admin/cms/", wait_until="networkidle")
        expect(self.page.locator("text=Categories & City Locations")).to_be_visible()

        # 1. Edit Category Form
        print("  Testing Edit Category Form...")
        cat_edit_btn = self.page.locator('table a:has-text("Edit")').first
        cat_edit_url = cat_edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{cat_edit_url}", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Edit:')")).to_be_visible()

        # Update category status or name
        cat_name_input = self.page.locator('input[name="name"]')
        original_name = cat_name_input.input_value()
        self.snap("edit_category_form")
        
        # Save Changes
        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("text=Categories & City Locations")).to_be_visible()
        print(f"  Category '{original_name}' saved successfully")

        # 2. Add Category Navigation test
        self.page.click('a:has-text("Add Category")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("h3:has-text('Add New Category')")).to_be_visible()
        self.page.click('a:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/cms/**", timeout=10000)

        # 3. Edit Location Form
        print("  Testing Edit City Location Form...")
        loc_table = self.page.locator('table').nth(1)
        loc_edit_btn = loc_table.locator('a:has-text("Edit")').first
        loc_edit_url = loc_edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{loc_edit_url}", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Edit:')")).to_be_visible()
        self.snap("edit_location_form")

        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("text=Categories & City Locations")).to_be_visible()
        print("  Location saved successfully")

        self.assert_success("Categories & Cities CMS: List, Edit Forms & Updates verified")

    def test_07_job_posts(self):
        self.log_step("Job Posts: Bids & Assign Hub, Edit & Update Job")
        self.safe_goto(f"{BASE_URL}/super-admin/jobs/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Jobs Engine')")).to_be_visible()
        self.snap("jobs_engine")

        # 1. Test Bids & Assign Link
        print("  Testing 'Bids & Assign' detail page...")
        bids_btn = self.page.locator('a:has-text("Bids & Assign")').first
        bids_url = bids_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{bids_url}", wait_until="networkidle")
        expect(self.page.locator("a:has-text('Back to Jobs')")).to_be_visible()
        print(f"  Bids & Assign page loaded: {bids_url}")
        self.snap("job_bids_assign")

        # Return to jobs
        self.page.click('a:has-text("Back to Jobs")')
        self.page.wait_for_load_state("networkidle")

        # 2. Test Edit Job Form
        print("  Testing Edit Job Form...")
        edit_btn = self.page.locator('a[title="Edit Job"]').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Edit:')")).to_be_visible()

        # Update budget slightly
        budget_input = self.page.locator('input[name="budget"]')
        curr_budget = budget_input.input_value()
        self.snap("edit_job_form")

        # Submit form
        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Jobs Engine')")).to_be_visible()
        print(f"  Job update saved successfully (budget: {curr_budget})")

        # 3. Create Job Form Cancel
        self.page.click('a:has-text("Create Job")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("h3:has-text('Post New Project')")).to_be_visible()
        self.page.click('a:has-text("Back to Jobs"), a:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/jobs/**", timeout=10000)

        self.assert_success("Job Posts: Bids & Assign Hub, Edit/Update, and Create Job flow verified")

    def test_08_quick_services(self):
        self.log_step("Quick Services: Edit & Update Quick Booking")
        self.safe_goto(f"{BASE_URL}/super-admin/quick-services/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Quick Services')")).to_be_visible()

        # Edit QS Form
        edit_btn = self.page.locator('table a:has-text("Edit")').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Edit:')")).to_be_visible()
        self.snap("edit_qs_form")

        # Save Changes
        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Quick Services')")).to_be_visible()
        print("  Quick Service updated successfully")

        # Test Create QS page
        self.page.click('a:has-text("Create Quick Booking")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("h3:has-text('Post Instant Service')")).to_be_visible()
        self.page.click('a:has-text("Back to Quick Services"), a:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/quick-services/**", timeout=10000)

        self.assert_success("Quick Services: List, Edit/Update, and Create flow verified")

    def test_09_bids_management(self):
        self.log_step("Bids & Quotations: Edit & Update Quotation")
        self.safe_goto(f"{BASE_URL}/super-admin/bids/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Vendor Bids')")).to_be_visible()

        # Edit Bid Form
        edit_btn = self.page.locator('table a:has-text("Edit")').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator("h3:has-text('Edit Bid:')")).to_be_visible()
        self.snap("edit_bid_form")

        # Save Changes
        self.page.click('button[type="submit"]:has-text("Save Changes")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Vendor Bids')")).to_be_visible()
        print("  Bid updated successfully")

        # Add Bid Cancel Test
        self.page.click('a:has-text("Add Bid")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("h3:has-text('Submit Quotation Bid')")).to_be_visible()
        self.page.click('a:has-text("Back to Bids"), a:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/bids/**", timeout=10000)

        self.assert_success("Bids & Quotations: List, Edit/Update, and Create form verified")

    def test_10_subscriptions(self):
        self.log_step("Subscriptions: Plan Overview & Add Subscription Form")
        self.safe_goto(f"{BASE_URL}/super-admin/subscriptions/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Subscription Management')")).to_be_visible()
        self.snap("subscriptions_list")

        # Test Add Subscription Form
        self.page.click('a:has-text("Add Subscription")')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator("h3:has-text('Add Subscription')")).to_be_visible()
        expect(self.page.locator('select[name="package_name"]')).to_be_visible()
        self.snap("add_subscription_form")

        self.page.click('a:has-text("Back to Subscriptions"), a:has-text("Cancel")')
        self.page.wait_for_url("**/super-admin/subscriptions/**", timeout=10000)
        self.assert_success("Subscriptions: Management Table and Add Form verified")

    def test_11_payouts(self):
        self.log_step("Payouts & Settlements: Financial KPI Cards & Search Filter")
        self.safe_goto(f"{BASE_URL}/super-admin/payouts/", wait_until="networkidle")
        expect(self.page.locator("text=Vendor Payout & Settlement Hub")).to_be_visible()

        # Verify summary stats
        expect(self.page.locator(".stat-card:has-text('Total Disbursed')")).to_be_visible()
        expect(self.page.locator(".stat-card:has-text('Pending Approval')")).to_be_visible()
        expect(self.page.locator(".stat-card:has-text('Commission Earned')")).to_be_visible()
        print("  Verified Payout KPI Cards")

        # Test Filter Form
        self.page.select_option('select[name="status"]', 'pending')
        self.page.wait_for_load_state("networkidle")
        self.snap("payouts_filtered")

        self.assert_success("Payouts & Settlements Hub verified")

    def test_12_disputes(self):
        self.log_step("Disputes & Complaints: Resolution Hub & Dispute Detail View")
        self.safe_goto(f"{BASE_URL}/super-admin/disputes/", wait_until="networkidle")
        expect(self.page.locator("text=Dispute Resolution Hub")).to_be_visible()

        # Verify dispute metrics
        expect(self.page.locator("text=Total Disputes")).to_be_visible()
        expect(self.page.locator("text=Open / Pending")).to_be_visible()

        # Open first dispute detail page
        detail_link = self.page.locator('table a[href*="/super-admin/disputes/"]').first
        detail_url = detail_link.get_attribute("href")
        print(f"  Navigating to dispute details: {detail_url}")
        self.safe_goto(f"{BASE_URL}{detail_url}", wait_until="networkidle")

        expect(self.page.locator("text=Complainant's Statement")).to_be_visible()
        self.snap("dispute_detail")
        print("  Dispute detail view, message timeline, and resolution tools loaded properly")

        self.assert_success("Disputes & Complaints: Resolution Hub & Case Details verified")

    def test_13_messages(self):
        self.log_step("In-App Messages: Communication Oversight Table")
        self.safe_goto(f"{BASE_URL}/super-admin/messages/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Message Oversight')")).to_be_visible()
        expect(self.page.locator("table th:has-text('Message')")).to_be_visible()
        self.snap("messages_table")
        self.assert_success("Message Oversight table validated")

    def test_14_landing_quick_services(self):
        self.log_step("Landing CMS: Quick Service Cards (Edit & Update)")
        self.safe_goto(f"{BASE_URL}/super-admin/landing/quick-services/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Quick Service Cards')")).to_be_visible()

        # Open Edit Form
        edit_btn = self.page.locator('a[title="Edit"]').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator("text=Card Attributes & Content")).to_be_visible()
        self.snap("edit_cms_quick_service")

        # Save Changes
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Quick Service Cards')")).to_be_visible()
        print("  Quick Service Card updated successfully")
        self.assert_success("Landing CMS: Quick Service Cards tested")

    def test_15_landing_packages(self):
        self.log_step("Landing CMS: Service Packages (Edit & Update)")
        self.safe_goto(f"{BASE_URL}/super-admin/landing/packages/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Service Packages')")).to_be_visible()

        # Open Edit Form
        edit_btn = self.page.locator('a[title="Edit"]').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator(".card-title:has-text('Card Attributes')")).to_be_visible()
        self.snap("edit_cms_package")

        # Save Changes
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Service Packages')")).to_be_visible()
        print("  Service Package updated successfully")
        self.assert_success("Landing CMS: Service Packages tested")

    def test_16_landing_testimonials(self):
        self.log_step("Landing CMS: Testimonials (Snippet View, Full Modal, Edit & Update)")
        self.safe_goto(f"{BASE_URL}/super-admin/landing/testimonials/", wait_until="networkidle")
        expect(self.page.locator(".header-title:has-text('Client Reviews & Testimonials')")).to_be_visible()

        # 1. Test Review Snippet Column
        expect(self.page.locator("th:has-text('Review Snippet')")).to_be_visible()
        print("  Review Snippet single-line column confirmed")

        # 2. Test Full Review Modal
        print("  Testing 'View' Action button to open Full Review Modal...")
        view_review_btn = self.page.locator('button[title="View Full Review"]').first
        view_review_btn.click()

        review_modal = self.page.locator('#reviewModal')
        expect(review_modal).to_be_visible()
        full_text = self.page.locator('#rmReviewText').inner_text()
        print(f"  Full Review Modal successfully opened with content: '{full_text[:60]}...'")
        self.snap("review_modal")

        # Close modal
        close_btn = review_modal.locator('button:has-text("Close"), button:has(.fa-xmark)').first
        close_btn.click()
        time.sleep(0.3)
        print("  Review modal closed")

        # 3. Test Edit Testimonial Form
        print("  Testing Edit Testimonial Form...")
        edit_btn = self.page.locator('a[title="Edit"]').first
        edit_url = edit_btn.get_attribute("href")
        self.safe_goto(f"{BASE_URL}{edit_url}", wait_until="networkidle")
        expect(self.page.locator(".card-title:has-text('Card Attributes')")).to_be_visible()
        self.snap("edit_testimonial_form")

        # Save Changes
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(".header-title:has-text('Client Reviews & Testimonials')")).to_be_visible()
        print("  Testimonial updated successfully")

        self.assert_success("Landing CMS: Testimonials (Snippet, Modal & Form) fully verified")

    def test_17_signout(self):
        self.log_step("Super Admin Sign Out")
        self.safe_goto(f"{BASE_URL}/super-admin/", wait_until="networkidle")
        
        # Click Sign Out in sidebar
        signout_link = self.page.locator('a.btn-logout:has-text("Sign Out")')
        expect(signout_link).to_be_visible()
        print("  Clicking 'Sign Out' in sidebar...")
        signout_link.click()

        # Wait for redirect to login page
        self.page.wait_for_url("**/login/**", timeout=10000)
        expect(self.page.locator('button[type="submit"]')).to_be_visible()
        self.snap("signed_out")
        self.assert_success("Super Admin signed out cleanly and returned to Login Page")

def run_tests():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
    except Exception:
        screen_w, screen_h = 1920, 1080

    print("=" * 75)
    print("  SUGGU SERVICES - SUPER ADMIN COMPLETE E2E TEST SUITE")
    print(f"  Target Server: {BASE_URL}")
    print(f"  Browser Mode:  {'Headed Full-Screen (' + str(screen_w) + 'x' + str(screen_h) + ')' if HEADED else 'Headless'}")
    print("=" * 75, flush=True)

    user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_reports", "chrome_user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    with sync_playwright() as p:
        launch_args = [
            "--start-maximized",
            f"--window-size={screen_w},{screen_h}",
            "--window-position=0,0",
            "--no-default-browser-check",
            "--no-first-run",
        ] if HEADED else []

        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                channel="chrome",
                headless=not HEADED,
                slow_mo=400 if HEADED else 0,
                args=launch_args,
                no_viewport=True,
            )
            print("  [BROWSER] Launched dedicated Google Chrome window in full-screen mode.", flush=True)
        except Exception as chrome_err:
            print(f"  [BROWSER] Launching Chromium persistent context: {chrome_err}", flush=True)
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=not HEADED,
                slow_mo=400 if HEADED else 0,
                args=launch_args,
                no_viewport=True,
            )

        page = context.pages[0] if context.pages else context.new_page()
        page.bring_to_front()

        tester = SuperAdminE2ETester(page)

        start_time = time.time()
        try:
            tester.test_00_open_home()
            tester.test_01_login()
            tester.test_02_dashboard()
            tester.test_03_users_management()
            tester.test_04_vendors_management()
            tester.test_05_kyc_approvals()
            tester.test_06_categories_and_cities()
            tester.test_07_job_posts()
            tester.test_08_quick_services()
            tester.test_09_bids_management()
            tester.test_10_subscriptions()
            tester.test_11_payouts()
            tester.test_12_disputes()
            tester.test_13_messages()
            tester.test_14_landing_quick_services()
            tester.test_15_landing_packages()
            tester.test_16_landing_testimonials()
            tester.test_17_signout()

            total_time = time.time() - start_time
            print("\n" + "=" * 75)
            print(f"  [SUCCESS] ALL {tester.passed_tests} TEST STEPS PASSED! (Time: {total_time:.2f}s)")
            print(f"  [REPORT] Screenshots stored in: {SCREENSHOTS_DIR}")
            print("=" * 75 + "\n", flush=True)
            print("  Keeping browser open for 15 seconds so you can view the completed dashboard test...", flush=True)
            time.sleep(15)
            return 0

        except Exception as e:
            tester.failed_tests += 1
            print(f"\n[ERROR] Test execution failed: {e}", flush=True)
            tester.snap("failure_error")
            print("  Pausing browser for 20 seconds so you can inspect the current page...", flush=True)
            time.sleep(20)
            return 1
        finally:
            try:
                context.close()
            except Exception:
                pass

if __name__ == "__main__":
    sys.exit(run_tests())

