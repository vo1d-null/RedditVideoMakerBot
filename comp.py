import os
import moviepy.editor as mp
import sys

def create_video_compilation():
    """
    Creates a video compilation from videos in a chosen subfolder within 'results',
    with optional intro and outro videos.
    """
    print("--- Video Compilation Script ---")

    # Define the base results directory
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Error: The '{results_dir}' directory was not found.")
        print("Please ensure your project structure is correct.")
        return

    # List subfolders in the results directory
    subfolders = [f.name for f in os.scandir(results_dir) if f.is_dir()]

    if not subfolders:
        print(f"No subfolders found in '{results_dir}'. Please add videos to a subfolder.")
        return

    print(f"\nAvailable subfolders in '{results_dir}':")
    for i, folder in enumerate(subfolders):
        print(f"{i + 1}. {folder}")

    # Get user choice for the source folder
    while True:
        try:
            choice = int(input(f"Enter the number of the subfolder to compile videos from (1-{len(subfolders)}): "))
            if 1 <= choice <= len(subfolders):
                selected_folder = subfolders[choice - 1]
                source_path = os.path.join(results_dir, selected_folder)
                break
            else:
                print("Invalid choice. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"Selected folder: {source_path}")

    # Get all video files from the selected folder
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    video_files = [os.path.join(source_path, f) for f in os.listdir(source_path)
                   if f.lower().endswith(video_extensions) and os.path.isfile(os.path.join(source_path, f))]

    if not video_files:
        print(f"No video files found in '{source_path}'. Exiting.")
        return

    print(f"\nFound {len(video_files)} video(s) in '{selected_folder}'.")
    for video in video_files:
        print(f"- {os.path.basename(video)}")

    # Optional Intro Video
    intro_clip = None
    add_intro = input("\nDo you want to add an intro video? (y/n): ").lower()
    if add_intro == 'y':
        while True:
            intro_path = input("Enter the full path to the intro video file: ").strip()
            if os.path.exists(intro_path) and intro_path.lower().endswith(video_extensions):
                try:
                    intro_clip = mp.VideoFileClip(intro_path)
                    print(f"Intro video '{os.path.basename(intro_path)}' loaded.")
                    break
                except Exception as e:
                    print(f"Error loading intro video: {e}. Please check the file.")
            else:
                print("Invalid path or not a supported video file. Please try again.")

    # Load main video clips
    print("\nLoading main video clips...")
    main_clips = []
    for video_file in video_files:
        try:
            clip = mp.VideoFileClip(video_file)
            main_clips.append(clip)
            print(f"Loaded: {os.path.basename(video_file)}")
        except Exception as e:
            print(f"Warning: Could not load '{os.path.basename(video_file)}'. Skipping. Error: {e}")

    if not main_clips:
        print("No main video clips could be loaded. Exiting.")
        if intro_clip:
            intro_clip.close()
        return

    # Optional Outro Video
    outro_clip = None
    add_outro = input("\nDo you want to add an outro video? (y/n): ").lower()
    if add_outro == 'y':
        while True:
            outro_path = input("Enter the full path to the outro video file: ").strip()
            if os.path.exists(outro_path) and outro_path.lower().endswith(video_extensions):
                try:
                    outro_clip = mp.VideoFileClip(outro_path)
                    print(f"Outro video '{os.path.basename(outro_path)}' loaded.")
                    break
                except Exception as e:
                    print(f"Error loading outro video: {e}. Please check the file.")
            else:
                print("Invalid path or not a supported video file. Please try again.")

    # Concatenate clips
    final_clips = []
    if intro_clip:
        final_clips.append(intro_clip)
    final_clips.extend(main_clips)
    if outro_clip:
        final_clips.append(outro_clip)

    if not final_clips:
        print("No clips to compile. Exiting.")
        return

    print("\nConcatenating videos...")
    final_video = None
    try:
        final_video = mp.concatenate_videoclips(final_clips)
    except Exception as e:
        print(f"Error during video concatenation: {e}")
        print("This might happen if video properties (e.g., resolution, FPS) are inconsistent.")
        print("Attempting to resize all clips to the first main clip's resolution and FPS.")

        # Try to standardize resolution and FPS
        if main_clips:
            first_clip_size = main_clips[0].size
            first_clip_fps = main_clips[0].fps
            print(f"Standardizing to resolution: {first_clip_size}, FPS: {first_clip_fps}")

            resized_clips = []
            for clip in final_clips:
                try:
                    # Resize and set FPS, if different
                    if clip.size != first_clip_size:
                        clip = clip.resize(newsize=first_clip_size)
                    if clip.fps != first_clip_fps:
                        clip = clip.set_fps(first_clip_fps)
                    resized_clips.append(clip)
                except Exception as resize_e:
                    print(f"Warning: Could not resize/standardize clip. Skipping. Error: {resize_e}")
            
            if resized_clips:
                try:
                    final_video = mp.concatenate_videoclips(resized_clips)
                except Exception as final_e:
                    print(f"Critical Error: Still unable to concatenate after resizing. {final_e}")
                    print("Please ensure all your source videos are compatible or try converting them first.")
                    # Close all clips before exiting
                    for clip in final_clips:
                        clip.close()
                    if intro_clip: intro_clip.close()
                    if outro_clip: outro_clip.close()
                    return
            else:
                print("No clips could be resized successfully. Exiting.")
                # Close all clips before exiting
                for clip in final_clips:
                    clip.close()
                if intro_clip: intro_clip.close()
                if outro_clip: outro_clip.close()
                return
        else:
            print("No main clips to use as reference for standardization. Exiting.")
            # Close all clips before exiting
            if intro_clip: intro_clip.close()
            if outro_clip: outro_clip.close()
            for clip in final_clips:
                clip.close()
            return


    # Define output path
    output_filename = f"compilation_{selected_folder}_{os.path.basename(os.getcwd())}.mp4"
    output_path = os.path.join(os.getcwd(), output_filename) # Save in the current working directory

    print(f"\nWriting final video to: {output_path}")
    try:
        # Write the final video file
        # Using preset='medium' for a balance between speed and quality.
        # You can adjust this (e.g., 'fast', 'slow', 'ultrafast')
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="medium")
        print("\nVideo compilation created successfully!")
    except Exception as e:
        print(f"Error writing the final video file: {e}")
        print("Ensure you have 'ffmpeg' installed and accessible in your system's PATH.")
        print("You can download ffmpeg from https://ffmpeg.org/download.html")
        print("Also, check disk space and file permissions.")
    finally:
        # Always close clips to free up resources
        if intro_clip: intro_clip.close()
        if outro_clip: outro_clip.close()
        for clip in main_clips:
            clip.close()
        if 'final_video' in locals() and final_video is not None:
            final_video.close()


if __name__ == "__main__":
    # Check for moviepy installation
    try:
        import moviepy.editor as mp
    except ImportError:
        print("moviepy is not installed.")
        print("Please install it using: pip install moviepy")
        print("You also need ffmpeg. Download it from https://ffmpeg.org/download.html")
        sys.exit(1)

    create_video_compilation()
