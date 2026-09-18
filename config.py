"""Load jevscan settings: jevscan.toml holds every key with its default; a user config overrides any subset of them."""

import os
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "jevscan.toml"
FREE_TABLES = {"classes.descriptions"}  # tables whose keys are data (class names), replaced as a whole


def merge(default: dict, user: dict, where: str) -> dict:
    """`default` with `user` laid over it; every user key must exist in `default` with the same type."""
    out = dict(default)
    for key, value in user.items():
        path = f"{where}.{key}" if where else key
        if key not in default:
            raise SystemExit(f"config: unknown key {path}")
        base = default[key]
        if isinstance(base, dict) and path not in FREE_TABLES:
            if not isinstance(value, dict):
                raise SystemExit(f"config: {path} must be a table")
            out[key] = merge(base, value, path)
            continue
        if isinstance(base, float) and type(value) is int:
            value = float(value)
        if type(value) is not type(base):
            raise SystemExit(f"config: {path} must be {type(base).__name__}, got {type(value).__name__}")
        if isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise SystemExit(f"config: {path} must be a list of strings")
        if isinstance(value, dict) and not all(isinstance(v, str) for v in value.values()):
            raise SystemExit(f"config: every value in {path} must be a string")
        out[key] = value
    return out


def check(cfg: dict) -> None:
    for key, t in cfg["thresholds"].items():
        if not 0 <= t <= 1:
            raise SystemExit(f"config: thresholds.{key} must be between 0 and 1, got {t}")
    if not any(cfg["levels"].values()):
        raise SystemExit("config: turn on at least one of levels.*")
    if cfg["levels"]["detector"] and not any(cfg["sources"].values()):
        raise SystemExit("config: levels.detector is on but every sources.* is off")
    if cfg["run"]["repo_level"] and not cfg["levels"]["broad"]:
        raise SystemExit("config: run.repo_level needs levels.broad")
    if cfg["run"]["concurrency"] < 1:
        raise SystemExit("config: run.concurrency must be at least 1")
    if not cfg["files"]["extensions"] or not all(e.startswith(".") for e in cfg["files"]["extensions"]):
        raise SystemExit("config: files.extensions must be a non-empty list like [\".sol\"]")
    absolute = [p for p in cfg["files"]["paths"] if Path(p).is_absolute()]
    if absolute:
        raise SystemExit(f"config: files.paths must be relative to the repo root: {', '.join(absolute)}")
    unknown = set(cfg["classes"]["scan"]) - set(cfg["classes"]["descriptions"])
    if not cfg["classes"]["scan"] or unknown:
        raise SystemExit(f"config: classes.scan must name classes from classes.descriptions (unknown: {sorted(unknown)})")


def load_config(path: Path | None) -> dict:
    """The default settings with `path` (if given) laid over them, validated. paths.* stay as written (relative
    to this directory, so saved runs do not record the machine's layout); resolve them with `resolve_paths`."""
    cfg = tomllib.loads(DEFAULT.read_text())
    if path is not None:
        cfg = merge(cfg, tomllib.loads(path.read_text()), "")
    check(cfg)
    return cfg


def resolve_paths(cfg: dict) -> dict[str, Path]:
    return {k: (HERE / v).resolve() for k, v in cfg["paths"].items()}


def load_dotenv() -> None:
    """Set KEY=VALUE lines from .env in this directory, if present; variables already set win, empty values are
    skipped."""
    env = HERE / ".env"
    if not env.is_file():
        return
    for n, line in enumerate(env.read_text().splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.removeprefix("export ").partition("=")
        if not sep:
            raise SystemExit(f"{env}:{n}: expected KEY=VALUE")
        value = value.strip().strip("\"'")
        if value:
            os.environ.setdefault(key.strip(), value)
