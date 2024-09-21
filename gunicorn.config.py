import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from requests.exceptions import ConnectionError, RequestException, SSLError


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    resource = Resource.create(attributes={"service.name": os.environ.get("OTEL_SERVICE_NAME")})

    trace.set_tracer_provider(TracerProvider(resource=resource))
    try:
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')}/v1/traces")
        )
        trace.get_tracer_provider().add_span_processor(span_processor)
    except (RequestException, ConnectionError, SSLError):
        pass
