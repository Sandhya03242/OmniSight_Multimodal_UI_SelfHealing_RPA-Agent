from pathlib import Path
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END,
)

from backend.action.engine import (
    extract_fixes,
)

from backend.vision.analyzer import (
    analyze_ui,
    verify_ui,
)


class HealingState(TypedDict, total=False):
    original_screenshot: str
    original_html: str
    screenshot_path: str
    html_path: str
    issues: list
    fixes: list
    css_fix: str
    verification: dict
    iteration: int
    max_iterations: int
    healed: bool
    message: str


async def analyze_node(
    state: HealingState,
):
    html = Path(
        state["html_path"]
    ).read_text(
        encoding="utf-8"
    )

    analysis = analyze_ui(
        state["screenshot_path"],
        html,
    )

    fixes_result = extract_fixes(
        analysis
    )

    return {
        "issues": analysis.get(
            "issues",
            []
        ),
        "fixes": fixes_result.get(
            "fixes",
            []
        ),
    }


async def generate_fix_node(
    state: HealingState,
):
    fixes = state.get(
        "fixes",
        []
    )

    css_blocks = []

    for fix in fixes:
        css = fix.get(
            "css_fix",
            ""
        )

        if css:
            css_blocks.append(
                css.strip()
            )

    css_fix = "\n\n".join(
        css_blocks
    )

    return {
        "css_fix": css_fix
    }


async def apply_fix_node(
    state: HealingState,
):
    from backend.healing.loop import (
        apply_css_and_capture,
    )

    css_fix = state.get(
        "css_fix",
        ""
    )

    iteration = (
        state.get(
            "iteration",
            0,
        )
        + 1
    )

    capture = await apply_css_and_capture(
        css_fix,
        device="mobile",
        filename=(
            f"healed_{iteration}.png"
        ),
    )

    return {
        "screenshot_path": capture[
            "screenshot"
        ],
        "html_path": capture[
            "html"
        ],
        "iteration": iteration,
    }


async def verify_node(
    state: HealingState,
):
    verification = verify_ui(
        state["screenshot_path"],
        state["html_path"],
        {
            "issues": state.get(
                "issues",
                []
            )
        },
    )

    fixed = bool(
        verification.get(
            "fixed",
            False,
        )
    )

    return {
        "verification": verification,
        "healed": fixed,
        "message": (
            "UI bug fixed"
            if fixed
            else "UI bug still present"
        ),
    }


def route_after_verify(
    state: HealingState,
):
    if state.get(
        "healed",
        False,
    ):
        return "fixed"

    if (
        state.get(
            "iteration",
            0,
        )
        >= state.get(
            "max_iterations",
            2,
        )
    ):
        return "failed"

    return "retry"


def build_healing_graph():
    graph = StateGraph(
        HealingState
    )

    graph.add_node(
        "analyze",
        analyze_node,
    )

    graph.add_node(
        "generate_fix",
        generate_fix_node,
    )

    graph.add_node(
        "apply_fix",
        apply_fix_node,
    )

    graph.add_node(
        "verify",
        verify_node,
    )

    graph.set_entry_point(
        "analyze"
    )

    graph.add_edge(
        "analyze",
        "generate_fix",
    )

    graph.add_edge(
        "generate_fix",
        "apply_fix",
    )

    graph.add_edge(
        "apply_fix",
        "verify",
    )

    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "fixed": END,
            "retry": "analyze",
            "failed": END,
        },
    )

    return graph.compile()


async def run_healing_agent(
    screenshot_path,
    html_path,
    max_iterations=2,
):
    graph = build_healing_graph()

    initial_state = {
        "original_screenshot": screenshot_path,
        "original_html": html_path,
        "screenshot_path": screenshot_path,
        "html_path": html_path,
        "iteration": 0,
        "max_iterations": max_iterations,
        "healed": False,
    }

    result = await graph.ainvoke(
        initial_state
    )

    return result