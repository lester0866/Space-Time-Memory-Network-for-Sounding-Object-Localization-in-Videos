import os
import multiprocessing
from moviepy.editor import VideoFileClip

WRITE_DIR = None
VIDEOS = []


# EXCLUSION_LIST = []
def single_video_to_audio(index):
    video_name = VIDEOS[index]
    audio_name = video_name.split("/")[-1][:-4] + '.wav'
    if os.path.exists(audio_name):
        return

    video = VideoFileClip(video_name)
    audio = video.audio
    audio.write_audiofile(os.path.join(WRITE_DIR, audio_name), fps=16000)


def video_range_to_audios(start_index, end_index):
    # need -1 so it starts from 0
    for index in range(start_index - 1, end_index):
        # if index in EXCLUSION_LIST:
        #     continue
        single_video_to_audio(index)

    return (start_index, end_index)


def multiprocess_videos_to_audios(node_start, node_end):
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_processes)

    num_videos = node_end + 1 - node_start

    if num_processes > num_videos:
        num_processes = num_videos

    videos_per_process = num_videos / num_processes

    print("[Nodes] {} - {}".format(node_start, node_end))
    print("Number of processes: " + str(num_processes))
    print("Number of videos: " + str(num_videos))

    tasks = []
    for num_process in range(1, num_processes + 1):
        start_index = (num_process - 1) * videos_per_process + 1
        end_index = num_process * videos_per_process

        start_index = int(start_index)
        end_index = int(end_index)
        if node_start is not None and node_end is not None:
            start_index += node_start
            end_index += node_start

        tasks.append((start_index, end_index))
        if start_index == end_index:
            print("Task #" + str(num_process) + ": Process slide " + str(start_index))
        else:
            print(
                "Task #"
                + str(num_process)
                + ": Process slides "
                + str(start_index)
                + " to "
                + str(end_index)
            )

    # start tasks
    results = []
    for t in tasks:
        results.append(pool.apply_async(video_range_to_audios, t))

    for result in results:
        (start_ind, end_ind) = result.get()
        if start_ind == end_ind:
            print("Done converting slide %d" % start_ind)
        else:
            print("Done converting slides %d through %d" % (start_ind, end_ind))
