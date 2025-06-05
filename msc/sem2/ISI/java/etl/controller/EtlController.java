@RestController
@RequiredArgsConstructor
@RequestMapping("/etl")
public class EtlController {

  private final JdbcTemplate jdbc;

  @PostMapping("/run")
  public ResponseEntity<Void> runEtl() {
    jdbc.execute("EXEC isi_Fin.etl_import_payments");
    return ResponseEntity.ok().build();
  }

  @PostMapping("/commit")
  public ResponseEntity<Void> commit() {
    jdbc.execute("EXEC isi_Fin.commit_transfer");
    return ResponseEntity.ok().build();
  }
}
