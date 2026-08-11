# Graph Report - server+client  (2026-08-11)

## Corpus Check
- Corpus is ~19,457 words - fits in a single context window. You may not need a graph.

## Summary
- 768 nodes · 1448 edges · 58 communities (50 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 142 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Client App Shell
- File Service Ops
- Vite Client Toolchain
- Password Reset Auth
- User Entity Model
- React Package Deps
- Mail And Ngrok
- Dev Upload Logging
- Boss Admin GUI
- Upload Validation CSV
- Auth Session Service
- TypeScript Config
- Flask Auth Routes
- Boss Admin Privilege
- Service Layer Core
- Pending Upload Repo
- Upload Service Moves
- Boss Admin Scripts
- Admin API Controllers
- Files API Controllers
- Session Before Request
- User Repository CRUD
- Role Status Toggles
- Uploads API Routes
- User ID Migration
- Email User Lookup
- Completed Upload Paths
- Admin Pending Denied
- App Blueprint Wiring
- Admin User Class
- Eye Crossed Icon
- Regular User Class
- Auth User Approvals
- Banner Logo Public
- Dark Banner Logo Public
- Admin Client Pages
- Dashboard Login Upload
- Auth Service Helpers
- Paths And Logging
- Src Banner Logo
- Dark Banner Logo Src
- Declined Upload Logs
- Read Upload Logs
- Eye Visibility Icon
- User ID Sequence
- Upload Search Cache
- CSV Metrics Bootstrap
- Server Version Package
- Forgot Reset Pages
- Client Version Info
- Version Reexports
- Repositories Package
- Services Package
- Assistant Font
- Register Page

## God Nodes (most connected - your core abstractions)
1. `User` - 42 edges
2. `FileService` - 27 edges
3. `get_project_root()` - 26 edges
4. `toastError` - 25 edges
5. `UserRepository` - 24 edges
6. `AuthService` - 22 edges
7. `UploadService` - 22 edges
8. `toastSuccess` - 22 edges
9. `UploadRepository` - 18 edges
10. `BossAdminGUI` - 16 edges

## Surprising Connections (you probably didn't know these)
- `create_app Flask factory` --conceptually_related_to--> `Flask CORS Mail Waitress JWT stack`  [INFERRED]
  server/app.py → server/requirements.txt
- `Vite Dev Proxy to Flask` --rationale_for--> `getBackendUrl`  [INFERRED]
  client/README.md → client/src/api.ts
- `Dashboard Security Challenge Code` --conceptually_related_to--> `AuthUser`  [AMBIGUOUS]
  client/src/assets/robots.txt → client/src/auth.tsx
- `humans.txt Angular Frontend Claim` --conceptually_related_to--> `Vite React Toolchain`  [AMBIGUOUS]
  client/src/assets/humans.txt → client/package.json
- `POST /login handler` --shares_data_with--> `Session and JWT timeout settings`  [INFERRED]
  server/controllers/auth_controller.py → server/config/config_template.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Dark Mode Banner Logo Composition** — client_public_assets_icons_banner_logo_dark_mode_hebrew_wordmark, client_public_assets_icons_banner_logo_dark_mode_latin_wordmark, client_public_assets_icons_banner_logo_dark_mode_yellow_stroke, client_public_assets_icons_banner_logo_dark_mode_dark_ui [INFERRED 0.85]
- **Youth Center Brand Identity Elements** — client_public_assets_icons_banner_logo_dark_mode_brand_mark, client_public_assets_icons_banner_logo_dark_mode_youth_center, client_public_assets_icons_banner_logo_dark_mode_hebrew_wordmark, client_public_assets_icons_banner_logo_dark_mode_latin_wordmark [INFERRED 0.95]
- **Merkaz Tzeirim Kfar Kama brand mark** — client_public_assets_icons_banner_logo_asset, client_public_assets_icons_banner_logo_merkaz_tzeirim, client_public_assets_icons_banner_logo_kfar_kama, client_public_assets_icons_banner_logo_hebrew_wordmark, client_public_assets_icons_banner_logo_latin_subtitle, client_public_assets_icons_banner_logo_yellow_brush [INFERRED 0.95]
- **Public assets banner logo for web header** — client_public_assets_icons_banner_logo_asset, client_public_assets_icons_banner_logo_web_header_role, client_public_assets_icons_banner_logo_merkaz_tzeirim [INFERRED 0.85]
- **Hebrew wordmark with Latin place subtitle** — client_public_assets_icons_banner_logo_hebrew_wordmark, client_public_assets_icons_banner_logo_latin_subtitle, client_public_assets_icons_banner_logo_merkaz_tzeirim, client_public_assets_icons_banner_logo_kfar_kama [INFERRED 1.00]
- **Merkaz Tzeirim Dark Mode Brand Lockup** — client_src_assets_icons_banner_logo_dark_mode_dark_mode_banner_logo, client_src_assets_icons_banner_logo_dark_mode_mustard_brushstroke, client_src_assets_icons_banner_logo_dark_mode_white_hebrew_wordmark, client_src_assets_icons_banner_logo_dark_mode_kfar_kama, client_src_assets_icons_banner_logo_dark_mode_black_background [EXTRACTED 1.00]
- **Banner Brand Mark Composition** — client_src_assets_icons_banner_logo_hebrew_merkaz_tzeirim, client_src_assets_icons_banner_logo_cyrillic_kfar_kama, client_src_assets_icons_banner_logo_yellow_brushstroke [EXTRACTED 1.00]
- **Shared Bearer token localStorage flow** — client_src_api_token_key, client_src_auth_authprovider, client_src_authfetch_authgetjson, client_src_authfetch_authpostjson, client_src_api_requestjson [EXTRACTED 1.00]
- **Upload progress reporting pipeline** — client_src_api_uploadfiles, client_src_api_uploadprogressevent, client_src_uploadprogress_uploadprogressprovider, client_src_uploadprogresswidget_uploadprogresswidget [INFERRED 0.75]
- **App provider and route shell composition** — client_src_app_app, client_src_auth_authprovider, client_src_uploadprogress_uploadprogressprovider, client_src_app_shell [EXTRACTED 1.00]
- **User auth lifecycle: register, login, password reset** — client_src_pages_registerpage_register, client_src_pages_loginpage_login, client_src_pages_forgotpasswordpage_forgot, client_src_pages_resetpasswordpage_reset, server_controllers_auth_controller_auth_bp [INFERRED 0.95]
- **Upload then admin approve or decline** — client_src_pages_uploadfilepage_upload, client_src_pages_myuploadspage_history, client_src_pages_admin_uploadspage_admin_uploads, server_controllers_uploads_controller_uploads_bp [INFERRED 0.95]
- **Admin tabs for users pending denied metrics uploads** — client_src_pages_admin_adminlayout_shell, client_src_pages_admin_pendingpage_pending, client_src_pages_admin_deniedpage_denied, client_src_pages_admin_userspage_users, client_src_pages_admin_metricspage_metrics [EXTRACTED 1.00]
- **Authentication Stack (login JWT session)** — server_services_auth_service_login, server_repositories_user_repository_find_by_email, server_models_user_entity_check_password, server_services_auth_service_create_session, server_services_jwt_service_issue_token, server_services_session_state_store_mark_online [EXTRACTED 1.00]
- **Upload Pipeline (validate log approve)** — server_services_upload_service_validate_file, server_services_upload_service_upload_files, server_services_upload_service_log_pending_upload, server_repositories_upload_repository_uploadrepository, server_services_upload_service_move_upload, server_services_upload_service_log_completed_upload, server_services_file_service_monitor_pending_log_changes [EXTRACTED 1.00]
- **Admin Tooling (approvals and boss admin)** — server_services_admin_service_approve_user, server_services_admin_service_toggle_user_role, server_dev_toolkit_set_boss_admin_set_boss_admin, server_dev_toolkit_set_boss_admin_gui_bossadmingui, server_models_user_entity_user, boss_admin_privilege [INFERRED 0.85]

## Communities (58 total, 8 thin omitted)

### Community 0 - "Client App Shell"
Cohesion: 0.06
Nodes (70): react-router-dom Dependency, localStorage token key, App, DarkModeToggle, Shell, Dashboard Security Challenge Code, AdminRoute, AuthContext (+62 more)

### Community 1 - "File Service Ops"
Cohesion: 0.06
Nodes (23): FileService, Recursively check if a directory contains any files at any depth. Args:…, Browse a directory and return files/folders with metadata., Delete an item by moving it to trash., Service for file management operations., Get the directory and filename for file download., Get MIME type of a file., Get the share directory path. (+15 more)

### Community 2 - "Vite Client Toolchain"
Cohesion: 0.09
Nodes (30): Merkaz File Library Portal, Vite React Toolchain, Merkaz Web UI, Flask Serves client/dist, Vite Dev Proxy to Flask, buildUrl(), getBackendUrl, getToken() (+22 more)

### Community 3 - "Password Reset Auth"
Cohesion: 0.13
Nodes (25): _db_path(), delete_token(), Password reset token persistence (one-time use)., save_token(), token_exists(), AuthService.is_session_valid(), AuthService.reset_password(), decode_token() (+17 more)

### Community 4 - "User Entity Model"
Cohesion: 0.09
Nodes (13): ABC, CSV Auth User Store, Format a name: lowercase and capitalize first letter., Returns the full name of the user., Returns True if user is an admin. Overridden in Admin class., Returns True if user status is active., Returns True if user is a boss admin (set manually by dev)., Checks the provided password against the stored hash. (+5 more)

### Community 5 - "React Package Deps"
Cohesion: 0.08
Nodes (25): dependencies, react, react-dom, react-router-dom, devDependencies, @types/react, @types/react-dom, typescript (+17 more)

### Community 6 - "Mail And Ngrok"
Cohesion: 0.10
Nodes (22): POST /register handler, run_ngrok.main(), Get all admin email addresses., Check if a user is an outside user (username part, case-insensitive)., _public_base_url(), Mail service - Email sending and notifications., Sends an email to the user when their account is denied (asynchronously)., Internal function that actually sends the email (runs in background thread). (+14 more)

### Community 7 - "Dev Upload Logging"
Cohesion: 0.11
Nodes (23): get_logged_paths(), get_max_upload_id_from_logs(), get_next_upload_id() (dev toolkit), get_share_folder(), get_upload_completed_log_file(), get_upload_id_sequence_file(), log_file_to_completed(), Get the next upload ID, ensuring it's higher than any existing ID. (+15 more)

### Community 8 - "Boss Admin GUI"
Cohesion: 0.12
Nodes (12): BossAdminGUI, main(), Extract username part from email (before @)., Refresh the user list and boss admins list., Handle search box changes., Update the boss admins listbox., Handle user selection from main list., Handle boss admin selection from boss admins list. (+4 more)

### Community 9 - "Upload Validation CSV"
Cohesion: 0.13
Nodes (20): Validate a file for upload., UploadService.upload_files(), UploadService.validate_file(), create_file_with_header(), csv_to_xlsx_in_memory(), get_max_user_id_from_files(), get_next_upload_id(), _get_upload_id_sequence_file_path() (+12 more)

### Community 10 - "Auth Session Service"
Cohesion: 0.12
Nodes (14): cross_origin, Refreshes the current user's session with latest data from database., refresh_session(), AuthService, get_current_user_email(), is_user_authenticated(), Create a session for the given user., Check if the current session is valid (not invalidated). (+6 more)

### Community 11 - "TypeScript Config"
Cohesion: 0.10
Nodes (19): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, resolveJsonModule (+11 more)

### Community 12 - "Flask Auth Routes"
Cohesion: 0.15
Nodes (14): Merkaz Server Application - Main entry point. backend made by Amir Labay…, api_forgot_password(), POST /login handler, POST /forgot-password handler, logout(), route, POST /reset-password/<token> handler, Clear the current session. (+6 more)

### Community 13 - "Boss Admin Privilege"
Cohesion: 0.15
Nodes (9): Set selected user as boss admin., Revoke boss admin status from selected user., Reads all users from the authentication database., Rewrites the entire auth user database., Returns a list of all admin email addresses., Toggles the role of a user between 'admin' and 'user'. Uses polymorphism to…, Toggles the status of a user between 'active' and 'inactive'., Factory method to create the appropriate user type based on role. Polymorphic… (+1 more)

### Community 14 - "Service Layer Core"
Cohesion: 0.17
Nodes (9): Upload repository - Manage upload logs and data., User repository - Data access layer for user data (CSV or DB)., Admin service - Admin operations, approvals, and reports., File service - File management and validation., Upload service - File upload logic and workflow., File operations and MIME validation utilities., get_logger(), Logging configuration module. Sets up Python logging with timestamp, file, line… (+1 more)

### Community 15 - "Pending Upload Repo"
Cohesion: 0.14
Nodes (10): Find a pending upload by upload_id., Find pending uploads by filename or path., Remove an entry from the pending log by upload_id., Repository for upload data operations., Get the path to the pending upload log file., UploadRepository, UploadService.log_pending_upload(), Remove an entry from the pending log by upload_id. (+2 more)

### Community 16 - "Upload Service Moves"
Cohesion: 0.17
Nodes (10): Generates a unique filename by appending _1, _2, etc. if a file with the same…, Process multiple file uploads., Service for upload operations., Get the next unique upload ID., Move a file from old_path to new_path in the share directory., Edit the path of a completed upload and move the file., Edit the path of a folder and move the folder, updating all nested…, UploadService (+2 more)

### Community 17 - "Boss Admin Scripts"
Cohesion: 0.16
Nodes (11): Boss Admin Privilege, BossAdminGUI.set_boss_admin(), Set boss admin status for a user., set_boss_admin(), User.create_user(), User.get_all(), User.save_all(), UserRepository.create_user() (+3 more)

### Community 18 - "Admin API Controllers"
Cohesion: 0.32
Nodes (13): GET /admin/denied users, admin_metrics(), GET /admin/pending users, GET /admin/users list, POST /admin/approve/<email>, POST /admin/deny/<email>, download_metrics_xlsx(), heartbeat() (+5 more)

### Community 19 - "Files API Controllers"
Cohesion: 0.23
Nodes (13): create_folder(), delete_item(), download_file(), download_folder(), downloads(), get_useful_links(), preview_file(), route (+5 more)

### Community 20 - "Session Before Request"
Cohesion: 0.15
Nodes (13): before_request(), before_request, Mark user as online and reset session timer with each request., before_request(), before_request, Mark user as online and reset the session timer with each request., before_request(), before_request (+5 more)

### Community 21 - "User Repository CRUD"
Cohesion: 0.19
Nodes (6): Create a new user using the factory method., Repository for user data operations., Find a user by email in the pending database., Find a user by email in the denied database., Save all pending users., UserRepository

### Community 22 - "Role Status Toggles"
Cohesion: 0.17
Nodes (6): Toggle a user's role between admin and user., Toggle a user's status between active and inactive., Check if a user is a boss admin., Toggle a user's role between admin and user. Uses polymorphic…, Toggle a user's status between active and inactive. Uses User.toggle_status()., Invalidate all sessions for a specific user by email.

### Community 23 - "Uploads API Routes"
Cohesion: 0.29
Nodes (9): GET /admin/uploads queue, POST /admin/decline_upload, POST /admin/edit_upload_path, POST /admin/move_upload approve, GET /my_uploads history, route, POST /upload pending review, Find a user by email in the authentication database. (+1 more)

### Community 24 - "User ID Migration"
Cohesion: 0.17
Nodes (7): migrate_user_ids(), Migration script to add unique IDs to existing users in CSV files. This script:…, Migrates existing users to include unique IDs. Preserves existing IDs if…, Rewrites the entire pending user database., Rewrites the entire denied user database., Helper to read users from a given CSV file., Helper to write a list of users to a given CSV file.

### Community 25 - "Email User Lookup"
Cohesion: 0.17
Nodes (6): Finds a user by email in the authentication database (case-insensitive)., Finds a user by email in the pending database (case-insensitive)., Reads all users from the pending registration database., Finds a user by email in the denied database (case-insensitive)., Reads all users from the denied registration database., Normalize email for storage and case-insensitive lookup.

### Community 26 - "Completed Upload Paths"
Cohesion: 0.18
Nodes (6): Update the path of a completed upload., Get the path to the completed upload log file., Monitor upload_pending_log.csv for changes. When row count hasn't changed for 1…, Move an upload from pending to approved location., Re-add pending row and remove completed row after a failed file move., Log a completed upload to the completed log.

### Community 27 - "Admin Pending Denied"
Cohesion: 0.21
Nodes (7): Get all pending users., Get all denied users., Save all denied users., AdminService, Move a denied user back to pending., Service for admin operations., Deny a pending user registration.

### Community 28 - "App Blueprint Wiring"
Cohesion: 0.20
Nodes (10): create_app Flask factory, Create and configure the Flask application., SPA catch-all static serve, Session and JWT timeout settings, admin_bp /admin blueprint, auth_bp blueprint, GET /browse directory listing, files_bp blueprint (+2 more)

### Community 29 - "Admin User Class"
Cohesion: 0.20
Nodes (5): Admin, Admin user class. Inherits from User base class with admin privileges., Admin users are always admins., Returns permissions for admin users. Overrides parent method., Admin users can manage other users. Overrides parent method.

### Community 30 - "Eye Crossed Icon"
Cohesion: 0.25
Nodes (8): crossed-out eye glyph, diagonal slash, eye outline, hidden or private content indicator, pairs with open-eye icon, password visibility toggle (hidden state), solid pupil circle, flat white line icon

### Community 31 - "Regular User Class"
Cohesion: 0.25
Nodes (5): Regular user class. Inherits from User base class., Regular users are not admins., Returns permissions for regular users., Regular users cannot manage other users., RegularUser

### Community 32 - "Auth User Approvals"
Cohesion: 0.29
Nodes (4): Get all authenticated users., Save all authenticated users., Approve a pending user registration., Reset a user's password.

### Community 33 - "Banner Logo Public"
Cohesion: 0.38
Nodes (7): banner-logo.webp banner brand mark, Hebrew wordmark מרכז / צעירים, Kfar Kama (KFAR - KAMA), Latin subtitle K Φ A R - K A M A, מרכז צעירים (Young Adults Center), Web header / banner logo role, Yellow painterly brush-stroke background

### Community 34 - "Dark Banner Logo Public"
Cohesion: 0.48
Nodes (7): Banner Logo Dark Mode WebP, Kfar Kama Youth Center Brand Mark, Dark Mode Banner UI Asset, Hebrew Wordmark Merkaz Tzeirim, Latin Wordmark KFAR-KAMA, Golden Yellow Paint Stroke, Youth Center of Kfar Kama

### Community 35 - "Admin Client Pages"
Cohesion: 0.33
Nodes (7): AdminLayout tab shell, DeniedPage denied users, MetricsPage Excel log downloads, PendingPage user approval queue, UploadsPage pending file review, UsersPage role and status toggles, MyUploadsPage upload history

### Community 36 - "Dashboard Login Upload"
Cohesion: 0.29
Nodes (7): GET /browse file listing, DashboardPage file browser, GET /search file search, POST /suggest bug report, LoginPage sign in, UploadFilePage multi-file dropzone, Upload extension and size limits

### Community 37 - "Auth Service Helpers"
Cohesion: 0.33
Nodes (4): cleanup_expired_sessions(), get_active_users(), mark_user_offline(), Auth service - Authentication and session handling.

### Community 38 - "Paths And Logging"
Cohesion: 0.29
Nodes (6): Get the upload directory path., Configure logging for the entire application. Args: log_level: Logging level…, setup_logging(), get_project_root(), Private alias for backward compatibility., Determines the project root directory. If path_utils.py is in server/utils/, go…

### Community 39 - "Src Banner Logo"
Cohesion: 0.67
Nodes (6): Hebrew-Cyrillic Circassian Identity, Cyrillic Text КФАР - КАМА, Hebrew Text מרכז צעירים, Banner Logo (Merkaz Tzeirim), Mustard Yellow Brushstroke, Youth Center of Kfar Kama

### Community 40 - "Dark Banner Logo Src"
Cohesion: 0.53
Nodes (6): Solid Black Dark-Mode Background, Dark Mode Banner Logo, Kfar Kama (K Φ A P - K A M A), מרכז צעירים (Merkaz Tzeirim / Youth Center), Mustard Yellow Brushstroke Accent, White Hebrew Wordmark

### Community 41 - "Declined Upload Logs"
Cohesion: 0.33
Nodes (3): Get the path to the declined upload log file., Read all declined uploads from the log file., Log a declined upload.

### Community 42 - "Read Upload Logs"
Cohesion: 0.33
Nodes (3): Read all pending uploads from the log file., Read all completed uploads from the log file., Get all uploads for a specific user.

### Community 43 - "Eye Visibility Icon"
Cohesion: 0.50
Nodes (5): Almond-shaped eye outline, Authentication form UI context, Password visibility eye icon, Show password visibility control, Central pupil circle

### Community 44 - "User ID Sequence"
Cohesion: 0.40
Nodes (5): AdminService.approve_user(), _get_id_sequence_file_path(), get_next_user_id(), Returns the absolute path to the user_id_sequence.txt file., Generates and returns the next unique user ID. Tracks the sequence in a…

### Community 45 - "Upload Search Cache"
Cohesion: 0.50
Nodes (3): Search for uploaded files in the upload_completed_log based on a query string…, get_root_search_cache_dir(), Search cache directory (letter CSV shards).

### Community 46 - "CSV Metrics Bootstrap"
Cohesion: 0.67
Nodes (3): CSV log and user DB bootstrap, CSV user DB and log paths, GET /admin/metrics/download/<log_type>

## Ambiguous Edges - Review These
- `delete_token()` → `AuthService.reset_password()`  [AMBIGUOUS]
  server/services/auth_service.py · relation: conceptually_related_to
- `AuthUser` → `Dashboard Security Challenge Code`  [AMBIGUOUS]
  client/src/assets/robots.txt · relation: conceptually_related_to
- `Vite React Toolchain` → `humans.txt Angular Frontend Claim`  [AMBIGUOUS]
  client/src/assets/humans.txt · relation: conceptually_related_to
- `Vite React Toolchain` → `Legacy npm start/test Tasks`  [AMBIGUOUS]
  client/.vscode/tasks.json · relation: conceptually_related_to
- `Vite React Toolchain` → `Angular Template Extension Recommendation`  [AMBIGUOUS]
  client/.vscode/extensions.json · relation: conceptually_related_to
- `humans.txt Angular Frontend Claim` → `Title and Logo Branding Template`  [AMBIGUOUS]
  client/src/enviroments/logos.template.txt · relation: conceptually_related_to

## Knowledge Gaps
- **90 isolated node(s):** `name`, `version`, `private`, `dev`, `build` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `delete_token()` and `AuthService.reset_password()`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `AuthUser` and `Dashboard Security Challenge Code`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Vite React Toolchain` and `humans.txt Angular Frontend Claim`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Vite React Toolchain` and `Legacy npm start/test Tasks`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Vite React Toolchain` and `Angular Template Extension Recommendation`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `humans.txt Angular Frontend Claim` and `Title and Logo Branding Template`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `User` connect `User Entity Model` to `Dev Upload Logging`, `Boss Admin GUI`, `Auth Session Service`, `Boss Admin Privilege`, `Boss Admin Scripts`, `User Repository CRUD`, `User ID Migration`, `Email User Lookup`, `Admin Pending Denied`, `Admin User Class`, `Regular User Class`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._