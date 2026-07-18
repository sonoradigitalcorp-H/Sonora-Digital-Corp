package tts

import (
	"bytes"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sync"

	meow "github.com/purpshell/meowcaller"
)

var errClosed = errors.New("source closed")

type EdgeSource struct {
	mu       sync.Mutex
	frames   [][]float32
	pos      int
	closed   bool
}

func NewEdgeSource(text, tmpDir string) (*EdgeSource, error) {
	path := filepath.Join(tmpDir, fmt.Sprintf("tts-%d.wav", os.Getpid()))
	script := fmt.Sprintf(`
import asyncio, sys
from edge_tts import Communicate
async def g():
    c = Communicate(%q, "es-MX-DaliaNeural")
    await c.save(%q)
asyncio.run(g())
print("ok")
`, text, path)
	cmd := exec.Command("python3", "-c", script)
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = io.Discard
	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("edge-tts: %w", err)
	}

	frames, err := decodeWAV(path)
	os.Remove(path)
	if err != nil {
		return nil, fmt.Errorf("decode tts: %w", err)
	}

	return &EdgeSource{frames: frames}, nil
}

func (e *EdgeSource) ReadFrame() ([]float32, error) {
	e.mu.Lock()
	defer e.mu.Unlock()
	if e.closed {
		return nil, errClosed
	}
	if e.pos >= len(e.frames) {
		return nil, io.EOF
	}
	f := e.frames[e.pos]
	e.pos++
	return f, nil
}

func (e *EdgeSource) Close() error {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.closed = true
	return nil
}

func decodeWAV(path string) ([][]float32, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	if len(data) < 44 || string(data[0:4]) != "RIFF" {
		return nil, fmt.Errorf("not a WAV file")
	}
	numChannels := int(binary.LittleEndian.Uint16(data[22:24]))
	sampleRate := int(binary.LittleEndian.Uint16(data[24:28]))
	bitsPerSample := int(binary.LittleEndian.Uint16(data[34:36]))
	pcm := data[44:]

	if sampleRate != 16000 {
		return nil, fmt.Errorf("expected 16kHz, got %d", sampleRate)
	}
	if bitsPerSample != 16 {
		return nil, fmt.Errorf("expected 16-bit, got %d", bitsPerSample)
	}

	var frames [][]float32
	var frame []float32
	for i := 0; i+1 < len(pcm); i += 2 {
		s := int16(binary.LittleEndian.Uint16(pcm[i:]))
		f := float32(s) / 32767.0
		if numChannels > 1 && i%4 == 0 {
			continue
		}
		frame = append(frame, f)
		if len(frame) == meow.FrameSamples {
			frames = append(frames, frame)
			frame = nil
		}
	}
	if frame != nil {
		for len(frame) < meow.FrameSamples {
			frame = append(frame, 0)
		}
		frames = append(frames, frame)
	}
	return frames, nil
}
