from pytest_bdd import scenario

from tests.steps.generate_video_steps import *


@scenario("generate-video.feature", "Generate basic lipsync video")
def test_basic_lipsync():
    pass


@scenario("generate-video.feature", "Generation fails with small image")
def test_small_image_rejected():
    pass
