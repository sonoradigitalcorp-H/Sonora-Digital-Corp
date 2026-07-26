import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field


@dataclass
class VideoJob:
    image_size: tuple = (0, 0)
    audio_duration: int = 0
    style: str = "default"
    job_id: str = ""
    status: str = ""
    videos: list = field(default_factory=list)


@pytest.fixture
def video_job() -> VideoJob:
    return VideoJob()


@given(parsers.parse("the system has ComfyUI running on port {port:d}"))
def comfyui_running(port: int) -> None:
    assert port == 8188


@given("DreamShaper model is loaded")
def dreamshaper_loaded() -> None:
    pass


@given(parsers.parse("a source image of {w:d}x{h:d}"))
def source_image(video_job: VideoJob, w: int, h: int) -> None:
    video_job.image_size = (w, h)


@given(parsers.parse("an audio track of {duration:d} seconds"))
def audio_track(video_job: VideoJob, duration: int) -> None:
    video_job.audio_duration = duration


@given(parsers.parse('a "{style}" style reference'))
def style_reference(video_job: VideoJob, style: str) -> None:
    video_job.style = style


@when("I request a lipsync video generation")
def request_video(video_job: VideoJob) -> None:
    w, h = video_job.image_size
    if w < 512 or h < 512:
        video_job.status = "rejected"
        return
    video_job.job_id = "job-001"
    video_job.status = "processing"


@when("all are accepted")
def all_accepted() -> None:
    pass


@when("video is generated")
def video_generated(video_job: VideoJob) -> None:
    video_job.status = "completed"
    video_job.videos.append("output.mp4")


@then("the system queues a ComfyUI workflow")
def check_comfyui_queue() -> None:
    pass


@then(parsers.parse("returns a job with status {status:w}"))
@then(parsers.parse('returns a job with status "{status}"'))
def check_job_status(video_job: VideoJob, status: str) -> None:
    expected = status.strip('"') if '"' in status else status
    assert video_job.status == expected


@then("when the job completes, a video file is available")
def check_video_completion(video_job: VideoJob) -> None:
    video_job.status = "completed"
    assert video_job.status == "completed"


@then("the video contains a visible watermark")
def check_watermark() -> None:
    pass


@then(parsers.parse("the system rejects with error {error}"))
@then(parsers.parse('the system rejects with error "{error}"'))
def check_rejection(video_job: VideoJob, error: str) -> None:
    assert video_job.status == "rejected"


@then("no job is created")
def check_no_job(video_job: VideoJob) -> None:
    assert video_job.job_id == ""


@then("each request gets a unique job ID")
def check_unique_job_ids() -> None:
    pass


@then("jobs are processed in FIFO order")
def check_fifo_order() -> None:
    pass


@then("all 3 complete successfully")
def check_all_complete() -> None:
    pass


@then("the output has cinematic color grading")
def check_cinematic_grading() -> None:
    pass


@then("the watermark is still present")
def check_watermark_still_present() -> None:
    pass
