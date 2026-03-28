from app.services.batch_scheduler import BatchScheduler


def test_build_batches_orders_parallel_roles_together() -> None:
    scheduler = BatchScheduler()
    nodes = [
        {"id": "PC"},
        {"id": "CA"},
        {"id": "FD"},
        {"id": "BD"},
        {"id": "DE"},
        {"id": "QT"},
    ]
    edges = [("PC", "CA"), ("CA", "FD"), ("CA", "BD"), ("FD", "DE"), ("BD", "DE"), ("DE", "QT")]

    batches = scheduler.build_batches(nodes, edges)

    assert batches == [["PC"], ["CA"], ["FD", "BD"], ["DE"], ["QT"]]
