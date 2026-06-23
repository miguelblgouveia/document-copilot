# Retrieval

Hybrid search over SEC filing chunks stored in Supabase Postgres. For the full path from analyst question through agent tools to grounding validation, see [`../assistant/README.md`](../assistant/README.md).

Each query runs **semantic** (pgvector) and **keyword** (full-text) searches in parallel, fuses the ranked lists with **Reciprocal Rank Fusion (RRF)**, then hydrates the top hits with document metadata and optional neighboring chunks for context.

---

## Pipeline

```mermaid
flowchart TD
    Q[User query + optional SearchFilters] --> PAR[Parallel prep]
    PAR --> E[embed_query full query]
    PAR --> KW[extract_fts_keywords LLM]

    E -->|Ollama embedding API| VEC[Query vector]
    KW -->|Ollama LLM (qwen3)| FTSQ[3-5 keyword terms]

    VEC --> DUAL[semantic_search + full_text_search in parallel]
    FTSQ --> DUAL

    DUAL -->|top candidate_k each| SEM_IDS[Semantic ranked IDs]
    DUAL --> FTS_IDS[FTS ranked IDs]

    SEM_IDS --> RRF[reciprocal_rank_fusion]
    FTS_IDS --> RRF
    RRF -->|slice to top_k| FUSED[Fused chunk IDs + scores]

    FUSED --> HYDRATE[get_chunks_by_ids]
    HYDRATE --> NEIGH[get_surrounding_chunks per hit]
    NEIGH --> OUT[list of RetrievedPassage]

    OUT --> FMT[format_passages_for_agent]
    FMT --> AGENT[Agent tool / smoke script output]