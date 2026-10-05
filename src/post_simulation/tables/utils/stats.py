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


def calculate_welch_satterthwaite_dof(
    se1: Union[float, np.ndarray],
    count1: Union[int, np.ndarray],
    se2: Union[float, np.ndarray],
    count2: Union[int, np.ndarray],
) -> Union[float, np.ndarray]:
    """Computes effective degrees of freedom via Welch-Satterthwaite equation."""
    dof1 = np.maximum(1.0, np.asarray(count1, dtype=float) - 1.0)
    dof2 = np.maximum(1.0, np.asarray(count2, dtype=float) - 1.0)
    se1_sq = np.square(se1)
    se2_sq = np.square(se2)
    numerator = np.square(se1_sq + se2_sq)
    denominator = (np.square(se1_sq) / dof1) + (np.square(se2_sq) / dof2)
    return np.nan_to_num(
        np.where(denominator > 0, numerator / denominator, 1.0), nan=1.0
    )


def calculate_margin_of_error(
    se: Union[float, np.ndarray],
    dof: Union[float, np.ndarray],
    confidence_level: float = 0.95,
) -> Union[float, np.ndarray]:
    """Computes margin of error using Student's t-distribution: MoE = t_(1 - alpha/2, dof) * SE."""
    valid_dof = np.maximum(1.0, np.asarray(dof, dtype=float))
    alpha = 1.0 - confidence_level
    t_critical = stats.t.ppf(1.0 - alpha / 2.0, valid_dof)
    return t_critical * se


def calculate_confidence_interval(
    mean: Union[float, np.ndarray],
    se: Union[float, np.ndarray],
    dof: Union[float, np.ndarray],
    confidence_level: float = 0.95,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """Computes lower and upper confidence bounds: CI_lower = mu - MoE, CI_upper = mu + MoE."""
    moe = calculate_margin_of_error(se, dof, confidence_level=confidence_level)
    return mean - moe, mean + moe


def calculate_welch_t_statistic(
    mean1: Union[float, np.ndarray],
    mean2: Union[float, np.ndarray],
    se_combined: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Computes Welch's t-test statistic: t = (mean1 - mean2) / se_combined."""
    valid_se = np.where(se_combined > 0, se_combined, np.nan)
    diff = mean1 - mean2
    return np.nan_to_num(diff / valid_se)


def calculate_p_value(
    t_stat: Union[float, np.ndarray],
    dof: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Computes two-tailed p-value from Student's t-distribution: p = 2 * (1 - CDF(|t|))."""
    valid_dof = np.maximum(1.0, np.asarray(dof, dtype=float))
    abs_t = np.abs(t_stat)
    p_val = 2.0 * stats.t.sf(abs_t, valid_dof)
    return np.nan_to_num(p_val)

