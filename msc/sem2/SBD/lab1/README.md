# Sprawozdanie

### Wymagania

- Ubuntu 22.04
- Docker
- [sqlcmd](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?view=sql-server-ver16&tabs=ubuntu-install)

### Instalacja

1. Uruchomienie kontenera z SQL Server:

```bash
docker run \
  --name airlines-temporal \
  --network host \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=Str0ngPassw0rd!" \
  -p 1433:1433 \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

2. Próba uruchomienia sqlcmd:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C
```

3. Skrypt tworzący schemat bazy danych:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -i create_schema.sql
```

4. Sprawdzenie czy schemat został utworzony poprawnie:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -Q "USE AirlinesTemporalDB; SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME;"
```

5. Skrypt wypełniający bazę danych:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -i load_data.sql
```

6. Sprawdzenie czy dane zostały wprowadzone poprawnie:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -Q "USE AirlinesTemporalDB; SELECT TOP 5 * FROM Airports;"
```

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -Q "USE AirlinesTemporalDB; SELECT TOP 5 * FROM Aircraft;"
```

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -Q "USE AirlinesTemporalDB; SELECT TOP 5 * FROM Routes;"
```

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -Q "USE AirlinesTemporalDB; SELECT * FROM MaintenanceStatus;"
```

7. Wykonanie zapytań:

```bash
sqlcmd -S localhost -U sa -P "Str0ngPassw0rd!" -C -i queries.sql
```
