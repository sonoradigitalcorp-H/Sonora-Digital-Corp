package stt

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sync"

)

type WhisperSink struct {
	mu       sync.Mutex
	buf      bytes.Buffer
	tmpDir   string
	onText   func(string)
	closed   bool
	sampleCount int
}

func NewWhisperSink(tmpDir string, onText func(string)) *WhisperSink {
	return &WhisperSink{tmpDir: tmpDir, onText: onText}
}

func (w *WhisperSink) WriteFrame(frame []float32) error {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.closed {
		return nil
	}
	for _, s := range frame {
		i := int16(s * 32767)
		if i > 32767 {
			i = 32767
		} else if i < -32768 {
			i = -32768
		}
		_ = binary.Write(&w.buf, binary.LittleEndian, i)
	}
	w.sampleCount += len(frame)
	return nil
}

func (w *WhisperSink) Close() error {
	w.mu.Lock()
	if w.closed {
		w.mu.Unlock()
		return nil
	}
	w.closed = true
	data := w.buf.Bytes()
	w.mu.Unlock()

	if len(data) < 32000 {
		return nil
	}

	path := filepath.Join(w.tmpDir, fmt.Sprintf("call-%d.wav", os.Getpid()))
	if err := writeWAV(path, data, 16000); err != nil {
		return fmt.Errorf("write wav: %w", err)
	}
	defer os.Remove(path)

	text, err := transcribe(path)
	if err != nil {
		return fmt.Errorf("transcribe: %w", err)
	}
	if text != "" && w.onText != nil {
		w.onText(text)
	}
	return nil
}

func transcribe(path string) (string, error) {
	script := fmt.Sprintf(`
import sys; sys.path.insert(0, "/home/mystic/sonora-digital-corp/apps")
from voice.stt import transcribe as t
r = t(%q)
print(r)
`, path)
	cmd := exec.Command("python3", "-c", script)
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = io.Discard
	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("whisper: %w", err)
	}
	return string(bytes.TrimSpace(out.Bytes())), nil
}

func writeWAV(path string, pcm []byte, sampleRate int) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	dataLen := len(pcm)
	header := make([]byte, 44)
	copy(header[0:4], []byte("RIFF"))
	binary.LittleEndian.PutUint32(header[4:8], uint32(36+dataLen))
	copy(header[8:12], []byte("WAVE"))
	copy(header[12:16], []byte("fmt "))
	binary.LittleEndian.PutUint32(header[16:20], 16)
	binary.LittleEndian.PutUint16(header[20:22], 1)
	binary.LittleEndian.PutUint16(header[22:24], 1)
	binary.LittleEndian.PutUint32(header[24:28], uint32(sampleRate))
	binary.LittleEndian.PutUint32(header[28:32], uint32(sampleRate*2))
	binary.LittleEndian.PutUint16(header[32:34], 2)
	binary.LittleEndian.PutUint16(header[34:36], 16)
	copy(header[36:40], []byte("data"))
	binary.LittleEndian.PutUint32(header[40:44], uint32(dataLen))

	if _, err := f.Write(header); err != nil {
		return err
	}
	_, err = f.Write(pcm)
	return err
}
