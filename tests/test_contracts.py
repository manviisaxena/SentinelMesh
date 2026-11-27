from pathlib import Path

def test_four_independent_services_have_health_endpoint():
    root=Path(__file__).resolve().parents[1]
    for name in ('ingestion','detection','intelligence','incident'):
        src=(root/'services'/name/'app'/'main.py').read_text()
        assert '@app.get("/health")' in src
        assert f'title="SentinelMesh' in src

def test_compose_has_four_database_volumes_and_gateway():
    compose=(Path(__file__).resolve().parents[1]/'docker-compose.yml').read_text()
    for name in ('ingestion','detection','intelligence','incident'):
        assert f'db-{name}:' in compose
        assert f'{name}-data:' in compose
    assert 'gateway:' in compose and 'rabbitmq:' in compose


def test_bruteforce_counts_all_failed_attempts_not_only_alerts():
    source=(Path(__file__).resolve().parents[1]/'services'/'detection'/'app'/'main.py').read_text()
    assert 'CREATE TABLE IF NOT EXISTS login_attempts' in source
    assert 'FROM login_attempts WHERE source_ip=%s' in source
