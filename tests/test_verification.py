import pytest

from tomatoai.verification import VerificationRecord, verify_task


def test_successful_verification():
    record = verify_task("t-1", True, evidence={"observation": "ok"})
    assert record.success
    assert record.evidence["observation"] == "ok"


def test_failed_verification_requires_reason():
    with pytest.raises(ValueError):
        VerificationRecord("t-1", False).validate()


def test_failed_verification_can_be_reviewed():
    record = verify_task("t-1", False, needs_review=True, reason="target not visible")
    assert record.needs_review
    assert not record.success
