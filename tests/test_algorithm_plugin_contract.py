from lekinpy.algorithms import SchedulingAlgorithm, FCFSAlgorithm, SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm
import pytest

ALL_ALGORITHMS = [FCFSAlgorithm, SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm]
REQUIRED_METADATA_KEYS = {"id", "display_name", "supports_multi_operation", "version"}


@pytest.mark.parametrize("algo_cls", ALL_ALGORITHMS)
def test_builtin_algorithm_has_complete_metadata(algo_cls):
    algo = algo_cls()
    assert REQUIRED_METADATA_KEYS.issubset(algo.metadata.keys())
    assert isinstance(algo.metadata["id"], str) and algo.metadata["id"]
    assert isinstance(algo.metadata["display_name"], str) and algo.metadata["display_name"]
    assert isinstance(algo.metadata["version"], str) and algo.metadata["version"]


@pytest.mark.parametrize("algo_cls", ALL_ALGORITHMS)
def test_builtin_algorithms_all_report_multi_operation_support(algo_cls):
    # True as of item 2's fix: FCFS always supported it; SPT/EDD/WSPT now do too.
    assert algo_cls().metadata["supports_multi_operation"] is True


def test_algorithm_ids_are_unique():
    ids = [cls().metadata["id"] for cls in ALL_ALGORITHMS]
    assert len(ids) == len(set(ids))


def test_subclass_without_metadata_fails_at_instantiation():
    class BrokenAlgorithm(SchedulingAlgorithm):
        def schedule(self, system):
            pass

    with pytest.raises(NotImplementedError):
        BrokenAlgorithm()


def test_subclass_with_partial_metadata_fails_at_instantiation():
    class PartialAlgorithm(SchedulingAlgorithm):
        metadata = {"id": "partial", "display_name": "Partial"}

        def schedule(self, system):
            pass

    with pytest.raises(NotImplementedError):
        PartialAlgorithm()


def test_subclass_with_complete_metadata_instantiates_fine():
    class CustomAlgorithm(SchedulingAlgorithm):
        metadata = {
            "id": "custom",
            "display_name": "Custom Rule",
            "supports_multi_operation": False,
            "version": "0.1.0",
        }

        def schedule(self, system):
            pass

    algo = CustomAlgorithm()  # should not raise
    assert algo.metadata["id"] == "custom"


def test_base_class_schedule_is_not_implemented():
    class NoScheduleAlgorithm(SchedulingAlgorithm):
        metadata = {
            "id": "no-schedule",
            "display_name": "No Schedule",
            "supports_multi_operation": False,
            "version": "1.0.0",
        }

    algo = NoScheduleAlgorithm()
    with pytest.raises(NotImplementedError):
        algo.schedule(system=None)
