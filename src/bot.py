import discord
import os
from dotenv import load_dotenv
import asyncio

from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI      # <-- CHANGE HERE
from langchain_google_genai import GoogleGenerativeAIEmbeddings # <-- CHANGE HERE
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

# --- 1. Load Environment Variables and API Keys ---
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') # <-- CHANGE HERE

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("Discord token and Google API key must be set in .env file")

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

# --- 2. Load the Knowledge Base (FAISS Vector Store) ---
VECTOR_STORE_PATH = "pypsa_ecosystem_faiss_index" # <-- Use the new Gemini index
print("Loading FAISS vector store...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001") # <-- CHANGE HERE
vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
print("Vector store loaded successfully.")

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

# --- 4. Set up the Discord Bot --- (No changes in this section)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print('Ready to answer questions about PyPSA with Google Gemini.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        async with message.channel.typing():
            # --- THIS IS THE UPDATED SECTION ---
            chat_history = []
            # Fetch the last 10 messages to get a better context
            async for msg in message.channel.history(limit=10, before=message):
                # We use the new AIMessage and HumanMessage objects
                if msg.author == client.user:
                    chat_history.append(AIMessage(content=msg.content))
                else:
                    chat_history.append(HumanMessage(content=msg.content))
            
            # Reverse the history to be in chronological order
            chat_history.reverse()
            # --- END OF UPDATED SECTION ---
            
            question = message.content.replace(f'<@!{client.user.id}>', '').strip()

            print(f"Invoking QA chain with Gemini for question: '{question}'")
            
            # Use .invoke() instead of .__call__() to avoid the deprecation warning
            result = await asyncio.to_thread(qa_chain.invoke, {"question": question, "chat_history": chat_history})
            answer = result['answer']

            if len(answer) > 2000:
                for chunk in [answer[i:i+2000] for i in range(0, len(answer), 2000)]:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(answer)

# Run the bot
client.run(TOKEN)