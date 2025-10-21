# Stock-exchange-database-CSE-111
Robinhood-style stock trading database system for CSE 111 Project.

# 📊 Stock Exchange Database (Robinhood Simulation)

CSE 111 – Database Systems | Project Checkpoint 1  
Team Members: **Ajay • Arsh • Rohit**

---

## 🧩 Project Overview
This project simulates a simplified stock-trading platform inspired by Robinhood.  
Users can register, view stocks, add them to a watchlist, and place mock buy/sell orders using virtual currency.

**Goals**
- Design a normalized relational database with realistic trading entities.  
- Demonstrate many-to-many and one-to-many relationships.  
- Build a foundation for a future interactive mock-trading app.

---

## ⚙️ Software Stack
| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Frontend** | React.js | Builds the web interface for login, stock browsing, and portfolio pages. |
| **Backend** | Python (Flask) | Handles user requests, logic, and API routes between UI and database. |
| **Database** | MySQL | Stores users, portfolios, stocks, orders, and transactions. |
| **Tools** | GitHub • VS Code • Draw.io | Version control, coding, and diagram creation. |

---

## 🧱 Database Design
The database consists of **8 core entities** and **8 relationships**  
(4 many-to-many, 4 one-to-many).

**Entities**
`Users`, `Portfolios`, `Stocks`, `Companies`, `Markets`, `Orders`, `Transactions`, `Watchlist`

**Relationships**
- Users ↔ Portfolios (M:N)  
- Portfolios ↔ Stocks (M:N)  
- Users ↔ Stocks (M:N watchlist)  
- Companies ↔ Markets (M:N dual listing)  
- Company → Stocks (1:M)  
- User → Orders (1:M)  
- Stock → Orders (M:1)  
- Order → Transactions (1:M)

---

## 🗂️ Docs and Diagrams
### 📘 E/R Diagram
![E/R Diagram](docs/ER_Diagram.png)

### 📗 Use Case Diagrams
- Investor Use Case → `docs/Investor_UseCase.png`  
- Admin Use Case → `docs/Admin_UseCase.png`

### 📙 Checkpoint Slides and Specs
- [Project Checkpoint 1 Presentation (PDF)](docs/Project_Checkpoint_1.pdf)  
- [Relation Specification (TXT)](docs/Relation_Specification.txt)

---

## 🧠 How to Run (when backend/frontend are added)
```bash
# clone the repo
git clone https://github.com/Rok051/Stock-exchange-database-CSE-111.git
cd Stock-exchange-database-CSE-111

# create MySQL schema later using:
mysql -u root -p < sql/schema.sql
