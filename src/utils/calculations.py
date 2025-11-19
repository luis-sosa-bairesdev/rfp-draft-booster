"""
ROI calculation utilities for RFP Draft Booster.

This module provides functions to calculate time savings, cost savings,
and ROI metrics based on RFP processing parameters.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Constants
TIME_REDUCTION_PERCENTAGE = 0.80  # 80% time reduction with automation
DEFAULT_RFPS_PER_MONTH = 10  # Average RFPs processed per month


def calculate_time_savings(
    rfp_pages: int,
    time_per_page: float
) -> Tuple[float, float, float]:
    """
    Calculate time savings from automated RFP processing.
    
    Args:
        rfp_pages: Number of pages in the RFP
        time_per_page: Manual processing time per page (hours)
    
    Returns:
        Tuple of (manual_time, automated_time, time_saved) in hours
    
    Example:
        >>> calculate_time_savings(50, 2.0)
        (100.0, 20.0, 80.0)
    """
    if rfp_pages <= 0:
        raise ValueError("RFP pages must be positive")
    if time_per_page <= 0:
        raise ValueError("Time per page must be positive")
    
    manual_time = rfp_pages * time_per_page
    automated_time = manual_time * (1 - TIME_REDUCTION_PERCENTAGE)
    time_saved = manual_time * TIME_REDUCTION_PERCENTAGE
    
    logger.debug(
        f"Time calculation: {rfp_pages} pages × {time_per_page}h/page = "
        f"{manual_time}h manual, {automated_time}h automated, "
        f"{time_saved}h saved ({TIME_REDUCTION_PERCENTAGE * 100}% reduction)"
    )
    
    return manual_time, automated_time, time_saved


def calculate_cost_savings(
    manual_time: float,
    automated_time: float,
    hourly_rate: float
) -> Tuple[float, float, float]:
    """
    Calculate cost savings from time reduction.
    
    Args:
        manual_time: Manual processing time (hours)
        automated_time: Automated processing time (hours)
        hourly_rate: Team hourly rate ($)
    
    Returns:
        Tuple of (cost_manual, cost_automated, cost_saved) in USD
    
    Example:
        >>> calculate_cost_savings(100.0, 20.0, 100)
        (10000.0, 2000.0, 8000.0)
    """
    if manual_time < 0:
        raise ValueError("Manual time cannot be negative")
    if automated_time < 0:
        raise ValueError("Automated time cannot be negative")
    if hourly_rate <= 0:
        raise ValueError("Hourly rate must be positive")
    
    cost_manual = manual_time * hourly_rate
    cost_automated = automated_time * hourly_rate
    cost_saved = cost_manual - cost_automated
    
    logger.debug(
        f"Cost calculation: ${cost_manual:,.0f} manual, "
        f"${cost_automated:,.0f} automated, ${cost_saved:,.0f} saved"
    )
    
    return cost_manual, cost_automated, cost_saved


def calculate_roi(
    cost_saved_per_rfp: float,
    rfps_per_month: int = DEFAULT_RFPS_PER_MONTH
) -> Tuple[float, float]:
    """
    Calculate monthly and annual ROI.
    
    Args:
        cost_saved_per_rfp: Cost savings per RFP ($)
        rfps_per_month: Number of RFPs processed per month
    
    Returns:
        Tuple of (roi_monthly, roi_annual) in USD
    
    Example:
        >>> calculate_roi(8000, 10)
        (80000.0, 960000.0)
    """
    if cost_saved_per_rfp < 0:
        raise ValueError("Cost saved cannot be negative")
    if rfps_per_month <= 0:
        raise ValueError("RFPs per month must be positive")
    
    roi_monthly = cost_saved_per_rfp * rfps_per_month
    roi_annual = roi_monthly * 12
    
    logger.debug(
        f"ROI calculation: ${cost_saved_per_rfp:,.0f}/RFP × {rfps_per_month} RFPs/month = "
        f"${roi_monthly:,.0f}/month, ${roi_annual:,.0f}/year"
    )
    
    return roi_monthly, roi_annual


def calculate_full_roi(
    rfp_pages: int,
    time_per_page: float,
    hourly_rate: float,
    rfps_per_month: int = DEFAULT_RFPS_PER_MONTH
) -> dict:
    """
    Calculate complete ROI metrics in one call.
    
    Args:
        rfp_pages: Number of pages in the RFP
        time_per_page: Manual processing time per page (hours)
        hourly_rate: Team hourly rate ($)
        rfps_per_month: Number of RFPs processed per month
    
    Returns:
        Dictionary with all ROI metrics:
        {
            'manual_time': float,
            'automated_time': float,
            'time_saved': float,
            'cost_manual': float,
            'cost_automated': float,
            'cost_saved': float,
            'roi_monthly': float,
            'roi_annual': float,
            'time_reduction_pct': float
        }
    
    Example:
        >>> metrics = calculate_full_roi(50, 2.0, 100, 10)
        >>> metrics['time_saved']
        80.0
        >>> metrics['roi_monthly']
        80000.0
    """
    logger.debug(
        f"Full ROI calculation: {rfp_pages} pages, {time_per_page}h/page, "
        f"${hourly_rate}/hour, {rfps_per_month} RFPs/month"
    )
    
    # Calculate time savings
    manual_time, automated_time, time_saved = calculate_time_savings(
        rfp_pages, time_per_page
    )
    
    # Calculate cost savings
    cost_manual, cost_automated, cost_saved = calculate_cost_savings(
        manual_time, automated_time, hourly_rate
    )
    
    # Calculate ROI
    roi_monthly, roi_annual = calculate_roi(cost_saved, rfps_per_month)
    
    metrics = {
        'manual_time': manual_time,
        'automated_time': automated_time,
        'time_saved': time_saved,
        'cost_manual': cost_manual,
        'cost_automated': cost_automated,
        'cost_saved': cost_saved,
        'roi_monthly': roi_monthly,
        'roi_annual': roi_annual,
        'time_reduction_pct': TIME_REDUCTION_PERCENTAGE * 100
    }
    
    logger.info(
        f"ROI calculated: {time_saved:.1f}h saved, "
        f"${cost_saved:,.0f} saved/RFP, ${roi_annual:,.0f}/year ROI"
    )
    
    return metrics

