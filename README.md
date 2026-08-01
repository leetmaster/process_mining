# Process Mining
## What if football were a business process?

This project replicates the methodology presented in *Process Mining of Football Event Data: A Novel Approach for Tactical Insights Into the Game* using the Wyscout World Cup event dataset and the PM4Py process mining framework. The analysis focuses on the 2018 FIFA World Cup match between **Mexico** and **Germany**.

Rather than evaluating the match using traditional football statistics such as possession percentage, passes completed, or shots on target, the project models each **possession** as an independent **process instance**. Every football action—such as a pass, duel, shot, or foul—is treated as an event within that process, allowing Process Mining algorithms to reconstruct the tactical workflows followed by each team. **The analysis is implemented using PM4Py, an open-source Python library for Process Mining that provides tools for event log manipulation, process discovery, conformance checking, and process analysis.** This enables the automatic generation of process models that reveal how each team builds and develops its attacks throughout the match.

After preparing the event log, the **Inductive Miner** discovers a process model that summarizes hundreds of possessions into a single representation of each team's attacking behavior. 

<img width="2684" height="337" alt="image" src="https://github.com/user-attachments/assets/649a742b-5544-4493-b317-4c834c62fb9a" />

The resulting Process Tree, BPMN diagram, and Petri Net reveal common sequences of play, decision points, repeated actions, and typical ways possessions conclude. 

<img width="4771" height="926" alt="image" src="https://github.com/user-attachments/assets/d5a44c36-b787-4b95-9e95-b9d3807f1bfe" />

<img width="3309" height="1133" alt="image" src="https://github.com/user-attachments/assets/c98bbc48-742c-45dc-b0e2-99b30471fdd1" />

Additional analyses, including variant analysis and player interaction networks, provide further insight into tactical patterns and collaboration between players.

<img width="506" height="507" alt="image" src="https://github.com/user-attachments/assets/5e922adf-b40f-4398-9edf-de675544fbb2" />

The project demonstrates that Process Mining offers a complementary perspective to conventional football analytics by shifting the focus from **counting events** to **understanding the processes that generate them**. This methodology makes it possible to compare playing styles, identify recurring tactical behaviors, and visualize the "grammar" of a team's attack directly from event data.
