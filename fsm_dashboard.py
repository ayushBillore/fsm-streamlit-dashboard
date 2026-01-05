import os
import shutil
import streamlit as st

# Backend imports
from Project_CDA_Tool import (
    derive_equations,
    draw_boolean,
    generate_verilog,
    generate_testbench
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FSM Gate-Level Synthesis Tool",
    layout="wide"
)

st.title("🧠 FSM Gate-Level Synthesis Dashboard")
st.caption("Generate flip-flop equations, gate-level diagrams, and Verilog automatically")

# ---------------- SIDEBAR INPUTS ----------------
st.sidebar.header("🔧 FSM Inputs")

seq_input = st.sidebar.text_input(
    "State Sequence (space separated)",
    value="0 1 3 2"
)

ff_type = st.sidebar.selectbox(
    "Flip-Flop Type",
    ["D", "T", "JK", "SR"]
)

generate = st.sidebar.button("▶ Generate Logic")

# ---------------- MAIN LOGIC ----------------
if generate:
    # 🔥 CLEAR STREAMLIT MEMORY (important)
    st.session_state.clear()

    try:
        sequence = [int(x) for x in seq_input.split()]
    except ValueError:
        st.error("Please enter valid integers separated by spaces.")
        st.stop()

    # 🔥 CLEAN OUTPUT FOLDER EVERY RUN
    out_folder = "output"
    if os.path.exists(out_folder):
        shutil.rmtree(out_folder)
    os.makedirs(out_folder)

    # ---------------- DERIVE EQUATIONS ----------------
    result = derive_equations(sequence, ff_type)
    equations = result["eqs"]
    bits = result["bits"]

    # ---------------- SUMMARY ----------------
    st.subheader("📌 Design Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Number of States", len(sequence))
    c2.metric("Flip-Flops Used", bits)
    c3.metric("Flip-Flop Type", ff_type)

    # ---------------- EQUATIONS ----------------
    st.subheader("🧮 Flip-Flop Excitation Equations")
    for name, expr in equations.items():
        st.code(f"{name} = {expr}", language="text")

    # ---------------- GATE-LEVEL DIAGRAMS ----------------
    st.subheader("🧩 Final Gate-Level Diagrams")

    # Generate diagrams (ONLY current run)
    generated_images = []
    for name, expr in equations.items():
        img_path = os.path.join(out_folder, f"{name}.png")
        draw_boolean(expr, name, img_path)
        generated_images.append(img_path)

    if generated_images:
        for img in generated_images:
            st.image(
                img,
                caption=f"Gate-Level Diagram for {os.path.basename(img).replace('.png','')}",
                use_container_width=True
            )
    else:
        st.warning("No gate-level diagrams generated.")

    # ---------------- VERILOG CODE ----------------
    st.subheader("💻 Generated Verilog Module")
    verilog_code = generate_verilog(
        ff_type,
        list(equations.values()),
        bits,
        out_folder
    )
    st.code(verilog_code, language="verilog")

    # ---------------- TESTBENCH ----------------
    st.subheader("🧪 Generated Testbench")
    tb_code = generate_testbench(bits, out_folder)
    st.code(tb_code, language="verilog")

    # ---------------- DOWNLOAD SECTION ----------------
    st.subheader("⬇ Download Generated Files")

    for file in os.listdir(out_folder):
        file_path = os.path.join(out_folder, file)
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download {file}",
                data=f,
                file_name=file
            )

    # ---------------- HELP ----------------
    with st.expander("ℹ What This Tool Does"):
        st.markdown("""
        • Accepts FSM state sequence  
        • Automatically derives flip-flop excitation equations  
        • Synthesizes final gate-level logic  
        • Generates Verilog + testbench  
        • Displays **only current-run hardware realization**
        """)

else:
    st.info("👈 Enter FSM inputs and click **Generate Logic**")
