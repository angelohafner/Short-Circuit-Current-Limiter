SCCL / TPSC EDUCATIONAL CIRCUIT DIAGRAM

This standalone Python artifact draws the accepted PSCAD study using Schemdraw.
It creates one three-panel figure in PNG (300 dpi), vector SVG and vector PDF.
All visible text is in English. No simulation is performed by the diagram script.

CONTENTS

draw_sccl_diagram.py       Editable drawing source.
diagram_inputs.json       Electrical parameters and accepted EMTDC result values.
requirements.txt          Dependency versions used for this delivery.
dependencies/             Official Schemdraw wheel and its URL/SHA-256 provenance.
output/                   The three final figure formats and verification evidence.
verify_diagram.py         Export, parameter-provenance and package verification.

PANELS

A: Three-phase single-line network. Source 1 supplies Bus 2 through the SCCL.
   Source 2 joins Bus 2 without passing through it. Both the R-L load and fault
   are downstream of the common three-pole feeder breaker. Source R-L values
   are per-phase Thevenin equivalents; 138 kV is line-to-line RMS. The switches
   describe the topology and are operated during the simulation sequence.

B: One phase of the SCCL, repeated in A/B/C. The main reactor and its winding
   resistance precede all parallel branches. The capacitor has a series ESR.
   The valve branch has a common discharge-limiting R-L followed by antiparallel
   SCRs. The MOV spans capacitor plus ESR. Each SCR has its own series RC snubber,
   shown in an auxiliary detail. The MOV symbol is a Schemdraw IEC resistor with
   a diagonal voltage-dependent marker; the 15 kV value is the curve reference,
   not a hard clamp voltage. Dashed orange arrows identify gate commands.

C: Simplified dominant current paths. Loss resistances, MOV and snubbers are
   omitted in these two explanatory views; their actual connections are in B.
   Both SCRs are blocked normally. The fault view highlights the forward SCR
   during a positive-current half-cycle. The other SCR conducts on reversal;
   the drawing does not imply simultaneous conduction. A dashed capacitor path
   means small residual current, not a physical disconnection of the capacitor.
   Colors, line styles and arrows provide redundant visual cues.

The four result values are symmetrical RMS values copied from the accepted
PSCAD outputs. They are not instantaneous peaks. Kirchhoff's law in panel A
uses instantaneous currents and includes the feeder load current.

RUN ON THIS WORKSTATION

From this directory, in PowerShell:

    .\.venv\Scripts\python.exe draw_sccl_diagram.py
    .\.venv\Scripts\python.exe verify_diagram.py

The local virtual environment uses the existing workstation's Matplotlib,
NumPy and Pillow packages and an isolated Schemdraw installation.

RUN AFTER EXTRACTING THE PACKAGE

With Python 3.11 and internet access:

    py -3.11 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe draw_sccl_diagram.py

If Matplotlib, NumPy and Pillow are already installed, use the included official
wheel to install Schemdraw without relying on the network:

    py -3.11 -m venv --system-site-packages .venv
    .\.venv\Scripts\python.exe -m pip install --no-index --no-deps dependencies\schemdraw-0.23-py3-none-any.whl
    .\.venv\Scripts\python.exe draw_sccl_diagram.py

The verification script additionally uses Poppler commands: pdfinfo, pdffonts,
pdfimages, pdftotext and pdftoppm. These are not required to create the figure.

EDITING

Edit diagram_inputs.json to change labels or the independently specified L/C
values. A parameter edit changes the diagram only; it does not recalculate the
measured-results box or update the PSCAD model. New simulation cases require
fresh EMTDC results before updating that box. Panel geometry and colors are in
draw_sccl_diagram.py. The script checks the actual start/end anchors of every
two-terminal symbol to catch rotated or disconnected symbol placements.

PROVENANCE AND VERIFICATION

Input provenance records hashes of the accepted parameters, metrics and three
native PSCAD project files. The original models and existing study archives
remain untouched. Full-study provenance checking is performed when those files
are present; a standalone extraction explicitly reports that they are absent.
All three final exports were inspected visually, including a Poppler-rendered
PDF. The PDF contains embedded fonts and no raster images. The SVG contains
editable text and vector circuit paths. Figure and archive payload hashes are
recorded in the verification files.

Official Schemdraw references used for implementation:
https://schemdraw.readthedocs.io/en/stable/classes/drawing.html
https://schemdraw.readthedocs.io/en/stable/usage/start.html

This is an educational representation of the electrical topology, not an
equipment manufacturing drawing or a new validation of equipment ratings.
