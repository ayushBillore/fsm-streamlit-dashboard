import os
import shutil
import pandas as pd
import streamlit as st

from Project_CDA_Tool import (
    derive_equations,
    draw_boolean,
    generate_verilog,
    generate_testbench
)

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="FSM Synthesis & Visualization Tool",
    layout="wide"
)

# -------------------------------------------------
# STABLE ECE-LAB THEME
# -------------------------------------------------
st.markdown("""
<style>
body { background-color: #eef2f7; }
.section {
    background-color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}
.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e3a8a;
    margin-bottom: 1rem;
}
.label { color: #374151; font-size: 0.9rem; }
.value { font-size: 1.8rem; font-weight: 600; color: #111827; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="section">
  <div class="section-title">🧠 FSM Gate-Level Synthesis Dashboard</div>
  <p style="color:#374151;">
    Design and visualize FSM logic, flip-flop excitation equations,
    gate-level hardware, and auto-generated Verilog.
  </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR INPUTS
# -------------------------------------------------
st.sidebar.header("🔧 FSM Configuration")

seq_input = st.sidebar.text_input(
    "State Sequence (space separated)",
    value="0 1 3 2"
)

ff_type = st.sidebar.selectbox(
    "Flip-Flop Type",
    ["D", "T", "JK", "SR"]
)

generate = st.sidebar.button("▶ Generate FSM")

# -------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------
if generate:
    out_folder = "output"
    if os.path.exists(out_folder):
        shutil.rmtree(out_folder)
    os.makedirs(out_folder)

    try:
        sequence = [int(x) for x in seq_input.split()]
    except ValueError:
        st.error("Invalid state sequence.")
        st.stop()

    result = derive_equations(sequence, ff_type)
    equations = result["eqs"]
    bits = result["bits"]

    # ---------------- DESIGN SUMMARY ----------------
    st.markdown(f"""
    <div class="section">
      <div class="section-title">📌 Design Summary</div>
      <div style="display:flex; justify-content:space-between; text-align:center;">
        <div><div class="label">Number of States</div><div class="value">{len(sequence)}</div></div>
        <div><div class="label">Flip-Flops Used</div><div class="value">{bits}</div></div>
        <div><div class="label">Flip-Flop Type</div><div class="value">{ff_type}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- TRUTH TABLE ----------------
    st.markdown("""
    <div class="section">
      <div class="section-title">📋 Truth Table of Selected Flip-Flop</div>
    </div>
    """, unsafe_allow_html=True)

    if ff_type == "D":
        df = pd.DataFrame({"Q": [0,1], "D": [0,1], "Q(next)": [0,1]})
    elif ff_type == "T":
        df = pd.DataFrame({"Q":[0,0,1,1], "T":[0,1,0,1], "Q(next)":[0,1,1,0]})
    elif ff_type == "JK":
        df = pd.DataFrame({
            "Q":[0,0,0,0,1,1,1,1],
            "J":[0,0,1,1,0,0,1,1],
            "K":[0,1,0,1,0,1,0,1],
            "Q(next)":[0,0,1,1,1,0,1,0]
        })
    else:
        df = pd.DataFrame({
            "Q":[0,0,0,1,1],
            "S":[0,0,1,0,1],
            "R":[0,1,0,0,1],
            "Q(next)":[0,0,1,1,"Invalid"]
        })

    st.dataframe(df, use_container_width=True)

    # ---------------- EQUATIONS ----------------
    st.markdown("<div class='section'><div class='section-title'>🧮 Excitation Equations</div></div>", unsafe_allow_html=True)
    for name, expr in equations.items():
        st.code(f"{name} = {expr}")

    # ---------------- GATE DIAGRAMS ----------------
    st.markdown("<div class='section'><div class='section-title'>🧩 Gate-Level Hardware</div></div>", unsafe_allow_html=True)
    for name, expr in equations.items():
        img_path = os.path.join(out_folder, f"{name}.png")
        draw_boolean(expr, name, img_path)
        st.image(img_path, use_container_width=True)
        st.markdown(f"<p style='text-align:center;color:#111827;'>Gate-Level Diagram for {name}</p>", unsafe_allow_html=True)

    # ---------------- VERILOG & TB ----------------
    st.markdown("<div class='section'><div class='section-title'>💻 Verilog</div></div>", unsafe_allow_html=True)
    st.code(generate_verilog(ff_type, list(equations.values()), bits, out_folder), language="verilog")

    st.markdown("<div class='section'><div class='section-title'>🧪 Testbench</div></div>", unsafe_allow_html=True)
    st.code(generate_testbench(bits, out_folder), language="verilog")

    # ---------------- DOWNLOADS ----------------
    st.markdown("<div class='section'><div class='section-title'>⬇ Download Outputs</div></div>", unsafe_allow_html=True)
    for file in os.listdir(out_folder):
        with open(os.path.join(out_folder, file), "rb") as f:
            st.download_button(f"Download {file}", f, file_name=file)

else:
    st.info("👈 Configure FSM parameters and click **Generate FSM**")
