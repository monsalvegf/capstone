# Quality Management System - Nonconformities Tracker

A Django-based web application for managing quality nonconformities in organizational settings.

**Video Demo:** [URL to be added]

**Course:** CS50's Web Programming with Python and JavaScript - Final Project (Capstone)

---

## Distinctiveness and Complexity

### Why This Project is Distinct

This Quality Management System is **fundamentally different** from all CS50W course projects. It is neither a social network (Project 4) nor an e-commerce platform (Project 2). Instead, it addresses a specialized **B2B use case: quality assurance and regulatory compliance tracking** for ISO 9001-certified organizations.

**Key distinctions:**

1. **Specialized Business Domain**: Serves quality managers and auditors in manufacturing/service industries. Implements ISO 9001-specific workflows including nonconformity lifecycle management (Open → In Progress → Closed → Reopen), severity classification, and mandatory audit trails. Unlike social networks focused on user interactions or e-commerce sites handling transactions, this system manages regulatory compliance data.

2. **Immutable Audit Trail System**: Every action automatically creates timestamped, user-attributed `NonconformityLine` records. This permanent audit log is a regulatory requirement—organizations must prove who did what and when. The system automatically logs creation, edits, status changes, closures, and reopenings.

3. **State Machine with Automatic Date Management**: Nonconformities follow controlled state transitions with smart business logic. When status changes to "Cerrada" (Closed), the system automatically sets `closure_date`. When reopened, it clears the closure date. This automated workflow management is unique to quality management systems.

4. **Modular Three-App Architecture**: Deliberately designed with `core` (shared models), `nonconformities` (main app), and `accounts` (authentication) to support future expansion with additional quality modules (audits, corrective actions, document control, supplier management, training tracking).

### Why This Project is Complex

This project demonstrates significant technical complexity beyond baseline requirements:

**1. Advanced Database Design**: Six interconnected models (`Nonconformity`, `NonconformityLine`, `Severity`, `Status`, `Category`, `Area`) with carefully configured relationships. Five foreign keys on `Nonconformity` use `SET_NULL` to preserve data integrity if reference records are deleted. `NonconformityLine` uses `CASCADE` to maintain referential integrity. Custom data migration in `0002_severity_alter_nonconformity_severity.py` preserves data during architectural refactoring.

**2. Sophisticated JavaScript Implementation**: Goes beyond basic DOM manipulation with modern Fetch API for AJAX calls, runtime responsive detection using `matchMedia()` to dynamically switch between modal (mobile) and side panel (desktop), progressive enhancement with traditional POST fallbacks, event delegation for dynamically loaded content, and keyboard navigation (Escape closes modals, Enter submits filters).

**3. Dynamic Query Builder with Filter Persistence**: The `get_filtered_nonconformities()` function constructs Django ORM queries on-the-fly from seven filter criteria using case-insensitive searches (`__icontains`) and date filtering (`__date`). Filters persist via URL query parameters and automatically apply to CSV exports, maintaining user context across requests.

**4. Five Custom-Validated Forms**: Each form includes specialized validation:
- `NonconformityForm`: Conditional uniqueness (only on create via `self.instance.pk` check), automatic uppercase conversion, minimum 10-character description
- `NonconformityCloseForm`: Required confirmation checkbox with optional comment
- All forms implement cross-field validation and dynamic field modification

**5. Dual-Mode AJAX/Traditional POST**: Views detect AJAX via `X-Requested-With` header and return JSON for AJAX clients or HTTP redirects for traditional POST, enabling progressive enhancement.

**6. Responsive Design System**: Two-column flexbox layout (50-50 desktop, stacked mobile), three CSS breakpoints (768px, 992px, 1200px) with progressive font sizing, CSS animations (`@keyframes slideIn`), modal overlay with body scroll locking, and table responsiveness with horizontal scrolling.

**7. Automatic User and Timestamp Tracking**: Models use `auto_now_add=True` for creation timestamps. Views automatically inject `request.user` into all records, creating complete audit trails without manual intervention.

---

## File Structure and Contents

### Django Project Core
- **`quality/settings.py`**: Main configuration (apps, database, static files, authentication, internationalization, security)
- **`quality/urls.py`**: Root URL routing to admin, accounts, and nonconformities apps
- **`manage.py`**: Django command-line utility

### Core App (Shared Models)
- **`core/models.py`**: `Area` model for organizational departments (cross-functional, reusable across future modules)
- **`core/admin.py`**: Admin registration for Area
- **`core/migrations/`**: Database schema history

### Nonconformities App (Main Application)
- **`nonconformities/models.py`**: Five models: `Severity`, `Status`, `Category`, `Nonconformity` (main entity with code, description, dates, and five foreign keys), `NonconformityLine` (audit trail with CASCADE delete)
- **`nonconformities/views.py`**: Ten views implementing full CRUD plus specialized workflows: list with filtering, detail (full + AJAX partial), create with auto-user assignment, update with audit logging, change status with automatic `closure_date` management, close with confirmation, reopen clearing closure date, add action (dual-mode AJAX), CSV export with applied filters, and dynamic query builder helper
- **`nonconformities/forms.py`**: Five forms with custom validation: `NonconformityForm` (conditional uniqueness, auto-uppercase), `NonconformityLineForm` (min 5 chars), `NonconformityStatusForm`, `NonconformityCloseForm` (required checkbox), `NonconformityFilterForm`
- **`nonconformities/urls.py`**: URL patterns with named routes
- **`nonconformities/admin.py`**: Admin configuration with custom list display and inline action lines
- **`nonconformities/migrations/`**: Includes `0002_severity_alter_nonconformity_severity.py` with custom data migration

### Templates
- **`templates/base.html`**: Master template with header, navigation, messages container, CSRF-protected logout
- **`templates/registration/login.html`**: Login form
- **`nonconformities/templates/nonconformities/`**:
  - `nonconformity_list.html`: Two-column layout with embedded filter form, clickable rows with data-id attributes, and modal structure
  - `nonconformity_detail_partial.html`: AJAX-loaded fragment with NC details, status form, close/reopen buttons, audit trail timeline, and add-action form with embedded JavaScript
  - `nonconformity_detail.html`: Full-page detail view
  - `create_nonconformity.html`: Create/edit form (toggled by `is_edit` context variable)
  - `close_nonconformity.html`: Closure confirmation with optional comment

### Static Files
- **`static/css/styles.css`**: 468 lines implementing responsive flexbox layout, three media query breakpoints, table styling with hover/selection effects, modal overlay system, animated message alerts, button variants, form styling
- **`static/js/scripts.js`**: 111 lines implementing AJAX fetch calls, responsive detection with `matchMedia()`, modal management with body scroll locking, filter auto-submit, keyboard navigation, selected row state management

### Accounts App
- **`accounts/views.py`**: Home redirect logic (authenticated → NC list, anonymous → login)
- **`accounts/urls.py`**: Root URL mapping

### Configuration
- **`requirements.txt`**: Django==5.2, asgiref==3.8.1, sqlparse==0.5.3
- **`.gitignore`**: venv, __pycache__, *.pyc, *.sqlite3, IDE folders

---

## How to Run the Application

### Prerequisites
- Python 3.8+, pip, Git

### Installation

```bash
# Clone repository
git clone https://github.com/monsalvegf/capstone.git
cd capstone/quality

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Initial Setup

1. Navigate to `http://127.0.0.1:8000/admin/` and login
2. Create reference data:
   - **Severities**: Critical, Major, Minor
   - **Statuses**: Abierta, Cerrada (Spanish names required - code looks for "abierta"/"cerrad")
   - **Categories**: Documentation, Process, Product
   - **Areas**: Production, Quality Control
3. Access app at `http://127.0.0.1:8000/`

### Key Features to Test

- **Filtering**: Use table header inputs to filter by code, date, description, severity, category, status
- **AJAX Detail Loading**: Click any row to load details dynamically (desktop panel or mobile modal)
- **Status Changes**: Dropdown in detail panel (AJAX-enabled)
- **Close/Reopen**: "Cerrar NC" requires confirmation; "Reabrir NC" clears closure date
- **Add Actions**: Form at bottom of detail panel (AJAX without page reload)
- **Edit**: "✏️ Editar NC" button
- **Export**: "Exportar" downloads CSV with current filters applied
- **Responsive**: Resize browser below 768px for mobile modal view

---

## Additional Information

### Technology Stack
- **Backend**: Django 5.2, Python 3.8+, SQLite3
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3, Fetch API
- **Authentication**: Django built-in with `@login_required` decorators

### Design Decisions

1. **No Delete Operations**: Following quality management best practices, nonconformities are closed (never deleted) to preserve complete audit trails for regulatory compliance.

2. **Automatic Audit Trail**: All actions automatically create `NonconformityLine` entries with timestamps and user attribution, ensuring ISO 9001 traceability requirements.

3. **Spanish UI with English Code**: Interface uses Spanish (target user language) while codebase uses English (programming conventions) for B2B applications targeting Spanish-speaking industries.

4. **Progressive Enhancement**: All features work without JavaScript via traditional POST; AJAX enhances user experience but isn't required.

5. **Modular Architecture**: Three-app separation supports future expansion (audits, CAPA, document control, supplier management, training tracking, risk management, customer complaints, KPI dashboards, calibration tracking).

### Browser Compatibility
Chrome/Chromium 90+, Firefox 88+, Safari 14+, Edge 90+

### Known Limitations
- No pagination (suitable for ~500 NCs; requires Django Paginator for larger datasets)
- No file attachments or email notifications (could add with Django FileField/email system)
- SQLite (development-appropriate; PostgreSQL recommended for production)
- Hardcoded SECRET_KEY and DEBUG (use environment variables for deployment)

---

**Author**: Fernando Monsalve
**Course**: CS50 Web Programming with Python and JavaScript
**Project**: Final Capstone - Quality Management System
