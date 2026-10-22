"""Run the whole pipeline, or chosen stages.

    python -m wigan_crime.run                 # everything, including downloads
    python -m wigan_crime.run --skip-download # reuse data already in data/
    python -m wigan_crime.run --stages forecast charts
"""
import argparse
import time

from . import analysis, charts, config, deprivation, download, forecast, prepare

STAGES = {
    "download": download.run,
    "prepare": prepare.run,
    "analysis": analysis.run,
    "deprivation": deprivation.run,
    "forecast": forecast.run,
    "charts": charts.run,
}


def main():
    parser = argparse.ArgumentParser(description="Wigan crime analysis pipeline")
    parser.add_argument("--stages", nargs="+", choices=list(STAGES), help="run only these stages")
    parser.add_argument("--skip-download", action="store_true", help="use files already in data/")
    args = parser.parse_args()

    config.ensure_dirs()
    stages = args.stages or [s for s in STAGES if not (args.skip_download and s == "download")]
    for name in stages:
        start = time.time()
        print(f"[{name}]")
        STAGES[name]()
        print(f"  done in {time.time() - start:.0f}s")


if __name__ == "__main__":
    main()
