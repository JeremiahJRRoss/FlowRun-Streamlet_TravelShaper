"""OTel routing — reads OTEL_DESTINATION from env and builds a
TracerProvider with the appropriate exporters attached.

Valid OTEL_DESTINATION values:
    phoenix   — local Phoenix or Phoenix Cloud
    arize     — Arize Cloud (uses arize.otel SDK)
    otlp      — any OTLP-compatible backend (Jaeger, Tempo, Honeycomb, etc.)
                OTLP_PROTOCOL selects transport: "http" (default) or "grpc"
    both      — Phoenix and Arize simultaneously
    all       — Phoenix, Arize, and generic OTLP simultaneously
    none      — disables all telemetry

Called once at startup from agent.py.
"""

import os
import sys

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter as OTLPGrpcSpanExporter,
    )
except ImportError:
    OTLPGrpcSpanExporter = None


def _destination() -> str:
    return os.getenv("OTEL_DESTINATION", "phoenix").strip().lower()


def _project_name() -> str:
    return os.getenv("OTEL_PROJECT_NAME", "travelshaper").strip()


def _phoenix_exporter() -> OTLPSpanExporter | None:
    endpoint = os.getenv("PHOENIX_ENDPOINT", "").strip()
    if not endpoint:
        print("[otel] PHOENIX_ENDPOINT not set — Phoenix disabled", file=sys.stderr)
        return None
    headers = {}
    if api_key := os.getenv("PHOENIX_API_KEY", "").strip():
        headers["authorization"] = f"Bearer {api_key}"
    return OTLPSpanExporter(endpoint=endpoint, headers=headers)


def _parse_otlp_headers() -> dict:
    """Parse OTLP_HEADERS env var from 'key1=val1,key2=val2' into a dict."""
    raw = os.getenv("OTLP_HEADERS", "").strip()
    if not raw:
        return {}
    headers = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            headers[k.strip()] = v.strip()
    return headers


def _otlp_exporter():
    """Build an OTLP exporter for a generic backend (HTTP or gRPC)."""
    endpoint = os.getenv("OTLP_ENDPOINT", "").strip()
    if not endpoint:
        print("[otel] OTLP_ENDPOINT not set — generic OTLP disabled", file=sys.stderr)
        return None

    protocol = os.getenv("OTLP_PROTOCOL", "http").strip().lower()
    headers = _parse_otlp_headers()

    if protocol == "grpc":
        if OTLPGrpcSpanExporter is None:
            print("[otel] opentelemetry-exporter-otlp-proto-grpc not installed — "
                  "falling back to HTTP", file=sys.stderr)
            return OTLPSpanExporter(endpoint=endpoint, headers=headers)
        return OTLPGrpcSpanExporter(endpoint=endpoint, headers=headers)

    return OTLPSpanExporter(endpoint=endpoint, headers=headers)


def _build_arize_provider() -> TracerProvider | None:
    """Use arize.otel.register() to create a TracerProvider for Arize Cloud."""
    api_key  = os.getenv("ARIZE_API_KEY",  "").strip()
    space_id = os.getenv("ARIZE_SPACE_ID", "").strip()
    if not all([api_key, space_id]):
        print("[otel] Arize credentials incomplete — Arize disabled", file=sys.stderr)
        return None
    try:
        from arize.otel import register
        provider = register(
            space_id=space_id,
            api_key=api_key,
            project_name=_project_name(),
        )
        return provider
    except ImportError:
        print("[otel] arize-otel not installed — Arize disabled", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[otel] Arize registration failed: {e}", file=sys.stderr)
        return None


def build_tracer_provider() -> TracerProvider:
    """Build and return a configured TracerProvider.

    Reads OTEL_DESTINATION to determine which exporters to attach.
    Logs which destinations are active to stderr on startup.
    Returns a no-op TracerProvider if destination is 'none' or
    all credentials are missing.
    """
    dest    = _destination()
    project = _project_name()

    if dest == "none":
        print("[otel] Telemetry disabled (OTEL_DESTINATION=none)")
        return TracerProvider(resource=Resource({"service.name": project}))

    # ── Arize-only: use arize.otel.register() directly ────────
    if dest == "arize":
        provider = _build_arize_provider()
        if provider:
            print(f"[otel] Traces → arize (project: {project})")
            return provider
        print("[otel] No active trace destinations — running without telemetry",
              file=sys.stderr)
        return TracerProvider(resource=Resource({"service.name": project}))

    # ── Phoenix-only: manual TracerProvider + OTLP exporter ───
    if dest == "phoenix":
        provider = TracerProvider(resource=Resource({"service.name": project}))
        exporter = _phoenix_exporter()
        if exporter:
            provider.add_span_processor(BatchSpanProcessor(exporter))
            print(f"[otel] Traces → phoenix (project: {project})")
        else:
            print("[otel] No active trace destinations — running without telemetry",
                  file=sys.stderr)
        return provider

    # ── Generic OTLP: manual TracerProvider + OTLP exporter ──
    if dest == "otlp":
        provider = TracerProvider(resource=Resource({"service.name": project}))
        exporter = _otlp_exporter()
        if exporter:
            provider.add_span_processor(BatchSpanProcessor(exporter))
            print(f"[otel] Traces → otlp (project: {project})")
        else:
            print("[otel] No active trace destinations — running without telemetry",
                  file=sys.stderr)
        return provider

    # ── Both: use arize.otel.register() then add Phoenix exporter ─
    if dest == "both":
        active = []
        # Start with Arize provider (register() returns a TracerProvider)
        provider = _build_arize_provider()
        if provider:
            active.append("arize")
            # Add Phoenix exporter to the same provider
            phoenix_exp = _phoenix_exporter()
            if phoenix_exp:
                provider.add_span_processor(BatchSpanProcessor(phoenix_exp))
                active.append("phoenix")
        else:
            # Arize failed — fall back to Phoenix-only
            provider = TracerProvider(resource=Resource({"service.name": project}))
            phoenix_exp = _phoenix_exporter()
            if phoenix_exp:
                provider.add_span_processor(BatchSpanProcessor(phoenix_exp))
                active.append("phoenix")

        if active:
            print(f"[otel] Traces → {', '.join(active)} (project: {project})")
        else:
            print("[otel] No active trace destinations — running without telemetry",
                  file=sys.stderr)
        return provider

    # ── All: Arize + Phoenix + generic OTLP ───────────────────
    if dest == "all":
        active = []
        provider = _build_arize_provider()
        if provider:
            active.append("arize")
        else:
            provider = TracerProvider(resource=Resource({"service.name": project}))

        phoenix_exp = _phoenix_exporter()
        if phoenix_exp:
            provider.add_span_processor(BatchSpanProcessor(phoenix_exp))
            active.append("phoenix")

        otlp_exp = _otlp_exporter()
        if otlp_exp:
            provider.add_span_processor(BatchSpanProcessor(otlp_exp))
            active.append("otlp")

        if active:
            print(f"[otel] Traces → {', '.join(active)} (project: {project})")
        else:
            print("[otel] No active trace destinations — running without telemetry",
                  file=sys.stderr)
        return provider

    # ── Unknown destination ───────────────────────────────────
    print(f"[otel] Unknown destination '{dest}' — running without telemetry",
          file=sys.stderr)
    return TracerProvider(resource=Resource({"service.name": project}))
