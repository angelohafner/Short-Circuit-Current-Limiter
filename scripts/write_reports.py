"""Write English reports from the accepted native run index and measured metrics."""
import json
import math
from pathlib import Path
from common import ROOT,PARAM

m=json.loads((ROOT/'results/metrics.json').read_text());v=json.loads((ROOT/'results/validation.json').read_text())
a=m['without_sccl'];b=m['with_sccl'];c=m['recovery']
selected=json.loads((ROOT/'results/selected_runs.json').read_text())
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n'
perf=[]
for title,key,unit in [('Source 1 symmetrical RMS','source1_rms_kA','kA'),('Source 2 symmetrical RMS','source2_rms_kA','kA'),('Total fault symmetrical RMS','fault_rms_kA','kA'),('Maximum asymmetrical fault peak, any phase','fault_peak_kA','kA'),('Reduction in total symmetrical RMS','total_rms_reduction_percent','%')]:
    perf.append([title,f'{a[key]:.4f}',f'{b[key]:.4f}',unit])
performance=table(['Quantity','Without SCCL','With SCCL','Unit'],perf)
ls=[b]+[x for k,x in m.items() if k.startswith('sensitivity/') and x['source_phase_deg']==0]
ls.sort(key=lambda x:x['L_mH'])
sensitivity=table(['L (mH)','C (uF)','Source 1 RMS (kA)','Fault RMS (kA)','Reduction (%)','Fault peak (kA)','Reactor peak voltage (kV)','Capacitor peak voltage (kV)','Valve peak (kA)'],[[f'{x["L_mH"]:.1f}',f'{x["C_uF"]:.3f}',f'{x["source1_rms_kA"]:.3f}',f'{x["fault_rms_kA"]:.3f}',f'{x["total_rms_reduction_percent"]:.2f}',f'{x["fault_peak_kA"]:.2f}',f'{x["reactor_voltage_peak_kV"]:.2f}',f'{x["capacitor_peak_kV"]:.3f}',f'{x["valve_branch_peak_kA"]:.3f}'] for x in ls])
angles=[b]+[x for k,x in m.items() if k.startswith('sensitivity/') and abs(x['L_mH']-15.9)<1e-5]
angles.sort(key=lambda x:x['source_phase_deg'])
angle_table=table(['Source phase setting (deg)','Phase A fault peak (kA)','Worst phase fault peak (kA)','Detection delay (ms)','First bypass response (ms)'],[[f'{x["source_phase_deg"]:g}',f'{x["fault_phase_peaks_kA"]["A"]:.3f}',f'{x["fault_peak_kA"]:.3f}',f'{x["detection_delay_ms"]:.3f}',f'{x["bypass_response_ms"]:.3f}'] for x in angles])
fixed=table(['L (mH)','Fixed C (uF)','Pre-fault Source 1 RMS (kA)','Normal SCCL voltage drop (%)','Fault RMS (kA)','Capacitor peak (kV)'],[[f'{x["L_mH"]:.1f}',f'{x["C_uF"]:.1f}',f'{x["prefault_source1_rms_kA"]:.4f}',f'{x["normal_drop_percent"]:.3f}',f'{x["fault_rms_kA"]:.3f}',f'{x["capacitor_peak_kV"]:.3f}'] for k,x in m.items() if k.startswith('fixed_C/')])
parameters=table(['Parameter','Value','Unit','Basis'],[
    ['Nominal source voltage',138,'kV line-line RMS','Specified'],['Frequency',60,'Hz','Specified'],
    ['Each source resistance',.1325,'ohm/phase','Specified equivalent'],['Each source inductance',5.272,'mH/phase','Specified equivalent'],
    ['Baseline interconnection', '0.001 ohm + 1 uH','per phase','Short busbar assumption'],
    ['Main reactor', '15.9 mH + 0.10 ohm','per phase','Specified initial design'],
    ['Series capacitor',442.5,'uF/phase','Specified; exact compensation is 442.527881 uF'],
    ['Capacitor ESR',.002,'ohm/phase','Equivalent bank-loss assumption'],
    ['Bypass discharge limiting branch','0.1 mH + 0.05 ohm','per phase','Damping and di/dt assumption'],
    ['Each equivalent SCR stack ON/OFF resistance','0.002 / 1e9','ohm','Assumed linear conduction / blocking'],
    ['SCR forward trigger threshold',.020,'kV','Assumed equivalent stack; native switch model'],
    ['SCR forward breakover / reverse withstand','100 / 100','kV','Conservative assumed stack limits'],
    ['SCR minimum extinction time',100,'us','Assumption; no reverse-recovery charge model'],
    ['Each SCR RC snubber','1000 ohm + 0.02 uF','series RC','Assumed equivalent stack'],
    ['MOV reference voltage / parallel stacks','15 / 1','kV / count','Native default nonlinear curve, scaled'],
    ['Fault resistance',.005,'ohm/phase','Low finite resistance for bolted-fault approximation'],
    ['Feeder breaker closed/open resistance','0.0001 / 1e10','ohm','Zero-current interruption, no arc model'],
    ['Load','75 MW, 0.95 lagging','at 138 kV','Constant-impedance grounded-wye R-L load'],
    ['Pickup current / capacitor voltage','2 / 18','kA peak / kV peak','Configurable engineering protection assumptions'],
    ['Gate delay',.1,'ms','Configurable intentional firing delay'],
    ['MOV energy interlock',5000,'kJ per phase','Assumed screening limit, not a thermal rating'],
    ['Recovery permissive','0.8 kA for 20 ms','peak / hold time','Requires all feeder poles open and no energy lockout'],
    ['Integration / output interval','10 / 10','us','5 us independent sensitivity runs'],
    ['Source energization ramp',.05,'s','Startup ramp only; no fault-time voltage changes']])
report=f'''# TPSC and Series-Reactor Short-Circuit Current Limiter

## 1. Objective and verified outcome

This study uses the native PSCAD 5.1 EMTDC engine to demonstrate a three-phase 138 kV, 60 Hz short-circuit current limiter. All network currents, internal capacitor and valve currents, voltages, and device switching timestamps come from actual electrical branches. Python generates the native projects and processes EMTDC output files; it does not synthesize the study waveforms.

{performance}

The unchanged two-source network produces the requested approximately 80 kA versus 50 kA comparison. The nominal limited total differs from 50 kA by {100*(b['fault_rms_kA']/50-1):+.3f}%. Source 1 differs from 10 kA by {100*(b['source1_rms_kA']/10-1):+.3f}%. Source 2 remains approximately 40 kA. These are fundamental symmetrical RMS quantities, not instantaneous peaks.

## 2. Operating principle

During normal operation, each phase carries current through a real reactor and a real capacitor. The six SCRs are blocked. The nominal reactances at 60 Hz are XL = 5.994159 ohm and XC = 5.994536 ohm. Their cancellation leaves the winding resistance, capacitor ESR and small residual reactance. The measured normal SCCL voltage drop is {b['normal_drop_percent']:.4f}% of nominal phase voltage.

A measured overcurrent or capacitor overvoltage latches the protective bypass. Both antiparallel SCR gates are enabled. Only the forward-biased device conducts; the opposite device takes over with the appropriate polarity. The capacitor is bypassed through the discharge-limiting R-L branch and SCR valve, while the main reactor stays in the Source 1 fault-current path. Source 2 connects directly to Bus 2 through its original Thevenin impedance.

This is protective TPSC operation. There is no TCSC firing-angle regulator and no continuously controlled reactor branch across the capacitor. The small valve-branch inductance limits capacitor discharge and is not the principal fault-current limiting reactor.

![Current paths](results/figures/Figure_5_Internal_Current_Path.png)

## 3. Electrical network and parameters

![Network](results/figures/Figure_1_Network_Topology.png)

Two native three-phase sources each include the specified series resistance and an external, visible phase inductance. The three feeder breaker poles receive a common command but each interrupts at its physical current zero. The three fault branches and modest R-L load lie downstream of the feeder breaker. There is no additional line impedance used to tune the current target.

{parameters}

The sources have fixed equal magnitudes and equal relative phase. The common source phase is varied only in the inception-angle study. L and C can be edited separately in every phase. Source startup ramping ends well before the fault. The reactor is treated as an air-core linear inductance; core saturation is not assumed.

## 4. Analytical Thevenin reference

The phase RMS source voltage is E = 138/sqrt(3) = 79.674337 kV. The source impedance is Zs = 0.1325 + j1.987497 ohm, with X/R approximately 15. The load is a constant impedance Zload = VLL^2 / (P - jQ); P = 75 MW and Q = P tan(acos(0.95)).

With the capacitor bypassed, the first-order SCCL impedance is Zdevice = (0.10 + 0.05 + 0.002) + j omega (0.0159 + 0.0001) ohm. The small remaining capacitor admittance and SCR threshold effects are represented by EMTDC, rather than this first-order expression. The baseline busbar impedance is 0.001 + j omega 1e-6 ohm.

For common equal source phasors, with Y1 = 1/(Zs + Zdevice), Y2 = 1/Zs and Rf including the closed feeder breaker, Vf = E(Y1 + Y2)/(Y1 + Y2 + 1/Rf). Then I1 = (E - Vf)Y1, I2 = (E - Vf)Y2, and Itotal = I1 + I2. The analytical reference neglects the very small load current at the depressed fault voltage; the EMTDC fault meter excludes that load current exactly.

The computed references are 79.9607 kA without SCCL and 49.9143 kA with SCCL, including 9.9270 kA from Source 1 and 39.9911 kA from Source 2. RMS magnitudes are not added arithmetically. The approximately 1.8 degree difference between the two limited-current contribution phasors produces a small but real difference between their scalar sum and the magnitude of their phasor sum.

## 5. Reactor, capacitor and equivalent valve sizing

Compensation follows L = 1/(omega^2 C). The specified 442.5 uF is within 0.007% of exact compensation for 15.9 mH. At 1 kA RMS, the main reactor exchanges approximately 17.982 MVAr three-phase and the capacitor exchanges approximately 17.984 MVAr with opposite sign. The actual Source 1 pre-fault current is {b['prefault_source1_rms_kA']:.4f} kA; its measured operating point corresponds to approximately {b['normal_reactor_MVAr']:.3f} MVAr in each compensated element. Consequently the 1 kA example is a rating illustration, not the simulated pre-fault current.

The bypass contains 0.1 mH and 0.05 ohm before the antiparallel valve. Its capacitor-discharge natural frequency is approximately {1/(2*math.pi*math.sqrt(.0001*442.5e-6)):.1f} Hz, well above the 60 Hz power frequency. It prevents an ideal short across stored capacitor energy and damps the discharge oscillation visible in Figure 5. Main-reactor current remains continuous as branch currents redistribute.

The native SCR model includes blocking, a forward trigger threshold, ON resistance, finite minimum extinction time, protective breakover, and current-zero turn-off. It does not allow a gate command to forcibly open a conducting SCR. The ON-state conduction characteristic is the native piecewise resistive equivalent, not a manufacturer semiconductor loss curve. The interpretation follows the [PSCAD thyristor documentation](https://www.pscad.com/webhelp-pscad-v5.1.0-ol/Master_Library_Models/HVDC_and_FACTS/PE_Switch/Thyristor.htm).

The native MOV uses its documented default nonlinear curve, scaled to a 15 kV reference. Its first tabulated point is 1 A at 1.1 times the reference, or 16.5 kV; 10 A corresponds to 24 kV. The selected voltage is well above the simulated normal capacitor voltage. Native low-voltage extrapolation gives a small leakage current; the measured pre-fault maximum is {b['normal_MOV_peak_A']:.4f} A, and the main scenarios do not require strong MOV clamping. These are engineering equivalent parameters, not verified manufacturing ratings. Electrical I-squared-t, peak voltage/current and absorbed energy are provided; junction temperature and cooling times are not calculated.

{table(['Measured electrical stress, maximum across phases/devices','Case B','Case C','Unit'],[
['Capacitor voltage',f'{b["capacitor_peak_kV"]:.4f}',f'{c["capacitor_peak_kV"]:.4f}','kV peak'],
['MOV terminal voltage including capacitor ESR',f'{b["MOV_voltage_peak_kV"]:.4f}',f'{c["MOV_voltage_peak_kV"]:.4f}','kV peak'],
['MOV current',f'{1000*b["MOV_peak_kA"]:.4f}',f'{1000*c["MOV_peak_kA"]:.4f}','A peak'],
['MOV absorbed energy',f'{b["MOV_energy_max_kJ"]:.5f}',f'{c["MOV_energy_max_kJ"]:.5f}','kJ per phase'],
['SCR terminal voltage',f'{b["SCR_voltage_peak_kV"]:.4f}',f'{c["SCR_voltage_peak_kV"]:.4f}','kV peak'],
['Valve bypass current',f'{b["valve_branch_peak_kA"]:.4f}',f'{c["valve_branch_peak_kA"]:.4f}','kA peak'],
['Individual SCR current-squared integral',f'{max(b["valve_I2t_kA2s"].values()):.4f}',f'{max(c["valve_I2t_kA2s"].values()):.4f}','kA^2 s']])}

Stress maxima cover the complete 0-1.50 s simulation, including energization, fault clearing and recovery. The MOV terminal voltage is calculated from its measured capacitor voltage plus the measured capacitor current times the physical 0.002 ohm ESR. All per-case stresses, including the sensitivity variants, are recorded in `results/metrics.json`.

## 6. Protection, switching and recovery

Protection monitors all three Source 1 currents, all three capacitor voltages, a one-cycle three-phase mean-square RMS estimate, and per-phase MOV energy. Instantaneous pickup avoids a full-cycle detection wait. Pickup is armed after 0.15 s to exclude the deliberate source energization ramp. Thresholds and timing are visible constants in the native protection block and are also listed in `config/parameters.json`.

The nominal measured detection delay is {b['detection_delay_ms']:.3f} ms and the first effective bypass response is {b['bypass_response_ms']:.3f} ms from actual fault application. The controller supplies continuous protective gate enable rather than firing-angle modulation. Device polarity and latching are decided by the native electrical SCRs.

Recovery requires all feeder poles to be open, low SCCL current for 20 ms, acceptable capacitor voltage and no MOV energy lockout. Gate withdrawal then permits natural current-zero turn-off. Recovery-ready additionally requires valve current below 1 A and acceptable voltage for 20 ms. Independent native turn-on/turn-off timestamps verify that all six SCRs have actually turned off before recovery-ready and remain off through reclosure. Excess MOV energy latches a feeder trip and blocks recovery/reclosure. Capacitor overvoltage reasserts protective bypass.

## 7. Scenarios and actual event times

Cases A and B use matched sustained faults from 0.50 s to the feeder opening command at 1.10 s. The fault path is removed at 1.15 s after isolation. This provides a settled six-cycle measurement window from 0.95 to 1.05 s. Case C uses the requested five-cycle opening command at 0.583333 s, fault removal at 0.62 s, and healthy-feeder reclosure at 1.20 s. Actual pole interruption follows current zeros, so it occurs a few milliseconds after the opening command.

{table(['Case C event','Measured time (s)'],[['Fault applied',f'{c["actual_fault_inception_s"]:.6f}'],['Detection',f'{c["Detect_first_s"]:.6f}'],['Gate enabled',f'{c["Gate_first_s"]:.6f}'],['All feeder poles open',f'{c["last_pole_open_s"]:.6f}'],['Gate removed',f'{c["gate_removal_s"]:.6f}'],['Last native SCR turn-off',f'{c["last_SCR_turn_off_s"]:.9f}'],['Recovery ready',f'{c["Recovery_first_s"]:.6f}'],['Reclosure command',f'{c["Reclose_first_s"]:.6f}']])}

Gate removal precedes the last actual SCR turn-off by {c['gate_off_to_last_SCR_turn_off_ms']:.2f} ms. The residual circulating current decays through physical resistances; it is not forced to zero by the controller. Small load-reconnection RLC oscillations decay after 1.20 s and remain visible in sliding RMS at the 1.50 s simulation endpoint. Source 1 reaches {c['post_source1_rms_kA']:.4f} kA fundamental RMS in the 1.40-1.49 s window, compared with {c['prefault_source1_rms_kA']:.4f} kA before the fault. This demonstrates stable recovery of the normal current path; it does not imply that every transient has fully settled by 1.50 s.

![Recovery](results/figures/Figure_6_Fault_Clearing_Recovery.png)

![Recovery detail](results/figures/Figure_9_Recovery_Detail.png)

## 8. Measurement definitions and provenance

The principal 80/50 kA comparison uses a least-squares 60 Hz RMS phasor over the same 0.95-1.05 s window. The sliding RMS channels are the square root of a one-cycle average of the mean of the three squared phase currents; they include transient DC offset. Instantaneous peak means the maximum absolute sample of any fault-current phase between inception and the opening command. The finite five-cycle Case C estimate fits a sinusoid, a constant and two exponential DC modes from the coupled two-source R-L network over 0.54-0.58 s. This remains an engineering approximation to the switched circuit; the main acceptance comparison relies on the longer settled A/B window.

Every run has a timestamped directory, source `.pscx` snapshot, `.inf` channel map, original `.out` files, generated Fortran/build evidence, and SHA-256 run receipt. `results/selected_runs.json` selects the accepted runs. Native `.inf` PGB indices determine the data columns; all OUT block time vectors are checked. `waveforms.npz` is a lossless numerical convenience copy of those native files.

Positive I1 and I2 point toward Bus 2; positive IF and ILOAD point into their downstream branches. Thus the exact conservation equation is I1 + I2 = IF + ILOAD. Finite fault resistance leaves a very small load current during the fault, which is retained rather than silently assigned to the fault meter. Internal conservation is I1 = IC + IV - IM because the native arrester current output uses the opposite reference direction. `VL` measures the reactor assembly including winding resistance; `VC` measures the capacitor itself; `VDROP` measures the full SCCL. `VS1/VS2` are the source-component terminal voltages before their external Thevenin inductors, and `VB1/VB2` are the resulting bus voltages.

Dedicated source ammeters and post-network-solution measurement processing keep the principal branch currents on the same EMTDC time level. There is no waveform time shifting or amplitude scaling to obtain current balance. The reason for explicit output ordering is explained in [PSCAD's DSDYN/DSOUT documentation](https://pscad.com/webhelp-v502-ol/EMTDC/Program_Structure/dsdyn_and_dsout_subroutines.htm). Native SCR timestamp channels retain the event time reported by the solver; effective 1 A conduction monitoring is distinguished from native device state.

## 9. Comparison with the supplied references

`Short-Circuit-Current-Limiter.png` supplies the capacitor-only bypass plus main reactor relationship. The order of series capacitor and reactor does not change this single-branch circuit principle; the native study places the reactor before the protected capacitor for readable wiring. `Results-Measurments.png` supplies the two-source arrangement and approximate RMS target levels. The original image contains no digitized waveform samples, so the comparison is topology- and magnitude-based, not a claim of exact sample equivalence.

`Screenshot 2026-11-03 094514.png` motivates fault clearing, valve release, dead time and reclosure. Its optional mechanical capacitor-bypass breaker and absolute thermal curves are not reproduced. This implementation demonstrates the requested SCR-only capacitor bypass and natural electrical recovery directly, using a physical feeder breaker. No claim is made about the illustrated 260 C temperature or multi-hour cooling times.

![Direct comparison](results/figures/Figure_4_Direct_Comparison.png)

## 10. Inductance, capacitance and inception-angle sensitivity

The main matrix has five inductances and three common source phase settings. C is retuned for 60 Hz compensation except that the specified 442.5 uF is retained at 15.9 mH. Source equivalents, load, fault resistance and timing are unchanged. Changing the common source phase changes the voltage point on wave at fixed fault time without introducing a relative phase shift between sources.

{sensitivity}

At nominal L, the inception-angle results are:

{angle_table}

The worst three-phase peak is the maximum over all phase peaks; it is less angle-sensitive than Phase A alone because another phase can become the worst phase. The full matrix, including every stress and result folder, is in `results/metrics.json`.

The independent-parameter teaching cases retain C = 442.5 uF:

{fixed}

Increasing L reduces the Source 1 fault contribution, but requires smaller C for equal 60 Hz compensation and increases the reactor voltage duty and magnetic energy. At a fixed normal current, reactor and capacitor reactive ratings rise with L. Leaving C unchanged alters normal transfer sharing, residual reactive voltage drop, natural frequencies and switching stress. A low fault current alone is therefore insufficient for selecting an acceptable SCCL design.

![Sensitivity](results/figures/Figure_8_Parameter_Sensitivity.png)

## 11. Numerical verification and limitations

The accepted checks currently pass {v['passed']}/{v['total']}; see `validation_report.md` for exact assertions and convergence values. Both network and SCCL branch KCL are checked at every saved time step. The switching transition energy check uses the measured SCCL input power, main-reactor and bypass-reactor magnetic energy, capacitor electric energy, winding/ESR/bypass losses, native switch-plus-snubber terminal power and MOV power. Its nominal worst relative residual is {max(x['relative_residual_percent'] for x in b['energy_balance']):.5f}% of maximum stored energy in the 0.49-0.56 s interval. This checks the electrical energy accounting; it is not a semiconductor thermal validation.

The 10 us runs are compared with independent 5 us runs for all three principal cases. Numerical integration, output intervals and native switch interpolation are recorded in each receipt. Peak sensitivity and capacitor/valve stress are checked in addition to RMS current. The finite native MOV approximation and switching event interpolation can leave milliamperes of instantaneous internal KCL residual; the acceptance bound is 1 A against kiloampere currents.

Limitations: linear Thevenin sources and air-core reactors; balanced three-phase faults only; no frequency-dependent line, transformer saturation, generator subtransient decay, breaker arc/TRV withstand model, failed-reclosure study, semiconductor reverse-recovery charge, manufacturing coordination study or thermal network. Equivalent SCR/snubber/MOV values are transparent assumptions. No standards compliance or certified equipment rating is claimed. There is a configurable 100 us SCR extinction-time assumption, and the native resistive switch characteristic cannot establish detailed switching losses or junction temperatures.

## 12. Engineering conclusion

The actual electrical network reproduces the requested current reduction with identical source equivalents: approximately {a['fault_rms_kA']:.2f} kA to {b['fault_rms_kA']:.2f} kA symmetrical RMS. The capacitor provides low normal series reactance, and its protective SCR bypass exposes the main reactor during the fault. Current division follows the physical source and branch impedances. Natural valve turn-off, capacitor reinsertion and healthy-feeder reclosure are demonstrated without forcibly opening an SCR.

The native editable projects, visible wiring, configurable controls, raw EMTDC outputs, generated analysis, figures, and verified packages provide an auditable educational study. The supplied reference images are preserved unchanged.

## Implementation references

- [PSCAD Automation Library overview](https://www.pscad.com/software/pscad/automation-library)
- [Application API](https://www.pscad.com/webhelp-v501-al/reference/pscad.html)
- [Project API](https://www.pscad.com/webhelp-v501-al/reference/project.html)
- [Component API](https://www.pscad.com/webhelp-v501-al/reference/component.html)
- [Component Wizard](https://www.pscad.com/webhelp-v501-al/reference/wizard.html)
- [Native Power Electronic Switch](https://www.pscad.com/webhelp-pscad-v5.1.0-ol/Master_Library_Models/HVDC_and_FACTS/PE_Switch/peswitch.htm)

Installed execution environment: PSCAD 5.1.0 Professional, licensed native EMTDC, GFortran 8.1 (64-bit), Python 3.11 and mhi.pscad 3.1.2. Actual local API signatures and Master Library port definitions were inspected before generation.
'''
(ROOT/'technical_report.md').write_text(report,encoding='utf8')
conv=json.loads((ROOT/'results/convergence.json').read_text())
validation='# Validation report\n\n'+f"**{v['passed']}/{v['total']} checks passed.** All numerical results below originate from recorded native EMTDC runs.\n\n"
validation+='## Numerical convergence\n\n'
for row in conv:
    validation+='### '+row['case']+'\n\n'+table(['Metric: 10 to 5 us','Absolute relative change (%)'],[[k.replace('_change_percent','').replace('_',' '),f'{val:.6f}'] for k,val in row.items() if k!='case'])+'\n'
validation+='## Individual checks\n\n'+table(['Check','Status','Observed value'],[[x['name'],'PASS' if x['pass_'] else 'FAIL',str(x.get('value',''))] for x in v['checks']])
validation+='\n## Accepted source-bound runs\n\n'+table(['Case / variant','Result folder'],[[k,f'[{p}]({p})'] for k,p in selected.items()])
validation+='\nSee `results/package_verification.json`, `results/reopen_verification.json` and `results/portability_receipt.json` for delivery-level checks, when present. These are separate from numerical model checks. Historical diagnostic runs remain on disk but are not selected as accepted results.\n'
(ROOT/'validation_report.md').write_text(validation,encoding='utf8')
readme=f'''# SCCL TPSC Study — Native PSCAD 5.1

**Measured result:** {a['fault_rms_kA']:.3f} kA to {b['fault_rms_kA']:.3f} kA symmetrical RMS ({b['total_rms_reduction_percent']:.2f}% reduction). Source 1: {b['source1_rms_kA']:.3f} kA. Source 2: {b['source2_rms_kA']:.3f} kA.

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
'''
(ROOT/'README.md').write_text(readme,encoding='utf8')
print('REPORTS WRITTEN',flush=True)
