"""Physics sub-package: GCS geometry, drag models, H-T fitting, and projection."""

from heliotrace.physics.geometry import (
    skeleton,
    gcs_mesh,
    rotate_mesh,
    gcs_mesh_rotated,
    apex_radius,
)
from heliotrace.physics.fitting import perform_linear_fit
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.physics.drag import (
    get_CME_mass_pluta,
    get_CME_cross_section_pluta,
    get_constant_drag_parameter_DBM,
    simulate_equation_of_motion_DBM,
    simulate_equation_of_motion_MODBM,
    find_time_and_velocity_at_distance,
)

__all__ = [
    "skeleton",
    "gcs_mesh",
    "rotate_mesh",
    "gcs_mesh_rotated",
    "apex_radius",
    "perform_linear_fit",
    "get_target_apex_ratio",
    "get_CME_mass_pluta",
    "get_CME_cross_section_pluta",
    "get_constant_drag_parameter_DBM",
    "simulate_equation_of_motion_DBM",
    "simulate_equation_of_motion_MODBM",
    "find_time_and_velocity_at_distance",
]
