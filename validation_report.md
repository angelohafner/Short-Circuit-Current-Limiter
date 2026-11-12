# Validation report

**332/332 checks passed.** All numerical results below originate from recorded native EMTDC runs.

## Numerical convergence

### without_sccl

| Metric: 10 to 5 us | Absolute relative change (%) |
| --- | --- |
| source1 rms kA | 0.000088 |
| source2 rms kA | 0.000088 |
| fault rms kA | 0.000088 |
| fault peak kA | 0.000130 |

### with_sccl

| Metric: 10 to 5 us | Absolute relative change (%) |
| --- | --- |
| source1 rms kA | 0.000108 |
| source2 rms kA | 0.000100 |
| fault rms kA | 0.000101 |
| fault peak kA | 0.000362 |
| capacitor peak kV | 1.253315 |
| valve branch peak kA | 0.005414 |

### recovery

| Metric: 10 to 5 us | Absolute relative change (%) |
| --- | --- |
| source1 rms kA | 0.000121 |
| source2 rms kA | 0.000113 |
| fault rms kA | 0.000115 |
| fault peak kA | 0.000362 |
| capacitor peak kV | 0.000234 |
| valve branch peak kA | 0.005414 |

## Individual checks

| Check | Status | Observed value |
| --- | --- | --- |
| with_sccl: fresh EMTDC receipt | PASS | None |
| with_sccl: source-bound project | PASS | None |
| with_sccl: complete native output hashes | PASS | None |
| with_sccl: unchanged specified source equivalents | PASS | None |
| with_sccl: both source phase settings match case label | PASS | None |
| with_sccl: network KCL < 1 A | PASS | 1.978596730900506e-10 |
| with_sccl: internal KCL < 1 A | PASS | 4.150163710339758e-06 |
| with_sccl: capacitor within assumed 15 kV peak operating envelope | PASS | 2.1227624342913 |
| with_sccl: bypass before feeder opening | PASS | None |
| with_sccl: no energy lockout | PASS | None |
| with_sccl: thyristors blocked during normal operation | PASS | None |
| with_sccl: bypass-transition energy residual below 1% | PASS | 0.0026716413986384254 |
| with_sccl: source1 phasor within 2% of circuit reference | PASS | 0.0017857932848031055 |
| with_sccl: source2 phasor within 2% of circuit reference | PASS | 0.00016481900987352915 |
| recovery: fresh EMTDC receipt | PASS | None |
| recovery: source-bound project | PASS | None |
| recovery: complete native output hashes | PASS | None |
| recovery: unchanged specified source equivalents | PASS | None |
| recovery: both source phase settings match case label | PASS | None |
| recovery: network KCL < 1 A | PASS | 1.980468566920024e-10 |
| recovery: internal KCL < 1 A | PASS | 4.150163710339758e-06 |
| recovery: capacitor within assumed 15 kV peak operating envelope | PASS | 2.4833113689691 |
| recovery: bypass before feeder opening | PASS | None |
| recovery: no energy lockout | PASS | None |
| recovery: thyristors blocked during normal operation | PASS | None |
| recovery: bypass-transition energy residual below 1% | PASS | 0.0026716413986384254 |
| without_sccl: fresh EMTDC receipt | PASS | None |
| without_sccl: source-bound project | PASS | None |
| without_sccl: complete native output hashes | PASS | None |
| without_sccl: unchanged specified source equivalents | PASS | None |
| without_sccl: both source phase settings match case label | PASS | None |
| without_sccl: network KCL < 1 A | PASS | 5.945749448343918e-11 |
| without_sccl: source1 phasor within 2% of circuit reference | PASS | 0.00012113346480324694 |
| without_sccl: source2 phasor within 2% of circuit reference | PASS | 0.00012122611445786191 |
| sensitivity/L_10mH_angle_0: fresh EMTDC receipt | PASS | None |
| sensitivity/L_10mH_angle_0: source-bound project | PASS | None |
| sensitivity/L_10mH_angle_0: complete native output hashes | PASS | None |
| sensitivity/L_10mH_angle_0: unchanged specified source equivalents | PASS | None |
| sensitivity/L_10mH_angle_0: both source phase settings match case label | PASS | None |
| sensitivity/L_10mH_angle_0: network KCL < 1 A | PASS | 1.780364189407635e-10 |
| sensitivity/L_10mH_angle_0: internal KCL < 1 A | PASS | 2.6712611388378642e-06 |
| sensitivity/L_10mH_angle_0: capacitor within assumed 15 kV peak operating envelope | PASS | 2.3062487609928 |
| sensitivity/L_10mH_angle_0: bypass before feeder opening | PASS | None |
| sensitivity/L_10mH_angle_0: no energy lockout | PASS | None |
| sensitivity/L_10mH_angle_0: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_10mH_angle_0: bypass-transition energy residual below 1% | PASS | 0.0029230926461995765 |
| sensitivity/L_10mH_angle_0: source1 phasor within 2% of circuit reference | PASS | 0.004568093279488927 |
| sensitivity/L_10mH_angle_0: source2 phasor within 2% of circuit reference | PASS | 0.0001918011369284045 |
| sensitivity/L_12mH_angle_0: fresh EMTDC receipt | PASS | None |
| sensitivity/L_12mH_angle_0: source-bound project | PASS | None |
| sensitivity/L_12mH_angle_0: complete native output hashes | PASS | None |
| sensitivity/L_12mH_angle_0: unchanged specified source equivalents | PASS | None |
| sensitivity/L_12mH_angle_0: both source phase settings match case label | PASS | None |
| sensitivity/L_12mH_angle_0: network KCL < 1 A | PASS | 4.287714627793093e-11 |
| sensitivity/L_12mH_angle_0: internal KCL < 1 A | PASS | 2.904964284760871e-06 |
| sensitivity/L_12mH_angle_0: capacitor within assumed 15 kV peak operating envelope | PASS | 2.1041725415779 |
| sensitivity/L_12mH_angle_0: bypass before feeder opening | PASS | None |
| sensitivity/L_12mH_angle_0: no energy lockout | PASS | None |
| sensitivity/L_12mH_angle_0: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_12mH_angle_0: bypass-transition energy residual below 1% | PASS | 0.002566008937118351 |
| sensitivity/L_12mH_angle_0: source1 phasor within 2% of circuit reference | PASS | 0.0032377361746105393 |
| sensitivity/L_12mH_angle_0: source2 phasor within 2% of circuit reference | PASS | 0.00018083267796509261 |
| sensitivity/L_20mH_angle_0: fresh EMTDC receipt | PASS | None |
| sensitivity/L_20mH_angle_0: source-bound project | PASS | None |
| sensitivity/L_20mH_angle_0: complete native output hashes | PASS | None |
| sensitivity/L_20mH_angle_0: unchanged specified source equivalents | PASS | None |
| sensitivity/L_20mH_angle_0: both source phase settings match case label | PASS | None |
| sensitivity/L_20mH_angle_0: network KCL < 1 A | PASS | 1.3840928403396902e-10 |
| sensitivity/L_20mH_angle_0: internal KCL < 1 A | PASS | 6.592624411211823e-06 |
| sensitivity/L_20mH_angle_0: capacitor within assumed 15 kV peak operating envelope | PASS | 2.6718859896475 |
| sensitivity/L_20mH_angle_0: bypass before feeder opening | PASS | None |
| sensitivity/L_20mH_angle_0: no energy lockout | PASS | None |
| sensitivity/L_20mH_angle_0: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_20mH_angle_0: bypass-transition energy residual below 1% | PASS | 0.0025575150588679593 |
| sensitivity/L_20mH_angle_0: source1 phasor within 2% of circuit reference | PASS | 0.0010342588860901003 |
| sensitivity/L_20mH_angle_0: source2 phasor within 2% of circuit reference | PASS | 0.0001691719552887605 |
| sensitivity/L_25mH_angle_0: fresh EMTDC receipt | PASS | None |
| sensitivity/L_25mH_angle_0: source-bound project | PASS | None |
| sensitivity/L_25mH_angle_0: complete native output hashes | PASS | None |
| sensitivity/L_25mH_angle_0: unchanged specified source equivalents | PASS | None |
| sensitivity/L_25mH_angle_0: both source phase settings match case label | PASS | None |
| sensitivity/L_25mH_angle_0: network KCL < 1 A | PASS | 1.0319312071516151e-10 |
| sensitivity/L_25mH_angle_0: internal KCL < 1 A | PASS | 1.0311514488346183e-05 |
| sensitivity/L_25mH_angle_0: capacitor within assumed 15 kV peak operating envelope | PASS | 3.4553103657691 |
| sensitivity/L_25mH_angle_0: bypass before feeder opening | PASS | None |
| sensitivity/L_25mH_angle_0: no energy lockout | PASS | None |
| sensitivity/L_25mH_angle_0: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_25mH_angle_0: bypass-transition energy residual below 1% | PASS | 0.0026942600575095453 |
| sensitivity/L_25mH_angle_0: source1 phasor within 2% of circuit reference | PASS | 0.0006713588262430292 |
| sensitivity/L_25mH_angle_0: source2 phasor within 2% of circuit reference | PASS | 0.00016241846104714242 |
| baseline_angle_45: fresh EMTDC receipt | PASS | None |
| baseline_angle_45: source-bound project | PASS | None |
| baseline_angle_45: complete native output hashes | PASS | None |
| baseline_angle_45: unchanged specified source equivalents | PASS | None |
| baseline_angle_45: both source phase settings match case label | PASS | None |
| baseline_angle_45: network KCL < 1 A | PASS | 5.945799408380026e-11 |
| baseline_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.00012113346476994025 |
| baseline_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.00012122611442455522 |
| sensitivity/L_10mH_angle_45: fresh EMTDC receipt | PASS | None |
| sensitivity/L_10mH_angle_45: source-bound project | PASS | None |
| sensitivity/L_10mH_angle_45: complete native output hashes | PASS | None |
| sensitivity/L_10mH_angle_45: unchanged specified source equivalents | PASS | None |
| sensitivity/L_10mH_angle_45: both source phase settings match case label | PASS | None |
| sensitivity/L_10mH_angle_45: network KCL < 1 A | PASS | 1.7803764018609058e-10 |
| sensitivity/L_10mH_angle_45: internal KCL < 1 A | PASS | 2.6091799877437253e-06 |
| sensitivity/L_10mH_angle_45: capacitor within assumed 15 kV peak operating envelope | PASS | 2.2509988424562 |
| sensitivity/L_10mH_angle_45: bypass before feeder opening | PASS | None |
| sensitivity/L_10mH_angle_45: no energy lockout | PASS | None |
| sensitivity/L_10mH_angle_45: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_10mH_angle_45: bypass-transition energy residual below 1% | PASS | 0.002616460472796254 |
| sensitivity/L_10mH_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.004574544195379282 |
| sensitivity/L_10mH_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.0001848744135446445 |
| sensitivity/L_12mH_angle_45: fresh EMTDC receipt | PASS | None |
| sensitivity/L_12mH_angle_45: source-bound project | PASS | None |
| sensitivity/L_12mH_angle_45: complete native output hashes | PASS | None |
| sensitivity/L_12mH_angle_45: unchanged specified source equivalents | PASS | None |
| sensitivity/L_12mH_angle_45: both source phase settings match case label | PASS | None |
| sensitivity/L_12mH_angle_45: network KCL < 1 A | PASS | 4.2875092365335377e-11 |
| sensitivity/L_12mH_angle_45: internal KCL < 1 A | PASS | 2.8336244945873203e-06 |
| sensitivity/L_12mH_angle_45: capacitor within assumed 15 kV peak operating envelope | PASS | 2.0728476584621 |
| sensitivity/L_12mH_angle_45: bypass before feeder opening | PASS | None |
| sensitivity/L_12mH_angle_45: no energy lockout | PASS | None |
| sensitivity/L_12mH_angle_45: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_12mH_angle_45: bypass-transition energy residual below 1% | PASS | 0.002211237096819411 |
| sensitivity/L_12mH_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.0032375409574791902 |
| sensitivity/L_12mH_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.0001829932429364689 |
| sensitivity/L_15.9mH_angle_45: fresh EMTDC receipt | PASS | None |
| sensitivity/L_15.9mH_angle_45: source-bound project | PASS | None |
| sensitivity/L_15.9mH_angle_45: complete native output hashes | PASS | None |
| sensitivity/L_15.9mH_angle_45: unchanged specified source equivalents | PASS | None |
| sensitivity/L_15.9mH_angle_45: both source phase settings match case label | PASS | None |
| sensitivity/L_15.9mH_angle_45: network KCL < 1 A | PASS | 1.9785556526485948e-10 |
| sensitivity/L_15.9mH_angle_45: internal KCL < 1 A | PASS | 4.046456895261964e-06 |
| sensitivity/L_15.9mH_angle_45: capacitor within assumed 15 kV peak operating envelope | PASS | 1.9649684436831 |
| sensitivity/L_15.9mH_angle_45: bypass before feeder opening | PASS | None |
| sensitivity/L_15.9mH_angle_45: no energy lockout | PASS | None |
| sensitivity/L_15.9mH_angle_45: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_15.9mH_angle_45: bypass-transition energy residual below 1% | PASS | 0.0023387562392867683 |
| sensitivity/L_15.9mH_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.0017722742660097879 |
| sensitivity/L_15.9mH_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.0001787257473684356 |
| sensitivity/L_20mH_angle_45: fresh EMTDC receipt | PASS | None |
| sensitivity/L_20mH_angle_45: source-bound project | PASS | None |
| sensitivity/L_20mH_angle_45: complete native output hashes | PASS | None |
| sensitivity/L_20mH_angle_45: unchanged specified source equivalents | PASS | None |
| sensitivity/L_20mH_angle_45: both source phase settings match case label | PASS | None |
| sensitivity/L_20mH_angle_45: network KCL < 1 A | PASS | 1.3840545376453406e-10 |
| sensitivity/L_20mH_angle_45: internal KCL < 1 A | PASS | 5.985826163051224e-06 |
| sensitivity/L_20mH_angle_45: capacitor within assumed 15 kV peak operating envelope | PASS | 2.4248020228285 |
| sensitivity/L_20mH_angle_45: bypass before feeder opening | PASS | None |
| sensitivity/L_20mH_angle_45: no energy lockout | PASS | None |
| sensitivity/L_20mH_angle_45: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_20mH_angle_45: bypass-transition energy residual below 1% | PASS | 0.004268095342221621 |
| sensitivity/L_20mH_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.0010148339920856841 |
| sensitivity/L_20mH_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.0001865779935106282 |
| sensitivity/L_25mH_angle_45: fresh EMTDC receipt | PASS | None |
| sensitivity/L_25mH_angle_45: source-bound project | PASS | None |
| sensitivity/L_25mH_angle_45: complete native output hashes | PASS | None |
| sensitivity/L_25mH_angle_45: unchanged specified source equivalents | PASS | None |
| sensitivity/L_25mH_angle_45: both source phase settings match case label | PASS | None |
| sensitivity/L_25mH_angle_45: network KCL < 1 A | PASS | 1.0319561871696692e-10 |
| sensitivity/L_25mH_angle_45: internal KCL < 1 A | PASS | 8.735727127886876e-06 |
| sensitivity/L_25mH_angle_45: capacitor within assumed 15 kV peak operating envelope | PASS | 3.2078039129478 |
| sensitivity/L_25mH_angle_45: bypass before feeder opening | PASS | None |
| sensitivity/L_25mH_angle_45: no energy lockout | PASS | None |
| sensitivity/L_25mH_angle_45: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_25mH_angle_45: bypass-transition energy residual below 1% | PASS | 0.00649704394631796 |
| sensitivity/L_25mH_angle_45: source1 phasor within 2% of circuit reference | PASS | 0.0006408683646430546 |
| sensitivity/L_25mH_angle_45: source2 phasor within 2% of circuit reference | PASS | 0.0001792133958344877 |
| baseline_angle_90: fresh EMTDC receipt | PASS | None |
| baseline_angle_90: source-bound project | PASS | None |
| baseline_angle_90: complete native output hashes | PASS | None |
| baseline_angle_90: unchanged specified source equivalents | PASS | None |
| baseline_angle_90: both source phase settings match case label | PASS | None |
| baseline_angle_90: network KCL < 1 A | PASS | 5.945832715070765e-11 |
| baseline_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.00012113346480324694 |
| baseline_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.00012122611445786191 |
| sensitivity/L_10mH_angle_90: fresh EMTDC receipt | PASS | None |
| sensitivity/L_10mH_angle_90: source-bound project | PASS | None |
| sensitivity/L_10mH_angle_90: complete native output hashes | PASS | None |
| sensitivity/L_10mH_angle_90: unchanged specified source equivalents | PASS | None |
| sensitivity/L_10mH_angle_90: both source phase settings match case label | PASS | None |
| sensitivity/L_10mH_angle_90: network KCL < 1 A | PASS | 1.7803508667313395e-10 |
| sensitivity/L_10mH_angle_90: internal KCL < 1 A | PASS | 2.481342871452271e-06 |
| sensitivity/L_10mH_angle_90: capacitor within assumed 15 kV peak operating envelope | PASS | 2.327427212067 |
| sensitivity/L_10mH_angle_90: bypass before feeder opening | PASS | None |
| sensitivity/L_10mH_angle_90: no energy lockout | PASS | None |
| sensitivity/L_10mH_angle_90: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_10mH_angle_90: bypass-transition energy residual below 1% | PASS | 0.002846662941234344 |
| sensitivity/L_10mH_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.004570747304799561 |
| sensitivity/L_10mH_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.0001887368208497442 |
| sensitivity/L_12mH_angle_90: fresh EMTDC receipt | PASS | None |
| sensitivity/L_12mH_angle_90: source-bound project | PASS | None |
| sensitivity/L_12mH_angle_90: complete native output hashes | PASS | None |
| sensitivity/L_12mH_angle_90: unchanged specified source equivalents | PASS | None |
| sensitivity/L_12mH_angle_90: both source phase settings match case label | PASS | None |
| sensitivity/L_12mH_angle_90: network KCL < 1 A | PASS | 4.2874648276125527e-11 |
| sensitivity/L_12mH_angle_90: internal KCL < 1 A | PASS | 2.8130698514185116e-06 |
| sensitivity/L_12mH_angle_90: capacitor within assumed 15 kV peak operating envelope | PASS | 2.1214778952785 |
| sensitivity/L_12mH_angle_90: bypass before feeder opening | PASS | None |
| sensitivity/L_12mH_angle_90: no energy lockout | PASS | None |
| sensitivity/L_12mH_angle_90: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_12mH_angle_90: bypass-transition energy residual below 1% | PASS | 0.0027303915981828817 |
| sensitivity/L_12mH_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.003229532206461272 |
| sensitivity/L_12mH_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.00018704944900749254 |
| sensitivity/L_15.9mH_angle_90: fresh EMTDC receipt | PASS | None |
| sensitivity/L_15.9mH_angle_90: source-bound project | PASS | None |
| sensitivity/L_15.9mH_angle_90: complete native output hashes | PASS | None |
| sensitivity/L_15.9mH_angle_90: unchanged specified source equivalents | PASS | None |
| sensitivity/L_15.9mH_angle_90: both source phase settings match case label | PASS | None |
| sensitivity/L_15.9mH_angle_90: network KCL < 1 A | PASS | 1.9784751614793095e-10 |
| sensitivity/L_15.9mH_angle_90: internal KCL < 1 A | PASS | 4.016419729937191e-06 |
| sensitivity/L_15.9mH_angle_90: capacitor within assumed 15 kV peak operating envelope | PASS | 1.8612727497482 |
| sensitivity/L_15.9mH_angle_90: bypass before feeder opening | PASS | None |
| sensitivity/L_15.9mH_angle_90: no energy lockout | PASS | None |
| sensitivity/L_15.9mH_angle_90: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_15.9mH_angle_90: bypass-transition energy residual below 1% | PASS | 0.004211923948553015 |
| sensitivity/L_15.9mH_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.001771048902821093 |
| sensitivity/L_15.9mH_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.00017523507912509118 |
| sensitivity/L_20mH_angle_90: fresh EMTDC receipt | PASS | None |
| sensitivity/L_20mH_angle_90: source-bound project | PASS | None |
| sensitivity/L_20mH_angle_90: complete native output hashes | PASS | None |
| sensitivity/L_20mH_angle_90: unchanged specified source equivalents | PASS | None |
| sensitivity/L_20mH_angle_90: both source phase settings match case label | PASS | None |
| sensitivity/L_20mH_angle_90: network KCL < 1 A | PASS | 1.3842144097608866e-10 |
| sensitivity/L_20mH_angle_90: internal KCL < 1 A | PASS | 6.130941621615147e-06 |
| sensitivity/L_20mH_angle_90: capacitor within assumed 15 kV peak operating envelope | PASS | 2.4230497121486 |
| sensitivity/L_20mH_angle_90: bypass before feeder opening | PASS | None |
| sensitivity/L_20mH_angle_90: no energy lockout | PASS | None |
| sensitivity/L_20mH_angle_90: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_20mH_angle_90: bypass-transition energy residual below 1% | PASS | 0.004505966604002647 |
| sensitivity/L_20mH_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.0010222437449414201 |
| sensitivity/L_20mH_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.00018091762209460072 |
| sensitivity/L_25mH_angle_90: fresh EMTDC receipt | PASS | None |
| sensitivity/L_25mH_angle_90: source-bound project | PASS | None |
| sensitivity/L_25mH_angle_90: complete native output hashes | PASS | None |
| sensitivity/L_25mH_angle_90: unchanged specified source equivalents | PASS | None |
| sensitivity/L_25mH_angle_90: both source phase settings match case label | PASS | None |
| sensitivity/L_25mH_angle_90: network KCL < 1 A | PASS | 1.0320372334504668e-10 |
| sensitivity/L_25mH_angle_90: internal KCL < 1 A | PASS | 9.173216252342864e-06 |
| sensitivity/L_25mH_angle_90: capacitor within assumed 15 kV peak operating envelope | PASS | 3.2061465396503 |
| sensitivity/L_25mH_angle_90: bypass before feeder opening | PASS | None |
| sensitivity/L_25mH_angle_90: no energy lockout | PASS | None |
| sensitivity/L_25mH_angle_90: thyristors blocked during normal operation | PASS | None |
| sensitivity/L_25mH_angle_90: bypass-transition energy residual below 1% | PASS | 0.006896546994411273 |
| sensitivity/L_25mH_angle_90: source1 phasor within 2% of circuit reference | PASS | 0.0006367034623089296 |
| sensitivity/L_25mH_angle_90: source2 phasor within 2% of circuit reference | PASS | 0.00018386816931226235 |
| convergence/without_sccl_5us: fresh EMTDC receipt | PASS | None |
| convergence/without_sccl_5us: source-bound project | PASS | None |
| convergence/without_sccl_5us: complete native output hashes | PASS | None |
| convergence/without_sccl_5us: unchanged specified source equivalents | PASS | None |
| convergence/without_sccl_5us: both source phase settings match case label | PASS | None |
| convergence/without_sccl_5us: network KCL < 1 A | PASS | 1.3529899423048164e-11 |
| convergence/without_sccl_5us: source1 phasor within 2% of circuit reference | PASS | 3.27685525047805e-05 |
| convergence/without_sccl_5us: source2 phasor within 2% of circuit reference | PASS | 3.285542425901511e-05 |
| convergence/with_sccl_5us: fresh EMTDC receipt | PASS | None |
| convergence/with_sccl_5us: source-bound project | PASS | None |
| convergence/with_sccl_5us: complete native output hashes | PASS | None |
| convergence/with_sccl_5us: unchanged specified source equivalents | PASS | None |
| convergence/with_sccl_5us: both source phase settings match case label | PASS | None |
| convergence/with_sccl_5us: network KCL < 1 A | PASS | 1.7043921829440478e-11 |
| convergence/with_sccl_5us: internal KCL < 1 A | PASS | 2.11112555650792e-06 |
| convergence/with_sccl_5us: capacitor within assumed 15 kV peak operating envelope | PASS | 2.1493673373356 |
| convergence/with_sccl_5us: bypass before feeder opening | PASS | None |
| convergence/with_sccl_5us: no energy lockout | PASS | None |
| convergence/with_sccl_5us: thyristors blocked during normal operation | PASS | None |
| convergence/with_sccl_5us: bypass-transition energy residual below 1% | PASS | 0.0014164829082246866 |
| convergence/with_sccl_5us: source1 phasor within 2% of circuit reference | PASS | 0.0018938959365444319 |
| convergence/with_sccl_5us: source2 phasor within 2% of circuit reference | PASS | 6.518898021390385e-05 |
| convergence/recovery_5us: fresh EMTDC receipt | PASS | None |
| convergence/recovery_5us: source-bound project | PASS | None |
| convergence/recovery_5us: complete native output hashes | PASS | None |
| convergence/recovery_5us: unchanged specified source equivalents | PASS | None |
| convergence/recovery_5us: both source phase settings match case label | PASS | None |
| convergence/recovery_5us: network KCL < 1 A | PASS | 1.7092272042162904e-11 |
| convergence/recovery_5us: internal KCL < 1 A | PASS | 2.11112555650792e-06 |
| convergence/recovery_5us: capacitor within assumed 15 kV peak operating envelope | PASS | 2.4833171812568 |
| convergence/recovery_5us: bypass before feeder opening | PASS | None |
| convergence/recovery_5us: no energy lockout | PASS | None |
| convergence/recovery_5us: thyristors blocked during normal operation | PASS | None |
| convergence/recovery_5us: bypass-transition energy residual below 1% | PASS | 0.0014164829082246866 |
| fixed_C/L_10mH_C_442p5uF: fresh EMTDC receipt | PASS | None |
| fixed_C/L_10mH_C_442p5uF: source-bound project | PASS | None |
| fixed_C/L_10mH_C_442p5uF: complete native output hashes | PASS | None |
| fixed_C/L_10mH_C_442p5uF: unchanged specified source equivalents | PASS | None |
| fixed_C/L_10mH_C_442p5uF: both source phase settings match case label | PASS | None |
| fixed_C/L_10mH_C_442p5uF: network KCL < 1 A | PASS | 2.0558144075977225e-10 |
| fixed_C/L_10mH_C_442p5uF: internal KCL < 1 A | PASS | 8.58917833059001e-06 |
| fixed_C/L_10mH_C_442p5uF: capacitor within assumed 15 kV peak operating envelope | PASS | 4.3818136002663 |
| fixed_C/L_10mH_C_442p5uF: bypass before feeder opening | PASS | None |
| fixed_C/L_10mH_C_442p5uF: no energy lockout | PASS | None |
| fixed_C/L_10mH_C_442p5uF: thyristors blocked during normal operation | PASS | None |
| fixed_C/L_10mH_C_442p5uF: bypass-transition energy residual below 1% | PASS | 0.0034930012203720933 |
| fixed_C/L_10mH_C_442p5uF: source1 phasor within 2% of circuit reference | PASS | 0.002300468901639263 |
| fixed_C/L_10mH_C_442p5uF: source2 phasor within 2% of circuit reference | PASS | 0.00018573574239733048 |
| fixed_C/L_25mH_C_442p5uF: fresh EMTDC receipt | PASS | None |
| fixed_C/L_25mH_C_442p5uF: source-bound project | PASS | None |
| fixed_C/L_25mH_C_442p5uF: complete native output hashes | PASS | None |
| fixed_C/L_25mH_C_442p5uF: unchanged specified source equivalents | PASS | None |
| fixed_C/L_25mH_C_442p5uF: both source phase settings match case label | PASS | None |
| fixed_C/L_25mH_C_442p5uF: network KCL < 1 A | PASS | 2.014042266296201e-10 |
| fixed_C/L_25mH_C_442p5uF: internal KCL < 1 A | PASS | 4.638704237840432e-06 |
| fixed_C/L_25mH_C_442p5uF: capacitor within assumed 15 kV peak operating envelope | PASS | 2.1491580237203 |
| fixed_C/L_25mH_C_442p5uF: bypass before feeder opening | PASS | None |
| fixed_C/L_25mH_C_442p5uF: no energy lockout | PASS | None |
| fixed_C/L_25mH_C_442p5uF: thyristors blocked during normal operation | PASS | None |
| fixed_C/L_25mH_C_442p5uF: bypass-transition energy residual below 1% | PASS | 0.0025434055375874657 |
| fixed_C/L_25mH_C_442p5uF: source1 phasor within 2% of circuit reference | PASS | 0.0011647071253673147 |
| fixed_C/L_25mH_C_442p5uF: source2 phasor within 2% of circuit reference | PASS | 0.00017559195953920081 |
| without_sccl: RMS within 5% of requested target | PASS | None |
| with_sccl: RMS within 5% of requested target | PASS | None |
| recovery: naturally conducting after gate removal | PASS | 161.54000000000002 |
| recovery: native SCR turn-off before recovery-ready | PASS | 0.81890929728319 |
| recovery: all six native SCRs remain off after reclosure | PASS | None |
| recovery: ready before reclosure | PASS | None |
| recovery: reclosure at 1.20 s | PASS | None |
| recovery: source1 normal transfer restored within 5% | PASS | None |
| without_sccl: 10/5 us source1_rms_kA change < 2% | PASS | 8.836501932396601e-05 |
| without_sccl: 10/5 us source2_rms_kA change < 2% | PASS | 8.837079732426645e-05 |
| without_sccl: 10/5 us fault_rms_kA change < 2% | PASS | 8.836756200114593e-05 |
| without_sccl: 10/5 us fault_peak_kA change < 2% | PASS | 0.00013023451970184396 |
| with_sccl: 10/5 us source1_rms_kA change < 2% | PASS | 0.00010810072128553116 |
| with_sccl: 10/5 us source2_rms_kA change < 2% | PASS | 9.963019387271288e-05 |
| with_sccl: 10/5 us fault_rms_kA change < 2% | PASS | 0.00010127619070043892 |
| with_sccl: 10/5 us fault_peak_kA change < 2% | PASS | 0.0003621399969011563 |
| with_sccl: 10/5 us capacitor_peak_kV change < 2% | PASS | 1.2533151432549516 |
| with_sccl: 10/5 us valve_branch_peak_kA change < 2% | PASS | 0.005413994944447609 |
| recovery: 10/5 us source1_rms_kA change < 2% | PASS | 0.0001210512150739973 |
| recovery: 10/5 us source2_rms_kA change < 2% | PASS | 0.00011333605487440224 |
| recovery: 10/5 us fault_rms_kA change < 2% | PASS | 0.00011484495110458681 |
| recovery: 10/5 us fault_peak_kA change < 2% | PASS | 0.0003621399969011563 |
| recovery: 10/5 us capacitor_peak_kV change < 2% | PASS | 0.0002340539238199213 |
| recovery: 10/5 us valve_branch_peak_kA change < 2% | PASS | 0.005413994944447609 |

## Accepted source-bound runs

| Case / variant | Result folder |
| --- | --- |
| with_sccl | [results/with_sccl/20261103T135835_358941Z](results/with_sccl/20261103T135835_358941Z) |
| recovery | [results/recovery/20261103T135929_154935Z](results/recovery/20261103T135929_154935Z) |
| without_sccl | [results/without_sccl/20261103T135757_805522Z](results/without_sccl/20261103T135757_805522Z) |
| sensitivity/L_10mH_angle_0 | [results/sensitivity/L_10mH_angle_0/20261103T132959_161724Z](results/sensitivity/L_10mH_angle_0/20261103T132959_161724Z) |
| sensitivity/L_12mH_angle_0 | [results/sensitivity/L_12mH_angle_0/20261103T133054_110909Z](results/sensitivity/L_12mH_angle_0/20261103T133054_110909Z) |
| sensitivity/L_20mH_angle_0 | [results/sensitivity/L_20mH_angle_0/20261103T133152_158021Z](results/sensitivity/L_20mH_angle_0/20261103T133152_158021Z) |
| sensitivity/L_25mH_angle_0 | [results/sensitivity/L_25mH_angle_0/20261103T133256_638910Z](results/sensitivity/L_25mH_angle_0/20261103T133256_638910Z) |
| baseline_angle_45 | [results/baseline_angle_45/20261103T133348_309105Z](results/baseline_angle_45/20261103T133348_309105Z) |
| sensitivity/L_10mH_angle_45 | [results/sensitivity/L_10mH_angle_45/20261103T133424_926356Z](results/sensitivity/L_10mH_angle_45/20261103T133424_926356Z) |
| sensitivity/L_12mH_angle_45 | [results/sensitivity/L_12mH_angle_45/20261103T133519_025577Z](results/sensitivity/L_12mH_angle_45/20261103T133519_025577Z) |
| sensitivity/L_15.9mH_angle_45 | [results/sensitivity/L_15.9mH_angle_45/20261103T133614_112633Z](results/sensitivity/L_15.9mH_angle_45/20261103T133614_112633Z) |
| sensitivity/L_20mH_angle_45 | [results/sensitivity/L_20mH_angle_45/20261103T133702_167649Z](results/sensitivity/L_20mH_angle_45/20261103T133702_167649Z) |
| sensitivity/L_25mH_angle_45 | [results/sensitivity/L_25mH_angle_45/20261103T133804_887977Z](results/sensitivity/L_25mH_angle_45/20261103T133804_887977Z) |
| baseline_angle_90 | [results/baseline_angle_90/20261103T133856_886606Z](results/baseline_angle_90/20261103T133856_886606Z) |
| sensitivity/L_10mH_angle_90 | [results/sensitivity/L_10mH_angle_90/20261103T133931_817343Z](results/sensitivity/L_10mH_angle_90/20261103T133931_817343Z) |
| sensitivity/L_12mH_angle_90 | [results/sensitivity/L_12mH_angle_90/20261103T134018_669847Z](results/sensitivity/L_12mH_angle_90/20261103T134018_669847Z) |
| sensitivity/L_15.9mH_angle_90 | [results/sensitivity/L_15.9mH_angle_90/20261103T134103_086360Z](results/sensitivity/L_15.9mH_angle_90/20261103T134103_086360Z) |
| sensitivity/L_20mH_angle_90 | [results/sensitivity/L_20mH_angle_90/20261103T134149_039462Z](results/sensitivity/L_20mH_angle_90/20261103T134149_039462Z) |
| sensitivity/L_25mH_angle_90 | [results/sensitivity/L_25mH_angle_90/20261103T134239_834852Z](results/sensitivity/L_25mH_angle_90/20261103T134239_834852Z) |
| convergence/without_sccl_5us | [results/convergence/without_sccl_5us/20261103T134324_077219Z](results/convergence/without_sccl_5us/20261103T134324_077219Z) |
| convergence/with_sccl_5us | [results/convergence/with_sccl_5us/20261103T134413_473351Z](results/convergence/with_sccl_5us/20261103T134413_473351Z) |
| convergence/recovery_5us | [results/convergence/recovery_5us/20261103T134521_376870Z](results/convergence/recovery_5us/20261103T134521_376870Z) |
| fixed_C/L_10mH_C_442p5uF | [results/fixed_C/L_10mH_C_442p5uF/20261103T134632_051561Z](results/fixed_C/L_10mH_C_442p5uF/20261103T134632_051561Z) |
| fixed_C/L_25mH_C_442p5uF | [results/fixed_C/L_25mH_C_442p5uF/20261103T134719_607764Z](results/fixed_C/L_25mH_C_442p5uF/20261103T134719_607764Z) |

See `results/package_verification.json`, `results/reopen_verification.json` and `results/portability_receipt.json` for delivery-level checks, when present. These are separate from numerical model checks. Historical diagnostic runs remain on disk but are not selected as accepted results.
