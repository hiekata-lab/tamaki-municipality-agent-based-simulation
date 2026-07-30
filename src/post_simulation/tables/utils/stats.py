from typing import Tuple, Union
import numpy as np
import scipy.stats as stats


def calculate_standard_error(
    std: Union[float, np.ndarray], count: Union[int, np.ndarray]
) -> Union[float, np.ndarray]:
    """Computes standard error of the mean: SE = s / sqrt(N)."""
    valid_count = np.maximum(count, 1)
    return np.nan_to_num(std / np.sqrt(valid_count))


def calculate_combined_standard_error(
    se1: Union[float, np.ndarray], se2: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Computes root-sum-of-squares combined standard error for independent estimates: SE_combined = sqrt(SE1^2 + SE2^2)."""
    return np.sqrt(np.square(se1) + np.square(se2))


def calculate_margin_of_error(
    se: Union[float, np.ndarray],
    count: Union[int, np.ndarray],
    confidence_level: float = 0.95,
) -> Union[float, np.ndarray]:
    """Computes margin of error using Student's t-distribution: MoE = t_(1 - alpha/2, dof) * SE, where dof = max(1, N - 1)."""
    dof = np.maximum(1, np.asarray(count) - 1)
    alpha = 1.0 - confidence_level
    t_critical = stats.t.ppf(1.0 - alpha / 2.0, dof)
    return t_critical * se


def calculate_confidence_interval(
    mean: Union[float, np.ndarray],
    se: Union[float, np.ndarray],
    count: Union[int, np.ndarray],
    confidence_level: float = 0.95,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """Computes lower and upper confidence bounds: CI_lower = mu - MoE, CI_upper = mu + MoE."""
    moe = calculate_margin_of_error(se, count, confidence_level=confidence_level)
    return mean - moe, mean + moe
