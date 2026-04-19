package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/chenhg5/cc-connect/config"
	discordplatform "github.com/chenhg5/cc-connect/platform/discord"
)

type transcriptBundleMeta struct {
	raw              map[string]any `json:"-"`
	SessionID        string         `json:"session_id"`
	OpenedAt         string         `json:"opened_at"`
	ClosedAt         *string        `json:"closed_at"`
	Substrate        string         `json:"substrate"`
	ChannelID        string         `json:"channel_id"`
	TranscriptSource string         `json:"transcript_source"`
}

type transcriptFetcher interface {
	FetchChannelMessages(channelID string, after, before time.Time) ([]*discordgo.Message, error)
}

type liveTranscriptFetcher struct {
	session *discordgo.Session
}

func (f liveTranscriptFetcher) FetchChannelMessages(channelID string, after, before time.Time) ([]*discordgo.Message, error) {
	return discordplatform.FetchChannelHistory(f.session, channelID, after, before)
}

func runTranscript(args []string) {
	if len(args) == 0 {
		printTranscriptUsage()
		os.Exit(1)
	}
	switch args[0] {
	case "export":
		runTranscriptExport(args[1:])
	case "source":
		runTranscriptSource(args[1:])
	case "help", "--help", "-h":
		printTranscriptUsage()
	default:
		fmt.Fprintf(os.Stderr, "Unknown transcript subcommand: %s\n", args[0])
		printTranscriptUsage()
		os.Exit(1)
	}
}

func runTranscriptExport(args []string) {
	fs := flag.NewFlagSet("transcript export", flag.ExitOnError)
	configPath := fs.String("config", "", "path to config file (default: auto-detect)")
	project := fs.String("project", "", "project name containing the Discord platform config")
	sessionDir := fs.String("session-dir", "", "path to observations/sessions/<session-id>")
	afterOverride := fs.String("after", "", "optional RFC3339 lower bound override")
	beforeOverride := fs.String("before", "", "optional RFC3339 upper bound override")
	_ = fs.Parse(args)

	if *sessionDir == "" {
		fmt.Fprintln(os.Stderr, "Error: --session-dir is required")
		os.Exit(1)
	}

	fetcher, err := newLiveTranscriptFetcher(resolveConfigPath(*configPath), *project)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	if err := exportTranscriptForBundleWithOverrides(*sessionDir, fetcher, *afterOverride, *beforeOverride); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Exported transcript to %s\n", filepath.Join(*sessionDir, "transcript.md"))
}

func runTranscriptSource(args []string) {
	fs := flag.NewFlagSet("transcript source", flag.ExitOnError)
	sessionDir := fs.String("session-dir", "", "path to observations/sessions/<session-id>")
	source := fs.String("source", "", "one of export, reauthored, hybrid")
	_ = fs.Parse(args)

	if *sessionDir == "" || *source == "" {
		fmt.Fprintln(os.Stderr, "Error: --session-dir and --source are required")
		os.Exit(1)
	}
	if err := setTranscriptSource(*sessionDir, *source); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Updated %s transcript_source to %s\n", *sessionDir, *source)
}

func printTranscriptUsage() {
	fmt.Fprintf(os.Stderr, `Usage: cc-connect transcript <subcommand>

Subcommands:
  export    Export Discord history into a session bundle transcript
  source    Update transcript_source on an existing session bundle

Flags for 'export':
  --config <path>       Path to config file (default: auto-detect)
  --project <name>      Project name containing the Discord platform config
  --session-dir <path>  Path to observations/sessions/<session-id>
  --after <rfc3339>     Optional lower bound override
  --before <rfc3339>    Optional upper bound override

Flags for 'source':
  --session-dir <path>  Path to observations/sessions/<session-id>
  --source <value>      export | reauthored | hybrid
`)
}

func exportTranscriptForBundle(sessionDir string, fetcher transcriptFetcher) error {
	return exportTranscriptForBundleWithOverrides(sessionDir, fetcher, "", "")
}

func exportTranscriptForBundleWithOverrides(sessionDir string, fetcher transcriptFetcher, afterOverride, beforeOverride string) error {
	meta, err := loadTranscriptBundleMeta(sessionDir)
	if err != nil {
		return err
	}
	after, before, err := transcriptWindow(meta, afterOverride, beforeOverride)
	if err != nil {
		return err
	}

	messages, err := fetcher.FetchChannelMessages(meta.ChannelID, after, before)
	if err != nil {
		return fmt.Errorf("discord transcript export failed: %w", err)
	}
	if len(messages) == 0 {
		return errors.New("discord transcript export produced no messages; use fallback and mark transcript_source as reauthored or hybrid")
	}

	rendered, err := discordplatform.RenderTranscript(meta.SessionID, messages)
	if err != nil {
		return err
	}
	if err := os.WriteFile(filepath.Join(sessionDir, "transcript.md"), []byte(rendered), 0o644); err != nil {
		return fmt.Errorf("write transcript.md: %w", err)
	}
	meta.TranscriptSource = "export"
	meta.raw["transcript_source"] = "export"
	return saveTranscriptBundleMeta(sessionDir, meta)
}

func setTranscriptSource(sessionDir, source string) error {
	source = strings.TrimSpace(source)
	switch source {
	case "export", "reauthored", "hybrid":
	default:
		return fmt.Errorf("invalid transcript source %q", source)
	}
	meta, err := loadTranscriptBundleMeta(sessionDir)
	if err != nil {
		return err
	}
	meta.TranscriptSource = source
	meta.raw["transcript_source"] = source
	return saveTranscriptBundleMeta(sessionDir, meta)
}

func transcriptWindow(meta *transcriptBundleMeta, afterOverride, beforeOverride string) (time.Time, time.Time, error) {
	after, err := time.Parse(time.RFC3339, meta.OpenedAt)
	if err != nil {
		return time.Time{}, time.Time{}, fmt.Errorf("invalid meta.json opened_at %q: %w", meta.OpenedAt, err)
	}
	var before time.Time
	if meta.ClosedAt != nil && strings.TrimSpace(*meta.ClosedAt) != "" {
		before, err = time.Parse(time.RFC3339, *meta.ClosedAt)
		if err != nil {
			return time.Time{}, time.Time{}, fmt.Errorf("invalid meta.json closed_at %q: %w", *meta.ClosedAt, err)
		}
	} else {
		before = time.Now().UTC()
	}
	if strings.TrimSpace(afterOverride) != "" {
		after, err = time.Parse(time.RFC3339, afterOverride)
		if err != nil {
			return time.Time{}, time.Time{}, fmt.Errorf("invalid --after %q: %w", afterOverride, err)
		}
	}
	if strings.TrimSpace(beforeOverride) != "" {
		before, err = time.Parse(time.RFC3339, beforeOverride)
		if err != nil {
			return time.Time{}, time.Time{}, fmt.Errorf("invalid --before %q: %w", beforeOverride, err)
		}
	}
	return after.UTC(), before.UTC(), nil
}

func loadTranscriptBundleMeta(sessionDir string) (*transcriptBundleMeta, error) {
	rawBytes, err := os.ReadFile(filepath.Join(sessionDir, "meta.json"))
	if err != nil {
		return nil, fmt.Errorf("read meta.json: %w", err)
	}
	raw := map[string]any{}
	if err := json.Unmarshal(rawBytes, &raw); err != nil {
		return nil, fmt.Errorf("parse meta.json: %w", err)
	}

	meta := &transcriptBundleMeta{
		raw:              raw,
		SessionID:        stringField(raw, "session_id"),
		OpenedAt:         stringField(raw, "opened_at"),
		Substrate:        stringField(raw, "substrate"),
		ChannelID:        stringField(raw, "channel_id"),
		TranscriptSource: stringField(raw, "transcript_source"),
	}
	if v, ok := raw["closed_at"]; ok && v != nil {
		switch s := v.(type) {
		case string:
			meta.ClosedAt = &s
		}
	}
	if meta.SessionID == "" {
		return nil, errors.New("meta.json missing session_id")
	}
	if meta.OpenedAt == "" {
		return nil, errors.New("meta.json missing opened_at")
	}
	if meta.Substrate != "discord" {
		return nil, fmt.Errorf("meta.json substrate = %q, want discord", meta.Substrate)
	}
	if meta.ChannelID == "" {
		return nil, errors.New("meta.json missing channel_id")
	}
	return meta, nil
}

func saveTranscriptBundleMeta(sessionDir string, meta *transcriptBundleMeta) error {
	raw, err := json.MarshalIndent(meta.raw, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal meta.json: %w", err)
	}
	raw = append(raw, '\n')
	if err := os.WriteFile(filepath.Join(sessionDir, "meta.json"), raw, 0o644); err != nil {
		return fmt.Errorf("write meta.json: %w", err)
	}
	return nil
}

func stringField(raw map[string]any, key string) string {
	if raw == nil {
		return ""
	}
	if v, ok := raw[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

func newLiveTranscriptFetcher(configPath, projectName string) (transcriptFetcher, error) {
	cfg, err := config.Load(configPath)
	if err != nil {
		return nil, err
	}
	token, err := discordTokenFromConfig(cfg, projectName)
	if err != nil {
		return nil, err
	}
	session, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, err
	}
	return liveTranscriptFetcher{session: session}, nil
}

func discordTokenFromConfig(cfg *config.Config, projectName string) (string, error) {
	if cfg == nil {
		return "", errors.New("nil config")
	}

	projects := cfg.Projects
	if projectName != "" {
		filtered := make([]config.ProjectConfig, 0, 1)
		for _, proj := range projects {
			if proj.Name == projectName {
				filtered = append(filtered, proj)
				break
			}
		}
		if len(filtered) == 0 {
			return "", fmt.Errorf("project %q not found in config", projectName)
		}
		projects = filtered
	} else if len(projects) != 1 {
		return "", errors.New("multiple projects configured; pass --project")
	}

	for _, proj := range projects {
		for _, plat := range proj.Platforms {
			if plat.Type != "discord" {
				continue
			}
			if token, ok := plat.Options["token"].(string); ok && strings.TrimSpace(token) != "" {
				return token, nil
			}
			return "", fmt.Errorf("project %q discord platform missing token", proj.Name)
		}
	}
	return "", fmt.Errorf("project %q has no discord platform", projects[0].Name)
}
