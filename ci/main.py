import sys
from build_staging import build_staging


def main():
    stage = sys.argv[1]
    if stage == "staging":
        build_staging()
    elif stage == "production":
        print("Production build not implemented yet")
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )


if __name__ == "__main__":
    main()
