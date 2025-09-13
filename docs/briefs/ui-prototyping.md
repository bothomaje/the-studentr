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