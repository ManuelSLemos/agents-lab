"""Publish the SQL eval cases to Phoenix and run one experiment per implementation.

    docker compose run --rm adk uv run python -m evals.phoenix_experiments

Compare the experiments in the Phoenix UI (Datasets > sql-guardrails > Experiments).
"""

from phoenix.client import Client
from phoenix.client.experiments import run_experiment

from .cases import ATTACKS, LEGIT
from .implementations import ALLOWED, BLOCKED, original, secure

DATASET = "sql-guardrails"


def build_examples() -> list[dict]:
    cases = [(ATTACKS, "attack", BLOCKED), (LEGIT, "legit", ALLOWED)]
    return [
        {"input": {"case": name, "sql": sql}, "output": {"expected": expected}, "metadata": {"kind": kind}}
        for group, kind, expected in cases
        for name, sql in group.items()
    ]


def correct(output: str, expected: dict) -> bool:
    """1 when the implementation made the expected decision for the case."""
    return output == expected["expected"]


def main() -> None:
    client = Client()  # reads PHOENIX_BASE_URL
    examples = build_examples()
    dataset = client.datasets.create_dataset(
        name=DATASET,
        examples=examples,
    )
    for name, implementation in {"original": original, "secure": secure}.items():
        run_experiment(
            dataset=dataset,
            task=lambda input, impl=implementation: impl(input["sql"]),
            evaluators=[correct],
            experiment_name=name,
            client=client,
        )


if __name__ == "__main__":
    main()
