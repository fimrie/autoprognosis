# stdlib
from typing import Any, List

# third party
import pandas as pd

# autoprognosis absolute
import autoprognosis.plugins.core.params as params
import autoprognosis.plugins.prediction.base as prediction_base


class RegressionPlugin(prediction_base.PredictionPlugin):
    """Base class for the regression plugins.

    It provides the implementation for plugin.Plugin's subtype, _fit and _predict methods.

    Each derived class must implement the following methods(inherited from plugin.Plugin):
        name() - a static method that returns the name of the plugin.
        hyperparameter_space() - a static method that returns the hyperparameters that can be tuned during the optimization. The method will return a list of `Params` derived objects.

    If any method implementation is missing, the class constructor will fail.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__()

        self.args = kwargs

    @staticmethod
    def subtype() -> str:
        return "regression"

    @staticmethod
    def hyperparameter_space(*args: Any, **kwargs: Any) -> List[params.Params]:
        return []

    def fit(self, X: pd.DataFrame, *args: Any, **kwargs: Any) -> "RegressionPlugin":
        if len(args) < 1:
            raise ValueError("Invalid input for fit. Expecting X and Y.")

        X = self._fit_input(X)
        self._fit(X, *args, **kwargs)

        return self

    def _predict_proba(
        self, X: pd.DataFrame, *args: Any, **kwargs: Any
    ) -> pd.DataFrame:
        raise NotImplementedError(f"Model {self.name()} doesn't support predict proba")

    def get_args(self) -> dict:
        return self.args
