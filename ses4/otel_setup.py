"""OpenTelemetry initialization for the SIP Calculator app.

Streamlit reruns this module's importer on every interaction, so
init_telemetry() is guarded to configure the global TracerProvider and
MeterProvider exactly once per process. There is no HTTP framework or
database in this app (Streamlit owns its own request lifecycle), so
instrumentation covers process/system metrics plus manual spans and
metrics around the app's actual work: computing and rendering the SIP
schedule.
"""
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_initialized = False


def init_telemetry(service_name: str = "sip-calculator") -> None:
    global _initialized
    if _initialized:
        return

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    resource = Resource.create({SERVICE_NAME: service_name, SERVICE_VERSION: "0.1.0"})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    SystemMetricsInstrumentor().instrument()

    _initialized = True


def get_tracer(name: str = "sip-calculator"):
    return trace.get_tracer(name)


def get_meter(name: str = "sip-calculator"):
    return metrics.get_meter(name)
