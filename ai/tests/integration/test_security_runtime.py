from pathlib import Path

from ai.integrations.security.security_runtime import SecurityToolRuntime
from ai.integrations.security.tool_registry import get_security_tools


def run_test():

    print()
    print("=" * 70)
    print(" SENTINELAI — SECURITY TOOL RUNTIME TEST")
    print("=" * 70)

    tools = get_security_tools()
    runtime = SecurityToolRuntime()

    expected = {
        "gitleaks",
        "trivy",
        "semgrep",
        "dependency-check",
        "sonar",
    }

    print("\n[1] Checking tool registry...")

    assert set(tools.keys()) == expected

    print("[PASS] Five security tools registered")

    print("\n[2] Checking executable configuration...")

    for name, config in tools.items():

        print(f"  {name}: {config.executable}")

        if name == "semgrep":
            # Semgrep is expected to resolve through the active venv/PATH.
            continue

        assert Path(config.executable).exists(), (
            f"{name} executable not found: "
            f"{config.executable}"
        )

    print("[PASS] Tool executable configuration")

    print("\n[3] Testing Gitleaks version...")

    result = runtime.execute(
        tools["gitleaks"],
        ["version"],
    )

    assert result.return_code == 0
    assert result.stdout or result.stderr

    print("[PASS] Gitleaks executable")

    print("\n[4] Testing Trivy version...")

    result = runtime.execute(
        tools["trivy"],
        ["--version"],
    )

    assert result.return_code == 0

    print("[PASS] Trivy executable")

    print("\n[5] Testing Semgrep version...")

    result = runtime.execute(
        tools["semgrep"],
        ["--version"],
    )

    assert result.return_code == 0

    print("[PASS] Semgrep executable")

    print("\n[6] Testing Dependency-Check executable...")

    result = runtime.execute(
        tools["dependency-check"],
        ["--version"],
    )

    assert result.return_code == 0

    print("[PASS] Dependency-Check executable")

    print("\n[7] Testing SonarScanner executable...")

    result = runtime.execute(
        tools["sonar"],
        ["--version"],
    )

    assert result.return_code == 0

    print("[PASS] SonarScanner executable")

    print()
    print("=" * 70)
    print(" SECURITY TOOL RUNTIME TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()