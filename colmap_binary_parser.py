#!/usr/bin/env python3
"""
COLMAP Binary File Parser
Reads cameras.bin, images.bin, points3D.bin for measurement system
Reference: https://colmap.github.io/format.html
"""

import struct
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class COLMAPBinaryParser:
    """Parse COLMAP binary reconstruction files"""
    
    @staticmethod
    def read_cameras(cameras_bin_path: str) -> Dict:
        """
        Read cameras.bin file
        Returns: {camera_id: {model, width, height, params}}
        """
        cameras = {}
        
        with open(cameras_bin_path, 'rb') as f:
            num_cameras = struct.unpack('Q', f.read(8))[0]
            
            for _ in range(num_cameras):
                camera_id = struct.unpack('I', f.read(4))[0]
                model_id = struct.unpack('i', f.read(4))[0]
                width = struct.unpack('Q', f.read(8))[0]
                height = struct.unpack('Q', f.read(8))[0]
                
                # Read camera parameters (varies by model)
                # Simple radial: fx, fy, cx, cy, k
                num_params = COLMAPBinaryParser._get_num_params(model_id)
                params = struct.unpack(f'{num_params}d', f.read(8 * num_params))
                
                cameras[camera_id] = {
                    'model': model_id,
                    'width': width,
                    'height': height,
                    'params': params
                }
        
        logger.info(f"Loaded {len(cameras)} cameras")
        return cameras
    
    @staticmethod
    def read_images(images_bin_path: str) -> Dict:
        """
        Read images.bin file
        Returns: {image_id: {qvec, tvec, camera_id, name, points2D}}
        """
        images = {}
        
        with open(images_bin_path, 'rb') as f:
            num_images = struct.unpack('Q', f.read(8))[0]
            
            for _ in range(num_images):
                image_id = struct.unpack('I', f.read(4))[0]
                
                # Quaternion (rotation)
                qvec = struct.unpack('4d', f.read(32))
                
                # Translation vector
                tvec = struct.unpack('3d', f.read(24))
                
                camera_id = struct.unpack('I', f.read(4))[0]
                
                # Image name (null-terminated string)
                name = b''
                while True:
                    char = f.read(1)
                    if char == b'\x00':
                        break
                    name += char
                name = name.decode('utf-8')
                
                # 2D points
                num_points2D = struct.unpack('Q', f.read(8))[0]
                points2D = []
                for _ in range(num_points2D):
                    x = struct.unpack('d', f.read(8))[0]
                    y = struct.unpack('d', f.read(8))[0]
                    point3D_id = struct.unpack('Q', f.read(8))[0]
                    points2D.append((x, y, point3D_id))
                
                images[image_id] = {
                    'qvec': qvec,
                    'tvec': tvec,
                    'camera_id': camera_id,
                    'name': name,
                    'points2D': points2D
                }
        
        logger.info(f"Loaded {len(images)} images")
        return images
    
    @staticmethod
    def read_points3D(points3D_bin_path: str) -> Dict:
        """
        Read points3D.bin file
        Returns: {point3D_id: {xyz, rgb, error, track}}
        """
        points3D = {}
        
        with open(points3D_bin_path, 'rb') as f:
            num_points = struct.unpack('Q', f.read(8))[0]
            
            for _ in range(num_points):
                point3D_id = struct.unpack('Q', f.read(8))[0]
                
                # XYZ coordinates
                xyz = struct.unpack('3d', f.read(24))
                
                # RGB color
                rgb = struct.unpack('3B', f.read(3))
                
                # Reconstruction error
                error = struct.unpack('d', f.read(8))[0]
                
                # Track (image observations)
                track_length = struct.unpack('Q', f.read(8))[0]
                track = []
                for _ in range(track_length):
                    image_id = struct.unpack('I', f.read(4))[0]
                    point2D_idx = struct.unpack('I', f.read(4))[0]
                    track.append((image_id, point2D_idx))
                
                points3D[point3D_id] = {
                    'xyz': xyz,
                    'rgb': rgb,
                    'error': error,
                    'track': track
                }
        
        logger.info(f"Loaded {len(points3D)} 3D points")
        return points3D
    
    @staticmethod
    def _get_num_params(model_id: int) -> int:
        """Get number of camera parameters for model type"""
        # COLMAP camera models
        # 0: SIMPLE_PINHOLE (f, cx, cy)
        # 1: PINHOLE (fx, fy, cx, cy)
        # 2: SIMPLE_RADIAL (f, cx, cy, k)
        # 3: RADIAL (f, cx, cy, k1, k2)
        # 4: OPENCV (fx, fy, cx, cy, k1, k2, p1, p2)
        model_params = {
            0: 3,  # SIMPLE_PINHOLE
            1: 4,  # PINHOLE
            2: 4,  # SIMPLE_RADIAL
            3: 5,  # RADIAL
            4: 8,  # OPENCV
            5: 8,  # OPENCV_FISHEYE
            6: 12, # FULL_OPENCV
            7: 10, # FOV
            8: 10, # SIMPLE_RADIAL_FISHEYE
            9: 11, # RADIAL_FISHEYE
            10: 12 # THIN_PRISM_FISHEYE
        }
        return model_params.get(model_id, 4)
    
    @staticmethod
    def load_reconstruction(sparse_path: str) -> Tuple[Dict, Dict, Dict]:
        """
        Load complete COLMAP reconstruction
        Returns: (cameras, images, points3D)
        """
        sparse_path = Path(sparse_path)
        
        cameras_path = sparse_path / "cameras.bin"
        images_path = sparse_path / "images.bin"
        points3D_path = sparse_path / "points3D.bin"
        
        # Check files exist
        if not cameras_path.exists():
            raise FileNotFoundError(f"cameras.bin not found at {cameras_path}")
        if not images_path.exists():
            raise FileNotFoundError(f"images.bin not found at {images_path}")
        if not points3D_path.exists():
            raise FileNotFoundError(f"points3D.bin not found at {points3D_path}")
        
        cameras = COLMAPBinaryParser.read_cameras(str(cameras_path))
        images = COLMAPBinaryParser.read_images(str(images_path))
        points3D = COLMAPBinaryParser.read_points3D(str(points3D_path))
        
        return cameras, images, points3D
    
    @staticmethod
    def get_point_cloud_array(points3D: Dict) -> np.ndarray:
        """
        Extract point cloud as numpy array
        Returns: (N, 3) array of XYZ coordinates
        """
        xyz_array = np.array([p['xyz'] for p in points3D.values()])
        return xyz_array
    
    @staticmethod
    def get_point_cloud_with_colors(points3D: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract point cloud with colors
        Returns: (xyz_array, rgb_array)
        """
        xyz_array = np.array([p['xyz'] for p in points3D.values()])
        rgb_array = np.array([p['rgb'] for p in points3D.values()])
        return xyz_array, rgb_array
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float, float], 
                          point2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two 3D points"""
        p1 = np.array(point1)
        p2 = np.array(point2)
        return np.linalg.norm(p2 - p1)
    
    @staticmethod
    def apply_scale(points3D: Dict, cameras: Dict, images: Dict, 
                    scale_factor: float) -> Tuple[Dict, Dict, Dict]:
        """
        Apply scale factor to entire reconstruction
        
        Args:
            points3D: 3D points dictionary
            cameras: Cameras dictionary (unchanged - intrinsics)
            images: Images dictionary (contains camera poses)
            scale_factor: Scale to apply
            
        Returns:
            Scaled (points3D, cameras, images)
        """
        # Scale 3D points
        scaled_points = {}
        for pid, point in points3D.items():
            scaled_points[pid] = {
                **point,
                'xyz': tuple(np.array(point['xyz']) * scale_factor)
            }
        
        # Scale camera translations (tvec)
        scaled_images = {}
        for iid, image in images.items():
            scaled_images[iid] = {
                **image,
                'tvec': tuple(np.array(image['tvec']) * scale_factor)
            }
        
        # Camera intrinsics don't change with scale
        scaled_cameras = cameras
        
        logger.info(f"Applied scale factor {scale_factor} to reconstruction")
        return scaled_points, scaled_cameras, scaled_images


class MeasurementSystem:
    """System for managing measurements on scaled COLMAP reconstructions"""
    
    def __init__(self, sparse_path: str):
        self.sparse_path = Path(sparse_path)
        self.cameras = None
        self.images = None
        self.points3D = None
        self.scale_factor = 1.0
        self.measurements = []
        
    def load_reconstruction(self):
        """Load COLMAP reconstruction files"""
        self.cameras, self.images, self.points3D = COLMAPBinaryParser.load_reconstruction(
            self.sparse_path
        )
        
    def find_nearest_point(self, target_position, max_distance=1.0):
        """
        Find nearest point in sparse reconstruction to given 3D position
        
        Args:
            target_position: numpy array [x, y, z]
            max_distance: Maximum distance to search (meters)
        
        Returns:
            Point ID of nearest point, or raises ValueError if none found
        """
        import numpy as np
        
        if not self.points3D:
            raise ValueError("Reconstruction not loaded")
        
        min_dist = float('inf')
        nearest_id = None
        
        for point_id, point_data in self.points3D.items():
            point_pos = np.array(point_data['xyz'])
            dist = np.linalg.norm(point_pos - target_position)
            
            if dist < min_dist and dist < max_distance:
                min_dist = dist
                nearest_id = point_id
        
        if nearest_id is None:
            raise ValueError(f"No point found within {max_distance}m of {target_position}")
        
        logger.info(f"Found nearest point {nearest_id} at distance {min_dist:.4f}m")
        return nearest_id
        
    def calibrate_scale(self, point1_id: int, point2_id: int, known_distance: float):
        """
        Calibrate scale using two points with known distance
        
        Args:
            point1_id: ID of first 3D point
            point2_id: ID of second 3D point
            known_distance: Real-world distance in meters
        """
        if point1_id not in self.points3D or point2_id not in self.points3D:
            raise ValueError("Point IDs not found in reconstruction")
        
        p1 = self.points3D[point1_id]['xyz']
        p2 = self.points3D[point2_id]['xyz']
        
        reconstruction_distance = COLMAPBinaryParser.calculate_distance(p1, p2)
        
        if reconstruction_distance == 0:
            raise ValueError("Points are identical - cannot calibrate scale")
        
        self.scale_factor = known_distance / reconstruction_distance
        
        # Apply scale to reconstruction
        self.points3D, self.cameras, self.images = COLMAPBinaryParser.apply_scale(
            self.points3D, self.cameras, self.images, self.scale_factor
        )
        
        logger.info(f"Scale calibrated: {self.scale_factor:.6f} (known: {known_distance}m, recon: {reconstruction_distance:.6f})")
        
        return {
            "scale_factor": self.scale_factor,
            "known_distance": known_distance,
            "reconstruction_distance": reconstruction_distance
        }
    
    def calculate_angle(self, point1_id: int, point2_id: int, point3_id: int) -> float:
        """
        Calculate angle between three points (point2 is vertex)
        
        Args:
            point1_id: ID of first point
            point2_id: ID of vertex point
            point3_id: ID of third point
            
        Returns:
            Angle in degrees
        """
        import numpy as np
        
        if point1_id not in self.points3D or point2_id not in self.points3D or point3_id not in self.points3D:
            raise ValueError("Point IDs not found in reconstruction")
        
        p1 = np.array(self.points3D[point1_id]['xyz'])
        p2 = np.array(self.points3D[point2_id]['xyz'])  # Vertex
        p3 = np.array(self.points3D[point3_id]['xyz'])
        
        # Vectors from vertex to points
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle numerical errors
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    def calculate_thickness(self, point1_id: int, point2_id: int) -> float:
        """
        Calculate thickness (distance) between two surface points
        
        Args:
            point1_id: ID of first surface point
            point2_id: ID of second surface point (opposite side)
            
        Returns:
            Thickness in meters (scaled)
        """
        if point1_id not in self.points3D or point2_id not in self.points3D:
            raise ValueError("Point IDs not found in reconstruction")
        
        p1 = self.points3D[point1_id]['xyz']
        p2 = self.points3D[point2_id]['xyz']
        
        distance = COLMAPBinaryParser.calculate_distance(p1, p2)
        return distance * self.scale_factor
    
    def calculate_radius(self, point_ids: list) -> Dict:
        """
        Calculate radius of curvature from 3+ points on a curve
        
        Args:
            point_ids: List of 3+ point IDs on the curve
            
        Returns:
            Dictionary with radius, center, and fit quality
        """
        import numpy as np
        
        if len(point_ids) < 3:
            raise ValueError("Need at least 3 points to calculate radius")
        
        # Get point positions
        points = []
        for pid in point_ids:
            if pid not in self.points3D:
                raise ValueError(f"Point ID {pid} not found")
            points.append(np.array(self.points3D[pid]['xyz']) * self.scale_factor)
        
        points = np.array(points)
        
        # Fit circle to points (2D projection on best-fit plane)
        # For simplicity, project to XY plane and fit circle
        # In production, use PCA to find best plane
        
        # Center estimate (centroid)
        center_estimate = np.mean(points, axis=0)
        
        # Calculate distances from center
        distances = np.linalg.norm(points - center_estimate, axis=1)
        radius_estimate = np.mean(distances)
        
        # Simple radius calculation (average distance from centroid)
        # For more accurate results, use circle fitting algorithm
        radius = radius_estimate
        
        return {
            "radius_meters": radius,
            "center": center_estimate.tolist(),
            "fit_quality": "good" if np.std(distances) / radius < 0.1 else "fair"
        }
    
    def get_point_info(self, point_id: int) -> Dict:
        """
        Get detailed information about a point
        
        Args:
            point_id: ID of point
            
        Returns:
            Dictionary with position, normal (if available), and other info
        """
        import numpy as np
        
        if point_id not in self.points3D:
            raise ValueError(f"Point ID {point_id} not found")
        
        point_data = self.points3D[point_id]
        position = np.array(point_data['xyz']) * self.scale_factor
        
        # Normal estimation (simplified - use average of neighboring points)
        # In production, use PCA or mesh normals
        normal = None  # TODO: Implement normal estimation
        
        return {
            "position": position.tolist(),
            "normal": normal,
            "rgb": point_data.get('rgb', [128, 128, 128]),
            "error": point_data.get('error', 0.0)
        }
    
    def add_measurement(self, point1_id: int, point2_id: int, label: str = "") -> Dict:
        """
        Add a distance measurement between two points
        
        Args:
            point1_id: ID of first 3D point
            point2_id: ID of second 3D point
            label: Optional label for measurement
            
        Returns:
            Measurement data dictionary
        """
        if point1_id not in self.points3D or point2_id not in self.points3D:
            raise ValueError("Point IDs not found in reconstruction")
        
        p1 = self.points3D[point1_id]['xyz']
        p2 = self.points3D[point2_id]['xyz']
        
        distance = COLMAPBinaryParser.calculate_distance(p1, p2)
        
        measurement = {
            "id": len(self.measurements),
            "point1_id": point1_id,
            "point2_id": point2_id,
            "point1_xyz": p1,
            "point2_xyz": p2,
            "distance_meters": distance,
            "distance_cm": distance * 100,
            "distance_mm": distance * 1000,
            "label": label or f"Measurement {len(self.measurements) + 1}",
            "scaled": self.scale_factor != 1.0
        }
        
        self.measurements.append(measurement)
        logger.info(f"Added measurement: {distance:.3f}m ({label})")
        
        return measurement
    
    def export_measurements(self, format: str = "json") -> str:
        """
        Export measurements to JSON or CSV
        
        Args:
            format: 'json' or 'csv'
            
        Returns:
            Formatted string
        """
        if format == "json":
            import json
            return json.dumps({
                "scale_factor": self.scale_factor,
                "measurements": self.measurements
            }, indent=2)
        
        elif format == "csv":
            lines = ["id,label,point1_id,point2_id,distance_m,distance_cm,distance_mm,scaled"]
            for m in self.measurements:
                lines.append(
                    f"{m['id']},{m['label']},{m['point1_id']},{m['point2_id']},"
                    f"{m['distance_meters']:.6f},{m['distance_cm']:.2f},{m['distance_mm']:.1f},"
                    f"{m['scaled']}"
                )
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_reconstruction_stats(self) -> Dict:
        """Get reconstruction statistics"""
        if not self.points3D:
            return {}
        
        xyz_array = COLMAPBinaryParser.get_point_cloud_array(self.points3D)
        
        return {
            "num_points": len(self.points3D),
            "num_cameras": len(self.cameras) if self.cameras else 0,
            "num_images": len(self.images) if self.images else 0,
            "num_measurements": len(self.measurements),
            "scale_factor": self.scale_factor,
            "is_scaled": self.scale_factor != 1.0,
            "bounds": {
                "min_x": float(xyz_array[:, 0].min()),
                "max_x": float(xyz_array[:, 0].max()),
                "min_y": float(xyz_array[:, 1].min()),
                "max_y": float(xyz_array[:, 1].max()),
                "min_z": float(xyz_array[:, 2].min()),
                "max_z": float(xyz_array[:, 2].max()),
            },
            "centroid": {
                "x": float(xyz_array[:, 0].mean()),
                "y": float(xyz_array[:, 1].mean()),
                "z": float(xyz_array[:, 2].mean()),
            }
        }
    def save_scaled_reconstruction(self, output_path: str = None):
        """
        Save scaled reconstruction back to disk
        
        Args:
            output_path: Optional output directory (defaults to self.sparse_path)
        """
        from pathlib import Path
        
        if output_path is None:
            output_path = str(self.sparse_path)
        else:
            output_path = str(Path(output_path))
            Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Save scale factor to a metadata file
        scale_file = Path(output_path) / "scale_factor.txt"
        with open(scale_file, 'w') as f:
            f.write(f"{self.scale_factor}\n")
        
        logger.info(f"✅ Saved scale factor {self.scale_factor:.6f} to {scale_file}")
        logger.info(f"ℹ️  Scaled reconstruction is in memory. Scale factor: {self.scale_factor:.6f}")
        
        return output_path


