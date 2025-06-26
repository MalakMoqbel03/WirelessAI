"""
AI‑Network‑App — Flask entry‑point
──────────────────────────────────
URL map
 • http://localhost:5000/           → index.html  (Home)
 • /wireless                        → wireless  (Wireless chain calculator)
 • /ofdm                            → ofdm      (OFDM RB calculator)
 • /link                            → link       (Link‑budget calculator)
 • /cellular                        → cellular  (Cellular system sizing)
"""
from ai_helper import explain          # NEW

import math
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import InputRequired

import math
from flask import Flask, render_template
from form import (
    WirelessSystemForm,
    OFDMForm,
    LinkBudgetForm,
    CellularForm,
)

# ──────────────────────────────────────────────────────────────
# App factory (single global instance)
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "replace‑with‑strong‑key"

# ──────────────────────────────────────────────────────────────
# Helper conversions
# ──────────────────────────────────────────────────────────────

def any_to_dB(value: float, unit: str, kind: str = "gain") -> float:
    """Return *plain dB* from a value given in dB, dBm or Watts."""
    unit = unit.lower()
    if unit in ("db", "dbi"):
        return value
    if unit == "dbm":
        return value if kind == "gain" else value
    if unit == "w":
        p_dbm = 10 * math.log10(value * 1e3)
        return p_dbm if kind == "power" else 10 * math.log10(value)
    return 10 * math.log10(value)

def db_to_w(p_db: float) -> float:
    return 10 ** (p_db / 10)

def w_to_db(p_w: float) -> float:
    return 10 * math.log10(p_w)

# Boltzmann constant (dBW/Hz/K)
K_dB_Hz = -228.6
# ────────────────────────────────────────────────
# Helper maths
# ────────────────────────────────────────────────
K_dB_Hz = -228.6  # Boltzmann (dBW/Hz/K)

def db_to_w(p_db: float) -> float:
    return 10 ** (p_db / 10)

# ────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/wireless", methods=["GET", "POST"])
def wireless():
    form = WirelessSystemForm()
    results = {}

    if form.validate_on_submit():
        # ── user inputs ──────────────────────────────────────────
        BW_hz   = form.lpf_bw.data              # LPF bandwidth
        fs      = 2 * BW_hz                     # Nyquist sampler
        n_bits  = form.quant_bits.data          # bits / sample

        R_s     = form.source_rate.data         # source-coding rate
        R_c     = form.channel_rate.data        # channel-coding rate

        O_bits  = form.burst_O.data             # burst overhead bits
        D_bits  = form.burst_D.data             # burst payload bits
        k_burst = O_bits / D_bits               # overhead fraction

        k_sym   = form.modulation.data          # bits / symbol

        # ── rate chain ───────────────────────────────────────────
        R_quant = fs * n_bits
        R_src   = R_quant * R_s
        R_chan  = R_src / R_c
        R_intl  = R_chan                        # no interleaver cost
        R_burst = R_intl * (1 + k_burst)
        sym_rate = R_burst / k_sym

        scheme = {
            1: "BPSK", 2: "QPSK", 3: "8-PSK",
            4: "16-QAM", 6: "64-QAM", 8: "256-QAM"
        }[k_sym]

        results = {
            "fs":          f"{fs:,.0f} Sa/s",
            "quant":       f"{R_quant:,.0f} bps",
            "src":         f"{R_src:,.0f} bps",
            "chan":        f"{R_chan:,.0f} bps",
            "intl":        f"{R_intl:,.0f} bps",
            "k_burst":     f"{k_burst:.3f}",
            "burst":       f"{R_burst:,.0f} bps",
            "sym":         f"{sym_rate:,.1f} sym/s",
            "explanation":
                f"fs = 2×BW = {fs/1e3:.1f} kSa/s. "
                f"{n_bits}-bit quantiser ⇒ {R_quant/1e3:.1f} kbps. "
                f"Source coding Rₛ={R_s} → {R_src/1e3:.1f} kbps; "
                f"channel coding R_c={R_c} → {R_chan/1e3:.1f} kbps. "
                f"O={O_bits}, D={D_bits} → overhead {k_burst:.3f}; "
                f"burst rate {R_burst/1e3:.1f} kbps. "
                
        }
        inputs  = {
            "Signal BW":       f"{BW_hz/1e3:.0f} kHz",
            "Quant bits":      form.quant_bits.data,
            "Rₛ":              form.source_rate.data,
            "R_c":             form.channel_rate.data,
            "Burst O":         form.burst_O.data,
            "Burst D":         form.burst_D.data,
            "Mod bits/sym":    form.modulation.data,
        }

        # ---------- AI story ----------
        results["explanation"] = explain("wireless", inputs, results)

       
    return render_template("wireless.html", form=form, results=results)
@app.route("/ofdm", methods=["GET", "POST"])
def ofdm():
    form = OFDMForm()
    results = {}
    if form.validate_on_submit():
        bw_rb = form.bw_rb.data * (1e3 if form.bw_unit.data == "k" else 1e6)
        df = form.spacing.data * (1e3 if form.spacing_unit.data == "k" else 1)
        ts = form.rb_duration.data * (1e-3 if form.dur_unit.data == "ms" else 1e-6)
        n_sub = bw_rb / df
        bits_sym = form.k_bits.data * n_sub
        bits_rb = bits_sym * form.n_symbols.data
        rb_rate = bits_rb / ts
        peak = rb_rate * form.n_parallel.data
        results = dict(bits_RE=f"{form.k_bits.data:.0f}", bits_symbol=f"{bits_sym:.0f}", bits_RB=f"{bits_rb:,.0f}", thrpt_RB=f"{rb_rate:,.0f} bps", peak_rate=f"{peak:,.0f} bps")
        results = {
        "bits_RE":   f"{form.k_bits.data:.0f}",
        "bits_symbol": f"{bits_sym:.0f}",
        "bits_RB":     f"{bits_rb:,.0f}",
        "thrpt_RB":    f"{rb_rate:,.0f} bps",
        "peak_rate":   f"{peak:,.0f} bps"
    }

        # ---------- NEW: human-readable inputs ----------
        inputs = {
            "RB bandwidth":          f"{form.bw_rb.data} {'kHz' if form.bw_unit.data=='k' else 'MHz'}",
            "Δf spacing":            f"{form.spacing.data} {'kHz' if form.spacing_unit.data=='k' else 'Hz'}",
            "# OFDM symbols / RB":   form.n_symbols.data,
            "RB duration":           f"{form.rb_duration.data} {form.dur_unit.data}",
            "Bits per RE (k)":       form.k_bits.data,
            "Parallel RBs":          form.n_parallel.data
        }

        # ---------- AI story ----------
        results["explanation"] = explain("OFDM", inputs, results)   

    return render_template("ofdm.html", form=form, results=results)

@app.route("/link", methods=["GET", "POST"])
def link():
    form = LinkBudgetForm()
    results = {}
    if form.validate_on_submit():
        r_bps = form.data_rate.data * 1e3
        pr_db = (form.link_margin.data + K_dB_Hz + 10*math.log10(form.noise_temp.data) + form.noise_figure.data + 10*math.log10(r_bps) + form.ebno.data)
        pt_db = (pr_db + form.path_loss.data + form.feed_loss.data + form.other_loss.data + form.fade_margin.data - form.gt.data - form.gr.data - form.tx_amp_gain.data - form.ar_gain.data)
        results = dict(pr_dBW=f"{pr_db:,.2f} dB", pr_W=f"{db_to_w(pr_db):.6f} W", pt_dBW=f"{pt_db:,.2f} dB", pt_W=f"{db_to_w(pt_db):.6f} W")
        
        
        # … previous calculations …

        results = {
            "P_rx (dBW)": f"{pr_db:,.2f}",
            "P_rx (W)":   f"{db_to_w(pr_db):.6f}",
            "P_tx (dBW)": f"{pt_db:,.2f}",
            "P_tx (W)":   f"{db_to_w(pt_db):.6f}"
        }

        # ---------- NEW inputs ----------
        inputs = {
            "Data-rate":          f"{form.data_rate.data} {form.dr_unit.data}",
            "Eb/N0":              f"{form.ebno.data} {form.ebno_unit.data}",
            "Link margin":        f"{form.link_margin.data} {form.lm_unit.data}",
            "Noise figure":       f"{form.noise_figure.data} dB",
            "Noise temperature":  f"{form.noise_temp.data} K",
            "Path loss":          f"{form.path_loss.data} dB",
            "Fade margin":        f"{form.fade_margin.data} dB",
            "Feed loss":          f"{form.feed_loss.data} dB",
            "Other losses":       f"{form.other_loss.data} dB",
            "G_t":                f"{form.gt.data} dB",
            "G_r":                f"{form.gr.data} dB",
            "Tx amp gain":        f"{form.tx_amp_gain.data} dB",
            "Rx amp gain":        f"{form.ar_gain.data} dB"
        }

        results["explanation"] = explain("Link Budget", inputs, results)

    return render_template("link_budget.html", form=form, results=results)
# ——— Standard cluster sizes (GSM / LTE reuse) ———










ALLOWED_CLUSTERS = [1,3,4,7,9,12,13,16,19,21,27,28,31,37]

def nearest_cluster(n_raw: float) -> int:
    for n in ALLOWED_CLUSTERS:
        if n >= n_raw - 1e-6:
            return n
    return math.ceil(n_raw)

def to_db(value: float, unit: str) -> float:
    u = unit.lower()
    if u == "db":  return value
    if u == "dbm": return value - 30
    if u == "w":   return 10*math.log10(value)
    return value

def db_to_w(dbw: float) -> float:
    return 10**(dbw/10)

def erlang_B(A: float, C: int) -> float:
    inv_G = 1.0
    for k in range(1, C+1):
        inv_G = 1.0 + inv_G * k / A
    return 1.0 / inv_G

def min_channels(A: float, PB: float, C_max: int = 300) -> int:
    for C in range(1, C_max+1):
        if erlang_B(A, C) <= PB:
            return C
    return C_max

# ───── cellular route ───────────────────────────────────────────
@app.route("/cellular", methods=["GET", "POST"])
def cellular():
    form, results = CellularForm(), {}

    if form.validate_on_submit():
        # 1) traffic
        t_sec  = form.call_len.data * (60 if form.call_len_unit.data == "min" else 1)
        Au     = form.calls_day.data * t_sec / 86400            # Erl / user
        AT     = Au * form.users.data                           # Erl total

        # 2) radio range
        p0_dbw = to_db(form.p0_d0.data, form.p0_unit.data)
        pr_dbw = to_db(form.rx_sens.data, form.rx_unit.data)
        d0_m   = form.d0_ref.data * (1 if form.d0_unit.data == "m" else 1000)
        n_exp  = form.n_exp.data
        d_max  = d0_m * 10 ** ((p0_dbw - pr_dbw) / (10 * n_exp))

        # 3) hex-cell area & cell count
        A_hex  = 3 * math.sqrt(3) / 2 * d_max**2               # m²
        Ncells = math.ceil(form.total_area.data * 1e6 / A_hex)
        A_cell = AT / Ncells                                   # Erl / cell

        # 4) cluster size
        gamma  = (10 ** (form.sir_min.data / 10)
                  if form.sir_unit.data == "dB" else form.sir_min.data)
        Q      = (gamma * form.i0.data) ** (1 / n_exp)
        N_req  = (Q**2) / 3
        N      = nearest_cluster(N_req)

        # 5) channels & carriers
        C_ch   = min_channels(A_cell, form.gos.data)
        carr_cell = math.ceil(C_ch / form.slots_carrier.data)
        carr_sys  = carr_cell * N

        # 6) pack results
        results = {
        "d_max":         f"{d_max:.2f} m",
        "cell_area":     f"{A_hex/1e6:.4f} km²",
        "n_cells":       Ncells,
        "A_user":        f"{Au:.4f} Erl",        #  ← NEW
        "A_total":       f"{AT:.3f} Erl",
        "A_cell":        f"{A_cell:.4f} Erl",
        "N":             N,
        "channels":      C_ch,
        "carriers_cell": carr_cell,
        "carriers_sys":  carr_sys,
    }

        inputs = {
            "Total area":          f"{form.total_area.data} km²",
            "# users":             form.users.data,
            "Calls/day":           form.calls_day.data,
            "Call length":         f"{form.call_len.data} {form.call_len_unit.data}",
            "n (path-loss)":       form.n_exp.data,
            "Rx sens":             f"{form.rx_sens.data} {form.rx_unit.data}",
            "SIR min":             f"{form.sir_min.data} {form.sir_unit.data}",
            "d₀":                  f"{form.d0_ref.data} {form.d0_unit.data}",
            "P₀(d₀)":              f"{form.p0_d0.data} {form.p0_unit.data}",
            "i₀":                  form.i0.data,
            "GoS P_B":             form.gos.data,
            "Slots/carrier":       form.slots_carrier.data,
        }

        results["explanation"] = explain("Cellular", inputs, results)


    return render_template("cellular.html", form=form, results=results)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
