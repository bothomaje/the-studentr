# UI Prototyping Phase

## Phase Objective
To create a small and implementation Qt desktop prototype that:
- lets a single user sign in and navigate between the main areas,
- lists modules and assignments with current statuses,
- shows computed year/exam/final marks and admission checks per module,
- allows basic CRUD for assignments and marks (happy-path),
- feels responsive (no blocking UI), and
- (optional) is packaged into an app bundle in CI (artifact).

No business-logic changes are expected—UI should call the existing DAL.

## Deliverables
### 1. UX/Flows
- App map (one diagram) of screens and stacked-widget routes.
- Low-fi wireframes for each screen (PNG or PDF).
- Micro-copy for empty, loading, and error states.

### 2. UI assets & sources
- App logo + app icon set (SVG source + PNG raster sizes).
- .ui files for each screen (Qt Designer).
- A single .qrc resource manifest referencing images/icons.

### 3. Generated UI & wiring
- PyQt-generated UI modules from .ui (no edits by hand).
- Screen logic files that import the generated UI.
- A host window that manages a QStackedWidget with all screens.

### 4. Tests & CI
- Smoke test using pytest-qt that flips between screens and asserts that lists populate (with seeded DB).
- CI pipeline steps that:
    - compile .ui to generated modules,
    - compile .qrc to resources module,
    - run UI tests (marker: ui),
    - build the app and upload artifacts.

### 5. Docs
- docs/ui/ folder: flows, wireframes, and style tokens.
- README section: how to run, how to regenerate UI/resources, where assets live, and “gotchas”.

## Action Plan
### 1. Plan & structure (½ day)
- Confirm screen list and navigation model.
- Decide the minimal data each screen needs from the DAL.
- Sketch wireframes (paper or Figma) and write micro-copy.

### 2. Project structure & assets (½ day)
- Add folders and resource manifest.
- Drop a placeholder logo and app icon; confirm scaling looks crisp.
- Add a simple colour/spacing token table (in the docs) to keep styles consistent as you prototype.

### 3. Build UI shells (.ui) (1 day)
- Create .ui per screen; get layout, tab order, and object names right (object names matter for the generated classes).
- Keep lists/tables read-only at first; stub buttons.

### 4. Generate modules & connect (½ day)
- Convert .ui to generated Python modules (one-time + repeatable).
- Create thin logic files that import the generated UI and raise signals for navigation via the stacked widget.

### 5. Hook up DAL (1 day)
- Wire minimal “happy-path” calls:
    - Dashboard: list modules with computed marks and admission flags.
    - Assignments: list/filter; set status; open “edit marks”.
    - Marks: view/enter weight+score; update derived colour.
- Surface DB errors as non-blocking toast/dialogs.

### 6. Polish, states, and tests (½ day)
- Add empty/loading/error states and status colours everywhere lists appear.
- Add a pytest-qt smoke test that:
    - launches the app,
    - switches tabs,
    - waits for lists to populate,
    - asserts seeded data appears.

### 7. CI & packaging (½ day)
- Ensure .ui/.qrc compilation happens in CI pre-tests.
- Ensure the macOS build job includes the resources and app icon.
- Verify the artifact launches on macOS.

## Screen inventory & flows (stacked widget)
### Primary screens
- *Login/Welcome:* username + password.
- *Dashboard:* per-module card/table with:
    - module code/name,
    - computed year mark, exam mark, final mark,
    - admission gates (min assignments, min year mark, exam subminimum),
    - visual status (pass/fail/at risk).
- *Modules:*
    - list (search by code/name) + “Add Module”.
    - detail pane with computed metrics and action buttons.
- *Assignments:*
    - list for selected module:
        - title, category, type, due date/time, status,
        - colour chip (Yellow/Orange/Green/Red) from rules,
        - filters: status, category, upcoming (next N days).
    - “Add/Edit Assignment” dialog (basic fields only for now).
- *Marks:*
    - per-assignment mark view:
        - weight (0–100), score (0–100 or empty),
        - write paths for weight/score with validation.
- *Settings:* only what you need:
    - DB ping, show current DB, and “Reload demo data” link to docs.

### Navigation
- QStackedWidget hosts all screens.
- A left sidebar or top toolbar triggers stack index changes.
- From Dashboard cards -> “Assignments” screen filtered by module.
- From an assignment row -> “Edit Mark” dialog.

### State rules
- Loading indicator when a DAL call is in flight.
- Empty state with actionable copy when no rows.
- Errors as non-blocking dialogs; keep UI interactive.

## Visual Guide & Accessibility Notes
### Colour tokens
- status.warning: Yellow (not Done)
- status.pending-score: Orange (Done, score empty)
- status.pass: Green (score ≥ 50)
- status.fail: Red (score < 50)
- Neutral greys for borders/disabled; one accent colour for actions.

### Typography
- Title: 16–18 pt; body: 12–13 pt; table text: 12 pt.
- Ensure a minimum 4.5:1 contrast ratio for text on backgrounds.

### Spacing & density
- 8-pt grid; 12–16 px padding in tables and cards.

### Icons
- SVG line icons for status and actions (edit, add, delete).
- Avoid semantic overload (don’t rely on colour alone—use icons + text).

### Keyboard & a11y
- Set tab order in .ui.
- Provide accessible names/tooltips for interactive widgets.

## Data & DAL contracts
- *User scope:* UI must always pass user_id into DAL reads/writes.
- *Dashboard card needs:*
    - year_mark, exam_mark, final_mark (from DAL),
    - admission_ok + which gate(s) failed,
    - module_id, module_code, module_name.
- *Assignments list needs:*
    - assignment_id, title, category, type, due_date/time,
    - status, score (nullable), colour (UI can compute if DAL doesn’t).
- *Marks view needs:*
    - weight, score (nullable), and min/max validation messages.

### Error handling
- Show DB errors as snackbars/dialogs (message + “details” toggle).
- Keep the view intact; only the failed control should reset/disable.

## Assets & resources
### Logo & app icon
- Source: assets/logo.svg (single colour and full colour variants).
- PNG exports: 512, 256, 128, 64, 32, 16 px.

### Qt resources
- resources/resources.qrc lists all assets by logical alias.
- Generate resources_rc.py from the .qrc (document the one-liner).

## Acceptance criteria (UI phase)
### 1. Navigation
From a single entry point, a user can switch between all major screens via the stacked widget.

### 2. Data surfaces
- Dashboard shows modules with computed marks and admission checks.
- Assignments list renders with status colours and due dates.
- Marks dialog updates weight/score and reflects colour rules.

### 3. UX states
Loading, empty, error states are present and readable.

### 4. Assets
Logo and icons load via Qt resources (no file-path assumptions).

### 5. Build & CI Workflow compiles .ui/.qrc, runs UI tests (or passes with none), and produces built app

### 6. Docs Wireframes, flows, and a short style guide are in docs/ui/; README explains “regenerate UI” and “run the prototype”.