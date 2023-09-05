import sys
from build_staging import build_staging, update_chart_staging


def main():
    stage = sys.argv[1]
    dry_run = False
    if len(sys.argv) > 2:
        dry_run = sys.argv[2]
        dry_run = dry_run == "--dry-run"
        print("Running with --dry-run")
    if stage == "staging":
        build_staging(dry_run)
        update_chart_staging(dry_run)
    elif stage == "production":
        print("Production build not implemented yet")
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )


if __name__ == "__main__":
    main()
