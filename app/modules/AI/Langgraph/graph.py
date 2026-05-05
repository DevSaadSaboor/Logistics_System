from langgraph.graph import StateGraph,END
from .state import AgentState
from .node import classify_node,retriever_node,generate_node

def build_graph(db):
    builder = StateGraph(AgentState)

    builder.add_node("classify", classify_node)


    async def retrieve_wrapper(state):
        return await retriever_node(state,db)
    
    builder.add_node("retriever", retrieve_wrapper)

    builder.add_node("generate", generate_node)

    builder.set_entry_point("classify")

    builder.add_edge("classify", "retriever")
    builder.add_edge("retriever", "generate")
    builder.add_edge("generate", END)



    return builder.compile()