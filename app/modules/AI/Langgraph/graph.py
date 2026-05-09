from langgraph.graph import StateGraph,END
from .state import AgentState
from .node import classify_node,generate_node,policy_retrieve_node,shipment_retriever_node,route_intent

def build_graph(db):
    builder = StateGraph(AgentState)

    builder.add_node("classify", classify_node)


    async def shipment_wrapper(state):
        return await shipment_retriever_node(state,db)
    builder.add_node("shipment_retrieve", shipment_wrapper)
    builder.add_node("policy_retrieve", policy_retrieve_node)

    builder.add_node("generate", generate_node)

    builder.set_entry_point("classify")

    builder.add_conditional_edges("classify",route_intent,{
        "shipment":"shipment_retrieve",
        "policy": "policy_retrieve"
    })

    builder.add_edge("shipment_retrieve", "generate")
    builder.add_edge("policy_retrieve", "generate")
    builder.add_edge("generate", END)



    return builder.compile()