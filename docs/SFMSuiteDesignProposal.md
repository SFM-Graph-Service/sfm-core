# Implementing the Social Fabric Matrix (SFM) Framework: Design Proposal for a Suite of Tools and Services
Author: Garrick Dabbs Date: 05/23/2025

# Table of Contents

1. [Introduction](#introduction)
2. [Data Modeling and Representation](#data-modeling-and-representation)
   - Entities (Nodes)
   - Relationships (Edges)
   - Example - Defining Data Structures
   - Data Storage Choices
3. [Relationship Mapping and Input Tools](#relationship-mapping-and-input-tools)
   - Interactive Editor
4. [References](#references)



## Introduction ##
The Social Fabric Matrix (SFM) is a holistic methodology for mapping complex social, economic, and institutional systems. It defines a network of system entities (such as cultural values, beliefs, technologies, institutions, etc.) and the relationships or flows (“deliveries”) between them [[1]](#1). By capturing these interconnections, SFM helps analysts identify feedback loops and understand how changes in one part of an organization or society can ripple through the whole system. However, building and analyzing an SFM by hand (traditionally using spreadsheets and written documentation) can be cumbersome. To address this, I propose a suite of software tools and services that implement the SFM framework for organizations. This suite will provide a detailed, extensible codebase with ready-to-use entities for data modeling, relationship mapping, graph-based analysis, visualization, and simulation. The following proposal outlines the design and features of this SFM software suite, with code examples and references to existing methodologies and libraries.

---

## Data Modeling and Representation

An SFM represents a system as a set of entities and the deliveries (direct influences or flows) between them. Each component belongs to a certain type (based on the SFM taxonomy) such as *cultural values, social beliefs, personal attitudes, natural environment, technology,* or *social institutions*. In software, a logical data model is needed to represent these entities, their categories, and their relationships. A straightforward representation is to treat the SFM as a directed graph: entities are nodes, and each delivery is a directed edge from a delivering node to a receiving node. This allows the system to be stored in a flexible structure that mirrors the real-world network of interdependencies.

- Entities (Nodes) Each entity can be modeled as an object or record with attributes like an ID, a name, a type (e.g. “Social Belief” or “Institution”), and optional metadata or description. For example, a component might be *“State Education Funding Policy”* (type: Institution) or *“Public Value: Equal Opportunity”* (type: Cultural Value).
- Relationships (Edges): Each directed relationship indicates that one component delivers something to another (e.g. an institutional policy delivers resources to school districts, or a societal value delivers criteria influencing institutional rules). Edges can carry properties such as a description of the delivery (what is being delivered or influenced), a type or label, and potentially a numeric weight if quantifying the strength or amount of flow. Using a property-graph model (nodes with properties, edges with properties) is ideal, because it can capture rich information and easily adapt to new attributes or relationship types.

- Example – Defining Data Structures: One could use an object-oriented approach or a schema in a database. For instance, using Python classes to represent the data model:
```python
class SFEntity:
    """
    Represents an entity (policy, regulation, program, etc.) within the Social Fabric Matrix.
    """
    def __init__(self, id: uuid.UUID, name: str, type: str, properties: dict):
        self.id = id
        self.name = name
        self.type = type
        self.properties = properties

    def __repr__(self):
        return f"{self.name} ({self.type})"

class Relationship:
    """
    Represents a directed relationship between two SFEntity objects.
    """
    def __init__(self, rel_id: uuid.UUID, sourceEntityId: uuid.UUID, targetEntityId: uuid.UUID, description: str,
                 value: float, metadata: dict):
        self.id = rel_id
        self.sourceEntityId = sourceEntityId
        self.targetEntityId = targetEntityId
        self.description = description  # e.g., 'impacts', 'supports', etc.
        self.value = value  # A weight or strength indicator between 0 and 1.
        self.metadata = metadata

    def __repr__(self):
        return f"{self.sourceEntityId} --{self.description}:{self.value}--> {self.targetEntityId}"
```
In a more data-driven approach, the SFM could be stored as JSON or in a graph database. A graph database (like Neo4j or similar) naturally stores nodes and edges, and excels at managing intricate     interconnections. For example, one could create nodes labeled with their type and connect them with relationships labeled “DELIVERS_TO”. This would allow writing queries to find particular patterns of interaction efficiently (thanks to optimized graph traversal). The adjacency structure can also be represented as a matrix for mathematical analysis, essentially an adjacency matrix where rows and columns correspond to the list of entities, and a cell contains a 1 (or a weight) if the row component delivers to the column component. The software should maintain this representation under the hood and update it as relationships are added or removed.

- Data storage choices: The codebase should be designed to be modular regarding data storage. For simplicity during development, an in-memory data model (lists of entities and edges, or a NetworkX graph) can be used. For larger projects or multi-user environments, a persistent storage like a graph database or a relational database with tables for entities and relationships can be integrated later. The key is that the data model abstraction (the classes or data structures and their API) remains consistent so that entities and relationships can be manipulated without needing to know the low-level storage details.

---

## Relationship Mapping and Input Tools

Constructing the SFM involves identifying and mapping all relevant relationships among entities. The software suite will include tools to intuitively create, edit, and import these relationships. In earlier SFM projects, researchers often relied on manually editing Excel spreadsheets and separate documents to describe each connection. Our goal is to streamline this with interactive mapping and robust import/export features.

- Interactive Editor: A graphical interface can allow users to add new entities and draw connections between them. For example, a user might drag a line from a *“Funding Policy”* node to a *“School Districts”* node to represent that policy delivering funding to districts. The interface can prompt for details (e.g. “describe what is delivered or influenced”) so that each edge in the matrix has documentation attached. This way, unlike having to cross-reference a separate narrative document, the explanation for each linkage is stored directly within the model. The editor should support groupings or color-coding by type, making it easier to navigate large models.
- Validation and Taxonomy Awareness: Since SFM has an underlying taxonomy of component categories and typical flows among them, the tool can optionally guide the user by highlighting unusual linkages. For instance, if *“Personal Attitudes”* typically influence *“Social Institutions”* but a user links an institution delivering to a personal attitude, the software might flag it for review (depending on SFM conventions). However, flexibility is crucial; the tool should not hard-code restrictions but can provide recommendations.
- Data Import/Export: To be useful in organizational settings, the suite should allow importing relationships from common formats. This includes reading an Excel or CSV file that lists triples (source, target, description) for deliveries, or a matrix format if one is prepared. Similarly, the tool can export the constructed SFM to formats like CSV, GraphML, or JSON for use in other applications. Maintaining compatibility with standard formats helps in integrating with other analysis tools or performing statistical analysis on the data.

**Example – Building the Matrix Relationships in Code:** The following Python snippet demonstrates how relationships might be added programmatically, using a network library like NetworkX to manage the directed graph structure:

```python
import networkx as nx

# Initialize an empty directed graph for the SFM
G = nx.DiGraph()

# Add entities (node id, attributes)
G.add_node("Policy", type="Institution", name="State Funding Policy")
G.add_node("Districts", type="Institution", name="Public School Districts")
G.add_node("Equal Opportunity", type="Cultural Value", name="Value: Equal Opportunity")

# Add relationships (edges with description)
G.add_edge("Policy", "Districts", description="Funds allocated to schools")
G.add_edge("Equal Opportunity", "Policy", description="Value criteria guiding policy")
```

In the above example, I add three entities and then define two directed edges: one indicating the policy delivers funds to the school districts, and another indicating that a cultural value influences the policy. Each edge carries a textual description (`description`) to explain the nature of that delivery. In a full application, these operations would be done through a user-friendly interface, but having a programmatic API (like shown) is important for extensibility as it allows advanced users or other software services to modify the SFM content directly, or to script the creation of large matrices.

Additionally, the platform could integrate with version control or project management systems if organizations need to track changes to the model over time. Since policies and environments change, an editable and expandable SFM means users can update entities or add new ones as new research or real-world changes occur, without starting from scratch.

---

## Graph-Based Analysis and Insights

Once the SFM is constructed (the network of relationships is in place), the next major feature is analytical tools to derive insights from the graph structure. The software suite will implement a variety of graph-based analysis methods to help users detect important patterns, measure influence, and explore the system’s properties. Since an SFM essentially forms a directed graph, I can leverage graph theory and network analysis algorithms heavily.

Some key analysis capabilities include:

- Connectivity and Reachability: Determine how entities are connected through direct and indirect paths. The software can compute a reachability matrix that shows, for each component, which other entities it can eventually influence through a chain of deliveries. This helps identify clusters of interconnected elements and the maximum scope of influence of a particular node. For instance, if *“Legislation”* can reach *“Student Outcomes”* via a chain of deliveries (through funding allocations, educational programs, etc.), the reachability analysis will highlight that path.
- Feedback Loop Detection: Identify cycles in the network, which correspond to feedback loops in the system. A feedback loop occurs when a sequence of deliveries eventually circles back to affect the original source. These can be reinforcing (positive feedback) or balancing (negative feedback) loops. The tool can automatically find all cycles in the directed graph. Detecting feedback loops is crucial because they often indicate self-reinforcing problems or virtuous cycles. For example, an economic growth loop could be *“Investment -> Jobs -> Income -> Spending -> Investment”*. The code might utilize an algorithm to find strongly connected entities or use existing network libraries to list cycles.

- Influence and Centrality Metrics: Calculate network metrics that show which entities are most influential or most affected. In-degree (number of inputs) and out-degree (outputs) counts for each node are a basic start; they tell which entities receive the most inputs and which provide the most outputs. More sophisticated metrics like betweenness centrality could identify entities that lie on many paths (acting as intermediaries or bottlenecks in the system). These metrics provide a quantitative hint of which parts of the social fabric are key leverage points. For example, if an institution has a high out-degree and high betweenness, it might be a critical hub through which many effects flow.
- Scenario and Sensitivity Analysis: The graph structure can be used to simulate the impact of removing or changing a link, even before running a full dynamic simulation. By toggling certain deliveries on or off, or by assigning weights and computing aggregated influence, one can compare different configurations. The software can support side-by-side comparisons of two SFM variants (e.g. current policy network vs. proposed policy network) to show how the connectivity or feedback loops differ. Additionally, if the relationships have weighted values, the tool can generate a sensitivity matrix or use matrix algebra to assess how changes propagate. For instance, using linear algebra, one could compute if the system has potential runaway positive feedback: in matrix terms, this could involve checking if any eigenvalue of a weighted adjacency matrix exceeds 1 (indicating an amplifying loop). Such analysis, drawn from input-output techniques and graph theory, provides early warning of unstable dynamics.

**Example – Finding Feedback Loops with Python:** Using NetworkX (Python library), I can easily find cycles in the directed graph:

```python
# Assume G is the directed graph from earlier
cycles = list(nx.simple_cycles(G))
for cycle in cycles:
    print("Feedback loop detected:", " -> ".join(cycle))
```

This snippet uses NetworkX’s `simple_cycles` function to get all feedback loops (cycles) in the SFM graph. The output might list something like: *“Feedback loop detected: Community Values -> School Board -> Community Values”* if, say, community values influence the school board’s decisions and the school board in turn shapes community values (a loop).

For reachability, one approach is to compute the transitive closure of the graph. I could do this via repeated matrix multiplication or a traversal algorithm. For example, to get a reachability matrix using adjacency matrices:

```python
import numpy as np

A = nx.to_numpy_array(G, dtype=int)       # adjacency matrix (binary) of the graph
n = A.shape[0]
# Compute transitive closure via repeated squaring (Floyd–Warshall or powers of A)
reach = (A.copy() > 0).astype(int)
for _ in range(n):  # worst-case n-1 iterations needed
    A = A.dot(A)                        # matrix multiplication
    reach |= (A > 0).astype(int)        # add new reachabilities
```

This code computes `reach[i,j] = 1` if there's any path from node *i* to node *j*. In practice, one would use higher-level functions or algorithms for this, but it illustrates how the tool can derive indirect relationships programmatically. The results from such analysis can be presented back to the user in meaningful ways, e.g., highlighting on the graph which nodes are downstream of a selected node.

Under the hood, these analytical functions rely on well-known graph algorithms and linear algebra operations. The codebase should organize these as a distinct module (e.g., an `analysis` package) so that new algorithms can be added over time. For example, if future users want to plug in community detection algorithms or more complex network flow calculations, they can extend this module without affecting the rest of the system.

---

## Visualization and User Interface

Visualization is a critical component of the SFM tool suite. A clear, interactive visual representation of the Social Fabric Matrix makes it easier for stakeholders to understand the web of relationships and to communicate findings. The software will support multiple visualization modes, primarily focusing on graph/network visualization but also offering a matrix view for those who prefer a tabular perspective.

Key features of the visualization module include:

- Interactive Network Graph: The SFM can be displayed as a network graph (nodes connected by arrows for deliveries). Using a force-directed layout or other graph layout algorithms, the nodes will be arranged visually, and arrows will indicate the direction of influence. Interactivity is crucial: users should be able to pan, zoom, and click on nodes or edges. Clicking on a node might highlight all its connections (both incoming and outgoing) to emphasize that component’s relationships. Hovering over an edge could show the description of that delivery as a tooltip (e.g., “Policy X provides resources to Program Y”). This interactive highlighting and tooltip behavior helps in navigating complex diagrams where many connections overlap.
- Categorical Distinction: Since SFM entities span various categories, the visualization should differentiate them with colors, shapes, or grouping. For example, *values* could be depicted as diamond-shaped nodes, *institutions* as rectangles, and *physical environment elements* as circles (just as a design choice). A legend can clarify these encodings. This way, users can visually parse which part of the system each node belongs to at a glance.
- Detail Panels and Annotations: In addition to floating tooltips, the UI might include a side panel that displays detailed information about the selected component or relationship. For instance, clicking on an edge might bring up its full description, any attached notes, or data (like a link to a policy document or statistical figures). Modern system mapping tools like Kumu incorporate narratives and media for each element and connection; similarly, our tool can allow text or links to be stored with each node/edge and shown on selection. This enriches the static graph with context and makes the SFM a living knowledge base, not just a diagram.
- Matrix View: A complementary view could be a matrix (rows and columns of entities with checkmarks or numbers where deliveries exist). This is essentially the traditional representation of SFM. While less immediately intuitive than a graph for some, it can be useful for systematically ensuring completeness or seeing patterns in a grid form. The software could allow toggling between the network diagram and matrix view. Any edit in one view (like adding a link) would reflect in the other.

**Example – Generating an Interactive Graph:** One way to implement the network visualization is to use a JavaScript library like D3.js or vis.js in a web interface, as these allow highly customizable graphics in the browser. Alternatively, for rapid development, the Python library PyVis provides a simple way to generate an interactive network visualization from a NetworkX graph. For instance:

```python
from pyvis.network import Network

# Suppose G is our NetworkX graph of the SFM (as built earlier)
net = Network(height="600px", width="100%", directed=True)
net.from_nx(G)  # load the NetworkX graph into PyVis
net.show("sfm_network.html")
```

This code will produce an HTML file `sfm_network.html` containing an interactive graph: one can open it in a browser to explore the SFM graph with zooming, dragging, and hovering functionality. In the final web application, instead of writing to a file, I would integrate such a visualization directly into the app’s interface (using either PyVis in a Flask/Django app or directly using D3.js in a JavaScript front-end).

To customize appearance, the code could assign colors or shapes based on categories. For example, using PyVis one can do:

```python
# Color nodes by type for clarity
for node, data in G.nodes(data=True):
    if data.get('type') == 'Institution':
        net.get_node(node)['color'] = 'cornflowerblue'
    elif data.get('type') == 'Cultural Value':
        net.get_node(node)['color'] = 'gold'
# (Other categories omitted for brevity)
```

In a D3.js implementation, one would bind data similarly and set SVG styles for nodes and links according to type. The principle is to make the visualization not only interactive but also semantically rich, so the user can visually discern structure and get information on demand.

Finally, the interface should allow saving or exporting visuals (e.g., as an image or PDF) for reporting purposes. It may also be useful to allow users to annotate the visual (like drawing an emphasis or writing commentary on certain loops) which can be saved with the project.

---

## Simulation and Scenario Analysis

Beyond static analysis, a powerful aspect of an SFM software suite is the ability to run simulations. While the SFM itself is a structural model (indicating what influences what), to see quantitative outcomes or time-dynamic behavior, I integrate it with simulation capabilities. This can range from system dynamics simulations (where I model stocks, flows, and feedback loops over time) to agent-based simulations for more granular behavior modeling. The goal is to let users experiment with *“what if” scenarios* in their SFM: for example, *“What if I increase funding in this area?”* or *“What if this regulatory connection is removed?”*, and observe potential consequences through the network.

Approaches to simulation in the SFM context include:

- System Dynamics Integration: One method is to translate the SFM into a system dynamics model. Each delivery could correspond to a flow or influence in a system dynamics diagram. For instance, in the Nebraska education finance SFM, researchers used the iThink system dynamics software to turn the SFM into stock-flow diagrams that represent money or information flowing between education funding entities. Our software could incorporate a simple system dynamics engine or connect to existing ones. With tools like PySD, which converts Vensim models to Python code for simulation, one could define equations for how one component quantitatively affects another (e.g., a formula for how policy funding translates to student outcomes). The SFM structure guides the model equations, ensuring that no connection is overlooked. Running the simulation then shows how values change over time or under different inputs.
- Discrete-Time Propagation: For a lighter approach, I can simulate step-by-step propagation on the network. For example, assign an initial value or shock to some nodes (say a 10% increase in a funding component) and then iteratively update other nodes based on the deliveries. If each edge has an “influence weight” (like elasticity or percent influence), I can propagate the changes through successive rounds until equilibrium or a time horizon is reached. This is essentially doing a simplified dynamic multiplier analysis on the graph. It’s useful for scenario testing when precise differential equations are not available. The code below demonstrates a simple propagation simulation:

```python
# Initial values for entities (for simulation purposes)
values = {"Policy": 100, "Districts": 50, "Equal Opportunity": 1}
# Assume I assign influence factors on edges (if weight is given, use it, else assume 1.0 for demonstration)
influences = {(u, v): (data.get('weight', 1.0) * 0.1)   # example: 0.1 scaling
              for u, v, data in G.edges(data=True)}

# Simulate for 5 time steps
for t in range(1, 6):
    new_values = values.copy()
    for (src, dst), factor in influences.items():
        new_values[dst] += values[src] * factor
    values = new_values
    print(f"After step {t}: {values}")
```

In this pseudocode, each step every node receives some fraction (`factor`) of each of its input nodes’ current value. Over iterations, one can see how an initial input spreads through the network. Of course, a real model would have more meaningful equations and possibly include decay or resource limitations to prevent infinite growth. The suite could allow users to specify the formula or rules for each delivery (perhaps via a small scripting interface or by attaching a function to edges).
- Agent-Based Modeling: For certain complex organizational simulations, an agent-based approach might be warranted (for example, simulating individuals or departments with behaviors, within the structure given by the SFM). While this goes beyond the traditional SFM usage, our extensible design can accommodate it. Using an open-source framework like Mesa (for Python), one could create agents whose interactions are informed by the SFM relationships. The software could launch an agent-based simulation where, say, each institution node becomes an agent following certain rules and exchanging resources/messages as per the SFM links.
- Scenario Management: The platform will let users define scenarios which alter the SFM or the simulation parameters. For instance, one scenario might disable a particular connection (simulating a policy removal) or change a value (simulating a budget increase) and then run the simulation. Multiple scenarios can be run and compared. The results (time series outputs, or key indicators) can be visualized, enabling the user to compare outcomes of alternative policies quantitatively. This fulfills a key promise of the SFM approach: not only mapping the system but also evaluating different policy interventions within that system.

It’s important to note that building a full simulation environment is a substantial task. Initially, the focus could be on providing hooks to export the SFM structure to established simulation tools (for example, generate a system dynamics model file, or feed the data to an external simulation engine). Over time, the suite can incorporate more built-in simulation capabilities. The codebase should therefore separate the model definition (i.e. the SFM graph) from the simulation logic. This way users can plug in different simulation methods without altering the core data structure.

---

## Codebase Architecture and Extensibility

To achieve the goal of a detailed and expandable codebase, the SFM software suite must be designed with modularity and flexibility in mind. Extensibility means that new features or modifications can be added with minimal changes to existing code. Below are key architectural considerations to ensure the platform remains robust and adaptable:

- Modular Design: The system should be divided into modules or services corresponding to major functionality: e.g., a data model module (handling storage and retrieval of SFM data), an analysis module (graph algorithms, metrics), a visualization module (UI and rendering logic), and a simulation module (dynamic modeling engine). This separation allows each part to evolve or be replaced independently. For instance, one could swap out the graph storage backend (say, move from an in-memory representation to a Neo4j database) without affecting the visualization or analysis code, as long as the module exposes the same interface. A modular design also supports scaling up: if heavy simulations are needed, the simulation component could run on a different server or be parallelized, without rewriting the front-end or analysis logic.
- APIs and Plugins: The suite can provide a clear API for external tools or developers to interact with. A RESTful API or a Python library interface would enable other applications to programmatically create SFM models, run analyses, or retrieve results. For example, an organization might integrate the SFM tool with their data warehouse to automatically populate some relationships from live data. Moreover, a plugin system could allow developers to add new analysis algorithms or import/export handlers. For example, if someone wanted to add an importer for a new data format, they could do so by writing a plugin that interfaces with the data model module. Using such plugin and microservice architecture principles ensures new functionality can be “plugged in” without altering the core, embodying the idea of building blocks for easy extension.
- Documentation and Code Samples: To make the codebase truly ready “out of the box” for editing and expansion, it should include comprehensive documentation and numerous code examples. Each module should come with example scripts or notebooks demonstrating how to use it (e.g., a tutorial on building a small SFM, running an analysis, and generating a visualization). This lowers the learning curve for new users or developers. In practice, the repository might include a set of Jupyter notebooks covering different use cases, as well as inline documentation within code (docstrings and comments). An emphasis on clarity and clean organization will make it easier for others to contribute or customize the software.
- Open-Source and Community Collaboration: Adopting an open-source approach can greatly accelerate extensibility. By releasing the code publicly (e.g., on GitHub) and encouraging contributions, the suite can benefit from community-driven improvements. Users might contribute new visualization templates, specialized analysis for particular domains, or connectors to other tools. A community of practice around the SFM suite would also help with validation and refinement of the framework itself as it gets applied to diverse organizational problems.
- Performance and Scalability: As the size of the SFM (number of entities and relations) grows, the software should remain responsive. This might involve using efficient algorithms (graph algorithms can be expensive, so use optimized libraries) and possibly asynchronous processing for simulations (so the UI doesn’t freeze during a long run). In a web service context, the architecture could allow distributing the load: for example, a separate analysis service that can be scaled horizontally if many users are running analyses simultaneously. By designing with scalability in mind, the toolset can serve small projects (maybe a dozen entities) up to very large models (hundreds of entities with thousands of connections) which might exist in big organizational or regional policy models.

**Table: Key Features and Implementation Choices**

| Feature Area          | Implementation Options                    | Notes (Pros/Cons)                                         |
|-----------------------|-------------------------------------------|-----------------------------------------------------------|
| **Data Storage & Model**   | - In-memory graph (NetworkX, etc.)<br>- Graph database (Neo4j, AWS Neptune)<br>- Relational DB (with join tables for edges) | Graph DBs excel at complex relationships and can scale for collaborative use. Relational DB is stable and familiar but may be less natural for network queries. |
| **Relationship Input** | - Interactive web UI (drag-and-drop nodes)<br>- Spreadsheet import (Excel/CSV)<br>- Domain-specific language (e.g., a simple script format) | UI is user-friendly for non-coders. Spreadsheet import is crucial for legacy data. A custom DSL could allow advanced users to define entities/links in text form. |
| **Analysis Algorithms** | - NetworkX (Python library)<br>- Custom algorithms (NumPy/GraphBLAS for matrix ops)<br>- Graph database queries (Cypher for path finding) | NetworkX provides many ready-made functions (shortest path, centrality, etc.) to speed development. Custom numeric code can optimize large-scale computations (using matrix math). Graph DBs can execute certain graph queries directly via their query languages. |
| **Visualization**    | - Web: D3.js or vis.js for full interactivity<br>- Python: PyVis or Plotly for quick interactive plots<br>- Static: Graphviz for printable diagrams | D3.js offers full flexibility for custom visuals and interactions (but needs more coding). PyVis/Plotly allow leveraging Python, though with somewhat less customization than raw D3. Graphviz can auto-generate neat diagrams but is static and lacks interactive features. |
| **Simulation Engine** | - System Dynamics: PySD (for ODE models)<br>- Custom discrete simulation (Python loops or agent-based)<br>- External integration (co-simulate with tools like AnyLogic, Vensim via exports) | PySD and similar allow using established SD modeling in Python, ideal if users are familiar with stock-flow models. Custom code gives flexibility (e.g., unique rules per link) but requires more validation. External tools might offer advanced simulation capabilities (optimization, calibration), so being able to export/import to them adds value. |

## References
<a id="1">[1]</a> 
Hayden, F. G. (2006). Policymaking for a good society: The social fabric matrix approach to policy analysis and program evaluation. Springer.
