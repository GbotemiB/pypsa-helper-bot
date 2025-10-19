import discord
import os
from dotenv import load_dotenv
import asyncio
import time
from pathlib import Path

from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

# Import storage utilities
from storage import ensure_index_available, IndexStorage

# --- 1. Load Environment Variables and API Keys ---
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("Discord token and Google API key must be set in .env file")

# Configuration
INDEX_CHECK_INTERVAL = int(os.getenv('INDEX_CHECK_INTERVAL', '300'))  # 5 minutes default

SYSTEM_PROMPT = """
You are PyPSA-AI-Helper, a friendly and expert AI assistant for the PyPSA (Python for Power System Analysis) community. Your purpose is to answer user questions accurately based on the provided context.

Your knowledge base includes the documentation, source code, configuration files, and GitHub issues/pull requests for the following repositories: pypsa, pypsa-eur, and pypsa-earth.

Follow these rules strictly:
1.  Base your answers *only* on the information provided in the CONTEXT section. Do not use any external knowledge or make assumptions.
2.  If the context does not contain the answer to the question, you MUST state that you cannot answer with the provided information. Do not try to guess.
3.  Be helpful and conversational. Address the user directly.
4.  When presenting code or configuration snippets, use Markdown code blocks for proper formatting.
5.  Cite your sources from the metadata of the provided context documents when possible to help users find more information.
"""

# --- 2. Download and Load the Knowledge Base (FAISS Vector Store) ---
VECTOR_STORE_PATH = "pypsa_ecosystem_faiss_index"

# Ensure index is available (download if needed)
print("Checking for FAISS index...")
if not ensure_index_available():
    raise RuntimeError("Failed to obtain FAISS index. Cannot start bot.")

print("Loading FAISS vector store...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
print("Vector store loaded successfully.")

# Initialize storage manager for hot-reloading
storage_manager = IndexStorage(VECTOR_STORE_PATH)

template = SYSTEM_PROMPT + """

    CONTEXT: {context}

    QUESTION: {question}

    YOUR ANSWER:"""

QA_PROMPT = PromptTemplate(
    template=template, input_variables=["context", "question"]
)

# --- 3. Set up the LangChain QA Chain ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3,) # <-- CHANGE HERE
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": QA_PROMPT},
)

# --- 4. Set up the Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Global variable for tracking bot health
bot_ready = False

async def check_for_index_updates():
    """Background task to check for index updates and reload if needed"""
    global vector_store, qa_chain, retriever
    
    await client.wait_until_ready()
    
    while not client.is_closed():
        try:
            await asyncio.sleep(INDEX_CHECK_INTERVAL)
            
            print("Checking for FAISS index updates...")
            if storage_manager.check_for_updates():
                print("📦 New index version available! Downloading...")
                
                if storage_manager.download_index(force=True):
                    print("🔄 Reloading vector store...")
                    
                    # Reload the vector store
                    new_vector_store = FAISS.load_local(
                        VECTOR_STORE_PATH, 
                        embeddings, 
                        allow_dangerous_deserialization=True
                    )
                    
                    # Update retriever and chain
                    new_retriever = new_vector_store.as_retriever(search_kwargs={"k": 3})
                    new_qa_chain = ConversationalRetrievalChain.from_llm(
                        llm=llm,
                        retriever=new_retriever,
                        return_source_documents=True,
                        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
                    )
                    
                    # Atomic swap
                    vector_store = new_vector_store
                    retriever = new_retriever
                    qa_chain = new_qa_chain
                    
                    print("✅ Vector store reloaded successfully!")
                else:
                    print("❌ Failed to download new index. Continuing with current version.")
            else:
                print("✓ Index is up to date")
                
        except Exception as e:
            print(f"Error checking for updates: {e}")

async def health_check_writer():
    """Write health check file for Docker/Fly.io"""
    await client.wait_until_ready()
    
    while not client.is_closed():
        try:
            # Write health check file
            Path("/tmp/bot_healthy").touch()
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Health check error: {e}")

@client.event
async def on_ready():
    global bot_ready
    
    print(f'{client.user} has connected to Discord!')
    print('Ready to answer questions about PyPSA with Google Gemini.')
    
    # Display index info
    index_info = storage_manager.get_index_info()
    print("\n📊 FAISS Index Information:")
    for key, value in index_info.items():
        print(f"  {key}: {value}")
    print()
    
    bot_ready = True
    
    # Start background tasks
    client.loop.create_task(check_for_index_updates())
    client.loop.create_task(health_check_writer())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        async with message.channel.typing():
            chat_history = []
            # Fetch the last 10 messages to get a better context
            async for msg in message.channel.history(limit=10, before=message):
                if msg.author == client.user:
                    chat_history.append(AIMessage(content=msg.content))
                else:
                    chat_history.append(HumanMessage(content=msg.content))
            
            # Reverse the history to be in chronological order
            chat_history.reverse()
            
            question = message.content.replace(f'<@!{client.user.id}>', '').strip()
            question = question.replace(f'<@{client.user.id}>', '').strip()  # Handle both mention formats

            print(f"Invoking QA chain with Gemini for question: '{question}'")
            
            try:
                # Use .invoke() instead of .__call__() to avoid the deprecation warning
                result = await asyncio.to_thread(qa_chain.invoke, {"question": question, "chat_history": chat_history})
                answer = result['answer']

                if len(answer) > 2000:
                    for chunk in [answer[i:i+2000] for i in range(0, len(answer), 2000)]:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(answer)
            except Exception as e:
                print(f"Error processing question: {e}")
                await message.channel.send("Sorry, I encountered an error processing your question. Please try again later.")

# Run the bot
client.run(TOKEN)