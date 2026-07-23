import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.statistics.traces.generic.pandas import case_statistics

data = pd.read_csv('events_World_Cup_MEX_GER_with_names.csv')

log = pm4py.format_dataframe(data, case_id='possession_id', activity_key='eventName', timestamp_key='time:timestamp')
#log.rename(columns={'playerName': 'org:resource'}, inplace=True)
num_events = len(log)
num_cases = len(log.eventId.unique())
print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))

process_tree = pm4py.discover_process_tree_inductive(log)
pm4py.view_process_tree(process_tree)

bpmn_model = pm4py.convert_to_bpmn(process_tree)
# pm4py.view_bpmn(bpmn_model)

map = pm4py.discover_bpmn_inductive(log)
# pm4py.view_bpmn(map)

map = pm4py.discover_heuristics_net(log)
# pm4py.view_heuristics_net(map)

variants = case_statistics.get_variants_df(log)
variants.value_counts().reset_index().tail(20)

pd.DataFrame(list(pm4py.get_variants_as_tuples(log).items()), columns=['variant', 'count'])

petri_net, initial_marking, final_marking = pm4py.discover_petri_net_heuristics(log)
replayed_traces = pm4py.conformance.conformance_diagnostics_token_based_replay(log, petri_net, initial_marking, final_marking)

pm4py.view_petri_net(petri_net)

pd.DataFrame(replayed_traces)

hw_values: dict = pm4py.discover_handover_of_work_network(log)

hw_values: dict = pm4py.discover_handover_of_work_network(log.loc[log['teamId'] == "Mexico"])

# pm4py.view_sna(hw_values)
