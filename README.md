# Quality Management System - Nonconformities Tracker

A Django-based web application for managing quality nonconformities in organizational settings.

**Video Demo:** [URL to be added]

**Course:** CS50's Web Programming with Python and JavaScript - Final Project (Capstone)

---

## Distinctiveness and Complexity

### Why This Project is Distinct

This Quality Management System represents a **fundamentally different domain** from all other projects in the CS50W course. It is neither a social network (Project 4) nor an e-commerce platform (Project 2). Instead, it addresses a specialized B2B use case: **quality assurance and regulatory compliance tracking**.

**Key distinctions that set it apart:**

1. **Specialized Business Domain**: This application serves quality managers, auditors, and compliance officers in manufacturing and service industries. It implements workflows specific to ISO 9001 quality management systems, including nonconformity lifecycle management (Open → Closed → Reopen), severity classification, and mandatory audit trails. Unlike social networks that focus on user interactions or e-commerce sites that handle transactions, this system manages regulatory compliance data.

2. **Unique Data Model Architecture**: The application features a deliberately modular architecture with three separate Django apps (`core`, `nonconformities`, `accounts`), designed for future scalability. The `core` app contains only truly cross-functional models (like `Area`) that would be shared across multiple quality modules, while domain-specific models like `Severity` live in their respective apps.

3. **Audit Trail and Compliance Features**: Every action on a nonconformity is automatically logged in `NonconformityLine` with user attribution and timestamps. This creates an immutable audit trail required for ISO 9001 compliance, where organizations must demonstrate who did what and when. The system automatically records status changes, edits, closures, and reopenings—a feature not present in any course project.

4. **State Machine Workflow**: Nonconformities follow a controlled state lifecycle with automatic date management. When a NC is closed, the system automatically sets `closure_date` and changes status. When reopened, it clears the closure date. This business logic is specific to quality management and demonstrates understanding of real-world regulatory requirements.

### Why This Project is Complex

Beyond meeting the baseline requirements of using Django models and JavaScript, this project demonstrates significant technical complexity across multiple dimensions:

**1. Advanced Database Design (6 Models with Complex Relationships)**

The application includes six interconnected models (`Nonconformity`, `NonconformityLine`, `Severity`, `Status`, `Category`, `Area`) with carefully configured foreign key relationships. For example, `Nonconformity` has five different ForeignKey relationships, each with specific `on_delete` behaviors (`SET_NULL` for preserving referential integrity, `CASCADE` for dependent data). The `NonconformityLine` model implements a one-to-many relationship that creates a temporal audit log—a pattern.

**2. Sophisticated JavaScript Implementation**

The frontend JavaScript (`static/js/scripts.js`) goes far beyond basic DOM manipulation:

- **AJAX with Fetch API**: Dynamic content loading without page refreshes, using the modern Fetch API with proper error handling and JSON parsing
- **Responsive Detection with matchMedia**: The code detects screen size at runtime and dynamically switches between modal overlay (mobile) and side panel (desktop) presentation modes
- **Progressive Enhancement**: Features work with traditional form POST as fallback if JavaScript fails
- **Event Delegation**: Handles clicks on dynamically loaded table rows using data attributes
- **Keyboard Navigation**: Implements Escape key to close modals and Enter key for form submission

**3. Complex Filtering System**

The `get_filtered_nonconformities()` function implements a dynamic query builder that accepts seven different filter criteria (code, creation_date, description, severity, category, status, area) and constructs Django ORM queries on-the-fly. It uses `Q` objects implicitly through dictionary unpacking and demonstrates understanding of case-insensitive searches (`__icontains`) and date filtering (`__date`). The filtered results persist across requests via URL query parameters, and the same filters apply to CSV exports.

**4. Five Specialized Forms with Custom Validation**

The application includes five different forms (`NonconformityForm`, `NonconformityLineForm`, `NonconformityStatusForm`, `NonconformityCloseForm`, `NonconformityFilterForm`), each with custom validation logic:

- **Conditional uniqueness validation**: The code validator only checks uniqueness on creation, not on edit (by checking `self.instance.pk`)
- **Cross-field validation**: The `clean()` method validates relationships between fields
- **Dynamic field modification**: The form's `__init__` method dynamically sets required fields and customizes empty labels based on context
- **Data transformation**: Automatic uppercase conversion of codes in the `clean_code()` method

**5. Dual-Mode AJAX/Traditional POST Support**

Several views (`change_status`, `add_action`) implement a pattern that detects AJAX requests using `request.headers.get('X-Requested-With')` and returns either JSON (for AJAX) or HttpResponse redirects (for traditional POST).

**6. Responsive CSS Architecture**

The CSS (`static/css/styles.css`) implements a complete responsive design system:

- **Flexbox-based two-column layout** that adapts to mobile (50-50 split → stacked)
- **Three breakpoints** (768px, 992px, 1200px) with progressive font size reduction
- **CSS animations** (`@keyframes slideIn` for messages)
- **Fixed-position message container** with z-index management
- **Table responsiveness** using `overflow-x: auto` and `min-width` constraints
- **Modal overlay system** with proper body scroll management

**7. Automatic Timestamp and User Tracking**

The models use `auto_now_add=True` for creation timestamps and the views automatically inject `request.user` into relevant objects, creating a complete audit trail without manual intervention. The `closure_date` is automatically managed by business logic in the views based on status changes.

**8. CSV Export with Applied Filters**

The export functionality doesn't just dump all data—it applies the exact same filters the user selected in the UI by reusing the `get_filtered_nonconformities()` function and passing `request.GET`. This maintains user context.

In summary, this project demonstrates complexity through: database relationships, JavaScript patterns, custom form validation, responsive design, dual-mode AJAX support, and domain-specific business logic—all integrated into an application that solves real-world regulatory compliance needs.

---

## File Structure and Description

### **Django Project Configuration**

- **`quality/settings.py`**: Main Django settings file configuring installed apps (`nonconformities`, `accounts`, `core`), database (SQLite), static files, authentication redirects (`LOGIN_URL`, `LOGIN_REDIRECT_URL`), internationalization (Spanish language, UTC timezone), and security settings (CSRF protection, password validators).

- **`quality/urls.py`**: Root URL configuration mapping `/admin/` to Django admin, `/` to accounts home, `/accounts/login/` and `/accounts/logout/` to authentication views, and `/nonconformities/` to the nonconformities app URLs.

- **`quality/wsgi.py`**: WSGI application entry point for deployment to production servers.

- **`manage.py`**: Django's command-line utility for running development server, creating migrations, running migrations, creating superusers, and other administrative tasks.

### **Core App (Shared Reference Data)**

- **`core/models.py`**: Defines the `Area` model representing organizational departments/areas. This model is designed to be cross-functional and reusable across future quality management modules (audits, training, document control, etc.). Contains `description` and `codification` fields.

- **`core/admin.py`**: Registers `Area` model with Django admin interface for easy data management.

- **`core/migrations/`**: Database migration files tracking schema changes for the core app.

### **Nonconformities App (Main Application)**

- **`nonconformities/models.py`**: Contains five core models:
  - `Severity`: Severity levels for nonconformities (e.g., Critical, Major, Minor)
  - `Status`: Workflow states (e.g., Open, Closed)
  - `Category`: Classification categories for grouping similar nonconformities
  - `Nonconformity`: Main entity with fields for code, description, creation_date, closure_date, user (creator), status, category, area, and severity. Implements automatic timestamping.
  - `NonconformityLine`: Audit trail entries linked to a nonconformity via ForeignKey with CASCADE delete. Records action_description, date, and user for every action taken.

- **`nonconformities/views.py`**: Contains 10 views implementing full CRUD plus specialized workflows:
  - `nonconformity_list`: Displays filtered list with context for filter dropdowns
  - `nonconformity_detail`: Full detail page view
  - `nonconformity_detail_partial`: AJAX endpoint returning HTML fragment for dynamic panel loading
  - `create_nonconformity`: Creates new NC with automatic user assignment and initial action line
  - `update_nonconformity`: Edits existing NC with automatic audit log entry
  - `change_status`: Changes NC status with automatic closure_date management, supports AJAX
  - `close_nonconformity`: Dedicated workflow for closing NCs with confirmation form
  - `reopen_nonconformity`: Reopens closed NCs, clearing closure_date
  - `add_action`: Adds action lines to NCs, supports AJAX with JSON response
  - `export_nonconformities`: Exports filtered NCs to CSV file
  - `get_filtered_nonconformities`: Helper function building dynamic ORM queries from GET parameters

- **`nonconformities/forms.py`**: Defines five forms with custom validation:
  - `NonconformityForm`: Main create/edit form with code uniqueness validation (only on create), minimum description length (10 chars), automatic uppercase conversion, and required field enforcement
  - `NonconformityLineForm`: Simple form for adding action descriptions with minimum 5 character validation
  - `NonconformityStatusForm`: Status change dropdown form
  - `NonconformityCloseForm`: Closure confirmation form with optional comment and required checkbox
  - `NonconformityFilterForm`: Advanced filtering form with ModelChoiceField for foreign key relations

- **`nonconformities/urls.py`**: URL routing for the nonconformities app mapping paths to views with named URLs (e.g., `nonconformity_list`, `create_nonconformity`, `nonconformity_detail`, `change_status`, `add_action`, `export`).

- **`nonconformities/admin.py`**: Registers all nonconformity models with Django admin. Includes custom `NonconformityAdmin` with list_display configuration, list_filter options, and inline `NonconformityLineInline` for editing action lines within the nonconformity admin page.

- **`nonconformities/migrations/`**: Database migration files including `0002_severity_alter_nonconformity_severity.py` which contains custom data migration code to copy severity records from core_severity to nonconformities_severity during the architectural refactoring, preserving all existing data.

### **Templates**

- **`templates/base.html`**: Master template defining HTML structure, including header with logo and user authentication status, logout form with CSRF protection, navigation, Django messages container with dismissible alerts, and blocks for content and extra scripts. Loads `styles.css` and `scripts.js`.

- **`templates/registration/login.html`**: Login page with username/password form, CSRF token, error messages display, and link to nonconformities list after successful authentication.

- **`nonconformities/templates/nonconformities/nonconformity_list.html`**: Main list view implementing two-column layout. Left column contains filter form embedded in table headers, action buttons (New NC, Export), and clickable NC rows with data-id attributes. Right column displays detail panel. Includes modal structure for mobile responsive view.

- **`nonconformities/templates/nonconformities/nonconformity_detail_partial.html`**: AJAX-loaded template fragment showing NC details, status change form, edit button, close/reopen buttons, action lines timeline, and add action form with embedded JavaScript for AJAX submission. This template is loaded into both the desktop panel and mobile modal.

- **`nonconformities/templates/nonconformities/nonconformity_detail.html`**: Full-page detail view (used when accessing NC directly via URL rather than through list interface).

- **`nonconformities/templates/nonconformities/create_nonconformity.html`**: Form page for creating and editing nonconformities. Dynamically displays "Create" or "Edit" based on context variable `is_edit`. Includes form rendering with error display.

- **`nonconformities/templates/nonconformities/close_nonconformity.html`**: Confirmation page for closing a nonconformity with optional closing comment field and required confirmation checkbox.

### **Static Files**

- **`static/css/styles.css`**: Complete CSS stylesheet (468 lines) implementing:
  - Responsive two-column layout using flexbox
  - Mobile-first responsive design with three breakpoints
  - Table styling with hover effects and selection highlighting
  - Modal overlay system for mobile
  - Django messages styling with slide-in animation
  - Button styles (primary, secondary, danger, warning)
  - Form input and select styling
  - Header and navigation layout

- **`static/js/scripts.js`**: JavaScript file (111 lines) implementing:
  - DOMContentLoaded event listener for initialization
  - Click handlers for table rows with data-id attributes
  - AJAX fetch calls to load NC details dynamically
  - Responsive behavior detection using matchMedia
  - Modal open/close functionality with body scroll locking
  - Filter form auto-submit on change
  - Enter key submission for filter inputs
  - Escape key modal closing
  - Selected row visual state management

### **Accounts App**

- **`accounts/views.py`**: Contains `home_view` which redirects authenticated users to nonconformities list and anonymous users to login page.

- **`accounts/urls.py`**: Maps root URL to home_view.

### **Configuration Files**

- **`requirements.txt`**: Python dependencies specification listing Django==5.2, asgiref==3.8.1, and sqlparse==0.5.3.

- **`.gitignore`**: Git ignore rules for virtual environment (`venv/`), Python cache files (`__pycache__/`, `*.pyc`), SQLite databases (`*.sqlite3`), and IDE configuration folders (`.vscode/`, `.idea/`).

---

## How to Run the Application

### **Prerequisites**

- Python 3.8 or higher
- pip (Python package installer)
- Git (to clone the repository)

### **Installation Steps**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/monsalvegf/capstone.git
   cd capstone/quality
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to set username, email, and password.

6. **Create initial reference data:**

   Access Django admin to populate initial data:
   ```bash
   python manage.py runserver
   ```

   Navigate to `http://127.0.0.1:8000/admin/` and log in with superuser credentials.

   Create at least:
   - 2-3 **Severities** (e.g., Critical, Major, Minor)
   - 2-3 **Statuses** (e.g., Abierta, Cerrada - note: use Spanish names as the code looks for "cerrad" and "abierta")
   - 2-3 **Categories** (e.g., Documentation, Process, Product)
   - 1-2 **Areas** (e.g., Production, Quality Control)

7. **Access the application:**

   Navigate to `http://127.0.0.1:8000/` and log in with your superuser credentials.

### **Creating Your First Nonconformity**

1. Click the **"+ Nueva NC"** button
2. Fill in the required fields:
   - **Code**: Unique identifier (e.g., NC-2024-001)
   - **Description**: Detailed description (minimum 10 characters)
   - **Severity**: Select from dropdown
   - **Category**: Select from dropdown
   - **Area** (optional): Select from dropdown
   - **Status**: Select or leave default (Abierta)
3. Click submit
4. The system automatically creates an initial action line and redirects to the detail view

### **Key Features to Test**

- **Filtering**: Use the input fields in the table header to filter by code, date, description, severity, category, or status
- **AJAX Detail Loading**: Click on any row in the list to load details dynamically in the right panel (or modal on mobile)
- **Status Changes**: Use the dropdown in the detail panel to change status
- **Close/Reopen**: Use the "Cerrar NC" button to close with confirmation, or "Reabrir NC" to reopen
- **Add Actions**: Use the form at the bottom of the detail panel to add action lines (audit trail)
- **Edit**: Click "✏️ Editar NC" to modify nonconformity details
- **Export**: Click "Exportar" to download filtered results as CSV
- **Responsive Design**: Resize browser window below 768px to see mobile layout with modal

---

## Additional Information

### **Technology Stack**

- **Backend**: Django 5.2 (Python web framework)
- **Database**: SQLite3 (development database)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **AJAX**: Fetch API for asynchronous requests
- **Authentication**: Django built-in authentication system
- **Admin Interface**: Django Admin for data management

### **Design Decisions**

1. **No Delete Functionality**: Following quality management best practices, nonconformities are never deleted. They are closed instead, preserving the complete audit trail for regulatory compliance.

2. **Automatic Audit Trail**: Every action (create, edit, status change, close, reopen) automatically creates a `NonconformityLine` entry with timestamp and user attribution, ensuring complete traceability.

3. **Spanish UI Labels with English Code**: The interface uses Spanish labels (the primary language for the target users) while the codebase uses English (following programming conventions). This is intentional for a B2B application targeting Spanish-speaking industries.

4. **Progressive Enhancement**: All features work with and without JavaScript. AJAX is used to enhance the experience, but traditional form POST provides fallback functionality.

5. **Modular Architecture**: The separation into three apps (`core`, `nonconformities`, `accounts`) is intentional to support future expansion with additional quality management modules (audits, corrective actions, document control, training, etc.).

### **Browser Compatibility**

Tested and working on:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### **Future Enhancements**

This application is designed as a foundation for a complete Quality Management System. Planned future modules include:
- Internal Audits Management
- Corrective and Preventive Actions (CAPA)
- Document Control
- Supplier Management
- Training and Competence Tracking
- Risk Management
- Customer Complaints
- Quality KPI Dashboard
- Equipment Calibration Tracking

### **Known Limitations**

- No pagination (suitable for up to ~500 NCs; would need Django Paginator for larger datasets)
- No file attachments (could be added with Django FileField)
- No email notifications (could be added with Django email system)
- SQLite database (suitable for development; PostgreSQL recommended for production)
- SECRET_KEY and DEBUG settings hardcoded (should use environment variables for production deployment)

### **License**

This project was created as the capstone project for CS50's Web Programming with Python and JavaScript course.

---

**Author**: Fernando Monsalve
**Course**: CS50 Web Programming with Python and JavaScript
**Project**: Final Capstone - Quality Management System
