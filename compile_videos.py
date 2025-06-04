import os
import json
from pathlib import Path
from typing import List
import ffmpeg
from rich.progress import track
from utils import settings
from utils.console import print_step, print_substep

def get_video_duration(filepath: str) -> float:
    """Get duration of video file in seconds"""
    probe = ffmpeg.probe(filepath)
    return float(probe['format']['duration'])

def get_available_videos(subreddit: str) -> List[str]:
    """Get list of available video files in results folder"""
    results_dir = Path(f"results/{subreddit}")
    if not results_dir.exists():
        return []
    
    return [str(f) for f in results_dir.glob("*.mp4")]

def create_compilation(videos: List[str], target_duration: int, transition: float, output_path: str):
    """Create compilation video from list of input videos"""
    print_step("Creating compilation video...")
    
    # Calculate total duration of input videos
    total_duration = sum(get_video_duration(v) for v in videos)
    
    if total_duration < target_duration:
        print_substep(f"Warning: Total duration ({total_duration}s) is less than target ({target_duration}s)")
    
    # Prepare video inputs
    video_inputs = []
    for video in track(videos, "Processing videos..."):
        input_video = ffmpeg.input(video)
        # Add transition effect between clips
        if transition > 0 and video != videos[-1]:
            input_video = input_video.filter('fade', type='out', duration=transition)
        video_inputs.append(input_video)
    
    # Concatenate videos
    joined = ffmpeg.concat(*video_inputs, v=1, a=1)
    
    # Write output file
    print_substep("Rendering final compilation...")
    output = joined.output(output_path, acodec='aac', vcodec='h264')
    output.overwrite_output().run(capture_stdout=True, capture_stderr=True)
    
    print_substep(f"Compilation saved to: {output_path}", style="bold green")

def main():
    """Main compilation function"""
    if not settings.config["compilation"]["enabled"]:
        print_step("Compilation feature is disabled in config")
        return
        
    # Get compilation settings
    target_duration = settings.config["compilation"]["target_duration"] 
    transition = settings.config["compilation"]["transition"]
    max_clips = settings.config["compilation"]["max_clips"]
    output_folder = settings.config["compilation"]["output_folder"]
    
    # Get subreddit
    subreddit = settings.config["reddit"]["thread"]["subreddit"]
    
    # Get available videos
    videos = get_available_videos(subreddit)
    if not videos:
        print_step(f"No videos found in results/{subreddit}")
        return
        
    # Sort videos by creation date
    videos.sort(key=os.path.getctime, reverse=True)
    
    # Limit number of clips
    if len(videos) > max_clips:
        videos = videos[:max_clips]
        
    # Create output folder
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename
    output_path = output_dir / f"compilation_{len(videos)}clips_{target_duration}s.mp4"
    
    # Create compilation
    create_compilation(videos, target_duration, transition, str(output_path))

if __name__ == "__main__":
    main()