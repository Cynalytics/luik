from luik.clients.scheduler_client import SchedulerClientInterface


def test_mock_scheduler_pop_full_queue_three_times(
    mock_scheduler_client: SchedulerClientInterface,
) -> None:
    assert mock_scheduler_client.pop_task("full_queue", ["abc"], ["def"])
    assert mock_scheduler_client.pop_task("full_queue", ["abc"], ["def"])
    assert not mock_scheduler_client.pop_task("full_queue", ["abc"], ["def"])
