import logging
import time
import re
from langchain_core.exceptions import OutputParserException
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from config import GOOGLE_API_KEY, QDRANT_PATH, COLLECTION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_db = None
try:
    vector_db = QdrantVectorStore.from_existing_collection(
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME,
        embedding=embedding_model,
    )
except Exception as e:
    logger.error(f"Failed to connect to Qdrant at startup: {e}")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",   # stable model, 15 RPM on free tier
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
    timeout=15,     # dropped from 60s to 15s to fail fast
    max_retries=0,  # we handle retries manually below
)

GREETING_KEYWORDS = {
    "hello", "hi", "hey", "howdy", "greetings", "sup",
    "good morning", "good afternoon", "good evening", "good night",
    "how are you", "how r you", "how do you do",
    "what can you do", "what do you do", "who are you",
    "what are you", "tell me about yourself",
}

GREETING_RESPONSE = (
    "Hello! 👋 I'm your **RAG Document Assistant**, powered by Gemini + Qdrant.\n\n"
    "I answer questions based on the uploaded document. "
    "Feel free to ask me anything about its content!"
)

NOISE_RESPONSE = (
    "I couldn't understand your question. "
    "Please ask a clear question related to the document."
)

SCOPE_RESPONSE = (
    "I can only answer questions based on the uploaded document."
)

RATE_LIMIT_RESPONSE = (
    "I'm currently receiving too many requests. "
    "Please wait a few seconds and try again."
)

RETRIEVAL_ERROR_RESPONSE = "I'm having trouble accessing the document right now."

NOT_FOUND_RESPONSE = "I could not find this information in the document."


def _is_noise(text: str) -> bool:
    """True if the text is purely symbols / numbers / junk with no real words."""
    stripped = text.strip()
    if len(stripped) < 3:
        return True
    # Remove symbols & digits; if barely any real letters remain → noise
    letters_only = re.sub(r"[^a-zA-Z]", "", stripped)
    return len(letters_only) < 3


def _is_greeting(text: str) -> bool:
    """True if the message is essentially a greeting / small-talk."""
    lower = text.lower().strip()
    # Short pure-greeting check
    if lower in GREETING_KEYWORDS:
        return True
    # Multi-word: check if every meaningful word is a greeting keyword
    words = lower.split()
    if len(words) <= 6:
        non_greeting = [
            w for w in words
            if w not in GREETING_KEYWORDS
            and w not in {"a", "an", "the", "i", "me", "you", "please", "thanks", "thank"}
        ]
        if len(non_greeting) == 0:
            return True
    # Phrase-level match
    for phrase in GREETING_KEYWORDS:
        if phrase in lower and len(words) <= 8:
            # Make sure most of the message IS the greeting phrase
            non_phrase_words = lower.replace(phrase, "").split()
            real_extra = [
                w for w in non_phrase_words
                if len(w) > 2 and w not in {"the", "and", "for", "are", "you"}
            ]
            if len(real_extra) <= 1:
                return True
    return False


def ask_question(query: str) -> str:
    # Rule 2 & 7 — Noise / random input
    if _is_noise(query):
        return NOISE_RESPONSE

    # Rule 1 — Greetings & small talk
    if _is_greeting(query):
        return GREETING_RESPONSE

    # Retrieve relevant document context (optimized from k=8 to k=4 to save tokens)
    if vector_db is None:
        logger.error("Vector DB was not initialized at startup.")
        return RETRIEVAL_ERROR_RESPONSE

    try:
        t0 = time.time()
        logger.info(f"Starting Qdrant retrieval for query: {query}")
        search_results = vector_db.max_marginal_relevance_search(
            query=query, k=4, fetch_k=10
        )
        logger.info(f"Qdrant retrieval finished in {time.time()-t0:.2f}s")
    except Exception as e:
        logger.error(f"Retrieval Error: {e}")
        return RETRIEVAL_ERROR_RESPONSE

    context = "\n\n".join(
        [
            f"Page {doc.metadata.get('page_label', 'N/A')}:\n{doc.page_content}"
            for doc in search_results
        ]
    )

    prompt = f"""You are a document-based chatbot. Follow ALL rules below strictly.

RULE 1 – SINGLE RESPONSE:
Generate only one final answer. Do not attempt multiple generations or self-retries.

RULE 2 – GREETING:
If input is a greeting (hello, hi, hey, how are you, what can you do),
respond politely and explain you answer document-based questions.

RULE 3 – NOISE:
If input is random text, symbols, or meaningless words, respond:
"I couldn't understand your question. Please ask a clear question related to the document."

RULE 4 – RETRIEVAL FAILURE:
If document context is empty or unavailable, respond:
"I'm having trouble accessing the document right now."

RULE 5 – HALLUCINATION PREVENTION:
Never guess or fabricate information when context is missing.

RULE 6 – ANSWER NOT FOUND:
If the answer is not in the document context, respond exactly:
"I could not find this information in the document."

RULE 7 – OUT OF SCOPE:
If the question is unrelated to the document, respond:
"I can only answer questions based on the uploaded document."

RULE 8 – CLARIFICATION:
If the question is unclear or incomplete, ask for clarification instead of multiple attempts.

RULE 9 – EFFICIENCY & TONE:
Keep answers short, simple, polite, and helpful. Avoid unnecessary reasoning steps.

=== DOCUMENT CONTEXT ===
{context}

=== USER QUESTION ===
{query}

=== YOUR ANSWER ==="""

    try:
        t1 = time.time()
        logger.info("Starting Gemini LLM generation...")
        response = llm.invoke(prompt)
        logger.info(f"Gemini LLM generation finished in {time.time()-t1:.2f}s")
        return response.content
    except Exception as e:
        err_str = str(e).lower()
        if any(kw in err_str for kw in ("429", "quota", "rate", "resource_exhausted")):
            return RATE_LIMIT_RESPONSE
        logger.error(f"LLM Error: {e}")
        return RETRIEVAL_ERROR_RESPONSE