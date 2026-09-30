from edgeguard_simulator.config import SimulatorConfig


def main() -> int:
    config = SimulatorConfig.from_env()
    print(
        "EdgeGuard device simulator is a pre-hackathon scaffold. "
        f"scenario={config.scenario} devices={config.device_count} "
        "Telemetry generation is not implemented."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
