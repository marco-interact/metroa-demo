#!/usr/bin/env python3
"""
OpenMVS Integration Module for Ultra Quality Mode

Converts COLMAP sparse reconstruction to OpenMVS format,
runs DensifyPointCloud, and optionally ReconstructMesh.
"""

import subprocess
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OpenMVSProcessor:
    """OpenMVS 3D Reconstruction Processor"""
    
    @staticmethod
    def _find_openmvs_tool(tool_name: str) -> str:
        """Find OpenMVS tool binary in common locations"""
        # Check common OpenMVS binary locations
        possible_paths = [
            tool_name,  # Try PATH first
            f"/usr/local/bin/{tool_name}",  # Standard install location
            f"/usr/local/bin/OpenMVS/{tool_name}",  # OpenMVS subdirectory
        ]
        
        for tool_path in possible_paths:
            try:
                result = subprocess.run(
                    [tool_path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 or result.returncode == 1:  # Some tools return 1 for --help
                    logger.debug(f"Found {tool_name} at: {tool_path}")
                    return tool_path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        # If not found, return the tool name and let subprocess handle the error
        logger.warning(f"⚠️  {tool_name} not found in standard locations, trying PATH")
        return tool_name
    
    def __init__(self, workspace_path: str):
        """
        Initialize OpenMVS processor
        
        Args:
            workspace_path: Base workspace path (e.g., /workspace/data/results/{scan_id})
        """
        self.workspace_path = Path(workspace_path)
        self.openmvs_path = self.workspace_path / "openmvs"
        self.colmap_sparse_path = self.workspace_path / "sparse" / "0"
        self.colmap_images_path = self.workspace_path / "images"
        
        # Create OpenMVS workspace
        self.openmvs_path.mkdir(parents=True, exist_ok=True)
        
        # Setup environment
        self.env = os.environ.copy()
        self.env['DISPLAY'] = os.getenv('DISPLAY', ':99')
        self.env['QT_QPA_PLATFORM'] = 'offscreen'
    
    def check_openmvs_available(self) -> bool:
        """Check if OpenMVS tools are available on PATH or in standard location"""
        # Check common OpenMVS binary locations
        openmvs_paths = [
            "InterfaceCOLMAP",  # Try PATH first
            "/usr/local/bin/InterfaceCOLMAP",  # Standard install location
            "/usr/local/bin/OpenMVS/InterfaceCOLMAP",  # OpenMVS subdirectory
        ]
        
        for tool_path in openmvs_paths:
            try:
                result = subprocess.run(
                    [tool_path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"✅ Found OpenMVS at: {tool_path}")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        logger.warning("⚠️  OpenMVS not found on PATH or standard locations")
        return False
    
    def export_colmap_to_openmvs(
        self,
        progress_callback=None
    ) -> Dict[str, any]:
        """
        Export COLMAP sparse reconstruction to OpenMVS format
        
        Uses InterfaceCOLMAP to convert COLMAP format to OpenMVS .mvs format
        
        Returns:
            Dictionary with status and output path
        """
        if not self.colmap_sparse_path.exists():
            raise FileNotFoundError(f"COLMAP sparse reconstruction not found: {self.colmap_sparse_path}")
        
        if not self.check_openmvs_available():
            raise RuntimeError("OpenMVS tools not available. Please install OpenMVS.")
        
        output_mvs = self.openmvs_path / "scene.mvs"
        
        if progress_callback:
            progress_callback("Exporting COLMAP to OpenMVS format...", 0)
        
        # Find InterfaceCOLMAP binary (check multiple locations)
        interface_colmap_path = self._find_openmvs_tool("InterfaceCOLMAP")
        
        # InterfaceCOLMAP command
        # Reference: https://github.com/cdcseacave/openMVS/wiki/InterfaceCOLMAP
        cmd = [
            interface_colmap_path,
            "--working-folder", str(self.openmvs_path),
            "--input-file", str(self.colmap_sparse_path),
            "--output-file", str(output_mvs),
            "--image-folder", str(self.colmap_images_path),
        ]
        
        try:
            logger.info(f"🔄 Exporting COLMAP to OpenMVS format...")
            logger.info(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                env=self.env,
                timeout=300  # 5 minute timeout
            )
            
            if progress_callback:
                progress_callback("COLMAP export complete", 50)
            
            if not output_mvs.exists():
                raise RuntimeError(f"OpenMVS scene file not created: {output_mvs}")
            
            logger.info(f"✅ Exported to OpenMVS format: {output_mvs}")
            
            return {
                "status": "success",
                "mvs_file": str(output_mvs),
                "workspace": str(self.openmvs_path)
            }
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else e.stdout if e.stdout else "No error output"
            logger.error(f"❌ COLMAP to OpenMVS export failed: {error_output}")
            raise RuntimeError(f"OpenMVS export failed: {error_output}")
        except subprocess.TimeoutExpired:
            logger.error("❌ OpenMVS export timed out")
            raise RuntimeError("OpenMVS export timed out")
    
    def densify_pointcloud(
        self,
        input_mvs: str,
        quality: str = "high",
        progress_callback=None
    ) -> Dict[str, any]:
        """
        Run OpenMVS DensifyPointCloud
        
        Args:
            input_mvs: Path to input .mvs file
            quality: Quality preset ("fast", "high_quality", "ultra_openmvs")
            progress_callback: Optional callback(stage_name, progress_pct)
        
        Returns:
            Dictionary with status and output PLY path
        """
        if not Path(input_mvs).exists():
            raise FileNotFoundError(f"Input MVS file not found: {input_mvs}")
        
        if not self.check_openmvs_available():
            raise RuntimeError("OpenMVS DensifyPointCloud not available")
        
        output_mvs = self.openmvs_path / "scene_dense.mvs"
        output_ply = self.openmvs_path / "scene_dense.ply"
        
        if progress_callback:
            progress_callback("Running OpenMVS DensifyPointCloud...", 0)
        
        # Quality-based parameters for DensifyPointCloud
        # Reference: https://github.com/cdcseacave/openMVS/wiki/DensifyPointCloud
        quality_params = {
            "fast": {
                "resolution-level": "1",      # Lower resolution for speed
                "min-resolution": "640",       # Minimum image resolution
                "max-resolution": "1920",      # Maximum image resolution
                "num-threads": "8",
            },
            "high_quality": {
                "resolution-level": "0",       # Full resolution
                "min-resolution": "1280",
                "max-resolution": "3200",
                "num-threads": "16",
            },
            "ultra_openmvs": {
                "resolution-level": "0",       # Full resolution
                "min-resolution": "1920",
                "max-resolution": "4096",
                "num-threads": "16",
            }
        }
        
        params = quality_params.get(quality, quality_params["high_quality"])
        
        cmd = [
            self._find_openmvs_tool("DensifyPointCloud"),
            "--working-folder", str(self.openmvs_path),
            "--input-file", str(input_mvs),
            "--output-file", str(output_mvs),
            "--resolution-level", params["resolution-level"],
            "--min-resolution", params["min-resolution"],
            "--max-resolution", params["max-resolution"],
            "--num-threads", params["num-threads"],
            "--estimate-colors", "1",          # Estimate colors from images
            "--estimate-normals", "1",         # Estimate normals
            "--check-densify", "1",            # Check consistency
        ]
        
        try:
            logger.info(f"🔬 Running OpenMVS DensifyPointCloud ({quality} quality)...")
            logger.info(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                env=self.env,
                timeout=1800  # 30 minute timeout
            )
            
            if progress_callback:
                progress_callback("DensifyPointCloud complete", 80)
            
            # Check if output was created
            if not output_mvs.exists():
                raise RuntimeError(f"Densified MVS file not created: {output_mvs}")
            
            # Export to PLY format
            if progress_callback:
                progress_callback("Exporting dense point cloud to PLY...", 80)
            
            export_cmd = [
                "ExportPointCloud",
                "--working-folder", str(self.openmvs_path),
                "--input-file", str(output_mvs),
                "--output-file", str(output_ply),
            ]
            
            subprocess.run(
                export_cmd,
                check=True,
                capture_output=True,
                text=True,
                env=self.env,
                timeout=300
            )
            
            if progress_callback:
                progress_callback("OpenMVS densification complete", 100)
            
            if not output_ply.exists():
                raise RuntimeError(f"PLY file not created: {output_ply}")
            
            logger.info(f"✅ OpenMVS densification complete: {output_ply}")
            
            return {
                "status": "success",
                "dense_mvs": str(output_mvs),
                "dense_ply": str(output_ply),
                "type": "openmvs"
            }
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else e.stdout if e.stdout else "No error output"
            logger.error(f"❌ OpenMVS DensifyPointCloud failed: {error_output}")
            raise RuntimeError(f"OpenMVS densification failed: {error_output}")
        except subprocess.TimeoutExpired:
            logger.error("❌ OpenMVS DensifyPointCloud timed out")
            raise RuntimeError("OpenMVS densification timed out")
    
    def reconstruct_mesh(
        self,
        input_mvs: str,
        progress_callback=None
    ) -> Optional[Dict[str, any]]:
        """
        Optionally run OpenMVS ReconstructMesh
        
        This is optional and can be enabled later if mesh generation is needed.
        For now, we focus on dense point clouds.
        
        Returns:
            Dictionary with mesh file path, or None if skipped
        """
        # Skip mesh reconstruction for now - focus on point clouds
        logger.info("ℹ️  Mesh reconstruction skipped (focusing on point clouds)")
        return None

