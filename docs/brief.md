# theStudentr App - Project Brief
_Developed by Botho Maje with Qt (Python) & MySQL_\
_Due by 16 September 2025_\
\
This brief defines the scope, requirements, constraints, and delivery plan for a desktop Student Assistant application built with Qt (Python) and MySQL.
The app is based on my assignment tracking spreadsheet and focuses on two core components:
1. a due-date tracker for assignments, and
2. a grade book for calculating year and final marks per module with clear, colour-based status cues.

## Project Objectives
- Provide a simple, reliable, single-user desktop tool to manage assignment due dates and grade calculations.
- Mirror the existing spreadsheet logic while enforcing validation and improving usability and persistence via MySQL.
- Offer clear visibility into deadlines (days remaining) and academic standing (per-module averages and final mark).
- Align to the module’s marking rubric: four GUI pages (Login, Dashboard, Assignments, Grades), working buttons, calendar and logo visible, screenshots for submission.

## Scope
The MVP includes two functional areas and a login page:
1. due-date tracker with CRUD for assignments and live “days left”, and
2. grade book for per-module assessment weights, scores, year mark, exam mark, and final mark with rule-driven colour states.

A dashboard provides a calendar, logo, clock, and “today at a glance” widgets.

## Out of Scope for Main Submission
- Multi-user accounts or remote sync.
- Push notifications or background services.
- Complex timetable management (can be a later enhancement).
- Role-based access control; analytics dashboards beyond averages.

## Users & Environment
Single user (student) on a local machine. The app is a Python Qt desktop application. Data is stored in a local MySQL instance.

## Functional Requirements
- **Login (GUI 1):** Accept a fixed username (surname) and password (student number). On success, open the dashboard; otherwise, show an error.
- **Dashboard (GUI 2):** Show a calendar, a visible logo, an active clock, and two panels:
  1. upcoming/due assignments (next 7–14 days);
  2. today’s submitted/graded status summary. Buttons navigate to Assignments and Grades pages.
- **Assignments (GUI 3):** CRUD for assignments: subject/module, title, due date, start date, submission date, status (Not Started / In Progress / Done / Skipped). Display days remaining = DATEDIFF(due_date, current_date). Filter by status.
- **Grades (GUI 4):** Per module, maintain assessment items (weight %, score %). Compute year mark, exam mark(s), and final mark using module-specific weights and rules. Provide per-row status colour and module-level indicators.

## Grade/Status Colour Logic
- **Yellow:** Submission not completed (e.g., assignment not submitted).
- **Orange:** Submission completed but score not yet recorded.
- **Green:** Score ≥ 50% (per assignment); module final mark ≥ 50% AND (if applicable) exam subminimum achieved AND all exam-entry criteria met.
- **Red:** Score < 50% (per assignment); OR final mark < 50%; OR exam subminimum not met even if final ≥ 50%; OR exam-entry criteria not satisfied.

## Per-Module Rules
- Final mark = (Year Mark × Year Weight) + (Exam Mark × Exam Weight). Weights are per module.
- Pass threshold: final ≥ 50%.
- Exam subminimum: if set (per module), the exam mark must be ≥ subminimum; otherwise, the final mark is flagged as red.
- Year mark = weighted average of all formative assessments for the module.
- Exam admission requirements (per module): minimum number of assignments submitted (default 1) and, if specified, a minimum year mark threshold

## Data Model (MySQL)
The schema is intentionally minimal and normalised for clarity. All write operations use parameterised queries.

|Table      |Fields (key fields in bold)                                                                                                                                                  |Notes|
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|
|modules    |**`id`**, `code`, `name`, `year_weight_pct`, `exam_weight_pct`, `min_assignments_for_exam` (default 1), `min_year_mark_for_exam` (nullable), `exam_subminimum_pct` (nullable)|Holds per-module rules for weights and admission thresholds.|
|assignments|**`id`**, `module_id` (FK->modules), `title`, `start_date`, `submit_date` (nullable), `status` ENUM(‘Not Started’, ‘In Progress’, ‘Done’, ‘Skipped’)                         |Due-date tracker; `days_left` computed in queries as `DATEDIFF(due_date, CURDATE())`.|
|marks      |**`id`**, `assignment_id` (FK->assignments), `weight_pct`, `score_pct` (nullable), `submitted` BOOL                                                                          |Stores assessment weight and score; if `submitted = TRUE` and `score` is NULL → Orange; if `submitted = FALSE` → Yellow; otherwise Green/Red based on score ≥ 50.|
|views      |`v_due_assignments`, `v_module_year_mark`, `v_module_final_status`                                                                                                           |Pre-computed lists for Dashboard and Grades with colour-classification fields (`v_due_assignments`, `v_module_year_mark`, `v_module_final_status`).|

## GUI Architecture
- **GUI 1 – Login:** Surname + student number. On success → Dashboard; Cancel → exit.
- **GUI 2 – Dashboard:** Calendar widget, visible logo, live clock. Panels: (i) Upcoming assignments (next 7–14 days), (ii) Quick status counts (Pending/Done). Buttons to open Assignments and Grades.
- **GUI 3 – Assignments:** Table + form controls for CRUD, status filter, instant days_left display; writes to MySQL.
- **GUI 4 – Grades:** Tabs per module or module selector. Shows assessment rows (weight/score), year mark, exam mark(s), final mark, and colour state. Warn if Σ(weights for a module) ≠ 100%.

## Non-Functional Requirements
- **Usability:** clear labels, input validation (dates, weights 0–100, scores 0–100).
- **Reliability:** immediate commits for CRUD; handle DB connectivity errors gracefully.
- **Performance:** dataset is small; all pages should load in under 200ms on a typical laptop.
- **Portability:** Python 3.10+, PyQt5/PySide6, MySQL 8.x; local single-user deployment.

## SDLC Phases & Deliverables
### Requirements & Analysis
- Confirm functional rules from the spreadsheet (statuses, colours, weights).
- Define per-module parameters (weights, subminima, min assignments/year mark).
- Acceptance criteria for each page.

### Design
- ERD + schema DDL; DAL API signatures; UI wireframes and widget lists.
- Navigation via QStackedWidget; model helpers for status/colour.

### Implementation
- Create database & seed modules; implement DAL with parameterised queries.
- Build 4 Qt pages; wire signals/slots; validation; colour mapping.

### Testing
- Unit tests for calculations; functional tests for CRUD; negative tests for validation.
- Smoke test on a clean machine; prepare screenshots for submission.

### Deployment & Submission
- Export schema.sql/seed.sql; package code and assets; include screenshots and short explanations per GUI page.

## Timeline & Management Plan
|Phase|Dates|Activities/Milestones|
|-----|-----|---------------------|
|Requirements & Analysis|20 Aug – 22 Aug|Confirm rules from sheet; lock scope & acceptance criteria.|
|Data Model & Setup|23 Aug – 26 Aug|MySQL install, schema.sql, seed.sql; DAL stubs.|
|UI Prototypes|27 Aug – 31 Aug|Qt Designer for 4 pages; navigation wiring; assets (logo).|
|Implementation I|1 Sept – 6 Sept|Assignments CRUD + Dashboard panels; days_left & filters.|
|Implementation II|7 Sept – 10 Sept|Grades logic: weights/scores, year/exam/final calc, colour rules.|
|Integration & Testing|11 Sept – 13 Sept|End-to-end tests, validation, error handling, polish.|
|Packaging|14 Sept – 15 Sept|Screenshots, explanations per GUI page; final review.|
|Submission|16 Sept|Submit all required artefacts by 17:00 SAST.|

## Risks & Mitigation
|Risk|Mitigation|
|----|----------|
|DB Driver Issues|Use mysql-connector-python + QTableWidget if QMYSQL plugin unavailable; keep config.json.|
|Time Overrun|Time-box; defer non-critical enhancements.|
|Validation Gaps|Unit tests for weight sums and final mark; manual test checklist.|
|Data Entry Errors|Combos for enums, date/time edits, numeric spin boxes; inline hints/errors.|

## Deliverables
- Source code (.py) + .ui files; assets (logo).
- schema.sql and seed.sql; config.json for DB connection.
- Four screenshots (full-screen) and brief explanations per GUI page (for submission).
- README with run instructions; test notes.
