"""Two-agent CrewAI crew for the deployable matrix sample.

A researcher (with one tool) and an editor run two sequential tasks. Each
/chat invocation drives LLM calls plus tasks, so the deployed agent emits
llm + agent + crewaitask spans for the heavy tier to assert. Mirrors the
emission-tier test/instrumentation-matrix/cells/crewai_sample.py so both tiers
exercise the same shape. Pinned to crewai 1.1.0 (see that suite's FINDINGS
F-004: 1.14 is unresolvable against traceloop-sdk 0.60).
"""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool


@tool("country_capital_lookup")
def country_capital_lookup(country: str) -> str:
    """Return the capital city of a country."""
    return f"The capital of {country} is Paris."


def create_crew() -> Crew:
    researcher = Agent(
        role="Geography researcher",
        goal="Answer the user's question, using the lookup tool for capitals.",
        backstory="You call the lookup tool to answer geography questions.",
        llm="gpt-4o-mini",
        tools=[country_capital_lookup],
        allow_delegation=False,
        verbose=False,
    )
    editor = Agent(
        role="Editor",
        goal="Shorten the researcher's answer to a single short sentence.",
        backstory="You compress answers to the minimum useful form.",
        llm="gpt-4o-mini",
        allow_delegation=False,
        verbose=False,
    )

    research_task = Task(
        description="Answer the user's question: {question}",
        expected_output="A sentence answering the question.",
        agent=researcher,
    )
    edit_task = Task(
        description="Shorten the researcher's previous answer to one short sentence.",
        expected_output="One short sentence.",
        agent=editor,
        context=[research_task],
    )

    return Crew(
        agents=[researcher, editor],
        tasks=[research_task, edit_task],
        process=Process.sequential,
        verbose=False,
    )
