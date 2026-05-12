package discord

import (
	"strings"
	"testing"
	"time"

	"github.com/bwmarrin/discordgo"
)

type fakeHistoryFetcher struct {
	batches map[string][]*discordgo.Message
	calls   []historyCall
}

type historyCall struct {
	channelID string
	limit     int
	beforeID  string
	afterID   string
	aroundID  string
}

func (f *fakeHistoryFetcher) ChannelMessages(channelID string, limit int, beforeID, afterID, aroundID string, options ...discordgo.RequestOption) ([]*discordgo.Message, error) {
	f.calls = append(f.calls, historyCall{
		channelID: channelID,
		limit:     limit,
		beforeID:  beforeID,
		afterID:   afterID,
		aroundID:  aroundID,
	})

	key := batchKey(beforeID, afterID, aroundID)
	return f.batches[key], nil
}

func batchKey(beforeID, afterID, aroundID string) string {
	switch {
	case beforeID != "":
		return "before:" + beforeID
	case afterID != "":
		return "after:" + afterID
	case aroundID != "":
		return "around:" + aroundID
	default:
		return "first"
	}
}

func TestRenderTranscript_ChronologicalAndReadable(t *testing.T) {
	messages := []*discordgo.Message{
		{
			ID:        "2",
			Timestamp: time.Date(2026, 4, 19, 10, 0, 2, 0, time.UTC),
			Content:   "second",
			Author:    &discordgo.User{Username: "codex"},
		},
		{
			ID:        "1",
			Timestamp: time.Date(2026, 4, 19, 10, 0, 1, 0, time.UTC),
			Content:   "first",
			Author:    &discordgo.User{Username: "claude"},
		},
	}

	got, err := renderTranscript("2026-04-19-demo", messages)
	if err != nil {
		t.Fatalf("renderTranscript() error = %v", err)
	}

	firstIdx := strings.Index(got, "## 2026-04-19T10:00:01Z · claude")
	secondIdx := strings.Index(got, "## 2026-04-19T10:00:02Z · codex")
	if firstIdx == -1 || secondIdx == -1 {
		t.Fatalf("renderTranscript() missing expected headings:\n%s", got)
	}
	if firstIdx > secondIdx {
		t.Fatalf("renderTranscript() did not sort chronologically:\n%s", got)
	}
	if !strings.Contains(got, "first") || !strings.Contains(got, "second") {
		t.Fatalf("renderTranscript() missing message content:\n%s", got)
	}
}

func TestRenderTranscript_ProducesUniqueTurnKeysForSameSecondMessages(t *testing.T) {
	base := time.Date(2026, 4, 19, 10, 0, 1, 100, time.UTC)
	messages := []*discordgo.Message{
		{
			ID:        "1",
			Timestamp: base,
			Content:   "first",
			Author:    &discordgo.User{Username: "claude"},
		},
		{
			ID:        "2",
			Timestamp: base,
			Content:   "second",
			Author:    &discordgo.User{Username: "codex"},
		},
	}

	got, err := renderTranscript("2026-04-19-demo", messages)
	if err != nil {
		t.Fatalf("renderTranscript() error = %v", err)
	}

	if !strings.Contains(got, "## 2026-04-19T10:00:01.0000001Z · claude") &&
		!strings.Contains(got, "## 2026-04-19T10:00:01.0000001Z · codex") {
		t.Fatalf("renderTranscript() did not preserve fractional-second turn keys:\n%s", got)
	}
	if strings.Count(got, "## 2026-04-19T10:00:01.0000001Z") != 1 {
		t.Fatalf("renderTranscript() expected exactly one first heading timestamp:\n%s", got)
	}
	if strings.Count(got, "## 2026-04-19T10:00:01.000000101Z")+strings.Count(got, "## 2026-04-19T10:00:01.000000102Z") == 0 {
		t.Fatalf("renderTranscript() did not disambiguate same-second timestamps:\n%s", got)
	}
}

func TestFetchChannelHistory_BoundedWindowAndChronological(t *testing.T) {
	after := time.Date(2026, 4, 19, 10, 0, 1, 0, time.UTC)
	before := time.Date(2026, 4, 19, 10, 0, 4, 0, time.UTC)
	firstPage := make([]*discordgo.Message, 0, 100)
	for i := 0; i < 98; i++ {
		firstPage = append(firstPage, &discordgo.Message{
			ID:        string(rune('a'+(i%26))) + string(rune('a'+((i/26)%26))) + string(rune('a'+((i/676)%26))),
			Timestamp: time.Date(2026, 4, 19, 10, 0, 5, i, time.UTC),
			Content:   "after-window filler",
		})
	}
	firstPage = append(firstPage,
		&discordgo.Message{ID: "4", Timestamp: time.Date(2026, 4, 19, 10, 0, 4, 0, time.UTC), Content: "in-range latest"},
		&discordgo.Message{ID: "3", Timestamp: time.Date(2026, 4, 19, 10, 0, 3, 0, time.UTC), Content: "in-range middle"},
	)
	fetcher := &fakeHistoryFetcher{
		batches: map[string][]*discordgo.Message{
			"before:" + beforeCursorForTime(before): firstPage,
			"before:3": {
				{ID: "2", Timestamp: time.Date(2026, 4, 19, 10, 0, 1, 0, time.UTC), Content: "in-range oldest"},
				{ID: "1", Timestamp: time.Date(2026, 4, 19, 9, 59, 59, 0, time.UTC), Content: "too old"},
			},
		},
	}

	got, err := FetchChannelHistory(fetcher, "channel-1", after, before)
	if err != nil {
		t.Fatalf("FetchChannelHistory() error = %v", err)
	}
	if len(got) != 3 {
		t.Fatalf("FetchChannelHistory() len = %d, want 3", len(got))
	}
	if got[0].ID != "2" || got[1].ID != "3" || got[2].ID != "4" {
		t.Fatalf("FetchChannelHistory() order = [%s %s %s], want [2 3 4]", got[0].ID, got[1].ID, got[2].ID)
	}
}

func TestFetchChannelHistory_AnchorsInitialRequestAtBeforeBoundary(t *testing.T) {
	after := time.Date(2026, 4, 19, 10, 0, 1, 0, time.UTC)
	before := time.Date(2026, 4, 19, 10, 0, 4, 0, time.UTC)
	fetcher := &fakeHistoryFetcher{
		batches: map[string][]*discordgo.Message{
			"before:" + beforeCursorForTime(before): nil,
		},
	}

	got, err := FetchChannelHistory(fetcher, "channel-1", after, before)
	if err != nil {
		t.Fatalf("FetchChannelHistory() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("FetchChannelHistory() len = %d, want 0", len(got))
	}
	if len(fetcher.calls) != 1 {
		t.Fatalf("ChannelMessages() calls = %d, want 1", len(fetcher.calls))
	}
	if fetcher.calls[0].beforeID != beforeCursorForTime(before) {
		t.Fatalf("ChannelMessages() beforeID = %q, want %q", fetcher.calls[0].beforeID, beforeCursorForTime(before))
	}
	if fetcher.calls[0].afterID != "" {
		t.Fatalf("ChannelMessages() afterID = %q, want empty", fetcher.calls[0].afterID)
	}
}
