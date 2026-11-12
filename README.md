# SCCL TPSC Study — Native PSCAD 5.1

**Measured result:** 79.959 kA to 49.913 kA symmetrical RMS (37.58% reduction). Source 1: 9.927 kA. Source 2: 39.991 kA.

Open **[pscad/SCCL_TPSC_Study.pswx](pscad/SCCL_TPSC_Study.pswx)** in licensed PSCAD 5.1 Professional. It contains:

- `SCCL_A_Without.pscx` — identical two-source network without the limiter.
- `SCCL_B_With.pscx` — reactor, capacitor, six native SCRs, MOVs and protective control.
- `SCCL_C_Recovery.pscx` — five-cycle opening command, natural SCR turn-off and 1.20 s healthy-feeder reclosure.

Use **[Figure 5](results/figures/Figure_5_Internal_Current_Path.png)** first for teaching: it displays reactor, capacitor and valve currents together before, during and after bypass activation. Read [technical_report.md](technical_report.md) for the engineering explanation and [validation_report.md](validation_report.md) for evidence.

## Run and edit

1. Open the workspace, select GFortran 8.1 (64-bit), and run any case. All electrical definitions are native Master Library components; the measurement-based protection definition is embedded in each project.
2. Change `Reactor_L_A/B/C` and `Capacitor_C_A/B/C` independently on the schematic. Keep all three phases equal for this balanced study. L = 1/(omega^2 C) is an option for compensation, not an enforced coupling.
3. Protection constants are visible in the lower-left control area. Current values are in kA, voltages in kV, MOV energy in kJ and time in seconds.
4. Native output channels and graph panels are included. Graphs populate when the project runs; the supplied PNG/SVG figures can be viewed immediately without PSCAD.

## Automation

Run from this study folder with Python 3.11 and the versions in `requirements-lock.txt`. No OpenAI API or other cloud service is required. A licensed PSCAD session and its automation port are needed. The observed port during this delivery was **63579**, which is session-specific and can change.

```powershell
py -3.11 scripts/probe_environment.py --port 63579
py -3.11 scripts/run_simulations.py --case without_sccl --port 63579
py -3.11 scripts/run_simulations.py --case with_sccl --port 63579
py -3.11 scripts/run_simulations.py --case recovery --port 63579
py -3.11 scripts/run_matrix.py --port 63579 --resume
py -3.11 scripts/analyze_results.py
py -3.11 scripts/plot_results.py
py -3.11 scripts/write_reports.py
py -3.11 -m unittest discover -s tests -v
```

To build a fresh project using the official API, use `build_project.py --case with_sccl --port <current-port>` (or `without_sccl` / `recovery`). Existing native project files are backed up before regeneration. Parameter defaults are in `config/parameters.json`. Use `run_simulations.py --L-mH 20 --C-uF 351.809665 --case with_sccl --label custom_case --port <current-port>` for an independently specified pair. `--angle` changes both source phases together; `--step-us` sets both integration and saved-output interval.

`probe_environment.py --launch` can start a fresh licensed PSCAD session through the official library if attaching to an older process causes native file-write failures. The script reports the license state. To identify that session's automation port, inspect the PSCAD PID's listening sockets with `netstat -ano`; the Python library also supports automatic session discovery. Do not terminate or overwrite unrelated PSCAD projects.

The final acceptance analysis is specific to the specified 138 kV, 60 Hz source equivalents. The independent L/C and angle studies are supported directly. If source voltage, frequency or network constants are changed for a new study, also revise the analytical references, measurement windows and acceptance targets. Resume skips only runs with matching configuration hashes, requested settings and intact native evidence; older receipts without configuration hashes rerun conservatively. Omit `--resume` after manual schematic edits.

## Results and reproducibility

- `results/selected_runs.json`: accepted-run index; older diagnostic runs are preserved separately.
- Each selected directory: original `.inf/.out`, source `.pscx`, compiled Fortran evidence, output hashes and `run_receipt.json`.
- `results/metrics.json`: full inductance/angle matrix, fixed-C cases, stresses and event times.
- `results/figures`: nine publication figures, each in PNG and SVG.
- `references`: unchanged copies of all three supplied reference images.
- `results/reopen_verification.json`, `results/portability_receipt.json`: native reopen and extracted-workspace run checks. The full package includes the relocated output evidence.
- `manifest.json` inside each archive lists every payload hash. `results/package_verification.json` alongside the delivery archives records ZIP CRC, payload verification and archive hashes; it is external to avoid a self-referential archive hash.

The native ZIP contains editable models, scripts, reports and figures. The full ZIP additionally contains every selected native run and the extracted-workspace reproduction. Use the full ZIP to rerun analysis immediately without first executing all cases.

The main A/B comparison uses 0.95-1.05 s symmetrical phasor RMS. The time-varying RMS curves include DC offset; instantaneous peaks are larger. The exact network KCL includes the small feeder load current: I1 + I2 = IF + ILOAD. No amplitude scaling or artificial source changes are used.

Equipment parameters are engineering equivalents. This study validates electrical behavior, not manufacturing ratings, thermal temperatures, breaker TRV capability, or standards compliance.
