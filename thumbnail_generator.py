#!/usr/bin/env python3
"""
Thumbnail Generator for 3D Point Clouds
Renders a preview image from PLY files
"""

import numpy as np
from pathlib import Path
import logging
from typing import Optional
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False

logger = logging.getLogger(__name__)


def read_ply_ascii(ply_path: Path) -> Optional[np.ndarray]:
    """Read ASCII PLY file and extract XYZ coordinates"""
    try:
        points = []
        with open(ply_path, 'r') as f:
            # Skip header
            in_header = True
            vertex_count = 0
            
            for line in f:
                if in_header:
                    if line.startswith('element vertex'):
                        vertex_count = int(line.split()[2])
                    elif line.startswith('end_header'):
                        in_header = False
                    continue
                
                # Parse vertex data
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                        points.append([x, y, z])
                    except ValueError:
                        continue
                        
                if len(points) >= vertex_count:
                    break
        
        return np.array(points) if points else None
    except Exception as e:
        logger.error(f"Error reading PLY: {e}")
        return None


def generate_thumbnail_matplotlib(ply_path: Path, output_path: Path, size: tuple = (400, 300)) -> bool:
    """Generate thumbnail using matplotlib (better for point clouds)"""
    if not MPL_AVAILABLE:
        logger.warning("Matplotlib not available for thumbnail generation")
        return False
    
    try:
        # Read point cloud
        points = read_ply_ascii(ply_path)
        if points is None or len(points) == 0:
            logger.warning(f"No points found in {ply_path}")
            return False
        
        # Sample points if too many (for performance)
        max_points = 10000
        if len(points) > max_points:
            indices = np.random.choice(len(points), max_points, replace=False)
            points = points[indices]
        
        # Create 3D plot
        fig = plt.figure(figsize=(size[0]/100, size[1]/100), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot points
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                  c=points[:, 2], cmap='viridis', s=1, alpha=0.6)
        
        # Remove axes for cleaner look
        ax.set_axis_off()
        
        # Set view angle
        ax.view_init(elev=20, azim=45)
        
        # Tight layout
        plt.tight_layout(pad=0)
        
        # Save
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close()
        
        logger.info(f"✅ Generated thumbnail: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating matplotlib thumbnail: {e}")
        return False


def generate_thumbnail_simple(ply_path: Path, output_path: Path, size: tuple = (400, 300)) -> bool:
    """Generate simple thumbnail with PIL (fallback)"""
    if not PIL_AVAILABLE:
        logger.warning("PIL not available for thumbnail generation")
        return False
    
    try:
        # Create a simple placeholder image
        img = Image.new('RGB', size, color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"3D Model\n{ply_path.stem}"
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill=(150, 150, 160))
        
        # Save
        img.save(output_path, 'JPEG', quality=85)
        
        logger.info(f"✅ Generated simple thumbnail: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating simple thumbnail: {e}")
        return False


def generate_thumbnail(ply_path: Path, output_path: Path = None, size: tuple = (400, 300)) -> Optional[Path]:
    """
    Generate thumbnail from PLY file
    
    Args:
        ply_path: Path to PLY file
        output_path: Output path for thumbnail (defaults to same folder as PLY)
        size: Thumbnail size (width, height)
    
    Returns:
        Path to generated thumbnail or None if failed
    """
    ply_path = Path(ply_path)
    
    if not ply_path.exists():
        logger.error(f"PLY file not found: {ply_path}")
        return None
    
    # Default output path
    if output_path is None:
        output_path = ply_path.parent / "thumbnail.jpg"
    else:
        output_path = Path(output_path)
    
    # Try matplotlib first (better quality)
    if generate_thumbnail_matplotlib(ply_path, output_path, size):
        return output_path
    
    # Fallback to simple PIL thumbnail
    if generate_thumbnail_simple(ply_path, output_path, size):
        return output_path
    
    logger.error("Failed to generate thumbnail with any method")
    return None


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        ply_file = Path(sys.argv[1])
        thumbnail = generate_thumbnail(ply_file)
        if thumbnail:
            print(f"✅ Thumbnail generated: {thumbnail}")
        else:
            print("❌ Failed to generate thumbnail")
    else:
        print("Usage: python thumbnail_generator.py <ply_file>")

