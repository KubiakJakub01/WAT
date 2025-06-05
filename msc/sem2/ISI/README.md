# ISI project

## Instrukcja

1. Uruchom kontener z MSSQL:
```bash
   docker compose up -d
```

2. Poczekaj aż baza się wystartuje (ok. 20–30s – sprawdź docker logs mssql)

3. Wykonaj kolejno:
```bash
   sqlcmd -S localhost -U sa -P "Your_password123" -C -i scripts/init_hr.sql
   sqlcmd -S localhost -U sa -P "Your_password123" -C -i scripts/init_fin.sql
   sqlcmd -S localhost -U sa -P "Your_password123" -C -i scripts/procedures.sql
```

4. Gotowe. Teraz możesz:
   - wywołać procedurę ręcznie: EXEC isi_Fin.etl_import_payments;
   - albo przez endpoint REST POST http://localhost:8080/etl/run
   - zatwierdzić zadanie w Camundzie i zakończyć proces commit
