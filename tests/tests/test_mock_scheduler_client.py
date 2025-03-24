from luik.clients.scheduler_client import SchedulerClientInterface


def test_mock_scheduler_pop_full_queue_three_times(
    full_mock_scheduler_client: SchedulerClientInterface,
) -> None:
    assert full_mock_scheduler_client.pop_task(["abc"], ["def"])
    assert full_mock_scheduler_client.pop_task(["abc"], ["def"])
    assert not full_mock_scheduler_client.pop_task(["abc"], ["def"])
