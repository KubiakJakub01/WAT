CREATE PROCEDURE isi_Fin.etl_import_payments AS
BEGIN
  INSERT INTO isi_Fin.payment_stage (receiver, amount)
  SELECT CONCAT(first_name, ' ', last_name), salary_base + bonus
  FROM isi_HR.employees_payments;
END;
GO

CREATE PROCEDURE isi_Fin.commit_transfer AS
BEGIN
  INSERT INTO isi_Fin.transfer (sender, receiver, amount)
  SELECT 'WAT', receiver, amount FROM isi_Fin.payment_stage;

  DELETE FROM isi_Fin.payment_stage;
END;
GO
