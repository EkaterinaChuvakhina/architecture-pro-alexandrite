from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "billing"})
    )
)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://simplest-collector:4318/v1/traces"
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def pay():
    with trace.get_tracer(__name__).start_as_current_span("pay"):
        res = requests.get("http://service-b:8080")
        return "Payed"+" "+res.text