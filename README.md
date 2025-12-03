# Stock Exchange Database (CSE 111 Project)

This is our Robinhood-style stock trading database system for the CSE 111 project.

**Team Members:** Ajay, Arsh, Rohit

---

## About this project
We built a simplified version of a stock trading platform like Robinhood. Basically, users can sign up, look at stocks, add them to a watchlist, and "buy" or "sell" them using fake money.

**Our Goals:**
- Make a database that actually makes sense for trading (normalized).
- Show that we know how to use many-to-many and one-to-many relationships.
- Build a backend and frontend so you can actually interact with it.

---

## Tech Stack
We used these tools to build it:

- **Frontend:** React.js (for the website part)
- **Backend:** Python with Flask (handles the logic)
- **Database:** MySQL (stores all the user and stock data)
- **Tools:** GitHub, VS Code, Draw.io

---

## Database Design
We have **8 main tables** and **8 relationships** in our database.

**The Tables:**
`Users`, `Portfolios`, `Stocks`, `Companies`, `Markets`, `Orders`, `Transactions`, `Watchlist`

**How they connect:**
- Users can have Portfolios (Many-to-Many)
- Portfolios have Stocks (Many-to-Many)
- Users can watch Stocks (Many-to-Many)
- Companies are on Markets (Many-to-Many)
- A Company has Stocks (One-to-Many)
- A User makes Orders (One-to-Many)
- A Stock is in Orders (Many-to-One)
- An Order creates Transactions (One-to-Many)

---

## Docs and Diagrams
Here are the diagrams we made for the design:

### E/R Diagram
![E/R Diagram](docs/ER_Diagram.png)

### Use Case Diagrams
- Investor Use Case: `docs/Investor_UseCase.png`
- Admin Use Case: `docs/Admin_UseCase.png`

### Checkpoint Slides
- [Project Checkpoint 1 Presentation (PDF)](docs/Project_Checkpoint_1.pdf)
- [Relation Specification (TXT)](docs/Relation_Specification.txt)

---

## How to Run It
Once you have everything set up:

```bash
# Clone our repo
git clone https://github.com/Rok051/Stock-exchange-database-CSE-111.git
cd Stock-exchange-database-CSE-111

# Load the database schema
mysql -u root -p < sql/schema.sql
```
