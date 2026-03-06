# Semester Two Project - Task Management Tracker?

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

	1. As a user, I want to  *** in order to *** so I can (benefit).
	2. As a user, I want to  *** in order to *** so I can (benefit). 
	3.
  4. 

### Use cases: 
-
-
-
-

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
3.Persistence Layer (Database): The physical data store (SQLite). You interact with a
database using an Object-Relational Mapper (ORM) to avoid writing SQL statements
directly.

---

### 1. Interactive App (Console Input)
 
---
The application interacts with the user via a web browser. Users can perform the following steps:

1. User Login:
   1. 

2. Task Status:
	1. 
   
3. Task Assignment:
	1. 

4. Manage Workflows/Tasks:
	1. 

---


### 2. Data Validation


### ?Information:

	`code`

### Database information:
-----

Core entities:
- Users — people who log in and get assigned tasks
- Projects — the top-level containers
- Tasks — the actual work items inside projects
- Assignments — links tasks to users (who's responsible)

Schema:

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

### 1. Presentation Tier (Frontend)
- **Technology:** NiceGUI
- Renders the user interface directly from Python — no separate HTML/CSS/JS codebase
- UI components (task boards, project views, dashboards) are defined and served by NiceGUI
- Runs in the user's browser via NiceGUI's built-in web server

### 2. Application Tier (Backend)
- **Technology:** Python + NiceGUI (server-side logic)
- Handles all business logic: task creation, assignment, deadlines, and user roles
- Manages user sessions and authentication
- Acts as the bridge between the UI layer and the database

### 3. Data Tier (Database)
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
- No external libraries

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

The first three libraries are part of the Python standard library, so no external installation is required. They were chosen for their simplicity and effectiveness in handling file management tasks in a console application.


## 👥 Team & Contributions


| Name                  | Final Contribution                                 |
|-----------------------|----------------------------------------------|
| Marta Greschuk        |  |
| Polina Yemelianenkova |  |
| Ayla Allen            |  |
| Sümeyya Güçlü-Babür   |  |


## 🤝 Contributing

- Use this repository as a starting point by importing it into your own GitHub account or VScode on Desktop.  
- Work only within your own copy — do not push to the original template.  
- Commit regularly to track your progress.

## 📝 License

This project is provided for **educational use only** as part of the Programming Foundations module.  
[MIT License](LICENSE)
