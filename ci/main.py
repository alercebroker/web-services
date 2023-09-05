import sys
from build_staging import build_staging


def main():
    stage = sys.argv[1]
    do_publish = sys.argv[2]
    do_publish = do_publish.lower() == "true"
    do_push = sys.argv[3]
    do_push = do_push.lower() == "true"
    if stage == "staging":
        build_staging(do_publish=do_publish, do_push=do_push)
    elif stage == "production":
        print("Production build not implemented yet")
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )


if __name__ == "__main__":
    main()
