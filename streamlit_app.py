"""Streamlit demo: process mining of the Mexico vs Germany World Cup match.

Built to be walked through in a 2-hour workshop: each section below is
load -> discover -> visualize, using the same steps as main.py.
The sidebar filters re-run the whole analysis on the selected slice.
"""

import pandas as pd
import pm4py
import streamlit as st
import streamlit.components.v1 as components
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.sna import visualizer as sna_visualizer

CSV_PATH = "events_World_Cup_MEX_GER_with_names.csv"

st.set_page_config(page_title="Football Process Mining", layout="wide")

# --- sidebar filters (drive every section below) ----------------------------

st.sidebar.header("Filters")
team = st.sidebar.selectbox("Team", ["All", "Mexico", "Germany"])
period = st.sidebar.selectbox("Half", ["All", "1H", "2H"])

st.title("What if football were a business process?")
st.caption(
    "Process mining of Mexico vs Germany (2018 World Cup) with pm4py — "
    "every possession is a process case, every action an event. "
    f"Showing: {team} · {period}"
)


# --- data -------------------------------------------------------------------

@st.cache_data
def load_log() -> pd.DataFrame:
    data = pd.read_csv(CSV_PATH)
    return pm4py.format_dataframe(
        data,
        case_id="possession_id",
        activity_key="eventName",
        timestamp_key="time:timestamp",
    )


def filter_log(log: pd.DataFrame, team: str, period: str) -> pd.DataFrame:
    """Slice the log by the sidebar filters."""
    if team != "All":
        log = log[log["teamId"] == team]
    if period != "All":
        log = log[log["matchPeriod"] == period]
    return log


@st.cache_resource
def discover_models(team: str, period: str):
    """Discover every model on the filtered slice (cached per filter combo)."""
    df = filter_log(load_log(), team, period)
    tree = pm4py.discover_process_tree_inductive(df)
    bpmn_model = pm4py.convert_to_bpmn(tree)
    heuristics_net = pm4py.discover_heuristics_net(df)
    net, im, fm = pm4py.discover_petri_net_heuristics(df)
    fitness = pm4py.fitness_token_based_replay(df, net, im, fm)
    return df, tree, bpmn_model, heuristics_net, net, im, fm, fitness


if load_log().pipe(filter_log, team, period).empty:
    st.warning("No events for this filter combination — pick another team or half.")
    st.stop()

df, tree, bpmn_model, heuristics_net, net, im, fm, fitness = discover_models(team, period)


# --- overview ---------------------------------------------------------------

st.header("1. The event log")
c1, c2, c3 = st.columns(3)
c1.metric("Events", len(df))
c2.metric("Possessions (cases)", df["case:concept:name"].nunique())
c3.metric("Teams", df["teamId"].nunique())
st.dataframe(df[["case:concept:name", "concept:name", "org:resource", "teamId"]].head(20))


# --- process discovery ------------------------------------------------------

st.header("2. Process discovery")

st.subheader("Process tree (Inductive Miner)")
st.graphviz_chart(pt_visualizer.apply(tree))

st.subheader("Same model as BPMN")
st.graphviz_chart(bpmn_visualizer.apply(bpmn_model))

st.subheader("Heuristics net")
st.graphviz_chart(hn_visualizer.apply(heuristics_net))

st.subheader("Petri net (Heuristics Miner)")
st.graphviz_chart(pn_visualizer.apply(net, im, fm))


# --- variants ---------------------------------------------------------------

st.header("3. Variants: the most common sequences of play")

sequences = (
    df.sort_values("time:timestamp")
    .groupby("case:concept:name")["concept:name"]
    .apply(tuple)
)
variant_counts = sequences.value_counts()

top_n = st.slider("Show top N variants", 5, 50, 10)
st.dataframe(
    pd.DataFrame(
        {
            "variant": [" → ".join(s) for s in variant_counts.head(top_n).index],
            "count": variant_counts.head(top_n).values,
        }
    )
)

labels = [" → ".join(s) for s in variant_counts.head(top_n).index]
choice_label = st.selectbox("Explore a variant", labels)
choice = variant_counts.head(top_n).index[labels.index(choice_label)]
cases = sequences[sequences == choice]
st.write(f"**{choice_label}** — the sequence of {len(cases)} possessions in this slice.")
st.write("Example possessions:", ", ".join(cases.index[:10]))


# --- conformance ------------------------------------------------------------

st.header("4. Conformance: how much of the log does the model replay?")
c1, c2 = st.columns(2)
c1.metric("Log fitness", f"{fitness['log_fitness']:.2%}")
c2.metric("Perfectly fitting traces", f"{fitness['percentage_of_fitting_traces']:.1f}%")


# --- social network ---------------------------------------------------------

st.header("5. Player interaction: handover-of-work network")
st.caption("Zoom, pan and hover to explore how players exchange the ball.")
hw = pm4py.discover_handover_of_work_network(df)
try:
    sna_html = sna_visualizer.apply(hw, variant=sna_visualizer.Variants.PYVIS)
    with open(sna_html, encoding="utf-8") as f:
        components.html(f.read(), height=600, scrolling=True)
except ImportError:
    sna_img = sna_visualizer.apply(hw, variant=sna_visualizer.Variants.NETWORKX)
    st.image(sna_img)
