"""Compare sql_agent and sql_agent_secure on the same cases.

    docker compose run --rm --no-deps adk uv run python -m evals.report
"""

from .cases import ATTACKS, CLEAN_ANSWERS, INDIRECT, LEAKY_ANSWERS, LEGIT, PROMPT_ATTACKS, PROMPT_LEGIT
from .implementations import (
    ALLOWED,
    BLOCKED,
    answer_replaced,
    is_marked_as_data,
    original,
    original_answerer,
    original_result,
    original_writer,
    prompt_blocked,
    secure,
    secure_answerer,
    secure_result,
    secure_writer,
)


def score(implementation) -> tuple[list[str], list[str]]:
    """Return the attacks that got through and the legitimate queries that broke."""
    leaked = [name for name, sql in ATTACKS.items() if implementation(sql) != BLOCKED]
    broken = [name for name, sql in LEGIT.items() if implementation(sql) != ALLOWED]
    return leaked, broken


def unmarked(result_of) -> list[str]:
    """Return the poisoned values that reach the LLM without being marked as data."""
    return [name for name, sql in INDIRECT.items() if not is_marked_as_data(result_of(sql))]


def main() -> None:
    results = {name: score(impl) for name, impl in {"original": original, "secure": secure}.items()}
    print(f"{'':28}{'original':>10}{'secure':>10}")
    rows = (("attacks blocked", len(ATTACKS), 0), ("legit queries OK", len(LEGIT), 1))
    for title, total, index in rows:
        cells = [f"{total - len(results[name][index])}/{total}" for name in ("original", "secure")]
        print(f"{title:28}{cells[0]:>10}{cells[1]:>10}")
    marked = {"original": unmarked(original_result), "secure": unmarked(secure_result)}
    cells = [f"{len(INDIRECT) - len(marked[name])}/{len(INDIRECT)}" for name in ("original", "secure")]
    print(f"{'poisoned data marked':28}{cells[0]:>10}{cells[1]:>10}")
    agents = {"original": (original_writer, original_answerer), "secure": (secure_writer, secure_answerer)}
    guard_rows = (
        ("prompts stopped (before)", PROMPT_ATTACKS, lambda w, a, t: prompt_blocked(w, t), True),
        ("legit prompts passed", PROMPT_LEGIT, lambda w, a, t: not prompt_blocked(w, t), True),
        ("leaky answers fixed (after)", LEAKY_ANSWERS, lambda w, a, t: answer_replaced(a, t), True),
        ("clean answers untouched", CLEAN_ANSWERS, lambda w, a, t: not answer_replaced(a, t), True),
    )
    for title, cases, check, _ in guard_rows:
        cells = []
        for name in ("original", "secure"):
            writer, answerer = agents[name]
            ok = sum(check(writer, answerer, text) for text in cases.values())
            cells.append(f"{ok}/{len(cases)}")
        print(f"{title:28}{cells[0]:>10}{cells[1]:>10}")
    for name, (leaked, broken) in results.items():
        for case in leaked:
            print(f"  [{name}] attack got through: {case}")
        for case in broken:
            print(f"  [{name}] legit query broken: {case}")
        for case in marked[name]:
            print(f"  [{name}] poisoned data reaches the LLM unmarked: {case}")


if __name__ == "__main__":
    main()
