"""
Tests for JARVIS Voice Module.
"""
import sys
import os
import time


import pytest
from voice.wake_word import WakeWordDetector, get_detector, detect_wake_word
from voice.tts import TTSEngine


class TestWakeWordDetector:
    def setup_method(self):
        self.detector = WakeWordDetector()

    def test_detect_hey_jarvis(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("Hey JARVIS") == True

    def test_detect_oye_jarvis(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("Oye JARVIS") == True

    def test_detect_hey_jarv(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("Hey Jarv") == True

    def test_detect_jarvis_standalone(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("JARVIS help me") == True

    def test_no_false_positive(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("hello world") == False
        assert self.detector.detect("how are you") == False
        assert self.detector.detect("nothing here") == False

    def test_cooldown(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("Hey JARVIS") == True
        assert self.detector.detect("Hey JARVIS") == False  # Within cooldown

    def test_case_insensitive(self):
        self.detector._last_trigger = 0
        assert self.detector.detect("HEY JARVIS") == True
        self.detector._last_trigger = 0
        assert self.detector.detect("hey jarvis") == True

    def test_callback(self):
        self.detector._last_trigger = 0
        callback_called = []
        def callback():
            callback_called.append(True)
        self.detector.on_wake(callback)
        self.detector.detect("Hey JARVIS")
        assert len(callback_called) == 1

    def test_singleton(self):
        d1 = get_detector()
        d2 = get_detector()
        assert d1 is d2

    def test_convenience_function(self):
        from voice.wake_word import get_detector
        detector = get_detector()
        detector._last_trigger = 0
        assert detect_wake_word("Hey JARVIS") == True


class TestTTSEngine:
    def setup_method(self):
        self.engine = TTSEngine()

    def test_initial_state(self):
        assert self.engine.is_playing == False
        assert self.engine.queue_size == 0

    def test_queue(self):
        self.engine.say("Hola mundo")
        assert self.engine.queue_size == 1

    def test_priority(self):
        self.engine.say("Normal")
        self.engine.say("Urgente", priority=True)
        assert self.engine.queue_size == 2

    def test_interrupt(self):
        self.engine.say("Mensaje 1")
        self.engine.say("Mensaje 2")
        assert self.engine.queue_size == 2
        self.engine.interrupt()
        assert self.engine.queue_size == 0

    def test_start_stop(self):
        self.engine.start()
        assert self.engine._running == True
        self.engine.stop()
        assert self.engine._running == False

    def test_callbacks(self):
        events = []
        self.engine.on_start(lambda: events.append("start"))
        self.engine.on_end(lambda: events.append("end"))

    def test_get_engine(self):
        from voice.tts import get_engine
        e1 = get_engine()
        e2 = get_engine()
        assert e1 is e2
