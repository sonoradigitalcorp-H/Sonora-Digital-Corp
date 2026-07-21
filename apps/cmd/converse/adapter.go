package main

import (
	meow "github.com/purpshell/meowcaller"
	"github.com/sonoradigitalcorp/call-engine/orchestrator"
)

type callAdapter struct {
	inner *meow.Call
}

func (a *callAdapter) OnReady(fn func()) {
	a.inner.OnReady(fn)
}

func (a *callAdapter) OnEnd(fn func(string)) {
	a.inner.OnEnd(fn)
}

func (a *callAdapter) Subscribe(p interface{ Play(source orchestrator.AudioSource); Stop(); OnFinish(fn func()) }) {
	if pl, ok := p.(*meow.Player); ok {
		a.inner.Subscribe(pl)
	}
}

func (a *callAdapter) Receive(sink orchestrator.AudioSink) {
	a.inner.Receive(sink)
}

func (a *callAdapter) Hangup() error {
	return a.inner.Hangup()
}
