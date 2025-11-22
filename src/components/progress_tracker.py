"""Progress Tracker Component - Enhanced loading states for long-running operations."""

import streamlit as st
from typing import Optional, List, Dict
from dataclasses import dataclass
import time


@dataclass
class ProgressStep:
    """A single step in a multi-step process."""
    name: str
    description: str
    icon: str = "⏳"
    weight: float = 1.0  # Relative weight for progress calculation


class ProgressTracker:
    """
    Enhanced progress tracker with detailed steps and visual feedback.
    
    Usage:
        tracker = ProgressTracker("Processing RFP", [
            ProgressStep("upload", "Uploading file", "📤", 0.2),
            ProgressStep("validate", "Validating PDF", "✓", 0.2),
            ProgressStep("extract", "Extracting text", "📄", 0.6)
        ])
        
        with tracker:
            tracker.start_step("upload")
            # ... do work ...
            tracker.complete_step("upload")
            
            tracker.start_step("validate")
            # ... do work ...
            tracker.complete_step("validate")
    """
    
    def __init__(self, title: str, steps: List[ProgressStep], show_elapsed: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            title: Overall title for the operation
            steps: List of steps to track
            show_elapsed: Whether to show elapsed time
        """
        self.title = title
        self.steps = {step.name: step for step in steps}
        self.step_order = [step.name for step in steps]
        self.show_elapsed = show_elapsed
        
        # Calculate total weight
        self.total_weight = sum(step.weight for step in steps)
        
        # State tracking
        self.current_step_idx = -1
        self.completed_steps = set()
        self.start_time = None
        
        # UI elements (created on __enter__)
        self.progress_bar = None
        self.status_text = None
        self.elapsed_text = None
        self.step_status_container = None
    
    def __enter__(self):
        """Start tracking progress."""
        self.start_time = time.time()
        
        # Create UI elements
        st.markdown(f"### {self.title}")
        self.progress_bar = st.progress(0, text="Starting...")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            self.status_text = st.empty()
        with col2:
            if self.show_elapsed:
                self.elapsed_text = st.empty()
        
        self.step_status_container = st.empty()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish tracking progress."""
        if exc_type is None:
            # Success - show completion
            self.progress_bar.progress(100, text="✅ Complete!")
            self.status_text.success(f"✅ {self.title} completed successfully")
            if self.show_elapsed:
                elapsed = time.time() - self.start_time
                self.elapsed_text.text(f"⏱️ {elapsed:.1f}s")
        else:
            # Error occurred
            self.status_text.error(f"❌ {self.title} failed")
        
        return False  # Don't suppress exceptions
    
    def start_step(self, step_name: str, message: Optional[str] = None):
        """
        Start a step.
        
        Args:
            step_name: Name of the step to start
            message: Optional custom message (uses step description if not provided)
        """
        if step_name not in self.steps:
            raise ValueError(f"Unknown step: {step_name}")
        
        self.current_step_idx = self.step_order.index(step_name)
        step = self.steps[step_name]
        
        # Calculate progress
        completed_weight = sum(
            self.steps[name].weight 
            for name in self.step_order[:self.current_step_idx]
        )
        progress_pct = int((completed_weight / self.total_weight) * 100)
        
        # Update UI
        display_message = message or step.description
        self.progress_bar.progress(progress_pct, text=f"{step.icon} {display_message}")
        self.status_text.info(f"{step.icon} **{display_message}**")
        
        if self.show_elapsed and self.elapsed_text:
            elapsed = time.time() - self.start_time
            self.elapsed_text.text(f"⏱️ {elapsed:.1f}s")
        
        # Update step status visualization
        self._update_step_status()
    
    def complete_step(self, step_name: str, success: bool = True):
        """
        Mark a step as complete.
        
        Args:
            step_name: Name of the step to complete
            success: Whether the step succeeded
        """
        if step_name not in self.steps:
            raise ValueError(f"Unknown step: {step_name}")
        
        self.completed_steps.add(step_name)
        self._update_step_status()
    
    def update_substep(self, message: str):
        """
        Update status within current step (for multi-part steps).
        
        Args:
            message: Status message to display
        """
        if self.current_step_idx < 0:
            return
        
        step = self.steps[self.step_order[self.current_step_idx]]
        self.status_text.info(f"{step.icon} {message}")
        
        if self.show_elapsed and self.elapsed_text:
            elapsed = time.time() - self.start_time
            self.elapsed_text.text(f"⏱️ {elapsed:.1f}s")
    
    def _update_step_status(self):
        """Update the visual step status display."""
        if not self.step_status_container:
            return
        
        # Create step status markdown
        status_lines = []
        for idx, step_name in enumerate(self.step_order):
            step = self.steps[step_name]
            
            if step_name in self.completed_steps:
                icon = "✅"
                style = "color: green;"
            elif idx == self.current_step_idx:
                icon = "⏳"
                style = "color: blue; font-weight: bold;"
            else:
                icon = "⏸️"
                style = "color: gray;"
            
            status_lines.append(f"<span style='{style}'>{icon} {step.description}</span>")
        
        self.step_status_container.markdown(
            "<br>".join(status_lines),
            unsafe_allow_html=True
        )


def simple_progress(message: str, progress: int = None):
    """
    Simple progress indicator for single-step operations.
    
    Args:
        message: Status message
        progress: Optional progress percentage (0-100)
    
    Returns:
        Context manager that shows spinner/progress
    """
    if progress is not None:
        return st.progress(progress, text=message)
    else:
        return st.spinner(message)

