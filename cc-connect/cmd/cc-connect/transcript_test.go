package main

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/bwmarrin/discordgo"
)

type fakeTranscriptFetcher struct {
	messages []*discordgo.Message
	err      error
	channel  string
	after    time.Time
	before   time.Time
}

func (f *fakeTranscriptFetcher) FetchChannelMessages(channelID string, after, before time.Time) ([]*discordgo.Message, error) {
	f.channel = channelID
	f.after = after
	f.before = before
	if f.err != nil {
		return nil, f.err
	}
	return f.messages, nil
}

func TestExportTranscriptForBundle_WritesTranscriptAndExportSource(t *testing.T) {
	originalUpdatedAt := "2026-04-19T09:59:00Z"
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "reauthored",
		UpdatedAt:        originalUpdatedAt,
	})

	fetcher := &fakeTranscriptFetcher{
		messages: []*discordgo.Message{
			{
				ID:        "m1",
				Timestamp: time.Date(2026, 4, 19, 10, 0, 1, 0, time.UTC),
				Content:   "hello",
				Author:    &discordgo.User{Username: "claude"},
			},
			{
				ID:        "m2",
				Timestamp: time.Date(2026, 4, 19, 10, 0, 2, 0, time.UTC),
				Content:   "hi",
				Author:    &discordgo.User{Username: "codex"},
			},
		},
	}

	if err := exportTranscriptForBundle(sessionDir, fetcher); err != nil {
		t.Fatalf("exportTranscriptForBundle() error = %v", err)
	}

	transcriptBytes, err := os.ReadFile(filepath.Join(sessionDir, "transcript.md"))
	if err != nil {
		t.Fatalf("read transcript.md: %v", err)
	}
	transcript := string(transcriptBytes)
	if !strings.Contains(transcript, "## 2026-04-19T10:00:01Z · claude") || !strings.Contains(transcript, "hello") {
		t.Fatalf("transcript.md missing exported content:\n%s", transcript)
	}

	meta := readTranscriptBundleMeta(t, sessionDir)
	if meta.TranscriptSource != "export" {
		t.Fatalf("transcript_source = %q, want export", meta.TranscriptSource)
	}
	if meta.UpdatedAt == "" {
		t.Fatal("updated_at = empty, want RFC3339 timestamp")
	}
	if meta.UpdatedAt == originalUpdatedAt {
		t.Fatalf("updated_at = %q, want value updated after export", meta.UpdatedAt)
	}
	if _, err := time.Parse(time.RFC3339, meta.UpdatedAt); err != nil {
		t.Fatalf("updated_at = %q, want RFC3339 timestamp: %v", meta.UpdatedAt, err)
	}
}

func TestExportTranscriptForBundle_FailsClosedOnFetchError(t *testing.T) {
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "reauthored",
	})

	err := exportTranscriptForBundle(sessionDir, &fakeTranscriptFetcher{err: errors.New("boom")})
	if err == nil {
		t.Fatal("exportTranscriptForBundle() error = nil, want failure")
	}

	meta := readTranscriptBundleMeta(t, sessionDir)
	if meta.TranscriptSource != "reauthored" {
		t.Fatalf("transcript_source changed on failure = %q, want reauthored", meta.TranscriptSource)
	}
}

func TestSetTranscriptSource_UpdatesMetadata(t *testing.T) {
	originalUpdatedAt := "2026-04-19T10:00:00Z"
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "export",
		UpdatedAt:        originalUpdatedAt,
	})

	if err := setTranscriptSource(sessionDir, "hybrid"); err != nil {
		t.Fatalf("setTranscriptSource() error = %v", err)
	}

	meta := readTranscriptBundleMeta(t, sessionDir)
	if meta.TranscriptSource != "hybrid" {
		t.Fatalf("transcript_source = %q, want hybrid", meta.TranscriptSource)
	}
	if meta.UpdatedAt == "" {
		t.Fatal("updated_at = empty, want RFC3339 timestamp")
	}
	if meta.UpdatedAt == originalUpdatedAt {
		t.Fatalf("updated_at = %q, want value updated after source change", meta.UpdatedAt)
	}
	if _, err := time.Parse(time.RFC3339, meta.UpdatedAt); err != nil {
		t.Fatalf("updated_at = %q, want RFC3339 timestamp: %v", meta.UpdatedAt, err)
	}
}

func TestExportTranscriptForBundleWithOverrides_UsesOverrideWindow(t *testing.T) {
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "reauthored",
	})
	fetcher := &fakeTranscriptFetcher{
		messages: []*discordgo.Message{
			{
				ID:        "m1",
				Timestamp: time.Date(2026, 4, 19, 10, 1, 0, 0, time.UTC),
				Content:   "hello",
				Author:    &discordgo.User{Username: "claude"},
			},
		},
	}

	if err := exportTranscriptForBundleWithOverrides(
		sessionDir,
		fetcher,
		"2026-04-19T10:01:00Z",
		"2026-04-19T10:02:00Z",
	); err != nil {
		t.Fatalf("exportTranscriptForBundleWithOverrides() error = %v", err)
	}

	if fetcher.channel != "channel-1" {
		t.Fatalf("FetchChannelMessages() channel = %q, want channel-1", fetcher.channel)
	}
	if got := fetcher.after.Format(time.RFC3339); got != "2026-04-19T10:01:00Z" {
		t.Fatalf("FetchChannelMessages() after = %q, want 2026-04-19T10:01:00Z", got)
	}
	if got := fetcher.before.Format(time.RFC3339); got != "2026-04-19T10:02:00Z" {
		t.Fatalf("FetchChannelMessages() before = %q, want 2026-04-19T10:02:00Z", got)
	}
}

func TestExportTranscriptForBundle_PreservesUniqueTurnReferences(t *testing.T) {
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "reauthored",
	})
	base := time.Date(2026, 4, 19, 10, 1, 0, 100, time.UTC)
	fetcher := &fakeTranscriptFetcher{
		messages: []*discordgo.Message{
			{
				ID:        "m1",
				Timestamp: base,
				Content:   "first",
				Author:    &discordgo.User{Username: "claude"},
			},
			{
				ID:        "m2",
				Timestamp: base,
				Content:   "second",
				Author:    &discordgo.User{Username: "codex"},
			},
		},
	}

	if err := exportTranscriptForBundle(sessionDir, fetcher); err != nil {
		t.Fatalf("exportTranscriptForBundle() error = %v", err)
	}

	transcriptBytes, err := os.ReadFile(filepath.Join(sessionDir, "transcript.md"))
	if err != nil {
		t.Fatalf("read transcript.md: %v", err)
	}
	transcript := string(transcriptBytes)
	if strings.Count(transcript, "## 2026-04-19T10:01:00.0000001Z") != 1 {
		t.Fatalf("transcript.md missing first unique turn key:\n%s", transcript)
	}
	if strings.Count(transcript, "## 2026-04-19T10:01:00.000000101Z")+strings.Count(transcript, "## 2026-04-19T10:01:00.000000102Z") == 0 {
		t.Fatalf("transcript.md missing disambiguated second turn key:\n%s", transcript)
	}
}

func TestExportTranscriptForBundle_FailsClosedOnEmptyHistory(t *testing.T) {
	sessionDir := newTranscriptBundleDir(t, transcriptBundleMeta{
		SessionID:        "2026-04-19-demo",
		OpenedAt:         "2026-04-19T10:00:00Z",
		ClosedAt:         strPtr("2026-04-19T10:05:00Z"),
		Substrate:        "discord",
		ChannelID:        "channel-1",
		TranscriptSource: "reauthored",
	})

	err := exportTranscriptForBundle(sessionDir, &fakeTranscriptFetcher{})
	if err == nil {
		t.Fatal("exportTranscriptForBundle() error = nil, want failure")
	}
	if !strings.Contains(err.Error(), "use fallback") {
		t.Fatalf("exportTranscriptForBundle() error = %q, want fallback guidance", err.Error())
	}

	meta := readTranscriptBundleMeta(t, sessionDir)
	if meta.TranscriptSource != "reauthored" {
		t.Fatalf("transcript_source changed on empty history = %q, want reauthored", meta.TranscriptSource)
	}
}

func newTranscriptBundleDir(t *testing.T, meta transcriptBundleMeta) string {
	t.Helper()

	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "transcript.md"), []byte("# placeholder\n"), 0o644); err != nil {
		t.Fatalf("write transcript.md: %v", err)
	}
	raw, err := json.MarshalIndent(meta, "", "  ")
	if err != nil {
		t.Fatalf("marshal meta: %v", err)
	}
	if err := os.WriteFile(filepath.Join(dir, "meta.json"), raw, 0o644); err != nil {
		t.Fatalf("write meta.json: %v", err)
	}
	return dir
}

func readTranscriptBundleMeta(t *testing.T, dir string) transcriptBundleMeta {
	t.Helper()

	raw, err := os.ReadFile(filepath.Join(dir, "meta.json"))
	if err != nil {
		t.Fatalf("read meta.json: %v", err)
	}
	var meta transcriptBundleMeta
	if err := json.Unmarshal(raw, &meta); err != nil {
		t.Fatalf("unmarshal meta.json: %v", err)
	}
	return meta
}

func strPtr(s string) *string {
	return &s
}
