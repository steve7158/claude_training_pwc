"""Optional OpenTelemetry instrumentation for the Helios evidence-review UI
backend (ui/server.py).

Kept as an optional import, not a hard dependency: `ui/server.py`'s stdlib-
only guarantee (documented in README.md) must hold even when
`opentelemetry-*` isn't installed. Everything here degrades to no-op stubs
if the packages are missing, so `import otel_setup` never breaks the server
— install `requirements-observability.txt` to get real traces/metrics.
"""
import os

_initialized = False
_tracer = None
_meter = None
_request_counter = None
_duration_histogram = None


class _NoopSpan:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def set_attribute(self, *_args, **_kwargs):
        pass


class _NoopTracer:
    def start_as_current_span(self, *_args, **_kwargs):
        return _NoopSpan()


class _NoopCounter:
    def add(self, *_args, **_kwargs):
        pass


class _NoopHistogram:
    def record(self, *_args, **_kwargs):
        pass


def init_telemetry(service_name: str = "helios-evidence-review") -> None:
    global _initialized, _tracer, _meter, _request_counter, _duration_histogram
    if _initialized:
        return
    _initialized = True

    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        _tracer = _NoopTracer()
        _request_counter = _NoopCounter()
        _duration_histogram = _NoopHistogram()
        return

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    resource = Resource.create({SERVICE_NAME: service_name, SERVICE_VERSION: "0.1.0"})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)
    _tracer = trace.get_tracer(service_name)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(service_name)

    _request_counter = _meter.create_counter(
        "helios.pipeline.requests_total",
        description="Evidence-review pipeline requests, tagged by outcome status",
    )
    _duration_histogram = _meter.create_histogram(
        "helios.pipeline.duration_ms",
        unit="ms",
        description="Wall-clock duration of a full evidence-review pipeline run",
    )


def get_tracer():
    return _tracer if _tracer is not None else _NoopTracer()


def record_pipeline_result(status: str, duration_ms: float) -> None:
    counter = _request_counter if _request_counter is not None else _NoopCounter()
    histogram = _duration_histogram if _duration_histogram is not None else _NoopHistogram()
    counter.add(1, {"status": status})
    histogram.record(duration_ms, {"status": status})
