import tensorflow as tf
from openfisca_uk import Microsimulation
from typing import Callable, Iterable, List, Tuple
from numpy.typing import ArrayLike
from openfisca_core.parameters import ParameterNode, Parameter


def weighted_squared_relative_deviation(
    pred: tf.Tensor, actual: ArrayLike
) -> tf.Tensor:
    return ((pred / actual) - 1) ** 2 * actual


class LossCategory:
    weight: float = 1
    label: str
    parameter_folder: ParameterNode
    years: List[int] = [2019, 2020, 2021, 2022]
    comparison_loss_function: Callable = weighted_squared_relative_deviation

    def get_loss_subcomponents(
        sim: Microsimulation, household_weights: tf.Tensor, year: int
    ) -> Iterable[Tuple]:
        """Gathers predictions used to measure weight performance.

        Args:
            sim (Microsimulation): A microsimulation from which to draw demographic data.
            household_weights (tf.Tensor): Household weights for each year.
            year (int): The year to test on.

        Returns:
            Iterable[Tuple]: A list of (name, pred, actual) triplets.
        """
        raise NotImplementedError()

    @classmethod
    def compute(
        cls,
        sim: Microsimulation,
        household_weights: tf.Tensor,
        excluded_metrics: List[str],
    ) -> Tuple[tf.Tensor, dict]:
        loss = 0
        log = []
        for year in cls.years:
            for name, pred, actual in cls.get_loss_subcomponents(
                sim, household_weights, excluded_metrics, year
            ):
                if name not in excluded_metrics:
                    l = cls.comparison_loss_function(pred, actual) * cls.weight
                    log += [
                        dict(
                            name=name,
                            pred=float(pred.numpy()),
                            actual=float(actual),
                            loss=l,
                            category=cls.label,
                        )
                    ]
                    loss += l

    @classmethod
    def get_metrics(cls) -> List[Parameter]:
        return list(
            filter(
                lambda p: isinstance(p, Parameter),
                cls.parameter_folder.get_descendants(),
            )
        )

    @classmethod
    def get_metric_names(cls) -> List[str]:
        for parameter in cls.parameter_folder.get_descendants():
            if isinstance(parameter, Parameter):
                yield from [f"{parameter.name}.{year}" for year in cls.years]
