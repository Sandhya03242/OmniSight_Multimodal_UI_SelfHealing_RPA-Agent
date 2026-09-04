from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
)

from pydantic import BaseModel

from backend.browser.navigator import run_navigation_sync

from backend.agent.self_healing import (
    run_self_healing,
)

from backend.github.integration import (
    create_pull_request,
)



# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="OmniSight",
    description=(
        "Multimodal UI Self-Healing "
        "RPA Agent"
    ),
    version="1.0.0",
)


# =====================================================
# REQUEST MODELS
# =====================================================


class BuildEvent(BaseModel):
    """
    CI/CD webhook payload.
    """

    event: str

    repository: str

    branch: str

    commit: str

    build_id: str | None = None

    environment: str = "staging"


class GitHubRequest(BaseModel):
    """
    GitHub Pull Request request.
    """

    repository: str

    base_branch: str = "main"


# =====================================================
# IN-MEMORY RESULTS
# =====================================================

RESULTS = {

    "navigation": None,

    "vision_audit": None,

    "self_healing": None,
}


# =====================================================
# ROOT
# =====================================================


@app.get("/")
async def root():

    return {

        "project":
            "OmniSight",

        "status":
            "running",

        "version":
            "1.0.0",

        "architecture": {

            "api":
                "FastAPI",

            "browser":
                "Playwright",

            "vision":
                "Qwen3.5-0.8B",

            "agent":
                "LangChain",

            "github":
                "PyGithub",
        },

        "pipeline": [

            "navigation",

            "vision_audit",

            "self_healing",

            "github",
        ],

        "endpoints": [

            "/navigation/run",

            "/navigation/results",

            "/vision-audit/analyze",

            "/vision-audit/results",

            "/self-healing/run",

            "/self-healing/results",

            "/github/create-pr",

            "/pipeline/run",

            "/webhook/build",
        ],
    }


# =====================================================
# HEALTH CHECK
# =====================================================


@app.get("/health")
async def health():

    return {

        "status":
            "healthy",

        "service":
            "OmniSight",

    }


# =====================================================
# NAVIGATION
# =====================================================


@app.post("/navigation/run")
async def navigation_run():

    print("\n")
    print("=" * 70)
    print(
        "          OMNISIGHT NAVIGATION"
    )
    print("=" * 70)

    print(
        "\n[FASTAPI] "
        "Starting browser navigation..."
    )

    try:

        navigation = await run_navigation_sync()

        RESULTS[
            "navigation"
        ] = navigation

        return {

            "status":
                "completed",

            "module":
                "navigation",

            "results":
                navigation,
        }

    except Exception as error:

        print(
            "[ERROR]",
            str(error),
        )

        raise HTTPException(

            status_code=500,

            detail=str(error),
        )


# =====================================================
# NAVIGATION RESULTS
# =====================================================


@app.get("/navigation/results")
async def navigation_results():

    if RESULTS[
        "navigation"
    ] is None:

        return {

            "status":
                "not_run",

            "message":
                "Run POST /navigation/run first.",
        }

    return {

        "status":
            "completed",

        "module":
            "navigation",

        "results":
            RESULTS[
                "navigation"
            ],
    }


# =====================================================
# VISION AUDIT
# =====================================================


@app.post("/vision-audit/analyze")
async def vision_audit_analyze():

    navigation = RESULTS.get(
        "navigation"
    )

    if not navigation:

        raise HTTPException(

            status_code=400,

            detail=(
                "Navigation has not been run. "
                "Run POST /navigation/run first."
            ),
        )

    print("\n")
    print("=" * 70)
    print(
        "          OMNISIGHT VISION AUDIT"
    )
    print("=" * 70)

    try:

        # -------------------------------------------------
        # MOBILE RESULT
        # -------------------------------------------------

        mobile = navigation.get(
            "mobile"
        )

        if not mobile:

            raise HTTPException(

                status_code=500,

                detail=(
                    "Mobile navigation result "
                    "was not found."
                ),
            )

        # -------------------------------------------------
        # IMPORT ANALYZER
        # -------------------------------------------------

        from backend.vision.analyzer import (
            analyze_ui,
        )

        # -------------------------------------------------
        # SCREENSHOT
        # -------------------------------------------------

        screenshot = mobile[
            "screenshots"
        ][
            "checkout"
        ]

        # -------------------------------------------------
        # HTML
        # -------------------------------------------------

        html = mobile[
            "html"
        ][
            "checkout"
        ]

        # -------------------------------------------------
        # RUN VISION ANALYSIS
        # -------------------------------------------------

        analysis = analyze_ui(

            screenshot,

            html,

            mobile,
        )

        RESULTS[
            "vision_audit"
        ] = analysis

        return {

            "status":
                "completed",

            "module":
                "vision_audit",

            "analysis":
                analysis,
        }

    except HTTPException:

        raise

    except Exception as error:

        print(
            "[VISION ERROR]",
            str(error),
        )

        raise HTTPException(

            status_code=500,

            detail=str(error),
        )


# =====================================================
# VISION AUDIT RESULTS
# =====================================================


@app.get("/vision-audit/results")
async def vision_audit_results():

    if RESULTS[
        "vision_audit"
    ] is None:

        return {

            "status":
                "not_run",

            "message":
                (
                    "Run POST "
                    "/vision-audit/analyze first."
                ),
        }

    return {

        "status":
            "completed",

        "module":
            "vision_audit",

        "analysis":
            RESULTS[
                "vision_audit"
            ],
    }


# =====================================================
# SELF-HEALING
# =====================================================


@app.post("/self-healing/run")
async def self_healing_run():

    print("\n")
    print("=" * 70)
    print(
        "          OMNISIGHT SELF-HEALING"
    )
    print("=" * 70)

    print(
        "\n[FASTAPI] "
        "Starting self-healing agent..."
    )

    try:

        result = await run_self_healing(

            introduce_bug=True,

            max_attempts=3,
        )

        RESULTS[
            "self_healing"
        ] = result

        return {

            "status":
                "completed",

            "module":
                "self_healing",

            "result":
                result,
        }

    except Exception as error:

        print(
            "[SELF-HEALING ERROR]",
            str(error),
        )

        raise HTTPException(

            status_code=500,

            detail=str(error),
        )


# =====================================================
# SELF-HEALING RESULTS
# =====================================================


@app.get("/self-healing/results")
async def self_healing_results():

    if RESULTS[
        "self_healing"
    ] is None:

        return {

            "status":
                "not_run",

            "message":
                (
                    "Run POST "
                    "/self-healing/run first."
                ),
        }

    return {

        "status":
            "completed",

        "module":
            "self_healing",

        "result":
            RESULTS[
                "self_healing"
            ],
    }


# =====================================================
# GITHUB
# =====================================================


@app.post("/github/create-pr")
async def github_create_pr(
    request: GitHubRequest,
):

    print("\n")
    print("=" * 70)
    print(
        "          OMNISIGHT GITHUB"
    )
    print("=" * 70)

    try:

        result = create_pull_request(

            repository_name=
                request.repository,

            base_branch=
                request.base_branch,
        )

        return {

            "status":
                "completed",

            "module":
                "github",

            "github":
                result,
        }

    except Exception as error:

        print(
            "[GITHUB ERROR]",
            str(error),
        )

        raise HTTPException(

            status_code=500,

            detail=str(error),
        )


# =====================================================
# COMPLETE PIPELINE
# =====================================================


@app.post("/pipeline/run")
async def pipeline_run():

    print("\n")
    print("=" * 70)
    print(
        "          OMNISIGHT COMPLETE PIPELINE"
    )
    print("=" * 70)

    # =================================================
    # 1. NAVIGATION
    # =================================================

    print("\n")
    print("-" * 70)
    print(
        "1. NAVIGATION"
    )
    print("-" * 70)

    try:

        navigation = await run_week1()

        RESULTS[
            "navigation"
        ] = navigation

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Navigation failed: "
                + str(error)
            ),
        )


    # =================================================
    # 2. VISION AUDIT
    # =================================================

    print("\n")
    print("-" * 70)
    print(
        "2. VISION AUDIT"
    )
    print("-" * 70)

    try:

        mobile = navigation.get(
            "mobile"
        )

        if not mobile:

            raise RuntimeError(
                "Mobile navigation result missing."
            )

        from backend.vision.analyzer import (
            analyze_ui,
        )

        vision_audit = analyze_ui(

            mobile[
                "screenshots"
            ][
                "checkout"
            ],

            mobile[
                "html"
            ][
                "checkout"
            ],

            mobile,
        )

        RESULTS[
            "vision_audit"
        ] = vision_audit

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Vision audit failed: "
                + str(error)
            ),
        )


    # =================================================
    # 3. SELF-HEALING
    # =================================================

    print("\n")
    print("-" * 70)
    print(
        "3. SELF-HEALING"
    )
    print("-" * 70)

    try:

        self_healing = await run_self_healing(

            introduce_bug=True,

            max_attempts=3,
        )

        RESULTS[
            "self_healing"
        ] = self_healing

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Self-healing failed: "
                + str(error)
            ),
        )


    # =================================================
    # 4. PIPELINE RESULT
    # =================================================

    print("\n")
    print("=" * 70)
    print(
        "          PIPELINE COMPLETED"
    )
    print("=" * 70)

    return {

        "status":
            "completed",

        "project":
            "OmniSight",

        "pipeline": [

            "navigation",

            "vision_audit",

            "self_healing",
        ],

        "navigation":
            navigation,

        "vision_audit":
            vision_audit,

        "self_healing":
            self_healing,
    }


# =====================================================
# CI/CD WEBHOOK
# =====================================================


@app.post("/webhook/build")
async def build_webhook(

    event: BuildEvent,

    background_tasks:
        BackgroundTasks,
):

    print("\n")
    print("=" * 70)
    print(
        "             CI/CD EVENT"
    )
    print("=" * 70)

    print(
        "Repository:",
        event.repository,
    )

    print(
        "Branch:",
        event.branch,
    )

    print(
        "Commit:",
        event.commit,
    )

    print(
        "Build ID:",
        event.build_id,
    )

    print(
        "Environment:",
        event.environment,
    )

    # =================================================
    # START PIPELINE IN BACKGROUND
    # =================================================

    background_tasks.add_task(
        pipeline_background
    )

    return {

        "status":
            "accepted",

        "message":
            "OmniSight pipeline started.",

        "repository":
            event.repository,

        "branch":
            event.branch,

        "commit":
            event.commit,

        "build_id":
            event.build_id,

        "environment":
            event.environment,
    }


# =====================================================
# BACKGROUND PIPELINE
# =====================================================


async def pipeline_background():

    try:

        await pipeline_run()

    except Exception as error:

        print(
            "\n[BACKGROUND PIPELINE ERROR]"
        )

        print(
            str(error)
        )