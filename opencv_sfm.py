#!/usr/bin/env python3
"""
OpenCV-based Structure from Motion (SfM) Pipeline

A lightweight SfM implementation using OpenCV for feature detection,
matching, camera pose estimation, and triangulation.

This can be used as an alternative to COLMAP for simpler reconstructions
or when a lightweight solution is needed.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    logger.warning("Open3D not available, visualization will be limited")


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters"""
    fx: float
    fy: float
    cx: float
    cy: float
    
    def to_matrix(self) -> np.ndarray:
        """Convert to 3x3 intrinsic matrix K"""
        return np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ], dtype=np.float32)
    
    @classmethod
    def from_matrix(cls, K: np.ndarray) -> 'CameraIntrinsics':
        """Create from 3x3 intrinsic matrix"""
        return cls(
            fx=float(K[0, 0]),
            fy=float(K[1, 1]),
            cx=float(K[0, 2]),
            cy=float(K[1, 2])
        )
    
    @classmethod
    def default(cls, width: int, height: int, fov_deg: float = 50.0) -> 'CameraIntrinsics':
        """Create default intrinsics from image dimensions"""
        f = (width / 2.0) / np.tan(np.radians(fov_deg / 2.0))
        return cls(
            fx=f,
            fy=f,
            cx=width / 2.0,
            cy=height / 2.0
        )


@dataclass
class CameraPose:
    """Camera pose (rotation and translation)"""
    R: np.ndarray  # 3x3 rotation matrix
    t: np.ndarray  # 3x1 translation vector
    
    def to_matrix(self) -> np.ndarray:
        """Convert to 4x4 transformation matrix"""
        T = np.eye(4, dtype=np.float32)
        T[:3, :3] = self.R
        T[:3, 3] = self.t.flatten()
        return T


class OpenCVSfM:
    """OpenCV-based Structure from Motion pipeline"""
    
    def __init__(
        self,
        intrinsics: Optional[CameraIntrinsics] = None,
        feature_type: str = "SIFT",
        matcher_type: str = "FLANN",
        ransac_threshold: float = 1.0,
        min_match_count: int = 50
    ):
        """
        Initialize SfM pipeline
        
        Args:
            intrinsics: Camera intrinsic parameters (None = auto-estimate)
            feature_type: Feature detector type ("SIFT", "SURF", "ORB")
            matcher_type: Matcher type ("FLANN" or "BF")
            ransac_threshold: RANSAC threshold for outlier rejection
            min_match_count: Minimum matches required between image pairs
        """
        self.intrinsics = intrinsics
        self.feature_type = feature_type
        self.matcher_type = matcher_type
        self.ransac_threshold = ransac_threshold
        self.min_match_count = min_match_count
        
        # Initialize feature detector
        if feature_type == "SIFT":
            self.detector = cv2.SIFT_create()
        elif feature_type == "SURF":
            self.detector = cv2.xfeatures2d.SURF_create() if hasattr(cv2, 'xfeatures2d') else cv2.SIFT_create()
        elif feature_type == "ORB":
            self.detector = cv2.ORB_create()
        else:
            raise ValueError(f"Unknown feature type: {feature_type}")
        
        # Initialize matcher
        if matcher_type == "FLANN":
            if feature_type == "ORB":
                FLANN_INDEX_LSH = 6
                index_params = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
            else:
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        else:  # Brute Force
            if feature_type == "ORB":
                self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            else:
                self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        
        # Storage
        self.images = []
        self.keypoints = []
        self.descriptors = []
        self.camera_poses = []
        self.points_3d = []
        self.colors_3d = []
    
    def load_images(self, image_paths: List[str]) -> bool:
        """
        Load images from file paths
        
        Args:
            image_paths: List of image file paths
        
        Returns:
            True if all images loaded successfully
        """
        self.images = []
        for img_path in image_paths:
            img = cv2.imread(str(img_path))
            if img is None:
                logger.error(f"Failed to load image: {img_path}")
                return False
            self.images.append(img)
            logger.info(f"Loaded image: {img_path} ({img.shape[1]}x{img.shape[0]})")
        
        # Auto-estimate intrinsics if not provided
        if self.intrinsics is None and len(self.images) > 0:
            h, w = self.images[0].shape[:2]
            self.intrinsics = CameraIntrinsics.default(w, h)
            logger.info(f"Auto-estimated intrinsics: fx={self.intrinsics.fx:.1f}, fy={self.intrinsics.fy:.1f}")
        
        return True
    
    def detect_features(self) -> bool:
        """
        Detect features in all images
        
        Returns:
            True if features detected successfully
        """
        self.keypoints = []
        self.descriptors = []
        
        for i, img in enumerate(self.images):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kp, desc = self.detector.detectAndCompute(gray, None)
            
            if desc is None or len(kp) < self.min_match_count:
                logger.warning(f"Image {i}: Insufficient features detected ({len(kp) if kp else 0})")
                return False
            
            self.keypoints.append(kp)
            self.descriptors.append(desc)
            logger.info(f"Image {i}: Detected {len(kp)} features")
        
        return True
    
    def match_features(self, idx1: int, idx2: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Match features between two images
        
        Args:
            idx1: Index of first image
            idx2: Index of second image
        
        Returns:
            Tuple of (matched points in image 1, matched points in image 2)
        """
        desc1 = self.descriptors[idx1]
        desc2 = self.descriptors[idx2]
        
        # Match features
        matches = self.matcher.knnMatch(desc1, desc2, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
        
        if len(good_matches) < self.min_match_count:
            logger.warning(f"Insufficient matches between images {idx1} and {idx2}: {len(good_matches)}")
            return np.array([]), np.array([])
        
        # Extract matched points
        pts1 = np.float32([self.keypoints[idx1][m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        pts2 = np.float32([self.keypoints[idx2][m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        return pts1, pts2
    
    def estimate_pose_pair(self, idx1: int, idx2: int) -> Optional[CameraPose]:
        """
        Estimate relative camera pose between two images
        
        Args:
            idx1: Index of first image (reference, identity pose)
            idx2: Index of second image
        
        Returns:
            Camera pose for second image relative to first, or None if failed
        """
        pts1, pts2 = self.match_features(idx1, idx2)
        
        if len(pts1) < self.min_match_count:
            return None
        
        K = self.intrinsics.to_matrix()
        
        # Find essential matrix
        E, mask = cv2.findEssentialMat(
            pts1, pts2,
            K,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=self.ransac_threshold
        )
        
        if E is None:
            logger.warning(f"Failed to find essential matrix between images {idx1} and {idx2}")
            return None
        
        # Recover pose
        _, R, t, mask_pose = cv2.recoverPose(E, pts1, pts2, K)
        
        if mask_pose.sum() < self.min_match_count:
            logger.warning(f"Insufficient inliers for pose recovery: {mask_pose.sum()}")
            return None
        
        logger.info(f"Pose estimation: {mask_pose.sum()}/{len(pts1)} inliers")
        
        return CameraPose(R=R, t=t)
    
    def triangulate_points(
        self,
        pts1: np.ndarray,
        pts2: np.ndarray,
        pose1: CameraPose,
        pose2: CameraPose
    ) -> np.ndarray:
        """
        Triangulate 3D points from 2D correspondences
        
        Args:
            pts1: Points in first image (Nx2)
            pts2: Points in second image (Nx2)
            pose1: Camera pose 1 (reference, identity)
            pose2: Camera pose 2
        
        Returns:
            3D points (Nx3)
        """
        K = self.intrinsics.to_matrix()
        
        # Projection matrices
        P1 = K @ np.hstack([pose1.R, pose1.t])
        P2 = K @ np.hstack([pose2.R, pose2.t])
        
        # Triangulate
        pts_4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
        
        # Convert from homogeneous to 3D
        pts_3d = (pts_4d[:3] / pts_4d[3]).T
        
        return pts_3d
    
    def reconstruct_pair(self, idx1: int, idx2: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstruct 3D points from image pair
        
        Args:
            idx1: Index of first image
            idx2: Index of second image
        
        Returns:
            Tuple of (3D points, colors)
        """
        # Match features
        pts1, pts2 = self.match_features(idx1, idx2)
        
        if len(pts1) < self.min_match_count:
            return np.array([]), np.array([])
        
        # Estimate pose
        pose1 = CameraPose(R=np.eye(3), t=np.zeros((3, 1)))  # Reference frame
        pose2 = self.estimate_pose_pair(idx1, idx2)
        
        if pose2 is None:
            return np.array([]), np.array([])
        
        # Filter matches using essential matrix mask
        K = self.intrinsics.to_matrix()
        E, mask = cv2.findEssentialMat(
            pts1, pts2, K,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=self.ransac_threshold
        )
        
        pts1_masked = pts1[mask.ravel() == 1]
        pts2_masked = pts2[mask.ravel() == 1]
        
        if len(pts1_masked) < self.min_match_count:
            return np.array([]), np.array([])
        
        # Triangulate
        points_3d = self.triangulate_points(pts1_masked, pts2_masked, pose1, pose2)
        
        # Extract colors
        colors = []
        for pt in pts1_masked:
            x, y = int(pt[0, 0]), int(pt[0, 1])
            if 0 <= y < self.images[idx1].shape[0] and 0 <= x < self.images[idx1].shape[1]:
                color = self.images[idx1][y, x]
                colors.append([color[2], color[1], color[0]])  # BGR to RGB
            else:
                colors.append([128, 128, 128])
        
        colors = np.array(colors, dtype=np.uint8)
        
        # Filter points behind cameras
        valid_mask = points_3d[:, 2] > 0
        points_3d = points_3d[valid_mask]
        colors = colors[valid_mask]
        
        logger.info(f"Triangulated {len(points_3d)} 3D points from images {idx1} and {idx2}")
        
        return points_3d, colors
    
    def reconstruct_incremental(self) -> bool:
        """
        Incremental reconstruction from image sequence
        
        Returns:
            True if reconstruction successful
        """
        if len(self.images) < 2:
            logger.error("Need at least 2 images for reconstruction")
            return False
        
        # Initialize with first two images
        logger.info("Initializing reconstruction with first two images...")
        points_3d, colors_3d = self.reconstruct_pair(0, 1)
        
        if len(points_3d) == 0:
            logger.error("Failed to initialize reconstruction")
            return False
        
        self.points_3d = points_3d.tolist()
        self.colors_3d = colors_3d.tolist()
        
        # Reference pose (identity)
        self.camera_poses = [CameraPose(R=np.eye(3), t=np.zeros((3, 1)))]
        
        # Estimate pose for second image
        pose2 = self.estimate_pose_pair(0, 1)
        if pose2 is None:
            logger.error("Failed to estimate pose for second image")
            return False
        self.camera_poses.append(pose2)
        
        # Incrementally add remaining images
        for i in range(2, len(self.images)):
            logger.info(f"Adding image {i} to reconstruction...")
            
            # Estimate pose relative to previous image
            pose = self.estimate_pose_pair(i-1, i)
            if pose is None:
                logger.warning(f"Failed to estimate pose for image {i}, skipping...")
                continue
            
            # Compose with previous pose
            prev_pose = self.camera_poses[-1]
            R_composed = pose.R @ prev_pose.R
            t_composed = prev_pose.t + prev_pose.R @ pose.t
            
            new_pose = CameraPose(R=R_composed, t=t_composed)
            self.camera_poses.append(new_pose)
            
            # Triangulate new points
            new_points, new_colors = self.reconstruct_pair(i-1, i)
            if len(new_points) > 0:
                self.points_3d.extend(new_points.tolist())
                self.colors_3d.extend(new_colors.tolist())
        
        self.points_3d = np.array(self.points_3d)
        self.colors_3d = np.array(self.colors_3d)
        
        logger.info(f"✅ Reconstruction complete: {len(self.points_3d)} 3D points, {len(self.camera_poses)} camera poses")
        
        return True
    
    def save_pointcloud(self, output_path: str, format: str = "ply") -> bool:
        """
        Save reconstructed point cloud to file
        
        Args:
            output_path: Output file path
            format: File format ("ply" or "xyz")
        
        Returns:
            True if successful
        """
        if len(self.points_3d) == 0:
            logger.error("No 3D points to save")
            return False
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "ply" and OPEN3D_AVAILABLE:
            # Use Open3D for PLY export (better format support)
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(self.points_3d)
            pcd.colors = o3d.utility.Vector3dVector(self.colors_3d / 255.0)
            success = o3d.io.write_point_cloud(str(output_path), pcd)
            if success:
                logger.info(f"✅ Saved point cloud to {output_path} ({len(self.points_3d)} points)")
            return success
        else:
            # Fallback: Simple PLY or XYZ export
            with open(output_path, 'w') as f:
                if format.lower() == "ply":
                    f.write("ply\n")
                    f.write("format ascii 1.0\n")
                    f.write(f"element vertex {len(self.points_3d)}\n")
                    f.write("property float x\n")
                    f.write("property float y\n")
                    f.write("property float z\n")
                    f.write("property uchar red\n")
                    f.write("property uchar green\n")
                    f.write("property uchar blue\n")
                    f.write("end_header\n")
                    
                    for i in range(len(self.points_3d)):
                        pt = self.points_3d[i]
                        color = self.colors_3d[i] if i < len(self.colors_3d) else [128, 128, 128]
                        f.write(f"{pt[0]} {pt[1]} {pt[2]} {color[0]} {color[1]} {color[2]}\n")
                else:  # XYZ
                    for i in range(len(self.points_3d)):
                        pt = self.points_3d[i]
                        f.write(f"{pt[0]} {pt[1]} {pt[2]}\n")
            
            logger.info(f"✅ Saved point cloud to {output_path} ({len(self.points_3d)} points)")
            return True
    
    def visualize(self) -> bool:
        """
        Visualize reconstructed point cloud using Open3D
        
        Returns:
            True if visualization successful
        """
        if not OPEN3D_AVAILABLE:
            logger.warning("Open3D not available, cannot visualize")
            return False
        
        if len(self.points_3d) == 0:
            logger.error("No 3D points to visualize")
            return False
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.points_3d)
        pcd.colors = o3d.utility.Vector3dVector(self.colors_3d / 255.0)
        
        # Add camera poses as coordinate frames
        geometries = [pcd]
        for i, pose in enumerate(self.camera_poses):
            frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
            frame.transform(pose.to_matrix())
            geometries.append(frame)
        
        o3d.visualization.draw_geometries(geometries)
        return True


def sfm_pipeline(
    image_paths: List[str],
    output_path: str,
    intrinsics: Optional[CameraIntrinsics] = None,
    feature_type: str = "SIFT",
    visualize: bool = False
) -> Tuple[np.ndarray, List[CameraPose]]:
    """
    Complete SfM pipeline
    
    Args:
        image_paths: List of input image paths
        output_path: Output PLY file path
        intrinsics: Camera intrinsics (None = auto-estimate)
        feature_type: Feature detector type
        visualize: Whether to visualize results
    
    Returns:
        Tuple of (3D points, camera poses)
    """
    sfm = OpenCVSfM(intrinsics=intrinsics, feature_type=feature_type)
    
    # Load images
    if not sfm.load_images(image_paths):
        raise RuntimeError("Failed to load images")
    
    # Detect features
    if not sfm.detect_features():
        raise RuntimeError("Failed to detect features")
    
    # Reconstruct
    if not sfm.reconstruct_incremental():
        raise RuntimeError("Failed to reconstruct")
    
    # Save point cloud
    sfm.save_pointcloud(output_path)
    
    # Visualize if requested
    if visualize:
        sfm.visualize()
    
    return sfm.points_3d, sfm.camera_poses


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenCV-based Structure from Motion")
    parser.add_argument("images", nargs="+", help="Input image paths")
    parser.add_argument("-o", "--output", required=True, help="Output PLY file path")
    parser.add_argument("--feature", choices=["SIFT", "ORB"], default="SIFT", help="Feature detector type")
    parser.add_argument("--fx", type=float, help="Camera focal length X")
    parser.add_argument("--fy", type=float, help="Camera focal length Y")
    parser.add_argument("--cx", type=float, help="Camera principal point X")
    parser.add_argument("--cy", type=float, help="Camera principal point Y")
    parser.add_argument("--visualize", action="store_true", help="Visualize results")
    
    args = parser.parse_args()
    
    # Setup intrinsics if provided
    intrinsics = None
    if args.fx and args.fy:
        intrinsics = CameraIntrinsics(
            fx=args.fx,
            fy=args.fy or args.fx,
            cx=args.cx or 0,
            cy=args.cy or 0
        )
    
    # Run pipeline
    points_3d, poses = sfm_pipeline(
        args.images,
        args.output,
        intrinsics=intrinsics,
        feature_type=args.feature,
        visualize=args.visualize
    )
    
    print(f"✅ Reconstruction complete: {len(points_3d)} 3D points, {len(poses)} camera poses")

