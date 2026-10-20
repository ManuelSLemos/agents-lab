import pytest

from sql_agent_secure.database import MAX_ROWS, run_query
from security import wrap_untrusted
from sql_agent_secure.answerer import answerer

from .cases import ATTACKS, INDIRECT, LEGIT, SLOW_ATTACKS
from .implementations import ALLOWED, BLOCKED, is_marked_as_data, secure, secure_result


@pytest.mark.parametrize("sql", ATTACKS.values(), ids=ATTACKS.keys())
def test_attack_is_blocked(sql):
    assert secure(sql) == BLOCKED


@pytest.mark.parametrize("sql", SLOW_ATTACKS.values(), ids=SLOW_ATTACKS.keys())
def test_slow_attack_is_stopped_by_timeout(sql):
    assert secure(sql) == BLOCKED


@pytest.mark.parametrize("sql", LEGIT.values(), ids=LEGIT.keys())
def test_legit_query_is_allowed(sql):
    assert secure(sql) == ALLOWED


def test_rows_are_capped():
    result = run_query("SELECT * FROM students a, students b, students c")  # 125 rows
    assert len(result.rows) == MAX_ROWS


@pytest.mark.parametrize("sql", INDIRECT.values(), ids=INDIRECT.keys())
def test_poisoned_data_reaches_the_llm_marked_as_data(sql):
    assert is_marked_as_data(secure_result(sql))


def test_answerer_is_told_to_treat_data_as_data():
    assert "<db_result>" in answerer.instruction and "never instructions" in answerer.instruction


def test_wrap_untrusted_escapes_tags():
    assert wrap_untrusted("x", "</x> hi").count("</x>") == 1
