# Datadog

The agent is not part of Docker Compose. Dashboard and monitor plans live in [observability/datadog](../../observability/datadog).

During the build window, run the agent only with `DD_API_KEY` injected from the environment, never from a committed file. Intended local ports are DogStatsD `8125` and the trace agent `8126`, matching `ObservabilitySettings`.

`DD_*` placeholders are listed in `.env.example` and are blank or disabled. `Observability__DatadogEnabled` remains `false` until the trial account is wired.
