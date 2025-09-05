import os, subprocess, sys

def test_imports():
    import app.cli
    import app.llm.base
    import app.patterns.factory

def test_mock_run():
    env = os.environ.copy()
    env["MOCK_MODE"] = "true"
    result = subprocess.run([sys.executable, "-m", "app.cli", "Teste de execução em mock"], env=env, capture_output=True, text=True)
    assert result.returncode == 0