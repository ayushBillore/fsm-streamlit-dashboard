import streamlit as st
import pandas as pd
import graphviz
from Project_CDA_Tool import derive_equations, bits_needed_for_sequence

st.set_page_config(page_title="FSM Visualization Tool", layout="wide")

st.title("🔁 FSM Counter Interactive Dashboard")
st.caption("Visualize how FSM logic, flip-flops, and equations work step-by-step")

# ---------------- INPUT PANEL ----------------
st.sidebar.header("🔧 Inputs")

seq_input = st.sidebar.text_input(
    "State Sequence (space separated)",
    value="0 1 3 2",
    help="Example: 0 1 3 2"
)

ff_type = st.sidebar.selectbox(
    "Flip-Flop Type",
    ["D", "T", "JK", "SR"]
)

run_btn = st.sidebar.button("▶ Generate FSM")

# ---------------- PROCESS ----------------
if run_btn:
    sequence = [int(x) for x in seq_input.split()]
    result = derive_equations(sequence, ff_type)

    bits = result["bits"]
    equations = result["eqs"]
    transitions = result["trans"]

    # ---------------- SUMMARY ----------------
    st.subheader("📌 FSM Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("States", len(sequence))
    col2.metric("Flip-Flops Used", bits)
    col3.metric("FF Type", ff_type)

    # ---------------- STATE TRANSITION GRAPH ----------------
    st.subheader("🔀 State Transition Diagram")

    dot = graphviz.Digraph()
    for p, n in transitions.items():
        dot.edge(str(p), str(n))

    st.graphviz_chart(dot)

    # ---------------- TRANSITION TABLE ----------------
    st.subheader("📋 State Transition Table")

    table = []
    for p, n in transitions.items():
        table.append({
            "Present State": format(p, f"0{bits}b"),
            "Next State": format(n, f"0{bits}b")
        })

    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)

    # ---------------- EQUATIONS ----------------
    st.subheader("🧮 Flip-Flop Excitation Equations")

    for k, v in equations.items():
        st.code(f"{k} = {v}", language="text")

    # ---------------- STEP SIMULATION ----------------
    st.subheader("⏱ Step-by-Step FSM Execution")

    step = st.slider(
        "Clock Cycle",
        0,
        len(sequence) - 1,
        0,
        help="Move clock to see FSM state"
    )

    present = sequence[step]
    next_state = transitions[present]

    colA, colB = st.columns(2)
    colA.metric("Present State", format(present, f"0{bits}b"))
    colB.metric("Next State", format(next_state, f"0{bits}b"))

    # ---------------- HELP ----------------
    with st.expander("ℹ How to Read This"):
        st.markdown("""
        • **Binary values** represent flip-flop outputs  
        • **Graph** shows FSM flow  
        • **Equations** are derived automatically  
        • **Slider** simulates clock cycles  
        """)

else:
    st.info("👈 Enter inputs and click **Generate FSM**")
