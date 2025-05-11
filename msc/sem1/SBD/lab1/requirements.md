## TEMPORAL DATABASES  
### Laboratory Assignment

#### To complete the laboratory classes on temporal databases, you must:

1. **Individually and independently prepare a database model** that includes aspects of temporality.
2. **Build a database using Microsoft SQL Server** in accordance with your developed model.
3. **Populate the built database with test data.**
4. **Prepare queries for the database** that utilize the temporal aspect.
5. **Prepare a report.**

---

### MODEL REQUIREMENTS

- The model should address a real business problem where temporality is important.
- The physical model should consist of **at least 6 related tables**, of which **at least 2 should be temporal tables**.

**Examples:**  
Book borrowing from a library, car rental, stock quotations, brokerage office, hotel room reservations, vehicle and driver location tracking, student grade records, code versioning, account or credit card management, warehouse inventory records, event planning, concert tour organization, etc.

- It is important to capture the aspect of temporality, e.g., product inventory changes over time, a book can be borrowed, returned, borrowed by another person, stock prices change over time.
- The model must be prepared in graphical form with a short description and included in the report.
- If several very similar models are submitted, they will be subject to detailed verification for similarity.

---

### ADDITIONAL REQUIREMENTS

- Microsoft SQL Server will be used during classes.
- Your databases may also be implemented and run on other database platforms that natively support temporality.
- Along with the report, you must submit the script that creates the database. **Do not include it in the report—attach it electronically.**
- Your model must be populated with data. **Each table should contain (including historical data) at least 20 rows, and the total number of rows should not be less than 150.**
- Along with the report, you must submit the script that fills the database with test data. **Do not include it in the report.**

---

### QUERY REQUIREMENTS

- Prepare **at least 5 queries** for your database. Each query must utilize the temporal aspect.
- Each query should make business sense in the context of your model.
- Along with the report, you must submit the script containing the queries.  
- The queries, along with a business description and your results (based on your test data), should be included in the report.
- The complexity and variety of queries will affect your grade.

---

### REPORT REQUIREMENTS

- The report must be prepared electronically—in PDF or MS Word format.
- The report must be concise and to the point. It does not have to follow any template—think of it as a project-technical description of your work.
- The complete report, along with all necessary attachments, should be zipped and named as follows:  
  `NrGrupy_Nazwisko_Imie_Lab1_BD-Temporalna.zip`
- Send the zip file to: **jaroslaw.koszela@wat.edu.pl**
- If you have questions or doubts, contact the instructor by email or via MS Teams (in your group/team).

---

### GRADING CRITERIA

| Grade | 3 | 4 | 5 |
|-------|---|---|---|
| **Domain description** | YES | YES | YES |
| **Number of tables + necessary rules/constraints + required data set** | min 5 | min 8 | min 10 |
| **Temporal tables** | min 3 | min 4 | min 5 |
| **Temporal rules/constraints** | NO | YES – min. 3 different temporal rules/constraints | YES – min. 3 different temporal rules/constraints + "temporal future" support in at least 1 table |
| **Implementation description** | YES | YES | YES |
| **CRUD, classic and temporal queries** | YES – min 5 temporal queries with different "FOR SYSTEM_TIME" expressions | YES + min. 10 temporal and temporal-analytical (aggregates) queries with different "FOR SYSTEM_TIME" expressions | YES + min. 10 temporal and temporal-analytical (aggregates) queries with different "FOR SYSTEM_TIME" expressions |
| **Conclusions** | YES | YES | YES |
| **Submission deadline** | By next class | By next class | By end of day/week |

---

**End of requirements.**
