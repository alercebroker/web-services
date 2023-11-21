# test_stage.py
import anyio
from test.utils import _tests_selection


async def test_stage(packages: list, stage: str):
    for package in packages:
        if package not in _tests_selection:
            raise ValueError(
                f"No tests found for package {package} in tests selection"
            )

    tests = _tests_selection[package]
    async with anyio.create_task_group() as tg:
        for test in tests:
            if stage not in test["args"]:
                raise ValueError(
                    f"No tests found for stage {stage} in test {test} for package {package}"
                )
            tg.start_soon(test["step"], *test["args"][stage])


if __name__ == "__main__":
    anyio.run(test_stage)
