public class TransferCommitDelegate implements JavaDelegate {

  @Autowired
  private DataSource dataSource;

  @Override
  public void execute(DelegateExecution execution) throws Exception {
    try (Connection conn = dataSource.getConnection();
         CallableStatement stmt = conn.prepareCall("{ call isi_Fin.commit_transfer }")) {
      stmt.execute();
    }
  }
}
