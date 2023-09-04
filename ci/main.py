import sys
from build_staging import build_staging


def main():
    stage = sys.argv[1] or "local"
    if stage == "staging":
        build_staging(publish=True)
    elif stage == "production":
        print("Production build not implemented yet")
    elif stage == "local":
        build_staging(publish=False)
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )


if __name__ == "__main__":
    main()
