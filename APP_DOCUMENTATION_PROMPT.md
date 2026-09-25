# Suggu Services — MASTER APP DEVELOPMENT PROMPT & SYSTEM SPECIFICATION

> **Target Platform:** Cross-Platform Mobile Application (Flutter / React Native / Native iOS & Android) & Web Client  
> **System Name:** Suggu Services Service & Project Marketplace  
> **Target Audience:** Customers (Users) & Service Providers (Normal/Individual Vendors and Company Vendors)  
> **Backend Reference:** Django REST Framework, Django Channels (WebSockets), SQLite/PostgreSQL Database  

---

## 1. SYSTEM ROLE & APP MISSION

You are an expert full-stack mobile system architect and senior mobile app developer. Build a production-ready, enterprise-grade marketplace mobile application called **"Suggu Services"**.

The application operates as a two-sided marketplace connecting:
1. **Users (Customers):** Individuals, homeowners, and business clients who post service needs categorized as either **Quick Services** (immediate, micro-tasks like plumbing repairs, AC servicing, emergency fixing) or **Jobs** (longer-term contracting projects, renovations, waterproofing, electrical rewiring).
2. **Vendors (Service Providers):**
   - **Normal / Individual Vendors:** Independent tradespeople, electricians, mechanics, plumbers, carpenters, and technicians.
   - **Company Vendors:** Registered contracting firms, maintenance agencies, and commercial contractors equipped with employee rosters, enterprise codes, and teams.

The app's core loop:
- Users create and publish Quick Services and Jobs with budgets, checklists, preferred dates, and locations.
- Vendors discover relevant local opportunities, inspect detailed scopes, and submit competitive bids (quotations) with price, timeline, proposal, and document attachments.
- Users compare incoming quotations side-by-side and select a winning vendor.
- Selecting a vendor unlocks full contact information, enables real-time 1-on-1 chat with media sharing, and progresses the project through status milestones until completion.
- Vendors manage a **Bid Credit / Subscription** balance to participate in bidding.

---

## 2. DATABASE SCHEMA & DATA MODELS SPECIFICATION

The application's data layer is strictly mapped to the following entities, fields, constraints, and relationships:

### 2.1. User & Authentication Layer
#### Table: `CustomUser` (Auth User)
- `id` (Integer, Primary Key, Auto Increment)
- `username` (VarChar 150, Unique, Required)
- `email` (EmailField 254, Unique, Required)
- `first_name` (VarChar 150, Required)
- `last_name` (VarChar 150, Optional)
- `role` (VarChar 20, Choices: `['USER', 'VENDOR', 'ADMIN']`, Default: `'USER'`)
- `is_active` (Boolean, Default: `True`)
- `date_joined` (DateTimeField, Default: `timezone.now`)

#### Table: `UserProfile` (Customer Profile)
- `id` (Integer, Primary Key)
- `user_id` (OneToOneField -> `CustomUser`, `on_delete=CASCADE`, `related_name='user_profile'`)
- `phone_number` (VarChar 20, Indexed, Supports 10-digit format / `+91`)
- `profile_image` (ImageField, `upload_to='user_profiles/'`, Optional)

#### Table: `VendorProfile` (Vendor Profile)
- `id` (Integer, Primary Key)
- `user_id` (OneToOneField -> `CustomUser`, `on_delete=CASCADE`, `related_name='vendor_profile'`)
- `company_name` (VarChar 255, Optional for Normal Vendor, Required for Company Vendor)
- `category` (VarChar 100, Primary trade domain e.g., "Plumbing", "Electrical", "Renovation")
- `location` (VarChar 255, e.g., "Ranchi, Jharkhand")
- `vendor_type` (VarChar 20, Choices: `['vendor', 'company']`, Default: `'vendor'`)
- `employee_code` (VarChar 50, Optional, Company-specific ID)
- `employee_details` (TextField, Optional, Roster/Staff count and certifications)
- `dob` (DateField, Optional, Date of Birth for personal verification)
- `gender` (VarChar 20, Optional: `['Male', 'Female', 'Other']`)
- `address` (TextField, Physical operating/business address)
- `experience` (Integer, Years of trade experience, Default: `0`)
- `id_proof` (VarChar 100, Aadhaar / PAN / Trade License number)
- `profile_image` (ImageField, `upload_to='vendor_profiles/'`, Optional)
- `about` (TextField, Business bio, certifications, warranty policies)
- `rating` (Decimal 3,1, Default: `0.0`, Scale: `0.0` - `5.0`)
- `registered_date` (DateTimeField, Default: `timezone.now`)

#### Table: `OTPVerification` (Mobile OTP Authentication)
- `id` (Integer, Primary Key)
- `mobile` (VarChar 50, Indexed, 10-digit normalized phone number)
- `otp` (VarChar 10, 6-digit numeric string)
- `purpose` (VarChar 20, Choices: `['login', 'signup', 'general']`, Default: `'general'`)
- `is_verified` (Boolean, Default: `False`)
- `created_at` (DateTimeField, Default: `timezone.now`)
- `expires_at` (DateTimeField, Default: `created_at + 10 minutes`)
- *Development Bypass Rule:* OTP `'123456'` is always accepted as valid in test environments.

---

### 2.2. Master Data Entities
#### Table: `Category` (Service Trade Categories)
- `id` (Integer, Primary Key)
- `name` (VarChar 100, e.g., "Plumbing", "Electrical", "AC Repair", "Carpentry", "Painting", "Cleaning", "Full Renovation", "Waterproofing")
- `service_type` (VarChar 20, Choices: `['job', 'quick_service', 'both']`, Default: `'both'`)
- `status` (VarChar 20, Choices: `['active', 'inactive']`, Default: `'active'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

#### Table: `Location` (Service Geographies)
- `id` (Integer, Primary Key)
- `state` (VarChar 100, e.g., "Jharkhand", "Maharashtra", "Delhi")
- `city` (VarChar 100, e.g., "Ranchi", "Mumbai", "New Delhi")
- `status` (VarChar 20, Choices: `['active', 'inactive']`, Default: `'active'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

---

### 2.3. Marketplace Postings & Bidding
#### Table: `QuickService` (Micro & Urgent Service Requests)
- `id` (Integer, Primary Key)
- `title` (VarChar 255, e.g., "Kitchen sink pipe leakage & drainage fix")
- `category_id` (ForeignKey -> `Category`, `null=True`, `blank=True`)
- `description` (TextField, Comprehensive task description)
- `required_work` (JSONField / List of Strings, e.g., `["Pipe Replacement", "Sealant Application"]`)
- `budget` (Decimal 10,2, Target budget in INR ₹)
- `shift_availability` (VarChar 50, e.g., "Morning (9 AM - 12 PM)", "Flexible")
- `preferred_date` (DateField, Optional)
- `preferred_time` (TimeField, Optional)
- `location_id` (ForeignKey -> `Location`, `null=True`, `blank=True`)
- `address` (TextField, Service delivery address)
- `additional_requirements` (TextField, Optional instructions)
- `contact_name` (VarChar 255, Customer point-of-contact)
- `contact_mobile` (VarChar 20, Contact phone number)
- `user_id` (ForeignKey -> `CustomUser`, `related_name='quick_services'`)
- `bids_count` (Integer, Default: `0`, Denormalized counter for performance)
- `status` (VarChar 20, Choices: `['open', 'selected', 'progress', 'completed', 'cancelled', 'closed']`, Default: `'open'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

#### Table: `Job` (Long-Term & Major Contracting Projects)
- `id` (Integer, Primary Key)
- `title` (VarChar 255, e.g., "Full 3BHK Apartment Interior Renovation")
- `category_id` (ForeignKey -> `Category`, `null=True`, `blank=True`)
- `description` (TextField, Project overview)
- `required_work` (JSONField / List of Strings, e.g., `["False Ceiling", "Modular Kitchen"]`)
- `scope_of_work` (TextField, Technical specifications & work breakdown)
- `materials_details` (TextField, Specifications of raw materials/brands to be used)
- `additional_requirements` (TextField, Special conditions, site access rules)
- `budget` (Decimal 10,2, Estimated project capital in INR ₹)
- `budget_type` (VarChar 50, e.g., "Fixed Price", "Hourly", "Milestone-Based")
- `preferred_start_date` (DateField, Expected commencement date)
- `expected_completion` (DateField, Delivery deadline)
- `required_time` (VarChar 100, e.g., "45 Days", "2 Months")
- `shift_availability` (VarChar 50, e.g., "Full Day (9 AM - 6 PM)", "Weekend Overnight")
- `working_hours` (VarChar 100, Daily operating shift hours)
- `location_id` (ForeignKey -> `Location`, `null=True`, `blank=True`)
- `address` (TextField, Project site address)
- `pincode` (VarChar 20, Postal index number)
- `contact_name` (VarChar 255)
- `contact_mobile` (VarChar 20)
- `user_id` (ForeignKey -> `CustomUser`, `related_name='jobs'`)
- `bids_count` (Integer, Default: `0`)
- `status` (VarChar 20, Choices: `['open', 'selected', 'progress', 'completed', 'cancelled', 'closed']`, Default: `'open'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

#### Table: `Bid` (Vendor Quotation & Proposal)
- `id` (Integer, Primary Key)
- `vendor_id` (ForeignKey -> `CustomUser`, `related_name='bids'`)
- `job_id` (ForeignKey -> `Job`, `null=True`, `blank=True`, `related_name='bids'`)
- `quick_service_id` (ForeignKey -> `QuickService`, `null=True`, `blank=True`, `related_name='bids'`)
- `amount` (Decimal 10,2, Proposed quotation fee in INR ₹)
- `estimated_time` (VarChar 100, Proposed duration e.g., "2 Hours", "35 Days")
- `message` (TextField, Optional quick note)
- `proposal` (TextField, Detailed pitch, terms of service, methodology)
- `attachment` (FileField, `upload_to='bid_attachments/'`, PDF quotation/spec sheet)
- `status` (VarChar 20, Choices: `['submitted', 'selected', 'rejected', 'withdrawn']`, Default: `'submitted'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

---

### 2.4. Messaging & Subscriptions Layer
#### Table: `Message` (1-on-1 Real-time Chat)
- `id` (Integer, Primary Key)
- `sender_id` (ForeignKey -> `CustomUser`, `related_name='sent_messages'`)
- `receiver_id` (ForeignKey -> `CustomUser`, `related_name='received_messages'`)
- `job_id` (ForeignKey -> `Job`, `null=True`, `blank=True`, `related_name='messages'`)
- `quick_service_id` (ForeignKey -> `QuickService`, `null=True`, `blank=True`, `related_name='messages'`)
- `content` (TextField, Text message body)
- `attachment` (FileField, `upload_to='message_attachments/'`, Images / Docs)
- `is_read` (Boolean, Default: `False`)
- `created_at` (DateTimeField, `auto_now_add=True`)

#### Table: `Subscription` (Bid Credits & Vendor Subscriptions)
- `id` (Integer, Primary Key)
- `vendor_id` (ForeignKey -> `CustomUser`, `related_name='subscriptions'`)
- `package_name` (VarChar 100, e.g., "Starter 15 Bids", "Professional 50 Bids", "Enterprise Annual")
- `amount` (Decimal 10,2, Transaction amount in INR ₹)
- `status` (VarChar 20, Choices: `['success', 'failed', 'pending']`, Default: `'success'`)
- `created_at` (DateTimeField, Default: `timezone.now`)

---

## 3. USER (CUSTOMER) APP EXPERIENCE & SCREENS

### 3.1. Authentication & Onboarding
- **Clean Segmented Login:**
  - Tab 1: **Mobile OTP Login** (Enter 10-digit mobile -> hits `/api/auth/check-phone/` -> hits `/api/auth/send-otp/` -> 6-box segmented OTP code entry -> hits `/api/auth/otp-login/`).
  - Tab 2: **Password Login** (Enter mobile / email / username + password -> hits `/api/auth/login/`).
- **Create Account Flow:**
  - Segmented choice: "Continue as User" (`/register/user/` or `/api/user/otp-signup/`).
  - Fields: Full Name, Mobile Number, Email, Password, Profile Avatar.

### 3.2. Customer Dashboard Screen
- **Personalized Header:** "Welcome back, {User Name}!", current date, city badge.
- **Top Summary Metric Cards (Horizontal scroll or grid):**
  1. *Active Quick Services* (Count of open/in-progress quick services)
  2. *Active Jobs* (Count of open/in-progress long-term projects)
  3. *Pending Quotations* (Total quotations waiting for review)
  4. *Selected Vendors* (Vendors awarded work)
  5. *Completed Services* (Finished quick tasks)
  6. *Completed Jobs* (Finished projects)
- **Action Buttons / Floating Action Bar (FAB):**
  - **"+ Post Quick Service"** (Primary Purple/Blue button)
  - **"+ Post a Job"** (Secondary Outline button)
- **Full-Width Section 1: Recent Quick Services Table/Cards**
  - Columns / Card Data: Title, Category, Budget, Number of Quotations received, Selected Vendor name (or '—'), Status badge, Posted date.
  - "View All" link directing to full Quick Services list.
- **Full-Width Section 2: Recent Long Jobs Table/Cards**
  - Columns / Card Data: Title, Category, Budget, Number of Bids received, Selected Vendor name (or '—'), Status badge, Posted date.
  - "View All" link directing to full Jobs list.
- *(Note: "Recent Activity" timeline is omitted from the user dashboard to give full width to data cards).*

### 3.3. Posting Flows
#### Screen: Post a Quick Service
- Category Dropdown (dynamically filtered where `service_type` in `['quick_service', 'both']`).
- Service Title & Description.
- Dynamic Required Work Checklists / Tag inputs (e.g., "Leakage fixing", "Pipe replacement").
- Target Budget (₹).
- Preferred Date & Preferred Time picker.
- Shift Availability selector ("Morning (9 AM - 12 PM)", "Afternoon", "Evening", "Flexible").
- Location: State & City dropdowns (populated from active `Location` table).
- Full Site Address & Landmark.
- Contact Name & Mobile Number (prefilled from User profile, editable).

#### Screen: Post a Long-Term Job
- Category Dropdown (filtered where `service_type` in `['job', 'both']`).
- Job Title & Description.
- Dynamic Required Work Checklist tags.
- Detailed Scope of Work text block.
- Materials Details & Brand specifications text block.
- Additional Requirements (e.g., "Safety certifications required", "Debris cleaning").
- Budget (₹) & Budget Type selector ("Fixed Price", "Hourly", "Cost + Material").
- Preferred Start Date & Expected Completion Date.
- Duration / Working Hours (e.g., "8 Hours daily", "Weekend only").
- Location: State & City dropdowns + Pincode + Full Address.
- Contact Name & Mobile Number.

### 3.4. Managing Services & Reviewing Quotations
#### Screen: Quick Services & Jobs Index
- Segmented status filters: **All**, **Open**, **Vendor Selected**, **In Progress**, **Completed**, **Cancelled**.
- Real-time card view displaying budget, bids counter, status badges, and quick link to details.

#### Screen: Quotation Comparison & Selection Engine
- Displays job summary and metrics: Total Bids, Lowest Bid (₹), Highest Bid (₹), Selected Vendor.
- Side-by-side or stacked vendor proposal cards:
  - Vendor / Company Name & Avatar / Initials badge.
  - Category & Verified Rating (e.g., 4.8 ★) with Years of Experience.
  - Quoted Price (₹) & Estimated Completion Time.
  - Proposal cover letter & downloadable attachment link (PDF / Image).
  - Status indicator (`submitted`, `selected`, `rejected`).
  - **"Accept Vendor" CTA Button**:
    - Prompts user confirmation.
    - Submits selection -> marks quotation as `selected` -> updates Job/QuickService status to `selected`.
    - Automatically displays vendor's direct contact phone number and opens the direct chat channel.

### 3.5. Customer Messaging & Profile
- **Messages Inbox:** List of active chats with vendors; unread counter, last message timestamp, category subtitle.
- **Chat Room:** Real-time chat bubbles, timestamp formatting, image and PDF attachments, WebSocket synchronization.
- **Profile & Settings:** Edit name, mobile number, email, avatar image, view posted activity statistics.

---

## 4. VENDOR (NORMAL & COMPANY) APP EXPERIENCE & SCREENS

### 4.1. Vendor Types & Distinction
The app caters specifically to two vendor personas:
1. **Normal / Individual Vendor (`vendor`):**
   - Electrician, plumber, painter, handyman, solo technician.
   - Profile emphasizes: Personal Name, Trade Category, Years of Experience, ID Proof, Rating, Past Reviews.
2. **Company Vendor (`company`):**
   - Contracting agency, facilities management firm, interior decor firm.
   - Profile emphasizes: Company Name, Corporate Registration / Employee Code, Team / Employee Details, Capacity, Experience, Commercial Projects Portfolio.

### 4.2. Vendor Dashboard Screen
- **Personalized Header:** Vendor or Company Name, Verification badge, Category tag, Location badge.
- **Key Performance & Opportunity Metrics:**
  1. *Available Quick Services* (New open local micro-tasks)
  2. *Available Jobs* (New open commercial/residential projects)
  3. *Remaining Bid Credits* (Live credit balance, with "Recharge" CTA)
  4. *Active Bids* (Proposals currently under user consideration)
  5. *Selected Jobs* (Contracts won where vendor is the chosen contractor)
  6. *Completed Work* (Successfully executed jobs)
  7. *Total Earnings* (Cumulative ₹ value of completed contracts)
- **Quick Discovery Feed:** Immediate preview of the newest open requests with budget and location tags.

### 4.3. Opportunities Marketplace (Job Feed)
- **Tab 1: Nearby Quick Services:**
  - List of open `QuickService` records matching vendor trade and region.
  - Card displays: Title, category, client's budget (₹), shift timing, area / city, posted timestamp, existing bids count.
- **Tab 2: Available Long-Term Projects:**
  - List of open `Job` records.
  - Card displays: Title, project scope snippet, budget (₹), budget type, projected timeline (start date & duration), area / city, bids count.
- **Filters & Search:**
  - Filter by Category, State/City, Budget range (Min - Max), Urgency / Shift.

### 4.4. Opportunity Details & Sending Quotations
#### Screen: Opportunity Deep-Dive
- Full project description, required work item list, scope breakdown, material preferences, working shift requirements, city/area.
- *(Note: Customer's direct phone number and exact house/flat address are hidden until quotation is selected to preserve marketplace integrity).*
- Indicator: Displays whether the vendor has already submitted a bid for this posting.

#### Screen / Modal: Send Quotation (Bidding Engine)
- Checks vendor's Remaining Bid Credits. If credits <= 0, displays a prompt: *"You need bid credits to submit a quotation. Please recharge your package."*
- Form Fields:
  1. **Quotation Amount (₹):** Vendor's competitive price.
  2. **Estimated Completion Time:** E.g., "2 Hours", "3 Days", "40 Days".
  3. **Proposal & Pitch:** Detailed message to customer explaining experience, warranty, quality of materials, and approach.
  4. **Document Attachment:** Upload PDF quotation, estimate sheet, or license.
- Submission increments the posting's `bids_count` and deducts 1 bid credit.

### 4.5. Won Contracts ("Selected Jobs")
- Dedicated hub listing all jobs/quick services where the vendor's quotation has been marked as `selected`.
- Displays **unlocked customer details:**
  - Customer Full Name
  - Customer Verified Contact Phone Number (with one-tap Call button)
  - Full Site Address & Pincode (with one-tap "Open in Google Maps" button)
- Status progress tracker (Selected -> In Progress -> Completed).
- Direct "Message Customer" button opening the 1-on-1 chat room.

### 4.6. Bid Credits & Subscription Packages
- **Current Balance Card:** Displays remaining credits and active package tier.
- **Credit Packages:**
  - *Starter Pack:* 15 Bids — ₹499
  - *Professional Monthly:* 50 Bids — ₹1,499
  - *Enterprise Annual (For Companies):* Unlimited / 250 Bids — ₹9,999
- **Transaction History Ledger:**
  - List of all past purchases with Transaction ID (`TXN-BC-XXXX`), package name, amount (₹), payment status (`success`, `failed`, `pending`), and date.

### 4.7. Vendor Profile & Reputation
- View and edit business profile: Company Name (if company), Personal Name, Category, Address, Bio / About, Experience (years), Profile Photo / Company Logo.
- For Company Vendors: Manage Employee Code and Team Details text.
- Live Rating display and aggregate stats of won & completed projects.

---

## 5. API SPECIFICATION CONTRACT

All endpoints accept and return `application/json` (or `multipart/form-data` when uploading files/images). Standard error responses return `{ "status": "error", "message": "<string>" }`.

### 5.1. Authentication Endpoints
| Method | Endpoint | Description | Request Parameters / Body | Key Response Fields |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/check-phone/` | Check if mobile is registered | `mobile` (req), `role` (opt) | `is_registered` (bool), `user` (if registered), `matches_role` |
| `POST` | `/api/auth/send-otp/` | Send 6-digit SMS OTP | `mobile` (req), `purpose` (`login`/`signup`), `role` (opt) | `status`, `mobile`, `otp`, `expires_in_minutes` (10) |
| `POST` | `/api/auth/verify-otp/` | Verify 6-digit SMS OTP | `mobile` (req), `otp` (req), `purpose` (opt) | `status`, `is_verified` (bool) |
| `POST` | `/api/auth/login/` | Unified Password Login | `username`/`email`/`mobile` (req), `password` (req) | `status`, `redirect_url`, `user` (`id`, `name`, `role`, `email`) |
| `POST` | `/api/auth/otp-login/` | Unified OTP Login | `mobile` (req), `otp` (req) | `status`, `redirect_url`, `user` (`id`, `name`, `role`, `mobile`) |
| `POST` | `/api/user/otp-signup/` | User OTP Registration | `name`, `mobile`, `otp`, `email` (opt), `password` (opt) | `status`, `user` (`id`, `user_code`, `name`, `role`) |
| `POST` | `/api/vendor/otp-signup/` | Vendor OTP Registration | `name`, `mobile`, `otp`, `company_name`, `category`, `location`, `vendor_type` | `status`, `vendor` (`id`, `vendor_code`, `company_name`, `role`) |

### 5.2. Customer (User) Endpoints
| Method | Endpoint | Description | Key Parameters / Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/user/dashboard-data/` | User dashboard counters & recent items | Auth token / session |
| `POST` | `/api/user/quick-services/create/` | Create Quick Service | `title`, `category_id`, `budget`, `required_work[]`, `preferred_date`, `preferred_time`, `shift_availability`, `location_id`, `address`, `contact_name`, `contact_mobile` |
| `POST` | `/api/user/jobs/create/` | Create Long-Term Job | `title`, `category_id`, `budget`, `budget_type`, `scope_of_work`, `materials_details`, `required_work[]`, `preferred_start_date`, `expected_completion`, `location_id`, `address`, `pincode`, `contact_name`, `contact_mobile` |
| `GET` | `/api/user/quotations/?id={posting_id}` | Fetch all bids for a posting | `id` (Job ID or QS ID) |
| `POST` | `/api/user/accept-vendor/` | Award quotation to vendor | `bid_id` (req) |

### 5.3. Vendor Endpoints
| Method | Endpoint | Description | Key Parameters / Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/vendor/dashboard-data/` | Vendor dashboard counters & feed | Auth token / session |
| `GET` | `/api/vendor/quick-services/nearby/` | Feed of open Quick Services | Filters: `category_id`, `location_id`, `search` |
| `GET` | `/api/vendor/jobs/available/` | Feed of open Long-Term Jobs | Filters: `category_id`, `location_id`, `budget_min`, `budget_max` |
| `POST` | `/api/vendor/send-quotation/` | Submit bid on QS or Job | `job_id` or `qs_id`, `amount`, `estimated_time`, `proposal`, `attachment` (file) |
| `GET` | `/api/vendor/selected-jobs/` | List of contracts won | Auth token / session |
| `GET` | `/api/vendor/bid-credits/history/` | Subscriptions and purchases ledger | Auth token / session |

### 5.4. Messaging & WebSocket Protocol
- **REST Messages:**
  - `GET /api/messages/conversations/`: Returns unique conversation threads with user initials, unread badge, and last message.
  - `GET /api/messages/thread/?other_user_id={id}`: Returns message history between authenticated user and counterpart.
  - `POST /api/messages/send/`: Body contains `receiver_id`, `content`, optional `attachment` file.
- **WebSocket Protocol:**
  - Connection URL: `ws://{host}/ws/chat/{min_user_id}_{max_user_id}/`
  - Payload sent/received:
    ```json
    {
      "type": "chat_message",
      "message": "Text content or HTML link to attachment",
      "sender_id": 12,
      "sender_name": "Ravi Kumar",
      "time": "10:30 AM"
    }
    ```

---

## 6. BUSINESS LOGIC & CRITICAL CONSTRAINTS

1. **Exclusivity of Vendor Selection:**
   - Once a customer clicks "Accept Vendor" on a quotation, that quotation's status changes to `selected`.
   - The associated `Job` or `QuickService` status changes to `selected`.
   - Other competing bids remain visible but inactive, preventing double-awarding.
2. **Contact Privacy Wall:**
   - Before selection: Vendors only see the general City, State, and Task Description. Exact residential flat numbers and phone numbers are redacted.
   - After selection: Full site address and phone numbers are unlocked for the selected vendor to coordinate execution.
3. **Credit Verification Rule:**
   - Vendors must hold at least 1 active bid credit to submit a quotation. If credit count is 0, submission is blocked with an alert to recharge credits.
4. **Master Bypass for Development:**
   - Entering OTP `'123456'` verifies immediately on any phone number without requiring active SMS gateway dispatch.
5. **No Demo Credentials on UI:**
   - The user interface must never display hardcoded demo buttons or credentials cards.
6. **Responsive Card Architecture:**
   - Tables and listing cards must span 100% full container width without awkward right-side blank columns.

---

## 7. TECH STACK IMPLEMENTATION RECOMMENDATIONS

- **Mobile Framework:** Flutter (Dart) or React Native (TypeScript).
- **State Management:**
  - Flutter: BLoC / Riverpod.
  - React Native: Redux Toolkit / Zustand.
- **Networking:** Axios / Dio with global interceptor attaching JWT Bearer tokens or Session Cookies (`csrftoken` and `sessionid`).
- **Real-Time Client:** `web_socket_channel` (Flutter) or `reconnecting-websocket` (React Native) connecting to Django Channels.
- **Local Storage:** SecureStore / Flutter Secure Storage for tokens and user role caching.
- **Styling:** Curated modern dark/light mode palette (Deep Indigo `#1E293B`, Electric Purple `#6366F1`, Emerald Green `#10B981`, Slate Grey `#64748B`), smooth border radii (`12px` - `16px`), glassmorphism app bars, and high contrast data tables.

---
*End of Master App Documentation Prompt — Ready for direct ingestion by mobile development agents or engineering teams.*
