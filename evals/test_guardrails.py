"""ADK callbacks: they are tested through the agents, so a callback that is not attached fails too."""

import pytest

from .cases import CLEAN_ANSWERS, LEAKY_ANSWERS, PROMPT_ATTACKS, PROMPT_BYPASSES, PROMPT_LEGIT
from .implementations import answer_replaced, prompt_blocked, secure_answerer, secure_writer


def test_callbacks_are_attached_to_the_agents():
    assert secure_writer.canonical_before_model_callbacks
    assert secure_answerer.canonical_after_model_callbacks


@pytest.mark.parametrize("text", PROMPT_ATTACKS.values(), ids=PROMPT_ATTACKS.keys())
def test_prompt_attack_is_stopped_before_the_model(text):
    assert prompt_blocked(secure_writer, text)


@pytest.mark.parametrize("text", PROMPT_LEGIT.values(), ids=PROMPT_LEGIT.keys())
def test_legit_prompt_reaches_the_model(text):
    assert not prompt_blocked(secure_writer, text)


@pytest.mark.xfail(strict=True, reason="keyword guardrail: known gap, the engine and validate still protect us")
@pytest.mark.parametrize("text", PROMPT_BYPASSES.values(), ids=PROMPT_BYPASSES.keys())
def test_known_bypass_of_the_keyword_guardrail(text):
    assert prompt_blocked(secure_writer, text)


@pytest.mark.parametrize("text", LEAKY_ANSWERS.values(), ids=LEAKY_ANSWERS.keys())
def test_leaky_answer_is_replaced(text):
    assert answer_replaced(secure_answerer, text)


@pytest.mark.parametrize("text", CLEAN_ANSWERS.values(), ids=CLEAN_ANSWERS.keys())
def test_clean_answer_is_untouched(text):
    assert not answer_replaced(secure_answerer, text)
