#!/bin/bash
################################################################################
# Cleanup Demo Data - Remove duplicates and ensure single demo project
# Run on RunPod to clean up database
################################################################################

set -e

echo "🧹 Cleaning up demo data..."

cd /workspace/colmap-demo
source venv/bin/activate

# Set environment variables
export DATABASE_PATH=/workspace/colmap-demo/data/database.db

python3 << 'PYEOF'
from database import Database
import sqlite3

db = Database()
conn = db.get_connection()

try:
    # Get demo user
    demo_user = conn.execute("SELECT id FROM users WHERE email = 'demo@colmap.app'").fetchone()
    
    if demo_user:
        demo_user_id = demo_user['id']
        
        # Get all demo projects
        demo_projects = conn.execute(
            "SELECT id, name, created_at FROM projects WHERE user_id = ? ORDER BY created_at DESC",
            (demo_user_id,)
        ).fetchall()
        
        print(f"Found {len(demo_projects)} demo projects:")
        for proj in demo_projects:
            scan_count = conn.execute(
                "SELECT COUNT(*) as count FROM scans WHERE project_id = ?",
                (proj['id'],)
            ).fetchone()['count']
            print(f"  - {proj['name']}: {scan_count} scans (created: {proj['created_at']})")
        
        if len(demo_projects) > 1:
            print(f"\n🗑️  Deleting {len(demo_projects) - 1} extra projects...")
            
            # Keep only the first (most recent) project
            keep_project_id = demo_projects[0]['id']
            
            for proj in demo_projects[1:]:
                proj_id = proj['id']
                # Delete scans and their technical details
                scan_ids = [row['id'] for row in conn.execute(
                    "SELECT id FROM scans WHERE project_id = ?", (proj_id,)
                ).fetchall()]
                
                for scan_id in scan_ids:
                    conn.execute("DELETE FROM scan_technical_details WHERE scan_id = ?", (scan_id,))
                    conn.execute("DELETE FROM processing_jobs WHERE scan_id = ?", (scan_id,))
                
                conn.execute("DELETE FROM scans WHERE project_id = ?", (proj_id,))
                conn.execute("DELETE FROM projects WHERE id = ?", (proj_id,))
                print(f"  ✅ Deleted: {proj['name']}")
            
            # Rename the kept project to the correct name
            conn.execute(
                "UPDATE projects SET name = ? WHERE id = ?",
                ("Reconstruction Test Project 1", keep_project_id)
            )
            print(f"\n✅ Renamed remaining project to: Reconstruction Test Project 1")
            
            # Ensure it has exactly 2 demo scans
            scans = conn.execute(
                "SELECT id, name FROM scans WHERE project_id = ?",
                (keep_project_id,)
            ).fetchall()
            
            print(f"✅ Final project has {len(scans)} scans:")
            for scan in scans:
                print(f"  - {scan['name']}")
            
            conn.commit()
            print("\n✅ Cleanup complete!")
        else:
            print("\n✅ Only one project found, no cleanup needed")
            # Still rename it to ensure correct name
            conn.execute(
                "UPDATE projects SET name = ? WHERE id = ?",
                ("Reconstruction Test Project 1", demo_projects[0]['id'])
            )
            conn.commit()
            print("✅ Ensured correct project name")
    else:
        print("⚠️  No demo user found")
        
finally:
    conn.close()

print("\n" + "="*60)
print("Database cleanup complete!")
print("="*60)
PYEOF

echo ""
echo "✅ Demo data cleaned up successfully!"

