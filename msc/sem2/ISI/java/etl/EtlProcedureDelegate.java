public class EtlProcedureDelegate implements JavaDelegate {

  @Autowired
  private DataSource dataSource;

  @Override
  public void execute(DelegateExecution execution) throws Exception {
    try (Connection conn = dataSource.getConnection();
         CallableStatement stmt = conn.prepareCall("{ call isi_Fin.etl_import_payments }")) {
      stmt.execute();
    }
  }
}
