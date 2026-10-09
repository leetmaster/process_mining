"""Process-mining exploration over World Cup MEX vs GER event data.

Functional-core / imperative-shell layout:
- pure transform functions own the data flow (no I/O, no view calls, no mutation);
- presentation functions own the side effects (print, pm4py.view_*);
- a thin main() wires the pipeline together.
"""

import pandas as pd
import pm4py
from pm4py.statistics.traces.generic.pandas import case_statistics

CSV_PATH = "events_World_Cup_MEX_GER_with_names.csv"


# --- pure transforms --------------------------------------------------------

def load_log(path: str) -> pd.DataFrame:
    """Read the CSV and format it into a pm4py event log."""
    data = pd.read_csv(path)
    return pm4py.format_dataframe(
        data,
        case_id="possession_id",
        activity_key="eventName",
        timestamp_key="time:timestamp",
    )


def count_events_and_cases(log: pd.DataFrame) -> tuple[int, int]:
    return len(log), len(log["eventId"].unique())


def discover_tree(log: pd.DataFrame):
    return pm4py.discover_process_tree_inductive(log)


def to_bpmn(process_tree):
    return pm4py.convert_to_bpmn(process_tree)


def discover_heuristics_net(log: pd.DataFrame):
    return pm4py.discover_heuristics_net(log)


def get_variants_df(log: pd.DataFrame) -> pd.DataFrame:
    """Variant counts via pm4py case_statistics."""
    variants = case_statistics.get_variants_df(log)
    return variants.value_counts().reset_index().tail(20)


def get_variants_as_tuples_df(log: pd.DataFrame) -> pd.DataFrame:
    """Variant counts via pm4py.get_variants_as_tuples."""
    return pd.DataFrame(
        list(pm4py.get_variants_as_tuples(log).items()),
        columns=["variant", "count"],
    )


def discover_petri(log: pd.DataFrame):
    """Discover a Petri net via the heuristics miner."""
    return pm4py.discover_petri_net_heuristics(log)


def conformance(log: pd.DataFrame, petri_net, initial_marking, final_marking) -> list:
    return pm4py.conformance.conformance_diagnostics_token_based_replay(
        log, petri_net, initial_marking, final_marking
    )


def handover(log: pd.DataFrame) -> dict:
    return pm4py.discover_handover_of_work_network(log)


def handover_for_team(log: pd.DataFrame, team_id: str) -> dict:
    return pm4py.discover_handover_of_work_network(log.loc[log["teamId"] == team_id])


# --- presentation (side effects) -------------------------------------------

def present_counts(counts: tuple[int, int]) -> None:
    num_events, num_cases = counts
    print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))


def present_process_tree(process_tree) -> None:
    pm4py.view_process_tree(process_tree)


def present_petri_net(petri_net, initial_marking, final_marking) -> None:
    pm4py.view_petri_net(petri_net, initial_marking, final_marking)


# --- pipeline ---------------------------------------------------------------

def main() -> None:
    log = load_log(CSV_PATH)

    present_counts(count_events_and_cases(log))

    process_tree = discover_tree(log)
    present_process_tree(process_tree)

    bpmn_model = to_bpmn(process_tree)
    # present_bpmn(bpmn_model)

    heuristics_net = discover_heuristics_net(log)
    # present_heuristics_net(heuristics_net)

    variants_df = get_variants_df(log)
    variants_tuples_df = get_variants_as_tuples_df(log)

    petri_net, initial_marking, final_marking = discover_petri(log)
    replayed_traces = conformance(log, petri_net, initial_marking, final_marking)
    replayed_df = pd.DataFrame(replayed_traces)

    present_petri_net(petri_net, initial_marking, final_marking)

    hw_all = handover(log)
    hw_mex = handover_for_team(log, "Mexico")
    # present_sna(hw_all)


if __name__ == "__main__":
    main()
