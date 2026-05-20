# Collaboratory

Collaboratory is a web-based team task management application built in Python. It supports role-based project collaboration for creating, managing, and tracking tasks and notes across projects.

The application follows a 3-tier architecture using NiceGUI for the presentation layer, Python for the application logic, and SQLite with SQLAlchemy for data persistence.

## 📝 Analysis

### Problem

Development teams lack a lightweight, role-aware tool for managing tasks within a project. Without structured access control, any team member can modify or delete any task, making it difficult to maintain clear ownership and accountability across a shared project.

### Scenario

A small team uses Collaboratory to manage a development project. The project owner creates the project and invites collaborators. Collaborators create tasks and assign them to team members. Assignees update task status (To Do → In Progress → Completed) and leave task notes to communicate progress. The owner monitors all tasks, manages collaborators, and can delete tasks when needed.


## User Stories

### Owner

- As an Owner, I want to create a new project so that I can organise tasks for my team in one place.
- As an Owner, I want to manage collaborators so that I can control who has access to the project.
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

## Use Case Diagram – Collaboratory

![Use Case Diagram](usecase_collaboratory.png)

### Main Use Cases

- **View Projects & Tasks** — Users can view projects and tasks they have access to.
- **Manage Tasks** — Tasks can be created, edited, and assigned within a project.
- **Delete Task** — The Owner can remove tasks.
- **Manage Collaborators** — The Owner adds or removes collaborators.
- **Change Task Status** — Assignees update the progress of tasks.
- **Add & View Project Notes** — Owners and Collaborators document project information.
- **Add & View Task Notes** — Assignees add updates or comments to tasks.

### Actors

- **Owner** — Creates and manages projects, tasks, collaborators, and project notes.
- **Collaborator** — Supports the Owner by managing tasks and project notes.
- **Assignee** — Works on assigned tasks and updates their status.

## Roles & Permissions

A user's role is specific to each project — it depends on their relationship to that project, not a global setting.

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

> Users with `is_admin = true` have Owner-level access across all projects.
> This is a simple override for recovery/admin purposes, not a normal role.

| Action | Owner | Assignee | Collaborator |
|---|---|---|---|
| View project & tasks | ✅ | ✅ | ✅ |
| Create task | ✅ | — | ✅ |
| Assign task to user | ✅ | — | ✅ |
| Edit task details | ✅ | — | ✅ |
| Change task status | — | ✅ | — |
| Delete task | ✅ | — | — |
| Add/remove collaborators | ✅ | — | — |
| Add Project Note | ✅ | — | ✅ |
| View Project Notes | ✅ | ✅ | ✅ |
| Add Task Note | — | ✅ | — |
| View Task Notes | ✅ | ✅ | ✅ |

---

## ✅ Project Requirements

The application contains the following elements using NiceGUI as the frontend technology.

### 1. Presentation Layer (Client-Side View)

- Browser acts as a thin client
- UI rendered with Vue.js and Quasar through NiceGUI
- No business logic stored in the browser

### 2. Application Logic (Server-Side Frontend)

- Business logic implemented in Python
- NiceGUI components instantiated on the server
- Object-oriented structure for modular logic

### 3. Persistence Layer (Database)

- SQLite used as persistent storage
- SQLAlchemy used as ORM
- No raw SQL required

---

### 1. Interactive App (GUI)

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

---

### 2. Data Validation

The application validates all user input to ensure:

- Data consistency
- Application stability
- Secure workflows

Validation is performed before data is processed or stored in the database.

Examples of validated input include:

- Usernames and email addresses
- Login credentials
- Project names and descriptions
- Task titles and task status values
- Collaborator assignments
- Required form fields

Invalid or incomplete input is rejected with clear feedback messages in the user interface.

### 3. Database Management

The application uses SQLite as its persistent database and SQLAlchemy as an Object-Relational Mapper (ORM).

The ORM is used to:

- Define database tables as Python classes
- Manage relationships between users, projects, tasks, assignments, project notes, and task notes
- Create, read, update, and delete persistent data
- Avoid writing raw SQL statements directly

Database access is separated from the user interface. Manager classes interact with the database through SQLAlchemy sessions to keep the architecture clean and maintainable.

### Input Validation and Error Handling

The application validates all user input before processing or storing it.

Examples include:

- Usernames
- Task titles
- Descriptions
- Status values

Invalid or incomplete data is rejected with clear error messages to ensure consistent and well-formed data in the database.

## Database Information

### Core Entities

- **User** — people who log in and get assigned tasks
- **Project** — top-level project containers
- **Task** — work items inside projects
- **Assignment** — links tasks to users
- **ProjectMember** — links projects to collaborators

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

#### Project

```text
id          (PK)
name
description
owner_id    (FK → Users.id)
created_at
```

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

#### Assignment

```text
id          (PK)
task_id     (FK → Tasks.id)
user_id     (FK → Users.id)
assigned_at
```

#### ProjectMember

```text
id          (PK)
project_id  (FK → Projects.id)
user_id     (FK → Users.id)
```

#### ProjectNote

```text
id          (PK)
content
project_id  (FK → Projects.id)
created_by  (FK → Users.id)
created_at
```

#### TaskNote

```text
id          (PK)
content
task_id     (FK → Tasks.id)
created_by  (FK → Users.id)
created_at
```

#### Entity Relationship Diagram

<img width="1213" height="1209" alt="ERCollab_Notes (2)" src="https://github.com/user-attachments/assets/199f9147-afc6-4767-9e04-17df8013b0eb" />

## Architecture

This application follows a 3-tier architecture.

### 1. Presentation Tier (Frontend)

- **Technology:** NiceGUI
- Renders the user interface directly from Python
- UI components are served through NiceGUI
- Runs in the browser

### 2. Application Tier (Backend)

- **Technology:** Python + NiceGUI
- Handles business logic
- Manages authentication and sessions
- Connects UI and database

### 3. Data Tier (Database)

- **Technology:** SQLAlchemy + SQLite
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

Simplifies database session handling and permission checking behind shared interfaces.

**Status:** Implemented

---

### Singleton (by convention)

**File:**
- `database/__init__.py`

Uses a shared `db_conn` database connection instance across the application.

**Status:** Partial
  
## ⚙️ Implementation

### Technology

- Python 3.x
- GitHub Codespaces
- NiceGUI
- SQLAlchemy
- bcrypt

### 📂 Repository Structure

```text
collaboratory/
├── database/            # physical data store connection and ORM models
├── logic/               # server-side business logic and state management
├── ui/                  # NiceGUI components and pages
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

### How to Run
### How to Run

1. Open the repository in **GitHub Codespaces** (or clone locally)

2. Open the **Terminal**

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
python main.py
```

5. Open your browser at the URL shown in the terminal:

```text
http://localhost:8080
```

### Libraries Used

- `nicegui` — builds the web-based user interface
- `sqlalchemy` — ORM for database models and queries
- `bcrypt` — password hashing and login verification

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Features

- User authentication and login
- Project creation and management
- Task creation, editing, assignment, and deletion
- Task status tracking
- Collaborator management
- Project and task notes
- Role-based permission system
- Input validation and error handling

## 👥 Team & Contributions

| Name | Main Contributions |
|---|---|
| Marta Greschuk | Application state management, dashboard UI, integration testing |
| Polina Yemelianenkova | Authentication system, database infrastructure, ORM configuration |
| Ayla Allen | Architecture, permissions system, collaboration layer, UI framework |
| Sümeyya Güçlü-Babür | Task management, assignee system, task page UI, README documentation |

---

### Collaborative Work

All team members contributed to:
- Integration and debugging
- Final testing
- README improvements
- UI and workflow refinements
- Cross-layer fixes during the final sprint

## 🤝 Contributing

This is a closed academic project submitted for assessment. External contributions are not accepted.

## Known Limitations & Deferred Decisions

### Known Limitations

- SQLite is suitable for small-scale projects but not large production systems
- Some UI workflows could still be improved
- Singleton behaviour is implemented by convention only

### Deferred Decisions

- Real-time collaboration features were not implemented
- Advanced notification systems were scoped out
- Additional user roles were not added to keep permissions manageable

## 📝 License

This project is provided for educational use only as part of the Programming Foundations module.

[MIT License](LICENSE)