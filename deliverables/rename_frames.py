#!/usr/bin/env python3
"""Rename video frame images to simpler names."""
import os
from pathlib import Path

def rename_frames():
    """Rename all PNG files in video-frames directory to frame-01.png, frame-02.png, etc."""
    frames_dir = Path(__file__).parent / "video-frames"
    
    if not frames_dir.exists():
        print(f"Directory not found: {frames_dir}")
        return
    
    # Get all PNG files and sort by name (chronological order based on timestamp)
    image_files = sorted([f for f in frames_dir.iterdir() if f.suffix == '.png'])
    
    print(f"Found {len(image_files)} images to rename")
    
    # Rename files
    for i, img_path in enumerate(image_files, 1):
        new_name = f"frame-{i:02d}.png"
        new_path = frames_dir / new_name
        
        try:
            img_path.rename(new_path)
            print(f"Renamed: {img_path.name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {img_path.name}: {e}")
    
    print(f"\nRenaming complete! {len(image_files)} files renamed.")

if __name__ == "__main__":
    rename_frames()

