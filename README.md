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

1. As an Owner, I want to create a new project so that I can organise tasks for my team in one place.
2. As an Owner, I want to manage collaborators so that I can control who has access to the project.
3. As an Owner, I want to create and assign tasks so that work is clearly distributed.
4. As an Owner, I want to edit and delete tasks so that the project stays organised and up to date.
5. As an Owner, I want to add and view project notes so that important information is documented and accessible.

### Assignee

1. As an Assignee, I want to view projects and tasks so that I understand my responsibilities clearly.
2. As an Assignee, I want to update the status of my tasks so that I can show my progress.
3. As an Assignee, I want to add and view task notes so that I can share updates and understand task context.

### Collaborator

1. As a Collaborator, I want to view projects and tasks so that I can support the Owner.
2. As a Collaborator, I want to create and edit tasks so that I can help organise the project work.
3. As a Collaborator, I want to assign tasks to users so that work is distributed effectively.
4. As a Collaborator, I want to add and view project notes so that important information is shared within the team.

## Use Case Diagram – Collaboratory

![Use Case Diagram](usecase_collaboratory.png)

### Main Use Cases

- **View Projects & Tasks**: Users can view projects and tasks they have access to.
- **Manage Tasks**: Tasks can be created, edited, and assigned within a project.
- **Delete Task**: The Owner can remove tasks.
- **Manage Collaborators**: The Owner adds or removes collaborators.
- **Change Task Status**: Assignees update the progress of tasks.
- **Add & View Project Notes**: Owners and Collaborators document project information.
- **Add & View Task Notes**: Assignees add updates or comments to tasks.

### Actors

- **Owner**: Creates and manages projects, tasks, collaborators, and project notes.
- **Collaborator**: Supports the Owner by managing tasks and project notes.
- **Assignee**: Works on assigned tasks and updates their status.

## Roles & Permissions

A user's role is specific to each project — it depends on their relationship
to that project, not a global setting. Users can be Owners or Collaborators, and can additionally be Assignees or Admins.
A user can simultaneously be a Collaboratory Admin, Owner or Collaborator of a project, and Assignee of tasks within that project.

| Role | How you get it |
|---|---|
| **Owner** | You created the project |
| **Assignee** | You have been assigned to at least one task in the project |
| **\* Collaborator** | The Owner added you to the project |

> Users with `is_admin = true` have Owner-level access across all projects.
> This is a simple override for recovery/admin purposes, not a normal role.

| Action                        | Owner | Assignee | * Collaborator |
|-------------------------------|-------|----------|---------------|
| View project & tasks          | ✅    | ✅       | ✅            |
| Create task                   | ✅    | —        | ✅             |
| Assign task to user           | ✅    | —        | ✅             |
| Edit task details             | ✅    | —        | ✅             |
| Change task status            | —     | ✅       | —              |
| Delete task                   | ✅    | —        | —              |
| Add/remove collaborators      | ✅    | —        | —              |
| Add Project Note              | ✅    | —        | ✅             |
| View Project Notes            | ✅    | ✅       | ✅             |
| Add Task Note                 | —     | ✅       | —              |
| View Task Notes               | ✅    | ✅       | ✅            |

---

## ✅ Project Requirements

Each application must contain the following elements. As “frontend” technology we have chosen
NiceGUI (https://nicegui.io/) which makes it possible to run Python apps in the browser:

1. Presentation Layer (Client-Side View): The browser acts as a thin client. It runs a generic
engine (based on Vue.js and Quasar) that renders UI components. It holds no business
logic and no persistent application state.
2. Application Logic (Server-Side Frontend): This is the core of the NiceGUI model. The UI
components (e.g., ui.button, ui.input etc.) are instantiated as Python objects on the
server. The state of these objects (their value, visibility, or enabled status) resides on the
server. Teams will use object-orientation in Python to organize business logic into
modular, reusable, and self-contained units.
3. Persistence Layer (Database): The physical data store (SQLite). You interact with a
database using an Object-Relational Mapper (ORM) to avoid writing SQL statements
directly.

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

The application validates all user input to ensure data consistency, application stability, and secure workflows.

Validation is performed before data is processed or stored in the database.

Examples of validated input include:

- usernames and email addresses
- login credentials
- project names and descriptions
- task titles and task status values
- collaborator assignments
- required form fields

Invalid or incomplete input is rejected with clear feedback messages in the user interface. This prevents inconsistent or malformed data from being stored in the SQLite database.

The application also validates permission-based actions to ensure that users can only perform actions allowed by their project role (Owner, Collaborator, or Assignee).

### 3. Database Management

The application uses SQLite as its persistent database and SQLAlchemy as an Object-Relational Mapper (ORM).

The ORM is used to:

- define database tables as Python classes
- manage relationships between users, projects, tasks, assignments, project notes, and task notes
- create, read, update, and delete persistent data
- avoid writing raw SQL statements directly in the application logic

Database access is separated from the user interface. The manager classes interact with the database through SQLAlchemy sessions, which helps keep the architecture clean and maintainable.

### Input validation and error handling

The application validates all user input (for example, usernames, task titles, descriptions, and status values) before processing or storing it. Invalid or incomplete data is rejected with a clear error message, ensuring that only consistent, well‑formed information is written to the database and used in workflows.

### Database information:
Core entities:
- Users — people who log in and get assigned tasks
- Projects — the top-level containers
- Tasks — the actual work items inside projects
- Assignments — links tasks to users (who's responsible)

#### Schema:
-------

#### Users

	id          (PK)
	username    (unique)
	name
	email       (unique)
	password    (hashed)
	is_admin	(bool)
	created_at

#### Projects

	id          (PK)
	name
	description
	owner_id    (FK → Users.id)
	created_at

#### Tasks

	id          (PK)
	title
	description
	status      (e.g. "todo", "in_progress", "completed")
	priority    (e.g. "low", "medium", "high")
	due_date
	project_id  (FK → Projects.id)
	created_by  (FK → Users.id)
	created_at

#### Assignments

	id          (PK)
	task_id     (FK → Tasks.id)
	user_id     (FK → Users.id)
	assigned_at

#### ProjectMember

	id          (PK)
	project_id  (FK → Projects.id)
	user_id     (FK → Users.id)

#### ProjectNote

	id          (PK)
	content
	project_id  (FK → Projects.id)
	created_by  (FK → Users.id)
	created_at

#### TaskNote

	id          (PK)
	content
	task_id     (FK → Tasks.id)
	created_by  (FK → Users.id)
	created_at

#### Entity Relationship Diagram

<img width="1213" height="1209" alt="ERCollab_Notes (2)" src="https://github.com/user-attachments/assets/199f9147-afc6-4767-9e04-17df8013b0eb" />

### Architecture

This application follows a 3-tier architecture:

#### 1. Presentation Tier (Frontend)
- **Technology:** NiceGUI
- Renders the user interface directly from Python — no separate HTML/CSS/JS codebase
- UI components (task boards, project views, dashboards) are defined and served by NiceGUI
- Runs in the user's browser via NiceGUI's built-in web server

#### 2. Application Tier (Backend)
- **Technology:** Python + NiceGUI (server-side logic)
- Handles all business logic: task creation, assignment, deadlines, and user roles
- Manages user sessions and authentication
- Acts as the bridge between the UI layer and the database

#### 3. Data Tier (Database)
- **Technology:** SQLAlchemy (ORM) + SQLite 
- SQLAlchemy models define the database schema in Python classes
- Stores all persistent data: users, projects, tasks, and assignments
- The backend interacts with the database exclusively through SQLAlchemy sessions

### Design Patterns

**Service Layer (Manager Pattern)** — `logic/user_manager.py`, `project_manager.py`, `task_manager.py`, `collab_manager.py`
Four manager classes each own all business logic for one domain. The UI calls manager methods; managers query the database via their SQLAlchemy session. No SQL or UI code appears in manager classes. Status: **implemented**.

**Mixin Pattern** — `database/mixins.py` (`TimestampMixin`)
Adds `created_at` and `updated_at` columns to `User`, `Project`, `Task`, `ProjectNote`, and `TaskNote` via multiple inheritance, avoiding repeated column definitions across models. Status: **implemented**.

**Façade Pattern** — `database/connection.py` (`DatabaseConnection`) and `logic/permissions_manager.py` (`require_permission`)
`DatabaseConnection` hides SQLAlchemy engine and session setup; callers use `init()` and `get_session()` only. `require_permission` hides an 18-action permission dispatch behind a single guard call. All four managers use the shared `db_conn` instance from `database/__init__.py`. Status: **implemented**.

**Singleton (by convention)** — `database/__init__.py`
A single shared `DatabaseConnection` instance (`db_conn`) is initialised at import time and used across all managers. Python does not enforce that additional instances cannot be created, but none are created in practice. Status: **partial** — convention enforced, not language-enforced.
  
## ⚙️ Implementation

### Technology
- Python 3.x
- Environment: GitHub Codespaces
- External libraries: `nicegui` (web-based UI), `sqlalchemy` (ORM/database), `bcrypt` (password hashing)

### 📂 Repository Structure
```
collaboratory/
├── database/            # physical data store connection and ORM models
├── logic/               # server-side business logic and state management
├── ui/                  # Python classes instantiating NiceGUI components
├── .gitignore           # specifies intentionally untracked files to ignore
├── LICENSE              # project usage license terms
├── README.md            # project documentation, user stories, and milestones
├── main.py              # application entry point linking the three tiers
└── requirements.txt     # list of Python dependencies for the project
```

### How to Run

1. Open the repository in **GitHub Codespaces** (or clone locally)
2. Open the **Terminal**
3. Install dependencies:
	pip install -r requirements.txt
4. Start the application:
    python main.py
5. Open your browser at the URL shown in the terminal (default: `http://localhost:8080`)

### Libraries Used

- `nicegui`: builds the web-based user interface; UI components are Python objects served by NiceGUI's built-in web server.
- `sqlalchemy`: ORM for defining models, managing sessions, and querying the SQLite database without writing raw SQL.
- `bcrypt`: hashes passwords at signup and verifies them at login, used in `UserManager`.

All three are external dependencies. Install before running:
pip install -r requirements.txt

## Features

- **User authentication** — sign up with name and email; login with bcrypt-hashed password; server-side session state via `AppState`
- **Project management** — create, view, edit, and delete projects; role-based permissions enforced per action
- **Collaborator management** — project owners can add collaborators; collaborators can assign tasks and write notes
- **Task management** — full create/read/update/delete for tasks within a project; status: To Do → In Progress → Completed
- **Task notes** — assignees, owners, and collaborators can write and view notes on individual tasks
- **Project notes** — owners and collaborators can write and view project-level notes
- **Permission system** — 18 permission actions across three roles (owner, collaborator, assignee) enforced by `PermissionsManager`

## 👥 Team & Contributions

| Name                  | Contribution |
| --------------------- | ------------ |
| Marta Greschuk        | Task ORM models, application state management, dashboard UI, README work distribution |
| Polina Yemelianenkova | Database architecture, ORM configuration, UserManager logic, authentication UI, README architecture and schema |
| Ayla Allen            | GitHub repository setup, database seeding, permission system, layout and routing UI |
| Sümeyya Güçlü-Babür   | User stories and use cases, TaskManager logic, task input UI, task and assignee management |

## 🤝 Contributing

This is a closed academic project submitted for assessment. External contributions are not accepted.

## Known Limitations & Deferred Decisions

### Known Limitations

- The application currently uses SQLite, which is suitable for development and small team collaboration but not intended for large-scale production environments.
- Some UI components and workflows could still be further improved regarding responsiveness and usability.
- Singleton behaviour for the shared database connection is implemented by convention and not strictly enforced by Python itself.

### Deferred Decisions

- Advanced notification features and real-time collaboration updates were intentionally scoped out due to project time constraints.
- Role expansion beyond Owner, Collaborator, Assignee, and Admin was not implemented to keep the permission system manageable.

## 📝 License

This project is provided for **educational use only** as part of the Programming Foundations module.  
[MIT License](LICENSE)