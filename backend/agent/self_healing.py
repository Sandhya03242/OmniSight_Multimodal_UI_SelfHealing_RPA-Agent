from pathlib import Path

from playwright.async_api import (
    async_playwright,
)

from backend.browser.navigator import (
    login,
    open_checkout,
    save_screenshot,
    save_html,
    get_page_dimensions,
)

from backend.vision.analyzer import (
    analyze_ui,
)

from backend.action.fixer import (
    generate_fix,
)

from backend.agent.tools import (
    detect_issue,
    select_fix,
    verification_decision,
)


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


SCREENSHOT_DIR = (
    ROOT_DIR
    / "backend"
    / "screenshots"
    / "mobile"
)


HTML_DIR = (
    ROOT_DIR
    / "backend"
    / "outputs"
    / "html"
)


async def run_self_healing(
    introduce_bug=True,
    max_attempts=3,
):

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport={
                "width": 375,
                "height": 812,
            }
        )

        page = await context.new_page()

        try:

            # ---------------------------
            # Initial browser navigation
            # ---------------------------

            await login(page)

            await open_checkout(page)

            # ---------------------------
            # Deliberate bug
            # ---------------------------

            if introduce_bug:

                print(
                    "[BUG] Hiding Continue button"
                )

                await page.add_style_tag(
                    content="""
                    #continue {
                        display: none !important;
                    }
                    """
                )

            final_result = None

            # ---------------------------
            # Agent loop
            # ---------------------------

            for attempt in range(
                1,
                max_attempts + 1,
            ):

                print(
                    f"\n"
                    f"===== ATTEMPT {attempt} ====="
                )

                # -----------------------
                # Capture
                # -----------------------

                screenshot = (
                    await save_screenshot(
                        page,
                        "mobile",
                        f"week3_attempt_{attempt}.png",
                    )
                )

                html_file = (
                    await save_html(
                        page,
                        "mobile",
                        f"week3_attempt_{attempt}.html",
                    )
                )

                dimensions = (
                    await get_page_dimensions(
                        page
                    )
                )

                continue_visible = (
                    await page.locator(
                        "#continue"
                    ).is_visible()
                )

                browser_state = {

                    "dimensions":
                        dimensions,

                    "continue_visible":
                        continue_visible,
                }

                # -----------------------
                # Week 2 analysis
                # -----------------------

                analysis = analyze_ui(

                    screenshot,

                    html_file,

                    browser_state,
                )

                # -----------------------
                # LangChain tool
                # -----------------------

                decision = detect_issue.invoke(
                    {
                        "status":
                            analysis[
                                "status"
                            ]
                    }
                )

                print(
                    "[LANGCHAIN]",
                    decision,
                )

                # -----------------------
                # No issue
                # -----------------------

                if decision == "NO_ISSUE":

                    final_result = {

                        "status":
                            "passed",

                        "attempt":
                            attempt,
                    }

                    break

                # -----------------------
                # Generate fix
                # -----------------------

                fix_result = (
                    generate_fix(
                        analysis
                    )
                )

                if not fix_result[
                    "fixes"
                ]:

                    final_result = {

                        "status":
                            "failed",

                        "reason":
                            "No fix generated.",
                    }

                    break

                # -----------------------
                # Apply fix
                # -----------------------

                for fix in fix_result[
                    "fixes"
                ]:

                    css = fix.get(
                        "code"
                    )

                    if not css:
                        continue

                    # LangChain tool
                    selected_css = (
                        select_fix.invoke(
                            {
                                "issue_type":
                                    (
                                        analysis[
                                            "issues"
                                        ][0].get(
                                            "type"
                                        )
                                    )
                            }
                        )
                    )

                    if selected_css:

                        css = selected_css

                    print(
                        "\n[FIX]"
                    )

                    print(css)

                    await page.add_style_tag(
                        content=css
                    )

                # -----------------------
                # Verify
                # -----------------------

                continue_visible = (
                    await page.locator(
                        "#continue"
                    ).is_visible()
                )

                dimensions = (
                    await get_page_dimensions(
                        page
                    )
                )

                overflow_fixed = (
                    dimensions[
                        "documentWidth"
                    ]
                    <=
                    dimensions[
                        "viewportWidth"
                    ]
                )

                passed = (
                    continue_visible
                    and overflow_fixed
                )

                print(
                    "\n[VERIFY]"
                )

                print(
                    "Continue:",
                    continue_visible,
                )

                print(
                    "Overflow:",
                    overflow_fixed,
                )

                verification = (
                    verification_decision.invoke(
                        {
                            "passed":
                                passed,

                            "attempt":
                                attempt,

                            "max_attempts":
                                max_attempts,
                        }
                    )
                )

                print(
                    "[LANGCHAIN]",
                    verification,
                )

                # -----------------------
                # Screenshot after fix
                # -----------------------

                after_fix = (
                    SCREENSHOT_DIR
                    / f"after_fix_{attempt}.png"
                )

                await page.screenshot(
                    path=str(after_fix),
                    full_page=True,
                )

                if passed:

                    final_result = {

                        "status":
                            "fixed",

                        "attempt":
                            attempt,

                        "verification":
                            "passed",

                        "screenshot":
                            str(after_fix),

                        "fix":
                            fix_result,
                    }

                    break

            if final_result is None:

                final_result = {

                    "status":
                        "failed",

                    "reason":
                        "Maximum attempts reached.",
                }

            return final_result

        finally:

            await context.close()
            await browser.close()