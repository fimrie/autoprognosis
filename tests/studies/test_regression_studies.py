# stdlib
import os
from pathlib import Path

# third party
from helpers import MockHook
import numpy as np
import pytest
from sklearn.datasets import load_diabetes

# autoprognosis absolute
from autoprognosis.exceptions import StudyCancelled
from autoprognosis.studies.regression import RegressionStudy
from autoprognosis.utils.serialization import load_model_from_file
from autoprognosis.utils.tester import evaluate_regression


def test_regression_search() -> None:
    X, Y = load_diabetes(return_X_y=True, as_frame=True)

    df = X.copy()
    df["target"] = Y

    storage_folder = Path("/tmp")
    study_name = "test_regressors_studies"
    workspace = storage_folder / study_name
    output = workspace / "model.p"
    try:
        os.remove(output)
    except OSError:
        pass

    study = RegressionStudy(
        study_name=study_name,
        dataset=df,
        target="target",
        num_iter=2,
        num_study_iter=2,
        timeout=10,
        regressors=["linear_regression", "random_forest_regressor"],
        workspace=storage_folder,
        score_threshold=0.3,
    )
    print("study name", study.study_name)

    study.run()

    assert output.is_file()

    model_v1 = load_model_from_file(output)

    metrics = evaluate_regression(model_v1, X, Y)
    score_v1 = metrics["clf"]["r2"][0]

    # resume the study - should get at least the same score
    study.run()

    assert output.is_file()

    model_v2 = load_model_from_file(output)

    metrics = evaluate_regression(model_v2, X, Y)
    score_v2 = metrics["clf"]["r2"][0]

    EPS = 0.05
    assert score_v2 + EPS >= score_v1


def test_hooks() -> None:
    hooks = MockHook()
    X, Y = load_diabetes(return_X_y=True, as_frame=True)

    df = X.copy()
    df["target"] = Y

    storage_folder = Path("/tmp")
    study_name = "test_regressors_studies"
    output = storage_folder / study_name

    try:
        os.remove(output)
    except OSError:
        pass

    study = RegressionStudy(
        study_name=study_name,
        dataset=df,
        target="target",
        num_iter=2,
        num_study_iter=2,
        timeout=10,
        regressors=["linear_regression", "random_forest_regressor"],
        workspace=storage_folder,
        hooks=hooks,
    )
    with pytest.raises(StudyCancelled):
        study.run()


@pytest.mark.parametrize("imputers", [["mean", "median"], ["mean"]])
@pytest.mark.slow
def test_regression_study_imputation(imputers: list) -> None:
    X, Y = load_diabetes(return_X_y=True, as_frame=True)
    storage_folder = Path("/tmp")
    study_name = "test_regressors_studies"
    workspace = storage_folder / study_name
    output = workspace / "model.p"
    try:
        os.remove(output)
    except OSError:
        pass

    X.loc[0, "mean smoothness"] = np.nan

    df = X.copy()
    df["target"] = Y

    study = RegressionStudy(
        study_name=study_name,
        dataset=df,
        target="target",
        imputers=imputers,
        num_iter=2,
        num_study_iter=2,
        timeout=10,
        regressors=["linear_regression", "random_forest_regressor"],
        workspace=storage_folder,
        score_threshold=0.3,
    )

    study.run()

    assert output.is_file()
