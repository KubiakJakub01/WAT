CREATE SCHEMA isi_Fin;
GO
CREATE TABLE isi_Fin.payment_stage (
  pk INT IDENTITY PRIMARY KEY,
  receiver NVARCHAR(200),
  amount INT
);
GO
CREATE TABLE isi_Fin.transfer (
  transfer_id INT IDENTITY PRIMARY KEY,
  sender NVARCHAR(100),
  receiver NVARCHAR(200),
  amount INT,
  created_at DATETIME DEFAULT GETDATE()
);
GO
