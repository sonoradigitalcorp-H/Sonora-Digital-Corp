package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"

	meow "github.com/purpshell/meowcaller"
	"github.com/rs/zerolog"
	"github.com/sonoradigitalcorp/call-engine/memory"
	"github.com/sonoradigitalcorp/call-engine/orchestrator"
	"github.com/sonoradigitalcorp/call-engine/scoring"
	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/store"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
	_ "modernc.org/sqlite"
)

type config struct {
	storePath     string
	target        string
	leadName      string
	leadID        string
	objective     string
	leadContext   string
	tone          string
	openRouterKey string
	model         string
	neo4jURL      string
	neo4jUser     string
	neo4jPass     string
}

func main() {
	cfg := parseFlags()
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	if err := run(ctx, cfg, os.Stderr); err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}

func parseFlags() config {
	var cfg config
	home, _ := os.UserHomeDir()
	defaultStore := filepath.Join(home, ".config", "meowcaller", "whatsapp.db")

	flag.StringVar(&cfg.storePath, "store", defaultStore, "MeowCaller store path")
	flag.StringVar(&cfg.target, "to", "", "target JID (e.g. 5216622681111@s.whatsapp.net)")
	flag.StringVar(&cfg.leadName, "name", "", "lead name")
	flag.StringVar(&cfg.leadID, "id", "", "lead ID")
	flag.StringVar(&cfg.objective, "objective", "ofrecer servicios", "call objective")
	flag.StringVar(&cfg.leadContext, "context", "", "lead context")
	flag.StringVar(&cfg.tone, "tone", "profesional, cálido", "tone")
	flag.StringVar(&cfg.openRouterKey, "key", os.Getenv("OPENROUTER_API_KEY"), "OpenRouter API key")
	flag.StringVar(&cfg.model, "model", "openai/gpt-4o-mini", "LLM model")
	flag.StringVar(&cfg.neo4jURL, "neo4j-url", os.Getenv("NEO4J_URL"), "Neo4j URL")
	flag.StringVar(&cfg.neo4jUser, "neo4j-user", os.Getenv("NEO4J_USER"), "Neo4j user")
	flag.StringVar(&cfg.neo4jPass, "neo4j-pass", os.Getenv("NEO4J_PASS"), "Neo4j password")
	flag.Parse()

	if cfg.target == "" || cfg.leadName == "" || cfg.openRouterKey == "" {
		flag.Usage()
		os.Exit(2)
	}
	return cfg
}

func run(ctx context.Context, cfg config, stderr io.Writer) error {
	log := zerolog.New(stderr).Level(zerolog.InfoLevel).With().Timestamp().Logger()
	ctx = log.WithContext(ctx)

	tmpDir, err := os.MkdirTemp("", "callengine-*")
	if err != nil {
		return fmt.Errorf("tmp dir: %w", err)
	}
	defer os.RemoveAll(tmpDir)

	container, err := sqlstore.New(ctx, "sqlite", sqliteDSN(cfg.storePath), waLog.Zerolog(log.Level(zerolog.WarnLevel)))
	if err != nil {
		return fmt.Errorf("open store: %w", err)
	}
	defer container.Close()

	device, err := container.GetFirstDevice(ctx)
	if err != nil {
		return fmt.Errorf("get device: %w", err)
	}
	if device.ID == nil {
		return errors.New("not paired; run 'meowcaller pair' first")
	}

	store.DeviceProps.Os = proto.String("Mac OS")

	waClient := whatsmeow.NewClient(device, nil)
	if err := waClient.Connect(); err != nil {
		return fmt.Errorf("connect: %w", err)
	}
	defer waClient.Disconnect()

	waClient.SendPresence(ctx, types.PresenceAvailable)
	log.Info().Msg("WhatsApp connected")

	client := meow.NewClient(waClient, meow.WithLogger(log))
	rawCall, err := client.Call(ctx, cfg.target)
	if err != nil {
		return fmt.Errorf("place call: %w", err)
	}

	log.Info().Str("target", cfg.target).Msg("Call placed, waiting for answer...")

	engine := orchestrator.New(orchestrator.Config{
		OpenRouterKey: cfg.openRouterKey,
		Model:         cfg.model,
		LeadName:      cfg.leadName,
		LeadID:        cfg.leadID,
		Objective:     cfg.objective,
		LeadContext:   cfg.leadContext,
		Tone:          cfg.tone,
		TmpDir:        tmpDir,
	})

	startTime := time.Now()
	var callEnded bool

	call := &callAdapter{inner: rawCall}
	player := meow.NewPlayer()

	call.OnReady(func() {
		log.Info().Msg("Call answered! Starting conversation...")
		go engine.Run(ctx, call, player)
	})

	call.OnEnd(func(reason string) {
		log.Info().Str("reason", reason).Msg("Call ended")
		callEnded = true
		engine.Stop()
	})

	<-ctx.Done()
	duration := time.Since(startTime)

	if callEnded && cfg.neo4jURL != "" {
		score, err := scoring.Analyze(cfg.openRouterKey, cfg.model, "")
		if err != nil {
			log.Warn().Err(err).Msg("scoring failed")
		} else {
			memCfg := memory.Config{
				URL: cfg.neo4jURL, User: cfg.neo4jUser, Pass: cfg.neo4jPass,
			}
			memory.SaveCall(memCfg, memory.Lead{
				ID: cfg.leadID, Name: cfg.leadName, Phone: cfg.target,
				Score: score.Score,
			}, memory.Entry{
				Timestamp: startTime, Type: "outbound",
				Summary:  score.Summary,
				Duration: int(duration.Seconds()),
				Objective: cfg.objective,
			})
			log.Info().Str("score", score.Score).Str("summary", score.Summary).Msg("Lead scored")
		}
	}

	return nil
}

func sqliteDSN(path string) string {
	return fmt.Sprintf("file:%s?_pragma=foreign_keys(1)&_pragma=busy_timeout(5000)", path)
}
