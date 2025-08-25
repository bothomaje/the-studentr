# Data Model and Setup
## Scope
Explains the purpose and responsibilities of each deliverable required for the Data Modeling stage under the local-user-only scope. Focuses on definitions, acceptance criteria, and verification steps.

## Reference Diagrams

## Deliverables
### db/schema.sql - Formal Database Contract
- Defines tables, columns, constraints, and relationships for local mode (users, modules, assignments, assessments).
- Expresses data ownership via `user_id` on every academic row to keep the model future-proof.
- Captures integrity rules: primary keys, foreign keys, uniqueness (module code per user), non-null constraints, and enumerated statuses.
- Specifies indexing for common queries (by user, status, due date, category).
- Documents soft-deletion expectations (deleted_at) for resilient UI behaviour.
- Serves as the single source of truth for seed, DAL, and UI layers.

#### Acceptance Criteria
- [ ] ERD and schema match exactly; no orphan records possible.
- [ ] Constraints prevent invalid states (invalid status, missing FKs, negative weights).
- [ ] Creation is idempotent and safe to re-apply on an empty DB.
- [ ] Numeric types support calculations and sorting correctly (e.g., DECIMAL for percentages).

### db/seed.sql - Baseline Data for Local Use
- Introduces a single local user profile (email NULL) to own all data.
- Optionally adds a small demo dataset for UI verification (a few modules, assignments, assessments).
- Uses stable identifiers (UUIDs) to enable future cloud promotion.
- Designed to be safe to run once; documented to avoid duplicate application.

#### Acceptance Criteria
- [ ] After seeding, the app can load main screens without manual input.
- [ ] Seeded data respects schema constraints and valid foreign keys.
- [ ] Dataset is small, purposeful, and well-documented.

### scripts/setup_db.py - One-Button Environment Setup
- Automates applying schema then seed in the correct order; optional database creation if needed.
- Reads configuration from environment variables first; falls back to a local, git-ignored config file.
- Emits clear logs (connection target, operation outcomes, per-table counts).
- Handles errors gracefully and exits non-zero on failure.

#### Acceptance Criteria
- [ ] Running on a clean machine produces a ready-to-use database matching the schema and seed.
- [ ] Repeat runs do not corrupt data; behaviour is predictable and documented.
- [ ] Output enables verification without reading the source code.

### app/dal/db.py - Connection and Query Infrastructure
- Centralizes connection handling so UI modules don’t duplicate boilerplate.
- Enforces parameterized queries and consistent transaction behaviour (commit/rollback).
- Provides helpers that repositories can layer on (fetch-one/many, execute).
- Abstracts credentials/config retrieval (from env or file).

#### Acceptance Criteria
- [ ] Single import path yields a functioning connection in all UI modules.
- [ ] Works with both environment variables and local config without code changes.
- [ ] Error handling is consistent and informative (no silent failures).

### app/dal/repositories/* - Feature-Focused Data Access
- Organizes SQL by domain area (modules, assignments, assessments).
- Each repository exposes predictable operations: list, create, update, delete, and specials (e.g., due soon).
- All operations require current_user_id and scope queries accordingly.
- Returns lightweight, UI-friendly structures without presentation concerns.

#### Acceptance Criteria
- [ ] UI screens accomplish use cases by calling repositories without embedding SQL.
- [ ] Repositories consistently enforce user scoping; no cross-user data leakage.
- [ ] Operations are atomic and clearly report success/failure.

### Config Loader - Environment-First Configuration
- Resolves settings from environment variables first (`host`, `user`, `password`, `database`, `current_user_id`).
- Falls back to a local, git-ignored config file for developer convenience.
- Validates required settings and reports what’s missing.
- Documents expected variable names and acceptable value ranges.

#### Acceptance Criteria
- [ ] Connecting via DAL succeeds with either environment variables or local config.
- [ ] No secrets are committed; a sample template is provided for guidance.
- [ ] Errors direct users to the precise variable or file to fix.

### DAL Connectivity Test - Verifying the Plumbing
- A simple, non-GUI check that confirms connectivity and basic query execution.
- Verifies table existence, sensible counts, and a sample query shape (e.g., due soon).
- Suited for local smoke tests and CI without GUI involvement.

##### Acceptance Criteria
- [ ] Passes on a fresh environment once variables are set.
- [ ] Failures clearly indicate whether the issue is connectivity, configuration, or schema mismatch.
- [ ] Does not require interactive secrets entry; no secrets leaked.

## Activities
- Finalize ERD and schema decisions (tables, keys, constraints, indexes).
- Write db/schema.sql from the ERD; validate in a blank database.
- Author db/seed.sql with one local user and minimal demo data.
- Implement scripts/setup_db.py to apply schema then seed; print a summary.
- Implement app/dal/db.py and repositories with parameterized operations and user scoping.
- Configure environment variables or local config; verify with the DAL connectivity test.
- Capture open items for the cloud phase (devices, sync)
