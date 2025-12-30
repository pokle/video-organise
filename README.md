# Video Organise

A simple tool to organise your video files into folders based on their metadata.

## Organisation Structure

The tool organises video files into a directory structure based on the following hierarchy:

```
/YYYY-MM-DD[-project-name]/raw/
```

- `YYYY-MM-DD`: The date the video was created.
- `project-name`: An optional project name that can be included in the folder name. Manually edit this part after the date if desired.
- `raw`: A subfolder where the original video files are stored.

## Features
- Automatically creates folders based on the video's creation date.
- Allows for manual addition of project names to the folder structure.
- Moves video files into the appropriate folders.

## Usage

```
video-organise [options] <source-directory> <destination-directory>
```

- source-directory: The directory containing the video files to be organised. This is usually an SD card or external drive.
- destination-directory: The directory where the organised folders will be created. This is usually the archive location.

