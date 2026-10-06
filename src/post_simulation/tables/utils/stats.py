from typing import Tuple, Union
import numpy as np
import scipy.stats as stats


def calculate_standard_error(
    std: Union[float, np.ndarray], count: Union[int, np.ndarray]
) -> Union[float, np.ndarray]:
    """Computes standard error of the mean: SE = s / sqrt(N)."""
    std_arr = np.asarray(std, dtype=float)
    count_arr = np.asarray(count, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        se = np.where(count_arr > 0, std_arr / np.sqrt(count_arr), np.nan)
    return float(se) if np.ndim(std) == 0 and np.ndim(count) == 0 else se


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
    c1 = np.asarray(count1, dtype=float)
    c2 = np.asarray(count2, dtype=float)
    dof1 = c1 - 1.0
    dof2 = c2 - 1.0

    invalid_counts = (dof1 <= 0) | (dof2 <= 0)
    safe_dof1 = np.where(dof1 > 0, dof1, 1.0)
    safe_dof2 = np.where(dof2 > 0, dof2, 1.0)

    se1_sq = np.square(np.asarray(se1, dtype=float))
    se2_sq = np.square(np.asarray(se2, dtype=float))
    numerator = np.square(se1_sq + se2_sq)
    denominator = (np.square(se1_sq) / safe_dof1) + (np.square(se2_sq) / safe_dof2)

    res = np.full_like(numerator, np.nan, dtype=float)
    valid_mask = (denominator > 0) & (~invalid_counts)
    np.divide(numerator, denominator, out=res, where=valid_mask)

    is_scalar = (
        np.ndim(se1) == 0
        and np.ndim(count1) == 0
        and np.ndim(se2) == 0
        and np.ndim(count2) == 0
    )
    return float(res) if is_scalar else res


def calculate_margin_of_error(
    se: Union[float, np.ndarray],
    dof: Union[float, np.ndarray],
    confidence_level: float = 0.95,
) -> Union[float, np.ndarray]:
    """Computes margin of error using Student's t-distribution: MoE = t_(1 - alpha/2, dof) * SE."""
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("confidence_level must be between 0 and 1 exclusive.")
    se_arr = np.asarray(se, dtype=float)
    dof_arr = np.asarray(dof, dtype=float)
    alpha = 1.0 - confidence_level

    with np.errstate(invalid="ignore"):
        valid_mask = (dof_arr >= 1.0) & (~np.isnan(dof_arr))
        safe_dof = np.where(valid_mask, dof_arr, 1.0)
        t_critical = stats.t.ppf(1.0 - alpha / 2.0, safe_dof)
        moe = np.where(valid_mask, t_critical * se_arr, np.nan)

    is_scalar = np.ndim(se) == 0 and np.ndim(dof) == 0
    return float(moe) if is_scalar else moe


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
    diff = np.asarray(mean1, dtype=float) - np.asarray(mean2, dtype=float)
    se = np.asarray(se_combined, dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        t_stat = np.where(
            se > 0,
            diff / se,
            np.where(
                se == 0,
                np.where(diff == 0, 0.0, np.where(diff > 0, np.inf, -np.inf)),
                np.nan,
            ),
        )

    is_scalar = np.ndim(mean1) == 0 and np.ndim(mean2) == 0 and np.ndim(se_combined) == 0
    return float(t_stat) if is_scalar else t_stat


def calculate_p_value(
    t_stat: Union[float, np.ndarray],
    dof: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Computes two-tailed p-value from Student's t-distribution: p = 2 * (1 - CDF(|t|))."""
    t_arr = np.asarray(t_stat, dtype=float)
    dof_arr = np.asarray(dof, dtype=float)

    valid_mask = (dof_arr >= 1.0) & (~np.isnan(dof_arr)) & (~np.isnan(t_arr))
    abs_t = np.abs(t_arr)

    p_val = np.full_like(abs_t, np.nan, dtype=float)
    safe_dof = np.where(valid_mask, dof_arr, 1.0)
    p_val = np.where(valid_mask, 2.0 * stats.t.sf(abs_t, safe_dof), np.nan)

    is_scalar = np.ndim(t_stat) == 0 and np.ndim(dof) == 0
    return float(p_val) if is_scalar else p_val


def calculate_holm_bonferroni(
    p_values: Union[list, np.ndarray],
) -> Union[float, np.ndarray]:
    """Computes Holm-Bonferroni step-down adjusted p-values, preserving NaNs."""
    p_arr = np.asarray(p_values, dtype=float)
    p_adj = np.full_like(p_arr, np.nan, dtype=float)
    valid_mask = ~np.isnan(p_arr)
    if not np.any(valid_mask):
        return float(p_adj) if np.ndim(p_values) == 0 else p_adj
    valid_p = p_arr[valid_mask]
    n = len(valid_p)
    order = np.argsort(valid_p)
    sorted_p = valid_p[order]
    multipliers = np.arange(n, 0, -1)
    adjusted_sorted = np.minimum(1.0, np.maximum.accumulate(sorted_p * multipliers))
    orig_indices = np.where(valid_mask)[0][order]
    p_adj[orig_indices] = adjusted_sorted
    return float(p_adj) if np.ndim(p_values) == 0 else p_adj
