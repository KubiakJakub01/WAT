CREATE SCHEMA isi_HR;
GO
CREATE TABLE isi_HR.employees_payments (
  id INT IDENTITY PRIMARY KEY,
  first_name NVARCHAR(100),
  last_name NVARCHAR(100),
  salary_base INT,
  bonus INT
);
GO
INSERT INTO isi_HR.employees_payments (first_name, last_name, salary_base, bonus) VALUES
(N'Anna', N'Nowak', 3500, 500),
(N'Piotr', N'Kowalski', 4200, 300);
GO
