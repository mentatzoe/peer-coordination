package discord

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
)

type transcriptTurn struct {
	Timestamp string
	Author    string
	Content   string
}

type historyFetcher interface {
	ChannelMessages(channelID string, limit int, beforeID, afterID, aroundID string, options ...discordgo.RequestOption) ([]*discordgo.Message, error)
}

// FetchChannelHistory fetches Discord messages for a bounded window and returns
// them in chronological order.
func FetchChannelHistory(fetcher historyFetcher, channelID string, after, before time.Time) ([]*discordgo.Message, error) {
	if channelID == "" {
		return nil, fmt.Errorf("discord transcript export: channel_id is required")
	}
	if before.IsZero() {
		before = time.Now().UTC()
	}
	if !after.IsZero() && before.Before(after) {
		return nil, fmt.Errorf("discord transcript export: before is earlier than after")
	}

	var (
		beforeID  string
		collected []*discordgo.Message
	)
	for {
		batch, err := fetcher.ChannelMessages(channelID, 100, beforeID, "", "")
		if err != nil {
			return nil, err
		}
		if len(batch) == 0 {
			break
		}

		stop := false
		for _, msg := range batch {
			if msg == nil {
				continue
			}
			ts := msg.Timestamp.UTC()
			if !before.IsZero() && ts.After(before) {
				continue
			}
			if !after.IsZero() && ts.Before(after) {
				stop = true
				continue
			}
			collected = append(collected, msg)
		}

		beforeID = batch[len(batch)-1].ID
		if stop || len(batch) < 100 {
			break
		}
	}

	sort.SliceStable(collected, func(i, j int) bool {
		ti := collected[i].Timestamp.UTC()
		tj := collected[j].Timestamp.UTC()
		if ti.Equal(tj) {
			return collected[i].ID < collected[j].ID
		}
		return ti.Before(tj)
	})
	return collected, nil
}

// RenderTranscript renders Discord messages into a bundle-compatible markdown transcript.
func RenderTranscript(sessionID string, messages []*discordgo.Message) (string, error) {
	return renderTranscript(sessionID, messages)
}

func renderTranscript(sessionID string, messages []*discordgo.Message) (string, error) {
	if sessionID == "" {
		return "", fmt.Errorf("discord transcript export: session_id is required")
	}
	if len(messages) == 0 {
		return "", fmt.Errorf("discord transcript export: no messages to render")
	}

	turns := normalizeTranscriptTurns(messages)
	var b strings.Builder
	b.WriteString("# Session transcript — ")
	b.WriteString(sessionID)
	b.WriteString("\n\n---\n\n")
	for i, turn := range turns {
		b.WriteString("## ")
		b.WriteString(turn.Timestamp)
		b.WriteString(" · ")
		b.WriteString(turn.Author)
		b.WriteString("\n\n")
		b.WriteString(turn.Content)
		b.WriteString("\n\n")
		if i != len(turns)-1 {
			b.WriteString("---\n\n")
		}
	}
	return b.String(), nil
}

func normalizeTranscriptTurns(messages []*discordgo.Message) []transcriptTurn {
	sorted := make([]*discordgo.Message, 0, len(messages))
	for _, msg := range messages {
		if msg != nil {
			sorted = append(sorted, msg)
		}
	}
	sort.SliceStable(sorted, func(i, j int) bool {
		ti := sorted[i].Timestamp.UTC()
		tj := sorted[j].Timestamp.UTC()
		if ti.Equal(tj) {
			return sorted[i].ID < sorted[j].ID
		}
		return ti.Before(tj)
	})

	used := make(map[string]struct{}, len(sorted))
	turns := make([]transcriptTurn, 0, len(sorted))
	for _, msg := range sorted {
		ts := msg.Timestamp.UTC()
		key := uniqueTimestampKey(ts, used)
		used[key] = struct{}{}
		turns = append(turns, transcriptTurn{
			Timestamp: key,
			Author:    transcriptAuthor(msg),
			Content:   transcriptContent(msg),
		})
	}
	return turns
}

func uniqueTimestampKey(ts time.Time, used map[string]struct{}) string {
	current := ts.UTC()
	for {
		key := current.Format(time.RFC3339Nano)
		if _, exists := used[key]; !exists {
			return key
		}
		current = current.Add(time.Nanosecond)
	}
}

func transcriptAuthor(msg *discordgo.Message) string {
	if msg.Author == nil {
		return "unknown"
	}
	if msg.Author.Username != "" {
		return msg.Author.Username
	}
	if msg.Author.GlobalName != "" {
		return msg.Author.GlobalName
	}
	if msg.Author.ID != "" {
		return msg.Author.ID
	}
	return "unknown"
}

func transcriptContent(msg *discordgo.Message) string {
	var parts []string
	if strings.TrimSpace(msg.Content) != "" {
		parts = append(parts, msg.Content)
	}
	for _, attachment := range msg.Attachments {
		if attachment == nil {
			continue
		}
		if attachment.URL != "" {
			parts = append(parts, fmt.Sprintf("[attachment] %s", attachment.URL))
		} else if attachment.Filename != "" {
			parts = append(parts, fmt.Sprintf("[attachment] %s", attachment.Filename))
		}
	}
	if len(parts) == 0 {
		return "_no textual content_"
	}
	return strings.Join(parts, "\n")
}
