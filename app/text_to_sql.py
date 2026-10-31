"""
text_to_sql.py — FEATURE 1.

Turns a natural-language programming question into a SQL query,
runs it, and turns the result into a friendly answer.

Three steps, clearly separated so each is easy to understand and test.
"""

import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.database import run_select

# Load the schema once, when this file is first imported.
with open(settings.schema_path, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

# temperature=0 makes the model more predictable. Good for SQL.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)


# ---------- STEP 1 PROMPT: write the SQL ----------
# Keep only the intended {placeholders} in this prompt.
SQL_PROMPT = PromptTemplate.from_template(
    """You are an expert programming education assistant.
Write ONE valid SQLite SELECT query that answers the user's question.

Rules:
- Only produce a SELECT query. Never write INSERT, UPDATE, DELETE, or DROP.
- Only use the tables and columns in the schema below.
- Use the concepts table for programming explanations and difficulty.
- Join concepts to languages and topics when the question mentions a language or topic.
- Join exercises to concepts when the user asks for practice exercises.
- Join attempts to learners and exercises when the user asks about learner activity.
- The schema gives "sample_values" for text columns. Prefer matching those exactly.
- Match text case-insensitively and allow singular/plural wording: compare with LIKE
  and wrap the value in %, e.g. WHERE lower(c.name) LIKE lower('%python%').
- Return ONLY the SQL query, with no explanation and no markdown fences.

Database schema (JSON):
{schema}

User question:
{question}

SQL query:"""
)

# ---------- STEP 3 PROMPT: describe the results ----------
ANSWER_PROMPT = PromptTemplate.from_template(
    """You are a friendly coding mentor.
Turn the raw database results into a short, helpful, natural answer.

Guidelines:
- Only use the data provided. Never invent concepts, exercises, or explanations.
- If the results are empty, say you couldn't find a match and suggest different search terms.
- Keep the answer conversational and concise.
- When relevant, mention the programming language, topic, and difficulty.
- If exercises are returned, explain what the learner is being asked to practice.

User question:
{question}

Raw database results:
{results}

Your answer:"""
)


def _clean_sql(raw: str) -> str:
    """
    Remove markdown fences and a single trailing semicolon.
    This lets the safety check distinguish one query from multiple statements.
    """
    return raw.replace("```sql", "").replace("```", "").strip().rstrip(";").strip()


def _is_safe_select(sql: str) -> bool:
    """
    Allow ONLY a single SELECT statement.
    Never trust generated SQL blindly.
    """
    lowered = sql.lower()
    starts_with_select = lowered.startswith("select")

    has_write_keyword = bool(
        re.search(
            r"\b(insert|update|delete|drop|alter|create|replace|truncate)\b",
            lowered,
        )
    )

    has_semicolon = ";" in lowered

    return starts_with_select and not has_write_keyword and not has_semicolon


def search_learning_content(question: str) -> str:
    """The full pipeline: question -> SQL -> rows -> friendly answer."""

    # STEP 1: ask the LLM to write SQL
    raw_sql = (SQL_PROMPT | llm | StrOutputParser()).invoke(
        {"schema": json.dumps(SCHEMA), "question": question}
    )

    sql = _clean_sql(raw_sql)
    print(f"[text_to_sql] generated SQL: {sql}")

    # STEP 2: check the SQL, then run it
    if not _is_safe_select(sql):
        return "I can only search the programming learning database, so I couldn't run that request."

    rows = run_select(sql)

    # STEP 3: ask the LLM to explain the results
    answer = (ANSWER_PROMPT | llm | StrOutputParser()).invoke(
        {
            "question": question,
            "results": rows if rows else "The query returned no rows.",
        }
    )

    return answer


# Test this file ALONE, without the agent or UI.
# Run: python -m app.text_to_sql
if __name__ == "__main__":
    print(
        search_learning_content(
            "Show me all beginner programming exercises"
        )
    )