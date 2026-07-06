#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2026 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

"""
Scan cloned Freqtrade strategy sources and print porting status vs catalog.

Usage:
    python -m nautilus_trader.examples.strategies.freqtrade_ported.scripts.analyze_source \\
        --source /path/to/freqtrade-strategies/user_data/strategies
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
from pathlib import Path


def _load_catalog():
    catalog_path = Path(__file__).resolve().parents[1] / "catalog.py"
    spec = importlib.util.spec_from_file_location("ft_catalog", catalog_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ft_catalog"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.FREQTRADE_STRATEGY_CATALOG, module.PortStatus, module.catalog_summary


FREQTRADE_STRATEGY_CATALOG, PortStatus, catalog_summary = _load_catalog()


def discover_strategy_classes(source_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in sorted(source_dir.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and any(
                (isinstance(base, ast.Name) and base.id == "IStrategy")
                or (isinstance(base, ast.Attribute) and base.attr == "IStrategy")
                for base in node.bases
            ):
                rel = path.relative_to(source_dir)
                found[node.name] = rel
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze Freqtrade strategy port status")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(".freqtrade-strategies-source/user_data/strategies"),
        help="Path to Freqtrade user_data/strategies directory",
    )
    args = parser.parse_args(argv)

    if not args.source.exists():
        print(f"Source not found: {args.source}", file=sys.stderr)
        return 1

    discovered = discover_strategy_classes(args.source)
    print(f"Discovered {len(discovered)} IStrategy classes in {args.source}\n")

    summary = catalog_summary()
    for status, count in sorted(summary.items()):
        print(f"  catalog[{status}]: {count}")

    missing_from_catalog = sorted(set(discovered) - set(FREQTRADE_STRATEGY_CATALOG))
    if missing_from_catalog:
        print("\nNot in catalog (add to catalog.py):")
        for name in missing_from_catalog:
            print(f"  - {name} ({discovered[name]})")

    ported = [n for n, e in FREQTRADE_STRATEGY_CATALOG.items() if e.status == PortStatus.PORTED]
    print(f"\nPorted modules ({len(ported)}): {', '.join(sorted(ported))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
