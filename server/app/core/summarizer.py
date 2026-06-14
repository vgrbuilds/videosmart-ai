from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model_to_use,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    return splitter.split_text(transcript)

def summarize(transcript: str) -> str:
    llm = get_llm()
    chunks = split_transcript(transcript)
    
    map_prompt = ChatPromptTemplate.from_template("Summarize this portion of a meeting transcript concisely:\n{text}")
    map_chain = map_prompt | llm | StrOutputParser()
    chunk_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]
    
    combined_prompt = ChatPromptTemplate.from_template(
        "You are an expert meeting summarizer. Combine these partial summaries "
        "into one final professional meeting summary in bullet points:\n{text}"
    )
    combined_chain = combined_prompt | llm | StrOutputParser()
    return combined_chain.invoke({"text": "\n\n".join(chunk_summaries)})

def generate_title(transcript: str) -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(
        "Based on the meeting transcript, generate a short professional meeting title (max 8 words). "
        "Only return the title, nothing else.\n\nTranscript: {text}"
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": transcript[:2000]})
