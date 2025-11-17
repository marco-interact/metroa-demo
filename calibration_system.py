#!/usr/bin/env python3
"""
Real-World Calibration System for 3D Measurements
Converts reconstruction units to real-world measurements (meters, cm, etc.)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class CalibrationSystem:
    """
    Calibration system for converting point cloud units to real-world measurements
    
    Calibration methods:
    1. Known distance: User provides two points with known real-world distance
    2. Camera metadata: Extract scale from camera sensor size and focal length
    3. GPS/EXIF: Use GPS data if available
    4. Manual scale: User manually sets scale factor
    """
    
    def __init__(self, scan_id: str, calibration_file: Optional[Path] = None):
        """
        Initialize calibration system for a scan
        
        Args:
            scan_id: Unique scan identifier
            calibration_file: Optional path to calibration JSON file
        """
        self.scan_id = scan_id
        self.calibration_file = calibration_file or Path(f"/workspace/data/results/{scan_id}/calibration.json")
        self.scale_factor = 1.0  # Default: no scaling
        self.calibration_method = "uncalibrated"
        self.reference_distance = None  # Known distance for calibration
        self.unit = "reconstruction_units"  # Current units
        
        # Load existing calibration if available
        if self.calibration_file.exists():
            self._load_calibration()
    
    def _load_calibration(self):
        """Load calibration data from file"""
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
                self.scale_factor = data.get('scale_factor', 1.0)
                self.calibration_method = data.get('method', 'uncalibrated')
                self.reference_distance = data.get('reference_distance')
                self.unit = data.get('unit', 'reconstruction_units')
                logger.info(f"✅ Loaded calibration: {self.scale_factor}x, method={self.calibration_method}")
        except Exception as e:
            logger.warning(f"Could not load calibration: {e}")
    
    def _save_calibration(self):
        """Save calibration data to file"""
        try:
            self.calibration_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'scale_factor': self.scale_factor,
                'method': self.calibration_method,
                'reference_distance': self.reference_distance,
                'unit': self.unit,
                'scan_id': self.scan_id
            }
            with open(self.calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"✅ Saved calibration: {self.scale_factor}x, method={self.calibration_method}")
        except Exception as e:
            logger.error(f"Could not save calibration: {e}")
    
    def calibrate_from_known_distance(
        self,
        point_a: Tuple[float, float, float],
        point_b: Tuple[float, float, float],
        known_distance_meters: float
    ) -> float:
        """
        Calibrate using two points with known real-world distance
        
        Args:
            point_a: First point coordinates (x, y, z)
            point_b: Second point coordinates (x, y, z)
            known_distance_meters: Real-world distance in meters
        
        Returns:
            scale_factor: Conversion factor (reconstruction units → meters)
        
        Example:
            User measures wall that's 3.5m in reality
            Distance in reconstruction: 175 units
            Scale factor: 3.5 / 175 = 0.02 (meters per reconstruction unit)
        """
        # Calculate distance in reconstruction units
        reconstruction_distance = np.linalg.norm(
            np.array(point_b) - np.array(point_a)
        )
        
        if reconstruction_distance < 1e-6:
            raise ValueError("Points are too close together for calibration")
        
        # Calculate scale factor
        self.scale_factor = known_distance_meters / reconstruction_distance
        self.calibration_method = "known_distance"
        self.reference_distance = known_distance_meters
        self.unit = "meters"
        
        # Save calibration
        self._save_calibration()
        
        logger.info(f"✅ Calibration complete:")
        logger.info(f"   Reconstruction distance: {reconstruction_distance:.2f} units")
        logger.info(f"   Real-world distance: {known_distance_meters:.2f} m")
        logger.info(f"   Scale factor: {self.scale_factor:.6f} m/unit")
        
        return self.scale_factor
    
    def calibrate_from_camera_metadata(
        self,
        focal_length_mm: float,
        sensor_width_mm: float,
        image_width_px: int
    ) -> float:
        """
        Calibrate using camera metadata (approximate)
        
        Args:
            focal_length_mm: Camera focal length in millimeters
            sensor_width_mm: Camera sensor width in millimeters
            image_width_px: Image width in pixels
        
        Returns:
            scale_factor: Approximate conversion factor
        
        Note: This method provides rough estimates. Known distance is more accurate.
        """
        # Calculate pixel size
        pixel_size_mm = sensor_width_mm / image_width_px
        
        # Approximate scale (this is simplified)
        # Real calibration would need triangulation depth
        self.scale_factor = pixel_size_mm / focal_length_mm
        self.calibration_method = "camera_metadata"
        self.unit = "meters (approximate)"
        
        self._save_calibration()
        
        logger.info(f"✅ Camera-based calibration (approximate):")
        logger.info(f"   Scale factor: {self.scale_factor:.6f}")
        logger.warning("   ⚠️ Camera-based calibration is approximate. Use known distance for accuracy.")
        
        return self.scale_factor
    
    def set_manual_scale(self, scale_factor: float, unit: str = "meters"):
        """
        Manually set scale factor
        
        Args:
            scale_factor: Conversion factor
            unit: Target unit (e.g., "meters", "centimeters", "feet")
        """
        self.scale_factor = scale_factor
        self.calibration_method = "manual"
        self.unit = unit
        self._save_calibration()
        
        logger.info(f"✅ Manual scale set: {self.scale_factor} {unit}/unit")
    
    def convert_distance(self, distance_units: float) -> float:
        """
        Convert distance from reconstruction units to real-world units
        
        Args:
            distance_units: Distance in reconstruction units
        
        Returns:
            distance in calibrated units (e.g., meters)
        """
        return distance_units * self.scale_factor
    
    def convert_area(self, area_units_squared: float) -> float:
        """
        Convert area from reconstruction units² to real-world units²
        
        Args:
            area_units_squared: Area in reconstruction units²
        
        Returns:
            area in calibrated units² (e.g., meters²)
        """
        return area_units_squared * (self.scale_factor ** 2)
    
    def convert_volume(self, volume_units_cubed: float) -> float:
        """
        Convert volume from reconstruction units³ to real-world units³
        
        Args:
            volume_units_cubed: Volume in reconstruction units³
        
        Returns:
            volume in calibrated units³ (e.g., meters³)
        """
        return volume_units_cubed * (self.scale_factor ** 3)
    
    def get_calibration_info(self) -> Dict:
        """Get current calibration information"""
        return {
            'scale_factor': self.scale_factor,
            'method': self.calibration_method,
            'unit': self.unit,
            'reference_distance': self.reference_distance,
            'is_calibrated': self.calibration_method != "uncalibrated"
        }
    
    def format_distance(self, distance_units: float, decimals: int = 2) -> str:
        """
        Format distance with appropriate units
        
        Args:
            distance_units: Distance in reconstruction units
            decimals: Number of decimal places
        
        Returns:
            Formatted string (e.g., "3.45 m")
        """
        real_distance = self.convert_distance(distance_units)
        
        if self.unit == "meters":
            if real_distance < 0.01:  # Less than 1cm
                return f"{real_distance * 1000:.{decimals}f} mm"
            elif real_distance < 1.0:  # Less than 1m
                return f"{real_distance * 100:.{decimals}f} cm"
            else:
                return f"{real_distance:.{decimals}f} m"
        else:
            return f"{real_distance:.{decimals}f} {self.unit}"
    
    def format_area(self, area_units_squared: float, decimals: int = 2) -> str:
        """Format area with appropriate units"""
        real_area = self.convert_area(area_units_squared)
        
        if self.unit == "meters":
            if real_area < 0.01:  # Less than 100 cm²
                return f"{real_area * 10000:.{decimals}f} cm²"
            else:
                return f"{real_area:.{decimals}f} m²"
        else:
            return f"{real_area:.{decimals}f} {self.unit}²"
    
    def format_volume(self, volume_units_cubed: float, decimals: int = 2) -> str:
        """Format volume with appropriate units"""
        real_volume = self.convert_volume(volume_units_cubed)
        
        if self.unit == "meters":
            if real_volume < 0.001:  # Less than 1L
                return f"{real_volume * 1000000:.{decimals}f} cm³"
            elif real_volume < 1.0:  # Less than 1m³
                return f"{real_volume * 1000:.{decimals}f} L"
            else:
                return f"{real_volume:.{decimals}f} m³"
        else:
            return f"{real_volume:.{decimals}f} {self.unit}³"


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create calibration system
    cal = CalibrationSystem("test-scan-123")
    
    # Example 1: Calibrate from known distance
    # User clicks two points on a wall they know is 3.5m wide
    point_a = (0.0, 0.0, 0.0)
    point_b = (175.0, 0.0, 0.0)  # 175 units apart in reconstruction
    
    cal.calibrate_from_known_distance(point_a, point_b, 3.5)
    
    # Now convert measurements
    print("\nMeasurements after calibration:")
    print(f"100 units = {cal.format_distance(100)}")
    print(f"250 units = {cal.format_distance(250)}")
    print(f"50 units = {cal.format_distance(50)}")
    print(f"1000 units² = {cal.format_area(1000)}")
    print(f"10000 units³ = {cal.format_volume(10000)}")
    
    # Example 2: Manual calibration
    cal2 = CalibrationSystem("test-scan-456")
    cal2.set_manual_scale(0.01, "meters")  # 1 unit = 1cm
    
    print("\nManual calibration:")
    print(f"100 units = {cal2.format_distance(100)}")

