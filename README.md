# project_template
Semester two project


> 🚧 This is a template repository for student projects in the course Advanced Programming at FHNW, BSc BIT.  
> 🚧 Do not keep this section in your final submission.

---

# 🍕 PizzaRP – Pizzeria Reference Project (Browser App)

> 🚧 Replace the screenshot with one that shows your main screen.

![UI Showcase](docs/ui-images/ui_showcase.png)

---

This project is intended to:

- Practice the complete process from **application requirements analysis to implementation**
- Apply advanced **Python** concepts in a browser-based application (NiceGUI)
- Demonstrate **data validation**, a clean architecture (presentation / application logic / persistence), and **database access via ORM**
- Produce clean, well-structured, and documented code (incl. tests)
- Prepare students for **teamwork and professional documentation**
- Use this repository as a starting point by importing it into your own GitHub account  
- Work only within your own copy — do not push to the original template  
- Commit regularly to track your progress

---

# 🍕 TEMPLATE for documentation

> 🚧 Please remove the paragraphs marked with "🚧". These are comments for preparing the documentation.

---

## 📝 Application Requirements

---

### Problem

> 🚧 Describe the real-world problem your application solves. (Not HOW, but WHAT)

💡 Example: In a small local pizzeria, the staff writes orders and calculates totals by hand. This causes mistakes and inconsistent orders or discounts.

---

### Scenario

> 🚧 Describe when and how a user will use your application

💡 Example: PizzaRP solves the part of the problem where orders and totals are created by letting a user select items from a menu, validating the inputs, storing orders in a database, and automatically generating a correct invoice.

---

### User stories

1. As a user, I want to see the pizza menu in the Browser App.
2. As a user, I want to select pizzas and see the running total.
3. As a user, I want a discount of 10% to be applied automatically, if the sum exceeds 50 Swiss Franks. 
4. As a user, I want an invoice to be created and saved as a file.
5. As an admin, I want to see all past transactions, ordered by date.

---

### Use cases

> 🚧 Name actors and briefly describe each use case. Ideally, a UML use case diagram specifies use cases and relationships.

![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png)

**Use cases**
- Show Menu (Customer)
- Create Order / Add Items (Customer)
- Show Current Order and Total (Customer)
- Checkout & Print Invoice (Staff) → generates `invoice_xxx.pdf`
- View Past Transactions (Admin)

**Actors**
- Customer (places orders)
- Staff (processes/prints invoices)
- Admin (reviews transactions)

---

### Wireframes / Mockups

> 🚧 Add screenshots of the wireframe mockups you chose to implement.

![Wireframe – Home](docs/ui-images/wireframe_home.png)
![Wireframe – Checkout](docs/ui-images/wireframe_checkout.png)

---

## 🏛️ Architecture

> 🚧 Document the architecture components, relationships, and key design decisions.

### Software Architecture

> 🚧 Insert your UML class diagram(s). Split into multiple diagrams if needed.

![UML Class Diagram](docs/architecture-diagrams/uml_class_architecture.png)

**Layers / components:**
- UI (NiceGUI pages/components, browser as thin client)
- Application logic (controllers + domain/services)
- Persistence (SQLite + ORM entities + repositories/queries)

**Design decisions (examples):**
- Organize code using **MVC**:
   - **Model:** domain + ORM entities (e.g. `models.py`)
   - **View:** NiceGUI UI components/pages
   - **Controller:** event handlers and coordination logic between UI, services, and persistence
- Separate UI (`app/main.py`) from domain logic (e.g. `pricing.py`) and persistence (e.g. `models.py`, `db.py`)
- Use and interaction of modules to minimize dependencies, by minimizing cohesion and maximizing coupling
- Keep business rules testable without starting the UI

**Design patterns used (examples):**
- MVC (Model–View–Controller)
- Repository/DAO for database access (e.g. `queries.py`)
- Strategy for business rules (e.g. discount calculation)
- Adapter for external services (e.g. invoice generation backend)

---

### 🗄️ Database and ORM

> 🚧 Describe the database and your ORM entities. Ideally, a diagram documents the database and it is described together with the ORM entities.

![ER Diagram](docs/architecture-diagrams/er_diagram.png)

**ORM and Entities (example):** In the database, order are stored in ... that are mapped an `Order` entity. The `Order` ↔ `OrderItem` relationship ... ensures that an `Order` has at least one `OrderItem` and an `OrderItem` always relates to an `Order`.

---

## ✅ Project Requirements

---

> 🚧 Requirements act as a contract: implement and demonstrate each point below.

Each app must meet the following criteria in order to be accepted (see also the official project guidelines PDF on Moodle):

1. Using NiceGUI for building an interactive web app
2. Data validation in the app
3. Using an ORM for database management

---

### 1. Browser-based App (NiceGUI)

> 🚧 In this section, document how your project fulfills each criterion.

The application interacts with the user via the browser. Users can:

- View the pizza menu
- Select pizzas and quantities
- See the running total
- Receive an invoice generated as a file

**Architecture note (per SS26 guidelines):** the browser is a thin client; UI state + business logic live on the server-side NiceGUI app.

---

### 2. Data Validation

The application validates all user input to ensure data integrity and a smooth user experience.
These checks prevent crashes and guide the user to provide correct input, matching the validation requirements described in the project guidelines.

---

### 3. Database Management

All relevant data is managed via an ORM (e.g. SQLModel or SQLAlchemy). For the pizza example this includes users, pizzas, and orders.

---

## ⚙️ Implementation

---

### Technology

- Python 3.x
- Environment: GitHub Codespaces
- External libraries (e.g. NiceGUI, SQLAlchemy, Pydantic)

---

### 📂 Repository Structure

```text
pizza-nicegui/
├─ README.md
├─ pyproject.toml                 # or requirements.txt
├─ .env.example                   # DATABASE_URL=sqlite:///data/pizza.db
├─ .gitignore
│
├─ docs/                          # screenshots, diagrams, additional documentation if needed
│  ├─ ui-images/
│  │  ├─ ui_showcase.png
│  │  ├─ ui_menu.png
│  │  ├─ ui_checkout.png
│  │  ├─ wireframe_home.png
│  │  └─ wireframe_checkout.png
│  └─ architecture-diagrams/
│     ├─ uml_use_case_diagram.png
│     ├─ uml_class_architecture.png
│     ├─ uml_class_domain.png
│     ├─ uml_class_persistence.png
│     └─ er_diagram.png
│
├─ app/
│  ├─ main.py                        # entrypoint, starts the main module(s)
|  └─ pizzarp/                       # main module
│     ├─ __main__.py                 # entrypoint of the module, starts NiceGui
|     ├─ persistence/                # example of a module; organize in modules according to the architecture
│     |  ├─ __main.py__              # initializes data access
│     |  ├─ models.py                # ORM models (User, Pizza, Order, OrderItem)
│     |  ├─ queries.py               # query helpers (menu, orders)
|     |  └─ db.py                    # create_engine + session factory + init_db()
│     ├─ pricing.py                  # subtotal/discount/total logic
│     ├─ invoice.py                  # generate invoice file
│     └─ seed.py                     # seed pizzas/users
│
├─ data/                          # sqlite database (gitignored)
├─ invoices/                      # generated invoices (gitignored)
└─ tests/
   ├─ test_pricing.py
   └─ test_invoice.py
```

---

### How to Run

> 🚧 Adjust to your project.

### 1. Project Setup
- Python 3.13 (or the course version) is required
- Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration
- E.g., setup of parameters or environment variables

### 3. Launch
- Start the NiceGUI app (example):
   ```bash
   python app/main.py
   ```
- Open the URL printed in the console.

### 4. Usage (document as steps)

> 🚧 Describe the usage of the main functions

Order Pizza:
1. Open the menu page and browse pizzas.
2. Add items (with quantities) to the current order.
3. Review total (incl. discounts) and validate inputs.
4. Checkout to persist the order and generate the invoice.

> 🚧 Add UI screenshots of the main screens (or a short video link):

![UI – Menu](docs/ui-images/ui_menu.png)
![UI – Checkout](docs/ui-images/ui_checkout.png)

---

## 🧪 Testing

> 🚧 Explain what you test and how to run tests.

**Types (examples):**
- Unit tests: pricing/discount rules, validators
- Integration tests: ORM mappings + queries against a test SQLite DB

**Run:**
```bash
pytest
```

> 🚧 If you provide separate commands, document them here (e.g. `pytest -m integration`).

---

### Libraries Used

- nicegui
- sqlalchemy / sqlmodel
- pydantic
- ...

## 👥 Team & Contributions

---

> 🚧 Fill in the names of all team members and describe their individual contributions below.

| Name      | Contribution |
|-----------|--------------|
| Student A | NiceGUI UI + documentation |
| Student B | Database & ORM + documentation |
| Student C | Business logic + documentation |

---

## 🤝 Contributing

---

> 🚧 This is a template repository for student projects.  
> 🚧 Do not change this section in your final submission.

- Use this repository as a starting point by importing it into your own GitHub account
- Work only within your own copy — do not push to the original template
- Commit regularly to track your progress

---

## 📝 License

---

This project is provided for **educational use only** as part of the Advanced Programming module.

[MIT License](LICENSE)
