# TPSC SCCL educational film

Format: 128 seconds, 1920 x 1080, 30 fps, light background. English visible content. Mathematical symbols, measurements and graph axes are rendered with LaTeX. The film is intentionally silent; the timing leaves space for an instructor's explanation.

| Chapter | Video interval | Electrical case | Teaching objective |
|---|---|---|---|
| NetworkOverview | 0-14 s | Topology | Source 1 crosses the SCCL; Source 2 joins at Bus 2. Both sources feed the downstream fault. |
| NormalOperation | 14-32 s | B, 0.45-0.483333 s | Blocked SCRs allow series L-C compensation. The reactor stays connected. |
| FaultTransfer | 32-58 s | B, 0.499-0.516 s | Synchronized reactor, capacitor and bypass currents show the protective current-path transfer. |
| FaultComparison | 58-80 s | A and B | Compare instantaneous phase-A current on identical axes, then 60 Hz symmetrical RMS contributions. |
| Recovery | 80-110 s | Extended C, 0.49-2.5 s | Breaker clearing, gate withdrawal, natural extinction, recovery and healthy feeder reclosure. |
| Sizing | 110-128 s | Five native sensitivity cases | Increasing L reduces fault current; compensating C is a separate design choice. |

## Pilot timing

The 26-second FaultTransfer scene is the pilot. It is rendered and visually reviewed before full production. Its display clock is simulation time, not video time. Slowing is piecewise and explicitly identified on screen.

| Pilot video interval | Simulation interval | Purpose |
|---|---|---|
| 0-2 s | 0.499 s held | Establish compensated path |
| 2-5 s | 0.499-0.500 s | Approach fault inception |
| 5-8 s | 0.500-0.50038 s | Fast detection |
| 8-8.5 s | held | Detection delay caption |
| 8.5-9.5 s | 0.50038-0.50048 s | Gate enabling |
| 9.5-10.5 s | 0.50048-0.50049 s | First sampled conduction |
| 10.5-11 s | held | Response caption |
| 11-13.5 s | 0.50049-0.5015 s | Capacitor discharge and redistribution |
| 13.5-23 s | 0.5015-0.516 s | Reactor-limited current |
| 23-26 s | 0.516 s held | Read synchronized traces |

Current arrows follow measured instantaneous sign and fade below 1 A. They are reference arrows, not representations of electron motion. SCR color follows native TON/TOFF switching timestamps, independently of gate commands. The main reactor is always electrically connected: bypass removes capacitor compensation rather than physically inserting a previously absent inductor.

The nominal fault command is 0.50000 s. The recorded fault switch first closes at 0.50001 s. All fault-state chips use the recorded FS switch states, and displayed detection / first-conduction delays are measured from that electrical closure: 0.37 ms and 0.48 ms respectively. The distinction is one native 10-microsecond step; it does not modify any waveform.

## Recovery observations

All feeder poles have opened at 0.58994 s. The gate command disappears at the sampled time 0.65606 s. The last physical SCR turn-off timestamp is 0.818909297 s; recovery-ready follows near 0.83760 s. Reclose is commanded at 1.20 s; physical poles close on the following integration step. The original 1.5-second run was extended to 2.5 seconds on a new native PSCAD project, preserving the originals. The final current is within 0.1% of its pre-fault value; final sliding-RMS ripple is 0.03834% of the pre-fault reference.
