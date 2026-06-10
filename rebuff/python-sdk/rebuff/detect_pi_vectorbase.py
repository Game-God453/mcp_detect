from typing import Dict, Union

import pinecone
try:
    from langchain_community.vectorstores import Pinecone, Chroma
except ImportError:
    from langchain.vectorstores import Pinecone, Chroma
    
from langchain_openai import OpenAIEmbeddings


# https://api.python.langchain.com/en/latest/vectorstores/langchain.vectorstores.pinecone.Pinecone.html
def detect_pi_using_vector_database(
    input: str, similarity_threshold: float, vector_store: Union[Pinecone, Chroma]
) -> Dict:
    """
    Detects Prompt Injection using similarity search with vector database.

    Args:
        input (str): user input to be checked for prompt injection
        similarity_threshold (float): The threshold for similarity between entries in vector database and the user input.
        vector_store (Union[Pinecone, Chroma]): Vector database of prompt injections

    Returns:
        Dict (str, Union[float, int]): top_score (float) that contains the highest score wrt similarity between vector database and the user input.
                                        count_over_max_vector_score (int) holds the count for times the similarity score (between vector database and the user input)
                                        came out more than the top_score and similarty_threshold.
    """

    top_k = 20
    results = vector_store.similarity_search_with_score(input, top_k)

    # If using Chroma, the scores are L2 distances (lower is better), 
    # but the logic below assumes cosine similarity (higher is better).
    # We invert the distance to get a similarity score in [0, 1] range.
    if isinstance(vector_store, Chroma):
        # Using a simple inversion: Similarity = 1 - Distance
        # For L2 normalized vectors, this is a reasonable approximation for ranking
        # Clamping to 0 if distance > 1
        results = [(doc, max(0.0, 1.0 - score)) for doc, score in results]

    top_score = 0
    count_over_max_vector_score = 0

    for _, score in results:
        if score is None:
            continue

        if score > top_score:
            top_score = score

        if score >= similarity_threshold and score > top_score:
            count_over_max_vector_score += 1

    vector_score = {
        "top_score": top_score,
        "count_over_max_vector_score": count_over_max_vector_score,
    }

    return vector_score


def init_pinecone(api_key: str, index: str, openai_api_key: str, openai_api_base: str = None) -> Pinecone:
    """
    Initializes connection with the Pinecone vector database using existing (rebuff) index.

    Args:
        api_key (str): Pinecone API key
        index (str): Pinecone index name
        openai_api_key (str): Open AI API key
        openai_api_base (str): Open AI API base

    Returns:
        vector_store (Pinecone)

    """
    if not api_key:
        raise ValueError("Pinecone apikey definition missing")

    pc = pinecone.Pinecone(api_key=api_key)
    pc_index = pc.Index(index)

    openai_embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key, model="text-embedding-ada-002", openai_api_base=openai_api_base
    )

    vector_store = Pinecone(pc_index, openai_embeddings, text_key="input")

    return vector_store


def init_chroma(openai_api_key: str, collection_name: str = "rebuff", persist_directory: str = "./chroma_db", openai_api_base: str = None) -> Chroma:
    """
    Initializes connection with the Chroma vector database.

    Args:
        openai_api_key (str): Open AI API key
        collection_name (str): Collection name
        persist_directory (str): Directory to persist the database
        openai_api_base (str): Open AI API base

    Returns:
        vector_store (Chroma)
    """
    openai_embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key, model="text-embedding-ada-002", openai_api_base=openai_api_base
    )

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=openai_embeddings,
        persist_directory=persist_directory,
    )

    return vector_store
