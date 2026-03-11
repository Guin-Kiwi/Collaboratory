# Semester Two Project - Task Management Tracker

This project is intended to:

- Practice the complete process from **problem analysis to implementation**
- Apply basic **Python** programming concepts learned in the Programming Foundations module
- Demonstrate the use of **console interaction, data validation, and file processing**
- Produce clean, well-structured, and documented code
- Prepare students for **teamwork and documentation** in later modules
- Use this repository as a starting point by importing it into your own GitHub account.  
- Work only within your own copy — do not push to the original template.  
- Commit regularly to track your progress.

## 📝 Analysis

### Problem


### Scenario


### User stories: stakeholder (for whom?), functionality (what do they want?), benefit (why is it useful?)

## Standard User

1. As a standard user, I want to create a new task so that I can report an issue.
2. As a standard user, I want to edit my own tasks so that I can update the description if requirements change.
3. As a standard user, I want to see the status of my tasks so that I know whether they are still open, in progress or completed.
4. As a standard user, I want to assign a task to a specific user so that responsibility for the task is clear.
5. As a standard user, I want to upload additional files or information to a task so that I can provide more details.

## Assignee User

6. As an assignee, I want to change the status of a task from "To Do" to "In Progress" and "Completed". So the team and the standard user knows the progress of the task.
7. As an assignee, I want to view tasks assigned to me so that I know which tasks I am responsible for.
8. As an assignee, I want to add comments or updates to a task so that I can communicate progress or issues with the team.
9. As an assignee, I want to receive updates when a task assigned to me is edited so that I stay informed about changes.

## Administrator User

10. As an administrator, I want to delete any task so I can remove spam, duplicates or invalid tasks.
11. As an administrator, I want to reassign tasks between users so that workload can be balanced across the team.


### Use cases: 

> 🚧 Name actors and briefly describe each use case. Ideally, a UML use case diagram specifies use cases and relationships.

![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png)

**Use cases**

## Use Case 1 - Standard user
- Create Task
- Edit own task
- Upload additional informations or files
- View task status

## Use Case 2 - Assignee
- View assigned tasks
- Change task status "To Do" - "In Progress" - "Completed"
- Add comments or updates
- Receive Updates when task is edited

## Use Case 3 - Administrator
- Delete Task
- Reassign tasks between users

**Actors**
- Standard user (creates a task)
- Assignee (works on assigned tasks and updates progress)
- Administrator (manages tasks and balances workload)

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
 
---
The application interacts with the user via a web browser. Users can perform the following steps:

1. User Login
2. Task Status
3. Task Assignment
4. Manage Workflows/Tasks
---


### 2. Data Validation


### ?Information:

	`code`

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
	email       (unique)
	password    (hashed)
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
	status      (e.g. "todo", "in_progress", "done")
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

### ?Gui information:



	`code`


### ?Logic information: 


  
  Requirements:
1. 
2.
3. 
4. 

**Criteria**




### 3. File Processing

The application writes and reads data using a ** file with a ** structure :

- **Input and Output file:** `.json` — Contains the **

		`code goes here`
  
## ⚙️ Implementation

### Technology
- Python 3.x
- Environment: GitHub Codespaces
- External libraries: `nicegui` (web-based UI), `sqlalchemy` (ORM/database)

### 📂 Repository Structure
```
advanced-prog-issue-tracker/
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

1. Open the repository in **GitHub Codespaces**
2. Open the **Terminal**
3. Run:
	```bash
	python3 main.py
	```

### Libraries Used

- `json`: used for working with JSON data.
- `random`: for generating random numbers and making random selections.
- `string`: provides useful string constants and helpers, generating random strings, passwords, or validating characters.
- `nicegui`: for building web-based user interface.
- `sqlalchemy`: for working with the database.

The first three libraries (`json`, `random`, `string`) are part of the Python standard library and require no installation. `nicegui` and `sqlalchemy` are external dependencies and must be installed before running the application (e.g., via `pip install -r requirements.txt`).


## 👥 Team & Contributions

| Name                  | Final Contribution                                                                   |
| --------------------- | ------------------------------------------------------------------------------------ |
| Marta Greschuk        | document the work distribution                                                       |
| Polina Yemelianenkova | libraries, the 3-tier architecture plan, and the database schema within the read.me |
| Ayla Allen            | GitHub repository setup                                                              |
| Sümeyya Güçlü-Babür   | user stories and user cases                                                          |
## 🤝 Contributing

- Use this repository as a starting point by importing it into your own GitHub account or VScode on Desktop.  
- Work only within your own copy — do not push to the original template.  
- Commit regularly to track your progress.

## 📝 License

This project is provided for **educational use only** as part of the Programming Foundations module.  
[MIT License](LICENSE)
