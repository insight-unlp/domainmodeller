from storage_template import storage
from domainmodeller.TaskHub import TaskHub

def test_stats_runs():
    storage.clear()
    task_hub = TaskHub(storage, None)
    task_hub.run('stats')