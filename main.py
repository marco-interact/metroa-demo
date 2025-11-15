#!/usr/bin/env python3
"""
ULTRA SIMPLE COLMAP Backend - ABSOLUTELY MINIMAL
Just FastAPI + basic endpoints - NO COMPLEX DEPENDENCIES
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
import sqlite3
import json
from datetime import datetime
import uuid
import subprocess
from pathlib import Path
import asyncio
# Configure logging FIRST (before any imports that might use logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from colmap_processor import COLMAPProcessor, process_video_to_pointcloud
from colmap_binary_parser import MeasurementSystem, COLMAPBinaryParser
from quality_presets import get_preset, map_legacy_quality, QUALITY_PRESETS
from pointcloud_postprocess import postprocess_pointcloud, get_pointcloud_stats
from openmvs_processor import OpenMVSProcessor

# Import OpenCV SfM for complementary reconstruction
try:
    from opencv_sfm import OpenCVSfM, sfm_pipeline, CameraIntrinsics
    from opencv_sfm_integration import (
        run_opencv_preview,
        run_opencv_fallback,
        compare_reconstructions
    )
    HAS_OPENCV_SFM = True
except ImportError:
    HAS_OPENCV_SFM = False
    logger.warning("OpenCV SfM not available")

# Import 360° video detection
try:
    from video_360_converter import detect_360_video
    HAS_360_SUPPORT = True
except ImportError:
    HAS_360_SUPPORT = False
    logger.warning("360° video support not available")

# Import GLTF converter
try:
    from ply_to_gltf import ply_to_glb, ply_to_gltf_ascii
    HAS_GLTF_SUPPORT = True
except ImportError:
    HAS_GLTF_SUPPORT = False
    logger.warning("GLTF export support not available")

# Create FastAPI app
app = FastAPI(title="Metroa Labs Backend", version="1.0.0")

# Mount static files for demo resources
app.mount("/demo-resources", StaticFiles(directory="demo-resources"), name="demo-resources")

# Mount results directory for user-uploaded reconstructions
app.mount("/results", StaticFiles(directory="/workspace/data/results"), name="results")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path - RunPod volume mount (50GB volume at /workspace)
DATABASE_PATH = os.getenv("DATABASE_PATH", "/workspace/database.db")

def update_scan_status(scan_id: str, status: str, error: str = None, progress: int = None, stage: str = None):
    """Update scan status in database with progress tracking"""
    conn = get_db_connection()
    try:
        # Add progress and stage columns if they don't exist
        try:
            conn.execute("ALTER TABLE scans ADD COLUMN progress INTEGER DEFAULT 0")
            conn.execute("ALTER TABLE scans ADD COLUMN current_stage TEXT")
        except:
            pass  # Columns already exist
        
        if error:
            conn.execute(
                "UPDATE scans SET status = ?, progress = 0 WHERE id = ?",
                (f"failed: {error}", scan_id)
            )
        else:
            update_query = "UPDATE scans SET status = ?"
            params = [status]
            
            if progress is not None:
                update_query += ", progress = ?"
                params.append(progress)
            
            if stage is not None:
                update_query += ", current_stage = ?"
                params.append(stage)
            
            update_query += " WHERE id = ?"
            params.append(scan_id)
            
            conn.execute(update_query, tuple(params))
        
        conn.commit()
    finally:
        conn.close()

def process_colmap_reconstruction(scan_id: str, video_path: str, quality: str):
    """
    Enhanced reconstruction pipeline with quality presets, OpenMVS, and Open3D post-processing
    
    Quality modes:
    - fast: Quick processing with conservative settings
    - high_quality: Enhanced COLMAP with Open3D cleanup
    - ultra_openmvs: COLMAP + OpenMVS + Open3D for maximum quality
    
    Legacy quality modes are automatically mapped:
    - low/medium → fast
    - high → high_quality
    - ultra → ultra_openmvs
    """
    import time
    start_time = time.time()
    
    try:
        # Map legacy quality to new preset system
        quality_mode = map_legacy_quality(quality)
        preset = get_preset(quality_mode)
        
        logger.info(f"🚀 Starting reconstruction for scan {scan_id}")
        logger.info(f"📊 Quality mode: {quality_mode} (mapped from legacy '{quality}')")
        logger.info(f"📋 Preset: {preset.description} ({preset.estimated_time}, target: {preset.target_points})")
        
        update_scan_status(scan_id, "extracting_frames")
        
        # Update database with quality_mode
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE scans SET quality_mode = ? WHERE id = ?",
                (quality_mode, scan_id)
            )
            conn.commit()
        finally:
            conn.close()
        
        # Create results directory
        results_dir = Path(f"/workspace/data/results/{scan_id}")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize COLMAP processor
        processor = COLMAPProcessor(str(results_dir))
        
        # Check if this is a 360° video
        conn = get_db_connection()
        scan_row = conn.execute("SELECT is_360 FROM scans WHERE id = ?", (scan_id,)).fetchone()
        is_360_video = False
        if scan_row:
            scan_dict = dict(scan_row)
            is_360_video = scan_dict.get('is_360', 0) == 1
        conn.close()
        
        # Step 1: Extract frames from video with AUTO FPS DETECTION
        stage_msg = "Converting 360° video to perspective frames..." if is_360_video else "Extracting frames from video..."
        update_scan_status(scan_id, "processing", progress=2, stage=stage_msg)
        logger.info(f"📹 Extracting frames from {video_path} {'(360° video)' if is_360_video else ''}")
        
        # Progress tracking for frame extraction (0-10%)
        def frame_progress_callback(current, total):
            if total > 0:
                progress_pct = 2 + int((current / total) * 8)  # 2-10%
                stage = f"Converting 360° video... ({current}/{total})" if is_360_video else f"Extracting frames... ({current}/{total})"
                update_scan_status(scan_id, "processing", progress=progress_pct, stage=stage)
        
        frame_count = processor.extract_frames(
            video_path=str(video_path),
            target_fps=None,  # Enable auto FPS detection
            quality=quality,
            progress_callback=frame_progress_callback,
            is_360=is_360_video
        )
        update_scan_status(scan_id, "processing", progress=10, stage=f"Extracted {frame_count} frames")
        logger.info(f"✅ Extracted {frame_count} frames")
        
        if frame_count < 3:
            raise Exception(f"Not enough frames extracted: {frame_count}. Need at least 3.")
        
        # Step 2: Extract SIFT features
        update_scan_status(scan_id, "processing", progress=10, stage="Extracting SIFT features...")
        logger.info(f"🔍 Extracting SIFT features")
        
        # Progress tracking for feature extraction (10-30%)
        def feature_progress_callback(current, total):
            if total > 0:
                progress_pct = 10 + int((current / total) * 20)  # 10-30%
                update_scan_status(scan_id, "processing", progress=progress_pct,
                                stage=f"Extracting SIFT features... ({current}/{total} images)")
        
        feature_stats = processor.extract_features(quality=quality, progress_callback=feature_progress_callback)
        update_scan_status(scan_id, "processing", progress=30, stage="Feature extraction complete")
        logger.info(f"✅ Feature extraction: {feature_stats}")
        
        # Step 3: Match features
        update_scan_status(scan_id, "processing", progress=30, stage="Matching features between images...")
        logger.info(f"🔗 Matching features")
        
        # Progress tracking for feature matching (30-50%)
        def match_progress_callback(current, total):
            if total > 0:
                progress_pct = 30 + int((current / total) * 20)  # 30-50%
                update_scan_status(scan_id, "processing", progress=progress_pct,
                                stage=f"Matching features... ({current}/{total} pairs)")
        
        match_stats = processor.match_features(quality=quality, progress_callback=match_progress_callback)
        update_scan_status(scan_id, "processing", progress=50, stage="Feature matching complete")
        logger.info(f"✅ Feature matching: {match_stats}")
        
        # Step 4: Sparse reconstruction
        update_scan_status(scan_id, "processing", progress=50, stage="Running sparse reconstruction...")
        logger.info(f"🏗️ Running sparse reconstruction")
        
        # Progress tracking for sparse reconstruction (50-65%)
        def sparse_progress_callback(stage_name, progress_pct):
            overall_pct = 50 + int(progress_pct * 0.15)  # 50-65%
            update_scan_status(scan_id, "processing", progress=overall_pct,
                            stage=f"Sparse reconstruction: {stage_name}")
        
        reconstruction_stats = processor.sparse_reconstruction(quality=quality, progress_callback=sparse_progress_callback)
        update_scan_status(scan_id, "processing", progress=65, stage="Sparse reconstruction complete")
        logger.info(f"✅ Sparse reconstruction: {reconstruction_stats}")
        
        # Extract sparse reconstruction metrics
        sparse_points = reconstruction_stats.get("best_model_points", 0)
        registered_images = reconstruction_stats.get("stats", {}).get("registered_images", 0)
        total_images = frame_count
        
        # Step 5: Dense reconstruction or OpenMVS (based on quality mode)
        ply_path = None
        raw_ply_path = None
        
        if quality_mode == "ultra_openmvs":
            # Ultra mode: Use OpenMVS for densification
            logger.info(f"🔬 Running OpenMVS densification (ultra_openmvs mode)...")
            
            try:
                openmvs_processor = OpenMVSProcessor(str(results_dir))
                
                # Progress tracking for OpenMVS (65-85%)
                def openmvs_progress_callback(stage_name, progress_pct):
                    overall_pct = 65 + int(progress_pct * 0.20)  # 65-85%
                    update_scan_status(scan_id, "processing", progress=overall_pct,
                                    stage=f"OpenMVS: {stage_name}")
                
                # Export COLMAP to OpenMVS format
                update_scan_status(scan_id, "processing", progress=65, stage="OpenMVS: Exporting COLMAP format...")
                export_result = openmvs_processor.export_colmap_to_openmvs(
                    progress_callback=lambda msg, pct: openmvs_progress_callback(msg, pct * 0.5)
                )
                
                # Run DensifyPointCloud
                update_scan_status(scan_id, "processing", progress=75, stage="OpenMVS: Densifying point cloud...")
                dense_result = openmvs_processor.densify_pointcloud(
                    input_mvs=export_result["mvs_file"],
                    quality="ultra_openmvs",
                    progress_callback=lambda msg, pct: openmvs_progress_callback(msg, 50 + pct * 0.5)
                )
                
                if dense_result.get("status") == "success" and dense_result.get("dense_ply"):
                    raw_ply_path = Path(dense_result["dense_ply"])
                    logger.info(f"✅ OpenMVS densification complete: {raw_ply_path}")
                    update_scan_status(scan_id, "processing", progress=85, stage="OpenMVS densification complete!")
                else:
                    raise RuntimeError("OpenMVS densification failed")
                    
            except Exception as e:
                logger.error(f"❌ OpenMVS processing failed: {e}")
                logger.warning("⚠️  Falling back to COLMAP dense reconstruction...")
                # Fallback to COLMAP dense
                quality_mode = "high_quality"
                preset = get_preset(quality_mode)
        
        # COLMAP dense reconstruction (for fast, high_quality, or OpenMVS fallback)
        if not raw_ply_path and preset.enable_dense:
            logger.info(f"🔬 Running COLMAP DENSE reconstruction ({quality_mode} mode)...")
            
            # Progress tracking for dense reconstruction (65-90%)
            def dense_progress_callback(stage_name, progress_pct):
                overall_pct = 65 + int(progress_pct * 0.25)  # 65-90%
                update_scan_status(scan_id, "processing", progress=overall_pct,
                                stage=f"Dense reconstruction: {stage_name}")
            
            update_scan_status(scan_id, "processing", progress=65, stage="Dense reconstruction: Undistorting images...")
            # Use legacy quality for COLMAP processor (it still uses old system)
            dense_stats = processor.dense_reconstruction(quality=quality, progress_callback=dense_progress_callback)
            logger.info(f"✅ Dense reconstruction: {dense_stats}")
            
            if dense_stats.get("status") == "success" and dense_stats.get("dense_ply"):
                raw_ply_path = Path(dense_stats["dense_ply"])
                logger.info(f"✅ Using COLMAP DENSE point cloud: {raw_ply_path}")
                update_scan_status(scan_id, "processing", progress=90, stage="Dense reconstruction complete!")
        
        # Step 6: Export sparse PLY (fallback if no dense)
        if not raw_ply_path:
            update_scan_status(scan_id, "processing", progress=80, stage="Exporting sparse point cloud...")
            logger.info(f"💾 Exporting SPARSE point cloud (no dense reconstruction)")
            raw_ply_path_str = processor.export_model(output_format="PLY")
            raw_ply_path = Path(raw_ply_path_str) if raw_ply_path_str else None
            logger.info(f"✅ Exported sparse PLY: {raw_ply_path}")
        
        # Step 7: Open3D Post-Processing (clean and optimize point cloud)
        final_ply_path = None
        postprocessing_stats = None
        
        # Ensure raw_ply_path is a Path object
        if raw_ply_path:
            if isinstance(raw_ply_path, str):
                raw_ply_path = Path(raw_ply_path)
        
        if raw_ply_path and raw_ply_path.exists():
            update_scan_status(scan_id, "processing", progress=90, stage="Post-processing point cloud with Open3D...")
            logger.info(f"🧹 Post-processing point cloud: {raw_ply_path}")
            
            # Get point count before post-processing
            raw_stats = get_pointcloud_stats(str(raw_ply_path))
            point_count_raw = raw_stats.get("point_count", 0)
            
            # Prepare Open3D post-processing parameters from preset
            open3d_config = {
                "open3d_outlier_removal": preset.open3d_outlier_removal,
                "open3d_statistical_nb_neighbors": preset.open3d_statistical_nb_neighbors,
                "open3d_statistical_std_ratio": preset.open3d_statistical_std_ratio,
                "open3d_downsample_threshold": preset.open3d_downsample_threshold,
                "open3d_voxel_size": preset.open3d_voxel_size,
            }
            
            # Post-process point cloud
            final_ply_path = results_dir / "pointcloud_final.ply"
            
            def postprocess_progress_callback(step, total, message):
                progress_pct = 90 + int((step / total) * 8)  # 90-98%
                update_scan_status(scan_id, "processing", progress=progress_pct,
                                stage=f"Open3D: {message}")
            
            try:
                postprocessing_stats = postprocess_pointcloud(
                    input_ply_path=str(raw_ply_path),
                    output_ply_path=str(final_ply_path),
                    quality_preset=open3d_config,
                    progress_callback=postprocess_progress_callback
                )
                
                point_count_final = postprocessing_stats.get("point_count_after", point_count_raw)
                logger.info(f"✅ Post-processing complete: {point_count_raw:,} → {point_count_final:,} points")
                
            except Exception as e:
                logger.error(f"❌ Post-processing failed: {e}")
                logger.warning("⚠️  Using raw point cloud without post-processing")
                # Fallback: use raw PLY
                final_ply_path = raw_ply_path
                postprocessing_stats = {"error": str(e), "point_count_after": point_count_raw}
        else:
            logger.error(f"❌ No point cloud file found for post-processing")
            raise RuntimeError("No point cloud file generated")
        
        # Use final PLY path for statistics
        ply_path = final_ply_path
        dense_points = postprocessing_stats.get("point_count_after", 0) if postprocessing_stats else 0
        
        # Step 8: Calculate processing time
        processing_time = time.time() - start_time
        
        # Step 9: Save reconstruction metrics
        try:
            from database import db
            metrics = {
                "quality_mode": quality_mode,  # Use new quality_mode, not legacy quality
                "sparse_points": sparse_points,
                "dense_points": dense_points,
                "registered_images": registered_images,
                "total_images": total_images,
                "avg_reproj_error": reconstruction_stats.get("stats", {}).get("avg_reproj_error", 0.0),
                "avg_track_length": reconstruction_stats.get("stats", {}).get("avg_track_length", 0.0),
                "coverage_percentage": (registered_images / max(total_images, 1)) * 100,
                "processing_time_seconds": processing_time
            }
            db.save_reconstruction_metrics(scan_id, metrics)
            logger.info(f"📊 Saved metrics: {dense_points:,} dense points ({dense_points/max(sparse_points,1):.1f}x multiplier)")
        except Exception as e:
            logger.warning(f"Could not save reconstruction metrics: {e}")
        
        # Step 10: Update database with final PLY path and statistics
        update_scan_status(scan_id, "processing", progress=98, stage="Finalizing reconstruction...")
        conn = get_db_connection()
        try:
            # Prepare postprocessing stats JSON
            postprocessing_stats_json = json.dumps(postprocessing_stats) if postprocessing_stats else None
            
            conn.execute(
                """UPDATE scans SET 
                    status = ?, 
                    ply_file = ?,
                    pointcloud_final_path = ?,
                    point_count_raw = ?,
                    point_count_final = ?,
                    postprocessing_stats = ?,
                    progress = 100, 
                    current_stage = ? 
                   WHERE id = ?""",
                (
                    "completed",
                    str(raw_ply_path),  # Keep original PLY path for compatibility
                    str(final_ply_path),  # New: final cleaned PLY path
                    postprocessing_stats.get("point_count_before", 0) if postprocessing_stats else 0,
                    postprocessing_stats.get("point_count_after", 0) if postprocessing_stats else dense_points,
                    postprocessing_stats_json,
                    "Reconstruction complete!",
                    scan_id
                )
            )
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"✅ Reconstruction complete for scan {scan_id} ({processing_time:.1f}s)")
        logger.info(f"📊 Quality mode: {quality_mode}, Points: {dense_points:,}")
        
    except Exception as e:
        logger.error(f"❌ COLMAP reconstruction failed for scan {scan_id}: {e}")
        update_scan_status(scan_id, "failed", str(e))

def get_db_connection():
    """Get database connection"""
    # Ensure /workspace directory exists (50GB persistent volume)
    os.makedirs("/workspace", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    try:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Projects table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                location TEXT,
                space_type TEXT,
                project_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Scans table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                video_filename TEXT,
                video_size INTEGER,
                processing_quality TEXT,
                status TEXT DEFAULT 'pending',
                ply_file TEXT,
                glb_file TEXT,
                thumbnail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Add new columns to existing scans table if they don't exist
        try:
            conn.execute('ALTER TABLE scans ADD COLUMN ply_file TEXT')
            logger.info("✅ Added ply_file column")
        except:
            pass  # Column already exists
        
        try:
            conn.execute('ALTER TABLE scans ADD COLUMN glb_file TEXT')
            logger.info("✅ Added glb_file column")
        except:
            pass  # Column already exists
            
        try:
            conn.execute('ALTER TABLE scans ADD COLUMN thumbnail TEXT')
            logger.info("✅ Added thumbnail column")
        except:
            pass  # Column already exists
        
        conn.commit()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
    finally:
        conn.close()

@app.get("/")
async def root():
    return {"message": "COLMAP Backend is running!", "database_path": DATABASE_PATH}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Backend is running", "database_path": DATABASE_PATH}

@app.get("/api/status")
async def get_status():
    """Get current backend status and demo data info"""
    try:
        conn = get_db_connection()
        
        # Get projects count
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        
        # Get projects
        projects = conn.execute("SELECT id, name FROM projects").fetchall()
        projects_list = [{"id": p["id"], "name": p["name"]} for p in projects]
        
        # Get scans count
        scans_count = conn.execute("SELECT COUNT(*) as count FROM scans").fetchone()["count"]
        
        status = {
            "backend": "running",
            "database_path": DATABASE_PATH,
            "projects_count": projects_count,
            "scans_count": scans_count,
            "projects": projects_list
        }
        
        conn.close()
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"backend": "error", "error": str(e)}

@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    try:
        conn = get_db_connection()
        projects = conn.execute("SELECT * FROM projects").fetchall()
        projects_list = [dict(p) for p in projects]
        conn.close()
        return {"projects": projects_list}
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New: get single project by id
@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a single project by ID"""
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/scans")
async def get_scans(project_id: str):
    """Get scans for a project"""
    try:
        conn = get_db_connection()
        scans = conn.execute("SELECT * FROM scans WHERE project_id = ?", (project_id,)).fetchall()
        scans_list = [dict(s) for s in scans]
        conn.close()
        return {"scans": scans_list}
    except Exception as e:
        logger.error(f"Error getting scans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scans/{scan_id}/details")
async def get_scan_details(scan_id: str):
    """Get detailed information for a specific scan"""
    try:
        conn = get_db_connection()
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        conn.close()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_dict = dict(scan)
        
        # Add results URLs based on scan files
        if scan_dict.get('ply_file'):
            ply_path = scan_dict['ply_file']
            
            # Check if it's a demo scan (relative path) or user scan (absolute path)
            if ply_path.startswith('/workspace/'):
                # User-uploaded scan - serve from results directory
                # Convert: /workspace/data/results/{scan_id}/point_cloud.ply
                # To: /api/backend/results/{scan_id}/point_cloud.ply
                relative_path = ply_path.replace('/workspace/data/results/', '')
                point_cloud_url = f"/results/{relative_path}"
            else:
                # Demo scan - serve from demo-resources
                point_cloud_url = f"/demo-resources/{ply_path}"
            
            scan_dict['results'] = {
                'point_cloud_url': point_cloud_url,
                'mesh_url': f"/demo-resources/{scan_dict['glb_file']}" if scan_dict.get('glb_file') and not scan_dict['glb_file'].startswith('/') else None,
                'thumbnail_url': f"/demo-resources/{scan_dict['thumbnail']}" if scan_dict.get('thumbnail') and not scan_dict['thumbnail'].startswith('/') else None
            }
        
        return scan_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reconstruction/{scan_id}/statistics")
async def get_reconstruction_statistics(scan_id: str):
    """
    Get detailed reconstruction statistics for a scan
    
    Returns metrics including:
    - Point counts (sparse vs dense)
    - Density multiplier
    - Registration rate
    - Quality grade
    - Processing time
    """
    try:
        from database import db
        metrics = db.get_reconstruction_metrics(scan_id)
        
        if not metrics:
            # Return default structure if no metrics found
            return {
                "scan_id": scan_id,
                "status": "no_metrics",
                "message": "Reconstruction metrics not yet available"
            }
        
        return {
            "scan_id": scan_id,
            "quality_mode": metrics.get("quality_mode", "unknown"),
            "sparse_points": metrics.get("sparse_points", 0),
            "dense_points": metrics.get("dense_points", 0),
            "density_multiplier": round(metrics.get("density_multiplier", 0.0), 2),
            "registered_images": metrics.get("registered_images", 0),
            "total_images": metrics.get("total_images", 0),
            "registration_rate": round(metrics.get("registration_rate", 0.0), 3),
            "avg_reproj_error": round(metrics.get("avg_reproj_error", 0.0), 3),
            "avg_track_length": round(metrics.get("avg_track_length", 0.0), 2),
            "coverage_percentage": round(metrics.get("coverage_percentage", 0.0), 1),
            "processing_time_seconds": round(metrics.get("processing_time_seconds", 0.0), 1),
            "quality_grade": metrics.get("quality_grade", "N/A")
        }
    except Exception as e:
        logger.error(f"Failed to get reconstruction statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan and its associated files"""
    try:
        conn = get_db_connection()
        
        # Get scan info before deleting
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        
        if not scan:
            conn.close()
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_dict = dict(scan)
        
        # Don't allow deleting demo scans
        if scan_dict.get('name') in ['Dollhouse Scan', 'demoscan-dollhouse']:
            conn.close()
            raise HTTPException(status_code=403, detail="Cannot delete demo scans")
        
        # Delete scan from database
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        conn.close()
        
        # Delete associated files
        import shutil
        scan_upload_dir = Path(f"/workspace/data/uploads/{scan_id}")
        scan_results_dir = Path(f"/workspace/data/results/{scan_id}")
        
        if scan_upload_dir.exists():
            shutil.rmtree(scan_upload_dir)
            logger.info(f"Deleted upload directory: {scan_upload_dir}")
        
        if scan_results_dir.exists():
            shutil.rmtree(scan_results_dir)
            logger.info(f"Deleted results directory: {scan_results_dir}")
        
        logger.info(f"✅ Deleted scan {scan_id}")
        
        return {
            "status": "success",
            "message": f"Scan {scan_dict.get('name')} deleted successfully",
            "scan_id": scan_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/point-cloud/{scan_id}/stats")
async def get_point_cloud_stats(scan_id: str):
    """Get point cloud statistics for a scan"""
    try:
        # Check if scan exists
        conn = get_db_connection()
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        conn.close()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_dict = dict(scan)
        
        # Check if point cloud file exists
        ply_file = scan_dict.get('ply_file')
        if not ply_file:
            # Return empty stats if no point cloud yet
            return {
                "status": "pending",
                "message": "Point cloud not yet generated",
                "point_count": 0,
                "bounds": None
            }
        
        # Try to get stats from COLMAP reconstruction
        results_dir = Path(f"/workspace/data/results/{scan_id}")
        sparse_path = results_dir / "sparse" / "0"
        
        if sparse_path.exists():
            try:
                from colmap_binary_parser import COLMAPBinaryParser
                parser = COLMAPBinaryParser(str(sparse_path))
                parser.load_reconstruction()
                
                return {
                    "status": "completed",
                    "point_count": len(parser.points3D),
                    "camera_count": len(parser.cameras),
                    "image_count": len(parser.images),
                    "bounds": {
                        "min": parser.points3D.min(axis=0).tolist() if len(parser.points3D) > 0 else [0, 0, 0],
                        "max": parser.points3D.max(axis=0).tolist() if len(parser.points3D) > 0 else [0, 0, 0]
                    }
                }
            except Exception as e:
                logger.warning(f"Could not parse COLMAP reconstruction: {e}")
        
        # Fallback: basic stats
        return {
            "status": "completed",
            "message": "Point cloud available",
            "point_count": 0,  # Unknown
            "bounds": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting point cloud stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status with detailed progress tracking"""
    try:
        conn = get_db_connection()
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        
        if scan:
            scan_dict = dict(scan)
            status = scan_dict.get("status", "pending")
            
            # Map status to progress percentage and stage
            status_map = {
                "pending": (0, "Queued"),
                "processing": (10, "Starting"),
                "extracting_frames": (20, "Extracting frames from video"),
                "extracting_features": (40, "Detecting SIFT features"),
                "matching_features": (60, "Matching features"),
                "reconstructing": (80, "Building 3D model"),
                "exporting": (90, "Exporting point cloud"),
                "completed": (100, "Complete"),
            }
            
            # Handle failed status
            if status.startswith("failed"):
                return {
                    "job_id": job_id,
                    "scan_id": job_id,
                    "status": "failed",
                    "progress": 0,
                    "message": status.replace("failed: ", ""),
                    "current_stage": "Failed"
                }
            
            progress, stage = status_map.get(status, (0, "Unknown"))
            
            return {
                "job_id": job_id,
                "scan_id": job_id,
                "status": status,
                "progress": progress,
                "message": f"Processing: {stage}",
                "current_stage": stage
            }
        
        # Job not found
        return {
            "job_id": job_id,
            "status": "not_found",
            "progress": 0,
            "message": "Job not found in system"
        }
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return {
            "job_id": job_id,
            "status": "error",
            "progress": 0,
            "message": str(e)
        }

# Measurement System Endpoints

@app.post("/api/measurements/calibrate")
async def calibrate_scale(
    scan_id: str = Form(...),
    point1_id: str = Form(None),  # Can be ID or position
    point2_id: str = Form(None),
    point1_position: str = Form(None),  # JSON array: "[x, y, z]"
    point2_position: str = Form(None),
    known_distance: float = Form(...)
):
    """Calibrate scale using two points with known distance
    
    Accepts either:
    - point1_id/point2_id: COLMAP point IDs (legacy)
    - point1_position/point2_position: 3D positions as JSON arrays "[x, y, z]" (new)
    """
    try:
        logger.info(f"🔧 Calibration request: scan_id={scan_id}, distance={known_distance}")
        
        # Find sparse reconstruction path
        scan_path = Path(f"/workspace/data/results/{scan_id}")
        sparse_path = scan_path / "sparse" / "0"
        
        if not sparse_path.exists():
            logger.error(f"❌ Sparse reconstruction not found at: {sparse_path}")
            raise HTTPException(status_code=404, detail=f"Reconstruction not found at {sparse_path}")
        
        # Load and calibrate
        measurement_system = MeasurementSystem(str(sparse_path))
        measurement_system.load_reconstruction()
        
        # Check if points exist
        if not measurement_system.points3D:
            raise HTTPException(status_code=404, detail="No 3D points found in reconstruction")
        
        logger.info(f"📊 Loaded {len(measurement_system.points3D)} points from reconstruction")
        
        # Determine point IDs - use positions if provided, otherwise use IDs
        if point1_position and point2_position:
            # New method: find nearest points by position
            import json
            import numpy as np
            
            try:
                pos1 = np.array(json.loads(point1_position))
                pos2 = np.array(json.loads(point2_position))
                
                logger.info(f"📍 Finding nearest points to positions: {pos1}, {pos2}")
                
                # Find nearest points in sparse reconstruction
                point1_id = measurement_system.find_nearest_point(pos1)
                point2_id = measurement_system.find_nearest_point(pos2)
                
                logger.info(f"✅ Found nearest points: {point1_id}, {point2_id}")
            except Exception as e:
                logger.error(f"❌ Error parsing positions: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid position format: {e}")
        elif point1_id and point2_id:
            # Legacy method: use point IDs directly
            try:
                point1_id = int(point1_id)
                point2_id = int(point2_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid point ID format")
        else:
            raise HTTPException(status_code=400, detail="Must provide either point IDs or positions")
        
        # Check if point IDs exist
        if point1_id not in measurement_system.points3D:
            available_ids = list(measurement_system.points3D.keys())[:10]
            raise HTTPException(
                status_code=400, 
                detail=f"Point ID {point1_id} not found in reconstruction. Available IDs (sample): {available_ids}"
            )
        if point2_id not in measurement_system.points3D:
            available_ids = list(measurement_system.points3D.keys())[:10]
            raise HTTPException(
                status_code=400, 
                detail=f"Point ID {point2_id} not found in reconstruction. Available IDs (sample): {available_ids}"
            )
        
        result = measurement_system.calibrate_scale(point1_id, point2_id, known_distance)
        
        logger.info(f"✅ Calibration successful: scale_factor={result['scale_factor']:.6f}")
        
        # Save scale factor to scan metadata
        conn = get_db_connection()
        # TODO: Add scale_factor column to scans table
        conn.close()
        
        return {
            "status": "success",
            "scan_id": scan_id,
            **result
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Scale calibration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calibration failed: {str(e)}")

@app.post("/api/measurements/add")
async def add_measurement(
    scan_id: str = Form(...),
    measurement_type: str = Form("distance"),
    point1_id: str = Form(None),
    point2_id: str = Form(None),
    point3_id: str = Form(None),
    point1_position: str = Form(None),
    point2_position: str = Form(None),
    point3_position: str = Form(None),
    point_position: str = Form(None),  # For info measurement
    points: str = Form(None),  # JSON array for radius measurement
    label: str = Form("")
):
    """Add a measurement of various types
    
    Measurement types:
    - distance: 2 points
    - angle: 3 points (point2 is vertex)
    - thickness: 2 points (surface to surface)
    - radius: 3+ points (on curve)
    - info: 1 point (coordinates and normal)
    
    Accepts either:
    - point IDs (legacy)
    - point positions as JSON arrays "[x, y, z]" (new)
    """
    try:
        import json
        import numpy as np
        
        scan_path = Path(f"/workspace/data/results/{scan_id}")
        sparse_path = scan_path / "sparse" / "0"
        
        if not sparse_path.exists():
            raise HTTPException(status_code=404, detail="Reconstruction not found")
        
        measurement_system = MeasurementSystem(str(sparse_path))
        measurement_system.load_reconstruction()
        
        # TODO: Load previously saved scale factor from database
        
        measurement = None
        
        if measurement_type == "distance" or measurement_type == "thickness":
            # Distance or Thickness: 2 points
            if point1_position and point2_position:
                pos1 = np.array(json.loads(point1_position))
                pos2 = np.array(json.loads(point2_position))
                point1_id = measurement_system.find_nearest_point(pos1)
                point2_id = measurement_system.find_nearest_point(pos2)
            elif point1_id and point2_id:
                point1_id = int(point1_id)
                point2_id = int(point2_id)
            else:
                raise HTTPException(status_code=400, detail="Need 2 points for distance/thickness")
            
            if measurement_type == "distance":
                measurement = measurement_system.add_measurement(point1_id, point2_id, label)
            else:  # thickness
                thickness = measurement_system.calculate_thickness(point1_id, point2_id)
                measurement = {
                    "id": len(measurement_system.measurements),
                    "type": "thickness",
                    "point1_id": point1_id,
                    "point2_id": point2_id,
                    "thickness_meters": thickness,
                    "label": label or f"Thickness {len(measurement_system.measurements) + 1}",
                    "scaled": measurement_system.scale_factor != 1.0
                }
                measurement_system.measurements.append(measurement)
        
        elif measurement_type == "angle":
            # Angle: 3 points (point2 is vertex)
            if point1_position and point2_position and point3_position:
                pos1 = np.array(json.loads(point1_position))
                pos2 = np.array(json.loads(point2_position))
                pos3 = np.array(json.loads(point3_position))
                point1_id = measurement_system.find_nearest_point(pos1)
                point2_id = measurement_system.find_nearest_point(pos2)
                point3_id = measurement_system.find_nearest_point(pos3)
            elif point1_id and point2_id and point3_id:
                point1_id = int(point1_id)
                point2_id = int(point2_id)
                point3_id = int(point3_id)
            else:
                raise HTTPException(status_code=400, detail="Need 3 points for angle (vertex in middle)")
            
            angle_deg = measurement_system.calculate_angle(point1_id, point2_id, point3_id)
            measurement = {
                "id": len(measurement_system.measurements),
                "type": "angle",
                "point1_id": point1_id,
                "point2_id": point2_id,
                "point3_id": point3_id,
                "angle_degrees": angle_deg,
                "label": label or f"Angle {len(measurement_system.measurements) + 1}",
                "scaled": measurement_system.scale_factor != 1.0
            }
            measurement_system.measurements.append(measurement)
        
        elif measurement_type == "radius":
            # Radius: 3+ points on curve
            if points:
                positions = json.loads(points)
                if len(positions) < 3:
                    raise HTTPException(status_code=400, detail="Need at least 3 points for radius")
                point_ids = []
                for pos in positions:
                    pos_array = np.array(pos)
                    pid = measurement_system.find_nearest_point(pos_array)
                    point_ids.append(pid)
            else:
                raise HTTPException(status_code=400, detail="Need points array for radius measurement")
            
            radius_result = measurement_system.calculate_radius(point_ids)
            measurement = {
                "id": len(measurement_system.measurements),
                "type": "radius",
                "points": point_ids,
                "radius_meters": radius_result["radius_meters"],
                "center": radius_result["center"],
                "label": label or f"Radius {len(measurement_system.measurements) + 1}",
                "scaled": measurement_system.scale_factor != 1.0
            }
            measurement_system.measurements.append(measurement)
        
        elif measurement_type == "info":
            # Info: 1 point
            if point_position:
                pos = np.array(json.loads(point_position))
                point_id = measurement_system.find_nearest_point(pos)
            elif point1_id:
                point_id = int(point1_id)
            else:
                raise HTTPException(status_code=400, detail="Need 1 point for info")
            
            info = measurement_system.get_point_info(point_id)
            measurement = {
                "id": len(measurement_system.measurements),
                "type": "info",
                "point_id": point_id,
                "position": info["position"],
                "normal": info["normal"],
                "label": label or f"Point Info {len(measurement_system.measurements) + 1}",
                "scaled": measurement_system.scale_factor != 1.0
            }
            measurement_system.measurements.append(measurement)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown measurement type: {measurement_type}")
        
        logger.info(f"✅ Added {measurement_type} measurement: {measurement.get('label', 'unnamed')}")
        
        return {
            "status": "success",
            "measurement": measurement
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add measurement failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurements/{scan_id}/export")
async def export_measurements(scan_id: str, format: str = "json"):
    """Export measurements for a scan"""
    try:
        scan_path = Path(f"/workspace/data/results/{scan_id}")
        sparse_path = scan_path / "sparse" / "0"
        
        if not sparse_path.exists():
            raise HTTPException(status_code=404, detail="Reconstruction not found")
        
        measurement_system = MeasurementSystem(str(sparse_path))
        measurement_system.load_reconstruction()
        
        # TODO: Load saved measurements from database
        
        export_data = measurement_system.export_measurements(format)
        
        if format == "csv":
            from fastapi.responses import Response
            return Response(content=export_data, media_type="text/csv")
        else:
            return JSONResponse(content=json.loads(export_data))
            
    except Exception as e:
        logger.error(f"Export measurements failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurements/{scan_id}/stats")
async def get_reconstruction_stats(scan_id: str):
    """Get reconstruction statistics for measurement system"""
    try:
        scan_path = Path(f"/workspace/data/results/{scan_id}")
        sparse_path = scan_path / "sparse" / "0"
        
        if not sparse_path.exists():
            raise HTTPException(status_code=404, detail="Reconstruction not found")
        
        measurement_system = MeasurementSystem(str(sparse_path))
        measurement_system.load_reconstruction()
        
        stats = measurement_system.get_reconstruction_stats()
        
        return {
            "status": "success",
            "scan_id": scan_id,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects")
async def create_project(user_email: str, name: str, description: str = "", location: str = "", space_type: str = "", project_type: str = ""):
    """Create a new project"""
    try:
        conn = get_db_connection()
        
        # Get or create user
        user_row = conn.execute("SELECT id FROM users WHERE email = ?", (user_email,)).fetchone()
        if not user_row:
            user_id = str(uuid.uuid4())
            conn.execute("INSERT INTO users (id, email) VALUES (?, ?)", (user_id, user_email))
            conn.commit()
        else:
            user_id = user_row["id"]
        
        # Create project
        project_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO projects (id, user_id, name, description, location, space_type, project_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (project_id, user_id, name, description, location, space_type, project_type)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Created project: {name} (ID: {project_id})")
        return {"status": "success", "project_id": project_id}
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/cleanup-duplicates")
async def cleanup_duplicates():
    """Clean up duplicate demo projects and scans"""
    try:
        logger.info("🧹 Cleaning up duplicate demo data...")
        from database import db
        result = db.cleanup_duplicate_demos()
        
        # Verify cleanup
        conn = get_db_connection()
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        scans_count = conn.execute("SELECT COUNT(*) as count FROM scans").fetchone()["count"]
        conn.close()
        
        logger.info(f"📊 After cleanup: {projects_count} projects, {scans_count} scans")
        
        return {
            "status": result.get("status", "success"),
            "message": result.get("message", "Cleanup completed"),
            "deleted_projects": result.get("deleted_projects", 0),
            "deleted_scans": result.get("deleted_scans", 0),
            "current_projects": projects_count,
            "current_scans": scans_count
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/force-delete-project")
async def force_delete_project(project_name: str = Form(...)):
    """Force delete a project by name and all its associated data"""
    try:
        logger.info(f"🗑️ Force deleting project: {project_name}")
        from database import db
        result = db.force_delete_project_by_name(project_name)
        
        # Also delete associated files from filesystem
        if result.get("status") == "success":
            project_id = result.get("project_id")
            if project_id:
                import shutil
                from pathlib import Path
                
                # Delete upload directories for all scans in this project
                conn = get_db_connection()
                try:
                    scan_ids = conn.execute(
                        "SELECT id FROM scans WHERE project_id = ?",
                        (project_id,)
                    ).fetchall()
                    # Note: scans are already deleted, but we can still try to clean up files
                    # if they exist
                except:
                    pass
                finally:
                    conn.close()
                
                # Try to delete any remaining scan directories
                # (scans are already deleted from DB, but files might still exist)
                upload_base = Path("/workspace/data/uploads")
                results_base = Path("/workspace/data/results")
                
                if upload_base.exists():
                    for scan_dir in upload_base.iterdir():
                        if scan_dir.is_dir():
                            try:
                                shutil.rmtree(scan_dir)
                                logger.info(f"Deleted upload directory: {scan_dir}")
                            except Exception as e:
                                logger.warning(f"Could not delete {scan_dir}: {e}")
                
                if results_base.exists():
                    for scan_dir in results_base.iterdir():
                        if scan_dir.is_dir():
                            try:
                                shutil.rmtree(scan_dir)
                                logger.info(f"Deleted results directory: {scan_dir}")
                            except Exception as e:
                                logger.warning(f"Could not delete {scan_dir}: {e}")
        
        # Verify deletion
        conn = get_db_connection()
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        scans_count = conn.execute("SELECT COUNT(*) as count FROM scans").fetchone()["count"]
        conn.close()
        
        logger.info(f"📊 After deletion: {projects_count} projects, {scans_count} scans")
        
        return {
            "status": result.get("status", "success"),
            "message": result.get("message", "Project deleted"),
            "deleted_projects": result.get("deleted_projects", 0),
            "deleted_scans": result.get("deleted_scans", 0),
            "current_projects": projects_count,
            "current_scans": scans_count
        }
    except Exception as e:
        logger.error(f"Error cleaning up duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/setup-demo")
async def setup_demo_data():
    """Setup demo data using database class"""
    try:
        logger.info("🔄 Setting up demo data...")
        from database import db
        
        # Clean up duplicates first
        cleanup_result = db.cleanup_duplicate_demos()
        if cleanup_result.get("deleted_projects", 0) > 0:
            logger.info(f"🧹 Cleaned up {cleanup_result.get('deleted_projects')} duplicate projects")
        
        result = db.setup_demo_data()
        
        # Verify demo data was created
        conn = get_db_connection()
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        scans_count = conn.execute("SELECT COUNT(*) as count FROM scans").fetchone()["count"]
        conn.close()
        
        logger.info(f"📊 Demo data ready: {projects_count} projects, {scans_count} scans")
        
        return {
            "status": "success", 
            "data": result,
            "verification": {
                "projects_count": projects_count,
                "scans_count": scans_count
            }
        }
    except Exception as e:
        logger.error(f"Demo data setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reconstruction/upload")
async def upload_video_for_reconstruction(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    scan_name: str = Form(...),
    quality: str = Form("high"),  # Default to "high" for best quality (recommended)
    user_email: str = Form("demo@metroa.app"),
    video: UploadFile = File(...)
):
    """
    Upload video for 3D reconstruction processing
    Based on: https://colmap.github.io/tutorial.html
    """
    try:
        logger.info(f"📹 Received video upload for project {project_id}")
        
        # Generate scan ID (used as job ID too)
        scan_id = str(uuid.uuid4())
        job_id = scan_id
        
        # Create job directory in data/uploads for persistence
        upload_dir = Path(f"/workspace/data/uploads/{scan_id}")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded video
        video_path = upload_dir / video.filename
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        logger.info(f"💾 Saved video to {video_path} ({len(content)} bytes)")
        
        # Detect 360° video format
        is_360_video = False
        video_format_info = {}
        if HAS_360_SUPPORT:
            try:
                video_format_info = detect_360_video(str(video_path))
                is_360_video = video_format_info.get('is_360', False)
                if is_360_video:
                    logger.info(f"🌐 Detected 360° video: {video_format_info.get('format', 'unknown')} ({video_format_info.get('width', 0)}x{video_format_info.get('height', 0)})")
            except Exception as e:
                logger.warning(f"Could not detect 360° format: {e}")
        
        # Map legacy quality to new quality_mode
        quality_mode = map_legacy_quality(quality)
        
        # Create scan record in database for persistence
        conn = get_db_connection()
        # Add is_360 column if it doesn't exist
        try:
            conn.execute("ALTER TABLE scans ADD COLUMN is_360 INTEGER DEFAULT 0")
            conn.commit()
        except:
            pass  # Column already exists
        
        conn.execute(
            """INSERT INTO scans (id, project_id, name, video_filename, video_size, processing_quality, quality_mode, status, is_360)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (scan_id, project_id, scan_name, video.filename, len(content), quality, quality_mode, 'processing', 1 if is_360_video else 0)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"📊 Quality mode set to: {quality_mode} (from legacy '{quality}')")
        
        logger.info(f"✅ Created scan record in database: {scan_id}")
        
        # Start COLMAP reconstruction in background
        background_tasks.add_task(
            process_colmap_reconstruction,
            scan_id=scan_id,
            video_path=str(video_path),
            quality=quality
        )
        
        logger.info(f"🚀 Queued COLMAP reconstruction task for scan {scan_id}")
        
        return {
            "status": "accepted",
            "job_id": job_id,
            "scan_id": scan_id,
            "message": "Video uploaded, COLMAP reconstruction started"
        }
        
    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reconstruction/{job_id}/status")
@app.get("/api/jobs/{job_id}")
async def get_reconstruction_status(job_id: str):
    """Get detailed status of reconstruction job with progress tracking"""
    try:
        conn = get_db_connection()
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Job not found")
        
        scan_dict = dict(scan)
        status = scan_dict.get('status', 'pending')
        
        # Determine overall status
        if status == 'completed':
            overall_status = 'completed'
        elif status.startswith('failed'):
            overall_status = 'failed'
        elif status == 'processing':
            overall_status = 'processing'
        else:
            overall_status = 'pending'
        
        # Get progress and stage
        progress = scan_dict.get('progress', 0) or 0
        current_stage = scan_dict.get('current_stage', 'Initializing...')
        
        # Map status to stage names for better UX
        stage_mapping = {
            'extracting_frames': 'Extracting frames from video...',
            'extracting_features': 'Extracting SIFT features...',
            'matching_features': 'Matching features between images...',
            'reconstructing': 'Running sparse reconstruction...',
            'dense_reconstruction': 'Running dense reconstruction...',
            'exporting': 'Exporting point cloud...',
        }
        
        # Use current_stage if available, otherwise map from status
        if not current_stage and status in stage_mapping:
            current_stage = stage_mapping[status]
        
        return {
            "job_id": job_id,
            "status": overall_status,
            "message": current_stage or "Processing...",
            "progress": progress,
            "current_stage": current_stage or "Initializing...",
            "created_at": scan_dict.get('created_at', ''),
            "results": {
                "ply_file": scan_dict.get('ply_file'),
                "point_count": None  # Could be added later
            } if overall_status == 'completed' else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reconstruction/{job_id}/export")
async def export_reconstruction(job_id: str, format: str = "PLY"):
    """
    Export reconstruction to various formats
    Reference: https://colmap.github.io/tutorial.html#importing-and-exporting
    
    Supported formats: PLY, TXT, BIN, NVM
    """
    try:
        job_path = Path(f"/workspace/{job_id}")
        
        if not job_path.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Initialize processor
        processor = COLMAPProcessor(str(job_path))
        
        # Export model
        output_path = processor.export_model(output_format=format.upper())
        
        logger.info(f"Exported reconstruction {job_id} to {format}: {output_path}")
        
        return {
            "status": "success",
            "format": format,
            "output_path": output_path,
            "message": f"Successfully exported to {format} format"
        }
        
    except ValueError as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scans/{scan_id}/export/{format}")
async def export_scan_model(scan_id: str, format: str = "glb"):
    """
    Export scan point cloud to GLTF/GLB format
    
    Formats: glb (binary), gltf (ASCII)
    """
    try:
        if format.lower() not in ["glb", "gltf"]:
            raise HTTPException(status_code=400, detail="Format must be 'glb' or 'gltf'")
        
        if not HAS_GLTF_SUPPORT:
            raise HTTPException(status_code=503, detail="GLTF export not available")
        
        # Get scan info
        conn = get_db_connection()
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        conn.close()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_dict = dict(scan)
        ply_file = scan_dict.get('ply_file')
        
        if not ply_file:
            raise HTTPException(status_code=404, detail="Point cloud not available for this scan")
        
        # Resolve PLY file path
        if ply_file.startswith('/workspace/'):
            ply_path = Path(ply_file)
        else:
            # Demo scan
            ply_path = Path("demo-resources") / ply_file
        
        if not ply_path.exists():
            raise HTTPException(status_code=404, detail="PLY file not found")
        
        # Create output directory
        results_dir = Path(f"/workspace/data/results/{scan_id}")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Export to GLTF/GLB
        output_ext = "glb" if format.lower() == "glb" else "gltf"
        output_path = results_dir / f"point_cloud.{output_ext}"
        
        success = False
        if format.lower() == "glb":
            success = ply_to_glb(str(ply_path), str(output_path))
        else:
            success = ply_to_gltf_ascii(str(ply_path), str(output_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to convert PLY to GLTF")
        
        # Update database with GLB file path
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE scans SET glb_file = ? WHERE id = ?",
                (str(output_path), scan_id)
            )
            conn.commit()
        finally:
            conn.close()
        
        # Return file for download
        return FileResponse(
            str(output_path),
            media_type="model/gltf-binary" if format.lower() == "glb" else "model/gltf+json",
            filename=f"{scan_dict.get('name', 'scan')}.{output_ext}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting scan to GLTF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reconstruction/{job_id}/download/{filename}")
async def download_export(job_id: str, filename: str):
    """
    Download exported reconstruction files
    Supports: point_cloud.ply, model_text/*.txt, model.nvm, etc.
    """
    try:
        job_path = Path(f"/workspace/{job_id}")
        
        if not job_path.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Support different export locations
        possible_paths = [
            job_path / filename,  # Direct file
            job_path / "model_text" / filename,  # Text format
            job_path / "model_binary" / filename,  # Binary format
        ]
        
        file_path = None
        for path in possible_paths:
            if path.exists() and path.is_file():
                file_path = path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        logger.info(f"Downloading {file_path} for job {job_id}")
        return FileResponse(file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reconstruction/{job_id}/database/inspect")
async def inspect_database(job_id: str):
    """
    Inspect COLMAP database contents
    Reference: https://colmap.github.io/tutorial.html#database-management
    
    Returns comprehensive database statistics
    """
    try:
        job_path = Path(f"/workspace/{job_id}")
        
        if not job_path.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        
        processor = COLMAPProcessor(str(job_path))
        result = processor.inspect_database()
        
        return result
        
    except Exception as e:
        logger.error(f"Database inspection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reconstruction/{job_id}/database/clean")
async def clean_database(job_id: str):
    """
    Clean COLMAP database by removing unused data
    Reference: https://colmap.github.io/tutorial.html#database-management
    
    Removes orphaned data, images without features, etc.
    """
    try:
        job_path = Path(f"/workspace/{job_id}")
        
        if not job_path.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        
        processor = COLMAPProcessor(str(job_path))
        result = processor.clean_database()
        
        return result
        
    except Exception as e:
        logger.error(f"Database cleaning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize database and demo data on startup"""
    try:
        logger.info("🚀 Starting up COLMAP Backend...")
        
        # Initialize database
        init_database()
        
        # Clean up duplicate demo data first
        logger.info("🧹 Cleaning up duplicate demo data...")
        from database import db
        cleanup_result = db.cleanup_duplicate_demos()
        if cleanup_result.get("deleted_projects", 0) > 0:
            logger.info(f"✅ Cleaned up {cleanup_result.get('deleted_projects')} duplicate projects")
        
        # Initialize demo data using database class
        logger.info("🔄 Initializing demo data...")
        result = db.setup_demo_data()
        
        if result.get("status") == "success":
            logger.info("✅ Demo data initialized successfully")
            logger.info(f"   Project ID: {result.get('project_id')}")
            if not result.get('skipped'):
                logger.info(f"   Scan IDs: {result.get('scan_ids')}")
        else:
            logger.error(f"❌ Demo data initialization failed: {result.get('error')}")
        
        # VERIFY DEMO DATA EXISTS
        conn = get_db_connection()
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        scans_count = conn.execute("SELECT COUNT(*) as count FROM scans").fetchone()["count"]
        conn.close()
        
        logger.info(f"🎯 FINAL VERIFICATION: {projects_count} projects, {scans_count} scans")
        logger.info("🎯 COLMAP Backend ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
