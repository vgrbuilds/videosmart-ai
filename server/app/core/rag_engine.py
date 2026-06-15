from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import settings
from app.core.vector_store import load_vector_store, get_retriever

PRONOUNS = {"he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "this", "that", "these", "those"}

def needs_rephrasing(question: str) -> bool:
    words = set(question.lower().split())
    return not words.isdisjoint(PRONOUNS)

def get_llm():
    return ChatGoogleGenerativeAI(model=settings.gemini_model_to_use, google_api_key=settings.GEMINI_API_KEY, temperature=0.3)

async def ask_question(video_id: str, chat_history: list, question: str) -> str:
    llm = get_llm()
    retriever = get_retriever(load_vector_store(), video_id=video_id, k=5)
    
    messages = [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in chat_history
    ]
    
    condensed = question
    if messages and needs_rephrasing(question):
        condense_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
            ("system", "Given the conversation above, rephrase this follow-up question to be standalone. Do not answer it.")
        ])
        condensed = await (condense_prompt | llm | StrOutputParser()).ainvoke({
            "chat_history": messages[-4:], "question": question
        })
        
    docs = await retriever.ainvoke(condensed)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the question based ONLY on the transcript context. If not found, say you cannot find it.\n\nContext:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
    return await (qa_prompt | llm | StrOutputParser()).ainvoke({
        "context": context, "chat_history": messages[-4:], "question": question
    })