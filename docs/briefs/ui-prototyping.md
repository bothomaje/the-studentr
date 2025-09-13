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
    - compile .ui → generated modules,
    - compile .qrc → resources module,
    - run UI tests (marker: ui),
    - build the app and upload artifacts.

### 5. Docs
- docs/ui/ folder: flows, wireframes, and style tokens.
- README section: how to run, how to regenerate UI/resources, where assets live, and “gotchas”.