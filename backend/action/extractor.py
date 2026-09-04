import json
import re


def extract_json(
    response: str,
):

    response = response.strip()

    response = re.sub(
        r"```json",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"```",
        "",
        response,
    )

    response = response.strip()

    try:

        return json.loads(
            response
        )

    except json.JSONDecodeError:

        start = response.find(
            "{"
        )

        end = response.rfind(
            "}"
        )

        if (
            start != -1
            and end != -1
        ):

            try:

                return json.loads(
                    response[
                        start:
                        end + 1
                    ]
                )

            except json.JSONDecodeError:

                pass

    return {

        "status":
            "parse_error",

        "issues":
            [],
    }


def extract_code_blocks(
    response: str,
):

    pattern = (
        r"```"
        r"(?:css|jsx|javascript|js|html|react)?"
        r"\s*"
        r"(.*?)"
        r"```"
    )

    return [
        item.strip()
        for item in re.findall(
            pattern,
            response,
            flags=
                re.DOTALL
                | re.IGNORECASE,
        )
    ]