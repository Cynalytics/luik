from tests.mock_clients.mock_scheduler_client import MockSchedulerClient


def test_mock_scheduler_pop_queue_1_three_times(mock_poppable_tasks):
    client = MockSchedulerClient(mock_poppable_tasks)

    assert client.pop_task("queue_1", ["abc"], ["def"])
    assert client.pop_task("queue_1", ["abc"], ["def"])
    assert not client.pop_task("queue_1", ["abc"], ["def"])
