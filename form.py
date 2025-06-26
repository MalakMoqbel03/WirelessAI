"""
AI‑Network‑App — unified app.py
───────────────────────────────
• http://localhost:5050/        → index.html
• /wireless  → wireless()       — Wireless chain calculator
• /ofdm      → ofdm()           — OFDM RB calculator
• /link      → link()           — Link‑budget calculator
• /cellular  → cellular()       — Cellular sizing tool

The file now holds **one** Flask app instance and **one** authoritative forms
section to avoid field mismatches.
"""

import math
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import InputRequired, NumberRange

# ────────────────────────────────────────────────
# Flask app
# ────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-with-strong-key"

# ────────────────────────────────────────────────
# Unit menus (shared by all forms)
# ────────────────────────────────────────────────
UNIT_DB         = [("dB", "dB")]
UNIT_DBM        = [("dBm", "dBm")]
UNIT_W          = [("W", "W")]
UNIT_DATA       = [("kbps", "kbps")]
UNIT_LOSS_GAIN  = [("dB", "dB"), ("dBm", "dBm"), ("W", "W")]

# ────────────────────────────────────────────────
# Forms
# ────────────────────────────────────────────────
class WirelessSystemForm(FlaskForm):
    # front-end
    lpf_bw      = FloatField("LPF Bandwidth (Hz)",
                             validators=[InputRequired(), NumberRange(min=1)])
    quant_bits  = FloatField("Quantiser Bits / Sample",
                             validators=[InputRequired(), NumberRange(min=1)])

    # coding
    source_rate  = FloatField("Source-coding Rate Rₛ (<1)",
                              validators=[InputRequired(), NumberRange(min=0)])
    channel_rate = FloatField("Channel-code Rate R_c (<1)",
                              validators=[InputRequired(), NumberRange(min=0)])

    # burst formatter inputs
    burst_O = FloatField("Burst Overhead Bits (O)",
                         validators=[InputRequired(), NumberRange(min=0)])
    burst_D = FloatField("Payload Bits per Burst (D)",
                         validators=[InputRequired(), NumberRange(min=1)])

    # modulation
    modulation = SelectField(
        "Modulation",
        choices=[(1,"BPSK"),(2,"QPSK"),(3,"8-PSK"),
                 (4,"16-QAM"),(6,"64-QAM"),(8,"256-QAM")],
        coerce=int)
    
    submit = SubmitField("Calculate")




class OFDMForm(FlaskForm):
    bw_rb       = FloatField("RB BW", validators=[InputRequired()])
    bw_unit     = SelectField("", choices=[("k","kHz"),("m","MHz")])
    spacing     = FloatField("Δf", validators=[InputRequired()])
    spacing_unit= SelectField("", choices=[("k","kHz"),("h","Hz")])
    n_symbols   = FloatField("# OFDM sym", validators=[InputRequired()])
    rb_duration = FloatField("RB dur.", validators=[InputRequired()])
    dur_unit    = SelectField("", choices=[("ms","ms"),("us","µs")])
    k_bits      = FloatField("Bits / RE", validators=[InputRequired()])
    n_parallel  = FloatField("# parallel RBs", validators=[InputRequired()])
    submit      = SubmitField("Calculate")

class LinkBudgetForm(FlaskForm):
    # QoS / noise
    data_rate    = FloatField("Data‑rate", validators=[InputRequired()])
    dr_unit      = SelectField("", choices=UNIT_DATA, default="kbps")

    ebno         = FloatField("Eb/N₀", validators=[InputRequired()])
    ebno_unit    = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    link_margin  = FloatField("Link margin", validators=[InputRequired()])
    lm_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    noise_figure = FloatField("Noise figure (dB)", validators=[InputRequired()])
    nf_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    noise_temp   = FloatField("Noise temperature (K)", validators=[InputRequired()])

    # Gains
    gt           = FloatField("Tx antenna gain", validators=[InputRequired()])
    gt_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    gr           = FloatField("Rx antenna gain", validators=[InputRequired()])
    gr_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    tx_amp_gain  = FloatField("Tx amplifier gain", default=0)
    tx_amp_unit  = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    ar_gain      = FloatField("Rx amplifier gain", default=0)
    ar_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    # Losses / margins
    fade_margin  = FloatField("Fade margin", default=0)
    fm_unit      = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    path_loss    = FloatField("Path loss", validators=[InputRequired()])
    path_unit    = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    feed_loss    = FloatField("Feed‑line loss", default=0)
    feed_unit    = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    other_loss   = FloatField("Other losses", default=0)
    other_unit   = SelectField("", choices=UNIT_LOSS_GAIN, default="dB")

    submit       = SubmitField("Calculate")

# Shared unit menus (keep in one place)
"""
forms.py – all WTForms used by the project
"""

from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange
# --- Cellular system design --------------------------------------------------
UNIT_TIME  = [("min", "Minutes"), ("sec", "Seconds")]
UNIT_DIST  = [("m", "Metres"),   ("km", "Kilometres")]
UNIT_POW   = [("dB", "dB"), ("dBm", "dBm"), ("W", "W")]
UNIT_SIR   = [("dB", "dB"), ("lin", "Ratio")]
# forms.py  –  only the CellularForm part shown
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange

UNIT_TIME   = [("min", "Minutes"), ("sec", "Seconds")]
UNIT_DIST   = [("m", "Metres"),   ("km", "Kilometres")]
UNIT_POWER  = [("dB", "dB"), ("dBm", "dBm"), ("W", "W")]
UNIT_SIR    = [("dB", "dB"), ("lin", "Ratio")]

class CellularForm(FlaskForm):
    # --- area & traffic inputs ---
    total_area    = FloatField("Total Area (km²)",
                               validators=[InputRequired(), NumberRange(min=0.001)])
    users         = FloatField("Number of Users",
                               validators=[InputRequired(), NumberRange(min=1)])
    calls_day     = FloatField("Calls / User / Day",
                               validators=[InputRequired(), NumberRange(min=0)])
    call_len      = FloatField("Avg Call Length",
                               validators=[InputRequired(), NumberRange(min=0)])
    call_len_unit = SelectField("", choices=UNIT_TIME, default="min")

    # --- radio / link inputs ---
    n_exp         = FloatField("Path-loss Exponent  n",
                               validators=[InputRequired(), NumberRange(min=1)], default=3)
    rx_sens       = FloatField("Receiver Sensitivity  Pᵣ(d)",
                               validators=[InputRequired()])
    rx_unit       = SelectField("", choices=UNIT_POWER, default="W")

    sir_min       = FloatField("Min S/I (target)",
                               validators=[InputRequired(), NumberRange(min=0)])
    sir_unit      = SelectField("", choices=UNIT_SIR, default="dB")

    p0_d0         = FloatField("Reference Power  P₀(d₀)",
                               validators=[InputRequired()])
    p0_unit       = SelectField("", choices=UNIT_POWER, default="dB")
    d0_ref        = FloatField("Reference Distance  d₀",
                               validators=[InputRequired(), NumberRange(min=0.001)])
    d0_unit       = SelectField("", choices=UNIT_DIST, default="m")

    i0            = FloatField("# Co-channel Interferers  i₀",
                               validators=[InputRequired(), NumberRange(min=1)], default=6)

    gos           = FloatField("Call-dropping Probability  P_B",
                               validators=[InputRequired(), NumberRange(min=0, max=1)],
                               default=0.02)

    slots_carrier = FloatField("Time-slots per Carrier",
                               validators=[InputRequired(), NumberRange(min=1)], default=8)

    submit        = SubmitField("Calculate")
