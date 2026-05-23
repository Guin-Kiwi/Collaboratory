# Collaboratory

Collaboratory is a web-based team task management application built in Python. It supports three user roles: project owner, collaborator, and assignee: each with role-based permissions for creating, managing, and tracking tasks and notes across projects.

The application follows a 3-tier architecture using NiceGUI for the presentation layer, Python for the application logic, and SQLite with SQLAlchemy for data persistence.

## 📝 Analysis

### Problem

Development teams lack a lightweight, role-aware tool for managing tasks within a project. Without structured access control, any team member can modify or delete any task, making it difficult to maintain clear ownership and accountability across a shared project.

**Specific pain points:**
- **Loss of accountability**: No clear record of who created, assigned, or modified tasks
- **Uncontrolled access**: Team members can accidentally overwrite or delete critical work
- **No clear delegation**: Task assignments lack visibility and status tracking
- **Communication breakdown**: No integrated mechanism for task-related discussions
- **Admin bottleneck**: Owners must manually oversee every change

### Target Users

Collaboratory is designed for:
- **Small development teams** (3–20 people) needing lightweight task management
- **Project-based work** with clear ownership and role distinctions
- **Teams using GitHub Codespaces** or local Python environments
- **Educational and professional settings** requiring role-based access control

### Scenario

A small team uses Collaboratory to manage a development project. The project owner creates the project and invites collaborators. Collaborators create tasks and assign them to team members. Assignees update task status (To Do → In Progress → Completed) and leave task notes to communicate progress. The owner monitors all tasks, manages collaborators, and can delete tasks when needed.

### Why Collaboratory?

Collaboratory solves these problems through:
- **Role-based access control**: Each team member has specific permissions tied to their role (Owner, Collaborator, Assignee, Admin)
- **Simple permission model**: 18 granular actions prevent unauthorized changes while enabling delegation
- **Built-in accountability**: Task creation, assignment, and status changes are all tracked
- **Lightweight and self-hosted**: No external service dependencies; runs in GitHub Codespaces or locally
- **Python-native**: Easy to understand, modify, and extend for educational purposes


## User Stories

### Owner

- As an Owner, I want to create a new project so that I can organise tasks for my team in one place.
- As an Owner, I want to manage collaborators so that I can control who has access to the project management.
- As an Owner, I want to create and assign tasks so that work is clearly distributed.
- As an Owner, I want to edit and delete tasks so that the project stays organised and up to date.
- As an Owner, I want to add and view project notes so that important information is documented and accessible.

### Assignee

- As an Assignee, I want to view projects and tasks so that I understand my responsibilities clearly.
- As an Assignee, I want to update the status of my tasks so that I can show my progress.
- As an Assignee, I want to add and view task notes so that I can share updates and understand task context.

### Collaborator

- As a Collaborator, I want to view projects and tasks so that I can support the Owner.
- As a Collaborator, I want to create and edit tasks so that I can help organise the project work.
- As a Collaborator, I want to assign tasks to users so that work is distributed effectively.
- As a Collaborator, I want to add and view project notes so that important information is shared within the team.

### Main Use Cases

## Project Management
- **View Projects & Tasks**: Users can view projects and tasks they have access to.
- **Create & Manage Projects**: Owners create new projects and manage project details.
- **Edit Project Details**: Owners and Collaborators update project information and status.
- **Delete Projects**: Owners can remove entire projects.
- **Manage Collaborators**: Owners add or remove collaborators to control project access.

**Task Management**
- **Create & Edit Tasks**: Owners and Collaborators create and edit tasks within a project.
- **Assign Tasks**: Owners and Collaborators assign tasks to team members.
- **Change Task Status**: Assignees update task progress (To Do → In Progress → Completed).
- **Delete Tasks**: Owners and Collaborators remove tasks from the project.

**Collaboration & Documentation**
- **Project Notes**: Owners and Collaborators add, view, edit, and manage project-level notes.
- **Task Notes**: Assignees add and edit updates on tasks; Owners and Assignees can delete task notes.

**Admin & Recovery**
- ~~**Manage Admin Status**~~: *Admins can only self-revoke their own admin status; they cannot revoke other admins' status to prevent malicious lockout of the recovery admin.*

> **Note:** Admin status is strictly a recovery/override mechanism, not a normal operational role. Admins can only revoke their own admin status, not other admins' status. This prevents malicious actors from locking the recovery admin out of the system.

### Actors

- **Owner**: Creates and manages projects, tasks, collaborators, and project notes.
- **Collaborator**: Supports the Owner by managing tasks and project notes.
- **Assignee**: Works on assigned tasks and updates their status.

## 📖 Detailed Use Cases (Inputs / Outputs)

### Use Cases

#### Project level

**1. Login / Sign up**
As a user, I want to log in or create an account to access the application.

- **Actors:** Owner, Collaborator, Assignee
- **Inputs:** username (`str`), password (`str`)
- **Outputs:** authenticated session, redirect to dashboard

---

**2. Create project**
As a user, I want to create a new project that I will own.

- **Actors:** Owner, Collaborator, Assignee
- **Inputs:** project name (`str`), description (`str`)
- **Outputs:** created `Project` object, user set as owner

---

**3. Delete own projects**
As an owner, I want to delete a project I own.

- **Actors:** Owner
- **Inputs:** project id (`int`)
- **Outputs:** project and all associated tasks, notes, and memberships deleted

---

**4. Edit project details**
As an owner or collaborator, I want to update a project's name or description.

- **Actors:** Owner, Collaborator
- **Inputs:** project id (`int`), name (`str`), description (`str`)
- **Outputs:** updated `Project` object

---

**5. Add / remove collaborators**
As an owner, I want to add or remove collaborators from my project.

- **Actors:** Owner
- **Inputs:** project id (`int`), user id (`int`), action (`add | remove`)
- **Outputs:** updated `ProjectMember` list

---

**6. View project and tasks**
As any project member, I want to see a project and all its tasks.

- **Actors:** Owner, Collaborator, Assignee
- **Inputs:** project id (`int`)
- **Outputs:** `Project` object, list of `Task` objects

---

**7. Delete any project note**
As an owner, I want to remove any project note regardless of who wrote it.

- **Actors:** Owner
- **Inputs:** project id (`int`), note id (`int`)
- **Outputs:** note deleted, updated notes list

---

**8. Add, edit and delete own project notes**
As an owner or collaborator, I want to write, update, and remove my own project notes.

- **Actors:** Owner, Collaborator
- **Inputs:** project id (`int`), content (`str`), note id (`int`) for edit/delete
- **Outputs:** created/updated/deleted `ProjectNote`

---

**9. View project notes**
As any project member, I want to read all notes on a project.

- **Actors:** Owner, Collaborator, Assignee
- **Inputs:** project id (`int`)
- **Outputs:** list of `ProjectNote` objects

---

**10. Create task**
As an owner or collaborator, I want to add a new task to a project.

- **Actors:** Owner, Collaborator
- **Inputs:** project id (`int`), title (`str`), description (`str`), priority (`low | medium | high`), due date (`datetime`)
- **Outputs:** created `Task` object

---

#### Task level

**11. Delete task**
As an owner or collaborator, I want to remove a task from a project.

- **Actors:** Owner, Collaborator
- **Inputs:** task id (`int`)
- **Outputs:** task and associated assignments and notes deleted

---

**12. Edit task details**
As an owner or collaborator, I want to update a task's title, description, priority, or due date.

- **Actors:** Owner, Collaborator
- **Inputs:** task id (`int`), title (`str`), description (`str`), priority (`low | medium | high`), due date (`datetime`)
- **Outputs:** updated `Task` object

---

**13. Add / remove assignees**
As an owner or collaborator, I want to assign or unassign users to a task.

- **Actors:** Owner, Collaborator
- **Inputs:** task id (`int`), user id (`int`), action (`add | remove`)
- **Outputs:** updated `Assignment` list for the task

---

**14. Delete any task note**
As an owner, I want to remove any task note regardless of who wrote it.

- **Actors:** Owner
- **Inputs:** task id (`int`), note id (`int`)
- **Outputs:** note deleted, updated notes list

---

**15. View task details and notes**
As any project member, I want to see a task's full details and all its notes.

- **Actors:** Owner, Collaborator, Assignee
- **Inputs:** task id (`int`)
- **Outputs:** `Task` object, list of `TaskNote` objects

---

**16. Add, edit and delete own task notes**
As an assignee, I want to write, update, and remove my own notes on a task I am assigned to.

- **Actors:** Assignee
- **Inputs:** task id (`int`), content (`str`), note id (`int`) for edit/delete
- **Outputs:** created/updated/deleted `TaskNote`

---

**17. Change task status**
As an assignee, I want to update the status of a task I am assigned to.

- **Actors:** Assignee
- **Inputs:** task id (`int`), status (`todo | in_progress | completed`)
- **Outputs:** updated `Task` status
---

## Use Case Diagrams – Collaboratory

![Use Case Diagram - Project Level](project_level.png)
![Use Case Diagram - Task Level](task_level.png)

---

## 🧩 Wireframes / Mockups

> 🚧 Add screenshots of the core UI screens (Dashboard, Project view, Task view).

![Wireframes – Dashboard/Project/Task](docs/ui-images/wireframes.png)


## Roles & Permissions

A user's role is specific to each project: it depends on their relationship to that project, not a global setting.

Users can be:
- Owners
- Collaborators
- Assignees
- Admins

A user can simultaneously be a Collaboratory Admin, Owner or Collaborator of a project, and Assignee of tasks within that project.

| Role | How you get it |
|---|---|
| **Owner** | You created the project |
| **Assignee** | You have been assigned to at least one task in the project |
| **Collaborator** | The Owner added you to the project |

> Users with `is_admin = true` have full access across all projects.
> This is a simple override for recovery/admin purposes, not a normal role.

| Action | Owner | Collaborator | Assignee |
|---|---|---|---|
| View project & tasks | ✅ | ✅ | ✅ |
| Edit project details | ✅ | ✅ |- |
| Change project status | ✅ | ✅ |- |
| Delete project | ✅ |- |- |
| Add/remove collaborators | ✅ |- |- |
| View project notes | ✅ | ✅ | ✅ |
| Add project note | ✅ | ✅ |- |
| Edit/Delete own project note | ✅ | ✅ |N/A |
| Delete any project note | ✅ |- |- |
| Create task | ✅ | ✅ |- |
| Edit task details | ✅ | ✅ |- |
| Change task status |- |- | ✅ |
| Delete task | ✅ | ✅ |- |
| Add/remove Assignees | ✅ | ✅ |- |
| View task notes | ✅ | ✅ | ✅ |
| Add task note |- |- | ✅ |
| Edit/Delete own task note |N/A |N/A | ✅ |
| Delete any task note | ✅ |- | ✅ |


---

## ✅ Project Requirements

Collaboratory meets the following criteria required by the course:

### 1. Browser-based App (NiceGUI)

The application interacts with users through a web browser using NiceGUI.

Users can perform the following actions:

- Register and log into the application securely
- Create and manage projects
- Create, assign, edit, and delete tasks
- Update task statuses (To Do → In Progress → Completed)
- Add and view project and task notes
- Manage collaborators within projects
- Navigate through dashboards and task views

The graphical user interface is implemented entirely with NiceGUI components running on the server side. The browser acts as a thin client while the application logic and UI state are managed by the Python backend.

**Architecture note:** The browser is a thin client; UI state and business logic live on the server-side NiceGUI application.

### 2. Data Validation

The application validates all user input to ensure data integrity and a smooth user experience.

**Validated input includes:**
- Usernames and email addresses (format, uniqueness)
- Login credentials (bcrypt verification)
- Project names and descriptions (non-empty)
- Task titles and task status values (valid status enums)
- Collaborator assignments (role validation)
- Required form fields (no empty submissions)
- Due dates (valid date format)
- Priority levels (valid priority enums)

**Validation behavior:** Invalid or incomplete input is rejected with clear feedback messages in the user interface. Validation is performed before data is processed or stored in the database to prevent crashes and guide users to provide correct input.

### 3. Database Management

The application uses SQLite as its persistent database and SQLAlchemy as an Object-Relational Mapper (ORM).

**ORM usage includes:**
- Define database tables as Python classes (User, Project, Task, Assignment, ProjectMember, ProjectNote, TaskNote)
- Manage relationships between entities (foreign keys, cascade rules, back-references)
- Create, read, update, and delete persistent data
- Avoid writing raw SQL statements directly (all queries use ORM methods)

**Architecture:** Database access is separated from the user interface. Manager classes (`UserManager`, `ProjectManager`, `TaskManager`, `CollabManager`) interact with the database through SQLAlchemy sessions to keep the architecture clean and maintainable.

## Database Information

### Core Entities

- **User**: people who log in, create projects, or get assigned to manage projects and/or tasks
- **Project**: top-level project containers
- **Task**: work items inside projects
- **Assignment**: links tasks to users
- **ProjectMember**: links projects to collaborators

### Schema

#### User

```text
id          (PK)
username    (unique)
name
email       (unique)
password    (hashed)
is_admin    (bool)
created_at
```

**Notes:** Users include audit timestamps (`created_at`, `updated_at`) via `TimestampMixin`.

#### Project

```text
id          (PK)
name
description
owner_id    (FK → Users.id)
created_at
```

**Notes:** Projects include audit timestamps (`created_at`, `updated_at`) via `TimestampMixin`.

#### Task

```text
id          (PK)
title
description
status      (e.g. "todo", "in_progress", "completed")
priority    (e.g. "low", "medium", "high")
due_date
project_id  (FK → Projects.id)
created_by  (FK → Users.id)
created_at
```

**Notes:** Tasks include audit timestamps (`created_at`, `updated_at`) via `TimestampMixin`.

#### Assignment

```text
id          (PK)
task_id     (FK → Tasks.id)
user_id     (FK → Users.id)
assigned_at
```

**Notes:** `Assignment.assigned_at` is timestamped at insertion (server_default=now). Assignments do not use the `TimestampMixin`.

#### ProjectMember

```text
id          (PK)
project_id  (FK → Projects.id)
user_id     (FK → Users.id)
```

**Notes:** `ProjectMember` is a join table with a unique constraint on `(project_id, user_id)`; no audit timestamps.

#### ProjectNote

```text
id          (PK)
content
project_id  (FK → Projects.id)
created_by  (FK → Users.id)
created_at
```

**Notes:** Project notes include audit timestamps (`created_at`, `updated_at`) via `TimestampMixin`. The `created_by` field references the `users.id` who authored the note.

#### TaskNote

```text
id          (PK)
content
task_id     (FK → Tasks.id)
created_by  (FK → Users.id)
created_at
```

**Notes:** Task notes include audit timestamps (`created_at`, `updated_at`) via `TimestampMixin`. The `created_by` field references the `users.id` who authored the note.

### Relationships

- One `User` → many `Project` (owner)
- One `Project` → many `Task`
- One `Task` → many `Assignment` (assignees)
- One `User` → many `Assignment`
- One `Project` → many `ProjectMember` (collaborators)
- One `Project` → many `ProjectNote`
- One `Task` → many `TaskNote`

The ORM uses SQLAlchemy relationships with cascade rules (e.g. projects → tasks cascade on delete) and `UniqueConstraint`s for join tables (`assignments`, `project_members`).

#### Entity Relationship Diagram

<img width="1213" height="1209" alt="ERCollab_Notes (2)" src="https://github.com/user-attachments/assets/199f9147-afc6-4767-9e04-17df8013b0eb" />

## Architecture

This application follows a 3-tier layered architecture.

### 1. Presentation Tier (Frontend)

- **Technology:** NiceGUI
- UI rendered with Vue.js and Quasar through NiceGUI
- Renders the user interface directly from Python
- UI components are served through NiceGUI
- Runs in the browser
- No business logic stored in the browser
- Browser acts as a thin client

### 2. Application Tier (Backend)

- **Technology:** Python + NiceGUI
- Business logic implemented in Python
- NiceGUI components instantiated on the server
- Object-oriented structure for modular logic
- Handles business logic and user interactions
- Manages authentication and sessions
- Connects UI and database

### 3. Data Tier (Database)

- **Technology:** SQLAlchemy + SQLite
- SQLite used as persistent storage
- SQLAlchemy used as ORM
- No raw SQL required
- Stores persistent application data
- Uses ORM models instead of raw SQL
- Database accessed through SQLAlchemy sessions

## Design Patterns

### Service Layer (Manager Pattern)

**Files:**
- `logic/user_manager.py`
- `project_manager.py`
- `task_manager.py`
- `collab_manager.py`

Four manager classes handle the business logic for different domains. The UI communicates with the managers, and managers interact with the database through SQLAlchemy sessions.

**Status:** Implemented

---

### Mixin Pattern

**File:**
- `database/mixins.py`

Adds shared timestamp fields (`created_at`, `updated_at`) to multiple ORM models through inheritance.

**Status:** Implemented

---

### Façade Pattern

**Files:**
- `database/connection.py`
- `logic/permissions_manager.py`

Simplifies database session handling and permission checking behind shared interfaces. All four managers use the shared `db_conn` instance from `database/__init__.py`. Note: `main.py` also constructs its own `DatabaseConnection()` at startup: see Known Limitations.

**Status:** Implemented

---

### Singleton (by convention)

**File:**
- `database/__init__.py`

Uses a shared `db_conn` database connection instance across the application. Python does not enforce that additional instances cannot be created; `main.py` creates an additional instance at startup.

**Status:** Partial
  
## ⚙️ Implementation

### Technology

- **Python 3.10+** (tested with Python 3.13)
- GitHub Codespaces (or local development environment)
- NiceGUI: web application framework
- SQLAlchemy: Object-Relational Mapper (ORM)
- bcrypt: password hashing
- SQLite: embedded database

### 📂 Repository Structure

```text
Collaboratory/
├── database/
│   ├── __init__.py             # shared db_conn singleton
│   ├── connection.py           # DatabaseConnection façade
│   ├── models.py               # core ORM models (User, Project, Task, Assignment)
│   ├── collab_models.py        # collaboration ORM models (ProjectMember, notes)
│   └── mixins.py               # shared timestamp mixin
├── logic/
│   ├── __init__.py
│   ├── app_state.py            # global AppState for session management
│   ├── user_manager.py         # user CRUD and authentication
│   ├── project_manager.py      # project CRUD and queries
│   ├── task_manager.py         # task CRUD, assignment, and status
│   ├── collab_manager.py       # collaborator and note management
│   ├── permissions_manager.py  # 18-action permission system
│   └── db_session.py           # session abstraction layer
├── ui/
│   ├── __init__.py
│   ├── layout.py               # reusable page frames and navigation
│   └── pages/
│       ├── __init__.py
│       ├── login_page.py       # authentication (login/signup/password reset)
│       ├── dashboard_page.py   # user dashboard with projects and tasks
│       ├── project_page.py     # project detail view with collaborators and notes
│       └── task_page.py        # task detail view with assignees and notes
├── tests/                      # 42 pytest tests (database, workflows, permissions)
├── .gitignore
├── LICENSE
├── README.md                   # this file
├── main.py                     # application entry point
└── requirements.txt            # Python dependencies
```

### How to Run

**Requirements:**
- Python 3.10 or higher
- pip or other Python package manager

**Setup:**

1. Clone or open the repository:
   ```bash
   git clone https://github.com/Guin-Kiwi/Collaboratory.git
   cd Collaboratory
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   # OR
   venv\Scripts\activate          # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:
   ```bash
   python main.py
   ```

5. Open your browser and navigate to the URL displayed in the terminal (typically `http://localhost:8080`)

**Troubleshooting:**
- If port 8080 is in use, NiceGUI will automatically try the next available port
- Check the terminal output for the actual URL
- For GitHub Codespaces, the browser may open automatically

### Libraries Used

- `nicegui`: browser-based UI framework (Vue.js + Quasar via Python)
- `sqlalchemy`: Object-Relational Mapper for database models and queries
- `bcrypt`: secure password hashing and verification
- `pytest`: unit and integration testing framework

All dependencies are listed in `requirements.txt` and installed via:

```bash
pip install -r requirements.txt
```

## Features

**Core Functionality:**
- ✅ User authentication and account management (login, signup, password reset, account deletion)
- ✅ Project creation and lifecycle management
- ✅ Task creation, editing, assignment, and deletion
- ✅ Task status workflow (To Do → In Progress → Completed)
- ✅ Collaborator management with granular role-based access
- ✅ Project-level and task-level note documentation
- ✅ Admin recovery mechanism for system access

**Technical Features:**
- ✅ 18-action permission system with Owner, Collaborator, Assignee, and Admin roles
- ✅ Input validation for usernames, emails, passwords, project names, task titles, and status values
- ✅ Error handling with user-friendly feedback messages
- ✅ Browser-based UI with real-time updates (no page reloads for most actions)
- ✅ SQLite database with cascade rules and referential integrity
- ✅ 42 unit, integration, and boundary tests
- ✅ Session management and security with bcrypt password hashing

**Architecture:**
- ✅ 3-tier layered architecture (UI, Logic, Database)
- ✅ Design patterns: Manager Pattern, Façade, Singleton (by convention), Mixin
- ✅ Clean separation of concerns: business logic independent of UI
- ✅ ORM-based data access with no raw SQL

## � Usage Walkthrough

### Scenario: Create a Project and Assign Tasks

**Step 1: Log In**
1. Open Collaboratory in your browser
2. Click **Sign Up** to create an account, or log in with existing credentials
3. You're now on the **Dashboard**, which shows your projects, collaborations, and task summary

**Step 2: Create a New Project**
1. On the Dashboard, click **Create New Project**
2. Enter a project name (e.g., "Website Redesign")
3. Optionally add a description
4. Click **Create**: you're now the **Owner** of this project

**Step 3: Add Collaborators**
1. Navigate to your project
2. In the **Collaborators** section, select a user from the dropdown
3. Click **Add Collaborator**: they can now view, create, and assign tasks in your project

**Step 4: Create Tasks**
1. In the project view, click **Create New Task**
2. Enter task title, description, priority, and due date
3. Click **Create Task**: the task appears in the project's task list

**Step 5: Assign Tasks**
1. Click on a task to open its detail view
2. In the **Assignees** section, select a user and click **Assign**
3. The user becomes an **Assignee** for that task

**Step 6: Update Task Status**
1. As an Assignee, open your assigned task
2. In **Task Status**, select the new status (To Do → In Progress → Completed)
3. Click **Update**: the status is saved immediately

**Step 7: Add Notes**
1. **Project Notes** (Owner/Collaborator only): Add team documentation in the project view
2. **Task Notes** (Assignee only): Add progress updates or blockers in the task detail view
3. All notes are visible to project members with appropriate access

### Key Workflows by Role

**As a Project Owner:**
- Create projects and manage all aspects
- Add/remove collaborators
- Create and assign tasks to team members
- Edit and delete tasks
- Add and delete project notes
- Monitor all project activity

**As a Collaborator:**
- View all project details
- Create and edit tasks
- Assign tasks to team members
- Add project notes
- View task progress

**As an Assignee:**
- View tasks assigned to you
- Update task status (track progress)
- Add task notes (communication with owner/collaborators)
- View project details for context

## 👥 Team & Contributions

Collaboratory was built by a team of four over approximately eight weeks, with a concentrated final sprint in the last week of May. Contributions are documented below by primary file ownership and README section, derived from commit history. Several files were worked on collaboratively and are noted under each contributor.

| Contributor | Primary responsibility |
|---|---|
| Ayla Allen | Permissions system, collaboration logic, project management, UI framework |
| Polina Yemelianenkova | User authentication, database models and infrastructure, login UI, database testing |
| Sümeyya Güçlü-Babür | Task management, task UI, documentation |
| Marta Greschuk | Application state, session abstraction, dashboard UI, test suite |

---

### Ayla Allen

**Role:** Repository setup, core architecture, collaboration layer, permissions system, project management, and integration.

**Primary file ownership**
- `database/collab_models.py`: `ProjectMember`, `ProjectNote`, and `TaskNote` ORM models including back-references and `UniqueConstraint` on project membership
- `logic/permissions_manager.py`: full 18-action permission system: `PermissionAction` enum, `check_permission`, `require_permission`, and all role checker functions (`is_owner`, `is_collaborator`, `is_assignee_on_task`, `is_assignee_in_project`) covering Owner, Collaborator, Assignee, and Admin roles
- `logic/collab_manager.py`: all collaboration business logic: adding/removing collaborators, project note CRUD, task note CRUD, permission-guarded access throughout, and author-bypass logic for note deletion
- `logic/project_manager.py`: project CRUD operations and membership queries
- `ui/pages/project_page.py`: collaborator display, task listing, project and task note creation and display, all permission-gated action buttons; worked on collaboratively with Polina and Sümeyya
- `tests/test_collab_manager_permissions.py`: permission boundary tests for collaborator actions

**Shared file contributions**
- `ui/layout.py`: authored the initial frame structure (`UnauthenticatedFrame`, `DashboardFrame`, `ProjectFrame`, `TaskFrame`) and the routing skeleton all pages inherit from; extended collaboratively with Polina and Marta during the sprint

**README contributions**
- Analysis: Problem statement, Scenario, and Why Collaboratory bullet points
- All 17 detailed use cases (inputs/outputs) at project and task level
- Use Case Diagrams section, including authoring both diagram images
- Data Validation section
- Implementation section: Technology, Repository Structure, How to Run, Libraries Used
- This contributions section

**Sprint activity**
- `ui/layout.py`: introduced `UnauthenticatedFrame`; kept `login_frame()` backwards-compatible; refactored page imports across the UI layer
- `ui/pages/project_page.py`: added task and note CRUD; wired permission-gated buttons across UI and logic layers; fixed note view wiring
- `logic/permissions_manager.py`: implemented permission checks for adding collaborators and deleting project notes without breaking layer separation
- `tests/`: moved SQLite backend seeding to test folder for isolation; added collaborator permission boundary tests
- Cross-branch: resolved merge conflicts maintaining `ui-layer` as source of truth (PRs #15, #17, #19)

---

### Polina Yemelianenkova

**Role:** User authentication, `UserManager`, ORM query layer, database infrastructure, login UI, and README schema documentation.

**Primary file ownership**
- `database/models.py`: `BaseModel` declarative base and all core ORM models (`User`, `Project`, `Task`, `Assignment`) including relationships, foreign keys, cascade rules, and Enum definitions for task status and priority
- `database/mixins.py`: shared model mixins
- `database/seed.py`: full database seeding logic
- `logic/user_manager.py`: `create_user` (bcrypt password hashing), `delete_user`, `update_user`, `validate_login`, `get_user_by_id`, `get_all_users`, `user_exists`
- `ui/pages/login_page.py`: full login and signup interface using `UnauthenticatedFrame`: bcrypt credential verification, signup with name/username/email/password, error handling, redirect for already-authenticated users, password reset flow, account deletion with password confirmation
- `tests/test_db.py`: integration test suite covering the full database layer

**Shared file contributions**
- `ui/layout.py`: added session handling, frame refinements, and import cleanup during the sprint
- `ui/pages/dashboard_page.py`: extended project listing, collaboration windows, and session wiring; worked on collaboratively with Marta
- `ui/pages/project_page.py`: contributed task, collaborator, and note management methods alongside Ayla

**README contributions**
- All database schema entity sections: User, Project, Task, Assignment, ProjectMember, ProjectNote, TaskNote
- Database Information: Core Entities, Relationships
- Architecture section: all three tiers, Design Patterns
- ERD section and diagram
- Features section

**Sprint activity**
- `ui/pages/login_page.py`: added login page; implemented login/signup handlers with `UnauthenticatedFrame`; added error handling; fixed authenticated user redirect; added password reset and account deletion with password confirmation; removed admin registration option
- `logic/user_manager.py`: added `create_user`, `delete_user`, `update_user`; added name and email parameters; added `user_exists`
- `logic/project_manager.py` / `logic/collab_manager.py`: refactored to `joinedload` for memberships, tasks, and notes; removed unused `collaborator_memberships` from project creation; added `is_admin` filter; refactored database connection usage across logic modules
- `DashboardFrame` / `ProjectFrame`: added session control; refactored session initialisation; introduced `db_session` module
- `ui/layout.py`: removed unused `public_frame` and `task_frame` functions; cleaned up `BaseView` and unused imports

---

### Sümeyya Güçlü-Babür

**Role:** Task page, `TaskManager`, assignee management, permission debugging, and primary README author.

**Primary file ownership**
- `logic/task_manager.py`: `create_task`, `get_task_by_id`, `get_tasks_by_user`, `update_task`, `delete_task`, `assign_task`, `remove_assignee`, `get_assignees`, `change_task_status`, and `get_task_project` helper: all with `require_permission` guards
- `ui/pages/task_page.py`: `TaskFrame` layout, task metadata display, status controls, assignee management UI, task notes, and all permission-gated buttons; worked on collaboratively with Ayla and Marta

**README contributions (primary author)**
- User Stories (Owner, Assignee, Collaborator)
- Initial use cases and use case diagram
- Roles and Permissions table structure and role descriptions
- Target Users, Why Collaboratory, Scenario framing
- Project Requirements: Browser-based App section
- Usage Walkthrough
- Testing section
- Known Limitations and Deferred Decisions

**Sprint activity**
- `ui/pages/task_page.py`: added initial task page; updated layout; added `TaskFrame` support and missing methods; refactored to use shared `TaskFrame` from `ui/layout.py`; fixed routing (`task_id` parameter, `project` argument passing)
- `logic/task_manager.py`: added `get_task_project` helper; fixed `get_tasks_by_user` permission check; fixed `CREATE_TASK` permission check; implemented `assign_task`, `remove_assignee`, `get_assignees`; resolved multiple `DetachedInstanceError` crashes on `task.project` access
- `logic/task_manager.py`: fixed detached task and project access in task permissions; fixed detached project lazy loading
- `ui/pages/task_page.py`: fixed task page session errors through multiple debugging iterations

---

### Marta Greschuk

**Role:** Application state, session abstraction, dashboard UI, and test suite.

**Primary file ownership**
- `logic/app_state.py`: `AppState` class managing the logged-in user across NiceGUI's page lifecycle (`login`, `logout`, `is_authenticated`, `get_current_user`, `is_admin`); shared global `app_state` instance used across all pages
- `tests/conftest.py`: shared test fixtures and SQLite backend setup
- `tests/test_models.py`: ORM model unit tests
- `tests/test_task_manager_workflow.py`: end-to-end task manager workflow tests against a real SQLite backend
- `tests/unit_testing.py`: unit test utilities

**Shared file contributions**
- `ui/layout.py`: contributed the initial dashboard layout structure and UI refinements during the sprint
- `ui/pages/dashboard_page.py`: built the initial dashboard view including project and collaboration sub-windows and per-project task display; extended collaboratively with Polina during the sprint
- `ui/pages/task_page.py`: contributed session and layout fixes alongside Sümeyya

**Sprint activity**
- `logic/app_state.py`: set up logic layer structure via `application_state` branch (PR #17); authored `AppState` with full session lifecycle
- `logic/permissions_manager.py`: added UI-level permission checks; fixed lazy-loaded relationship bug causing unnecessary DB queries on every permission check
- `logic/`: implemented `AdminManager`; fixed `is_admin()` crash (method called and result compared to string)
- `db_session.py`: created thin wrapper around `db_conn.get_session()`; added session management to dashboard; added optional session parameter across managers
- `ui/pages/dashboard_page.py`: built initial dashboard; added project and collaboration sub-windows; added per-project task display with titles; fixed duplicated task display; added db session; added task creation and edit button; aligned project and task page layouts
- `tests/`: wrote task manager workflow tests; resolved merge conflicts in test files

---

> **Note:** During the final sprint (18-24 May), all team members worked collaboratively across the codebase. The commit history reflects active parallel contributions to shared files, session management, and integration fixes across all layers. Attributions above reflect primary authorship based on commit history.

---

### 🤖 AI Assistance

GitHub Copilot was used for initial project scaffolding (PR #1), README spelling and consistency fixes (PRs #5, #6), multi-file rename refactors, PR review checks, and as a learning aid throughout development. `database/connection.py` and `database/mixins.py` originated from the Copilot scaffold and were subsequently refined by the team.


## 🤝 Contributing

This is a closed academic project submitted for assessment. External contributions are not accepted.

## 🧪 Testing

**Explain what you test and how to run tests.**

**Test mix:**
- **Overall 42 tests**
- **35 Database tests**: e.g., user creation persists to DB, username/email uniqueness constraints prevent duplicates, project-task relationships cascade on deletion, ProjectNote and TaskNote CRUD operations
- **5 Task Manager Workflow tests**: e.g., owner can create task, owner can assign user to task, assignee can change task status, non-owners cannot perform restricted actions
- **1 Collaborator Manager Permission test**: e.g., adding/removing collaborators, permission boundaries for different roles
- **1 Constraint test**: e.g., unique constraint prevents duplicate assignments

### How to Run Tests

Run all tests:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_db.py -v
pytest tests/test_task_manager_workflow.py -v
pytest tests/test_collab_manager_permissions.py -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=logic --cov=database --cov-report=term-missing
```

### Template for Writing Test Cases

When adding new tests, follow this structure:

1. **Test case ID**: unique identifier (e.g., TC_001)
2. **Test case title/description**: What is the test about?
3. **Preconditions**: Requirements before executing the test (e.g., "User must exist", "Project must be created")
4. **Test steps**: Actions to perform (e.g., "Create task", "Assign user", "Update status")
5. **Test data/input**: Example values (e.g., task title "Implement API", assignee ID 5)
6. **Expected result**: What should happen (e.g., "Task status changes to 'in_progress'")
7. **Actual result**: What actually happened
8. **Status**: Pass or fail
9. **Comments**: Additional notes or defects found

### Example Test Cases

**TC_001: Database: User creation persists to DB**
- **Preconditions:** In-memory SQLite database initialized
- **Test steps:** Create User object, add to session, commit
- **Test data:** username="testuser", email="test@example.com"
- **Expected result:** User retrieved from DB has correct username and email
- **Status:** ✅ Pass

**TC_002: Task Manager: Owner can create task in owned project**
- **Preconditions:** Owner user exists, project created by owner
- **Test steps:** Call `tm.create_task(owner, project, title="Implement API", ...)`
- **Test data:** title="Implement API", priority="high", status="todo"
- **Expected result:** Task created with correct fields, task.id is not None
- **Status:** ✅ Pass

**TC_003: Task Manager: Non-owner cannot create task in project**
- **Preconditions:** Normal user exists, project owned by different user
- **Test steps:** Call `tm.create_task(normal_user, project, ...)`
- **Test data:** title="Test Task"
- **Expected result:** `PermissionDenied` exception raised
- **Status:** ✅ Pass

**TC_004: Collaborator Manager: Adding collaborators to project**
- **Preconditions:** Owner user exists, collaborator user exists, project created by owner
- **Test steps:** Call `cm.add_collaborator(owner, project, collaborator)`
- **Test data:** collaborator is normal (non-admin) user
- **Expected result:** ProjectMember entry created, collaborator can now view project
- **Status:** ✅ Pass

**TC_005: Collaborator Manager: Permission boundary enforcement**
- **Preconditions:** Project exists, user is not owner or collaborator
- **Test steps:** Attempt to add collaborator as non-owner
- **Test data:** user_id=5 (non-owner), project_id=1
- **Expected result:** Permission denied or operation fails
- **Status:** ✅ Pass

## Known Limitations & Deferred Decisions

### Known Limitations

- SQLite is suitable for small-scale projects but not large production systems
- Some UI workflows could still be improved
- Singleton behaviour is implemented by convention only
- UI-level permission checks were introduced for button visibility where a single permission enum value could not cleanly express both display and logic concerns. This is a known deviation from the permissions layer design that would be resolved in a future refactor
- **Single concurrent user (`app_state`):** `logic/app_state.py` stores the currently logged-in user as a module-level Python singleton (`app_state = AppState()`). Because Python module state is shared across all browser connections on the same server process, logging in as a second user overwrites the first user's session — the first user's subsequent page loads will run under the second user's identity. The fix is to replace the in-memory `current_user` object with NiceGUI's per-connection `app.storage.user` (stores a user ID keyed to the browser session) and load the full `User` from the database in each page route. This requires setting a `storage_secret` in `ui.run()` and updating `app_state.py` and the three page route functions (`dashboard`, `project`, `task`). The application is safe for single-user use or sequential (non-overlapping) logins.

### Deferred Decisions

- Real-time collaboration features were not implemented
- Advanced notification systems were scoped out
- Additional user roles were not added to keep permissions manageable

## 📝 License

This project is provided for educational use only as part of the Programming Foundations module.

[MIT License](LICENSE)