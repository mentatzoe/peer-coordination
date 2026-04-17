package core

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// LocalSTTMCP implements SpeechToText by spawning a local MCP server over stdio
// and calling its transcription tool.
type LocalSTTMCP struct {
	Command string
	Args    []string
	Model   string
	Tool    string
}

func NewLocalSTTMCP(command string, args []string, model, tool string) *LocalSTTMCP {
	if command == "" {
		command = "node"
	}
	if model == "" {
		model = "base.en"
	}
	if tool == "" {
		tool = "transcribe"
	}
	return &LocalSTTMCP{
		Command: command,
		Args:    append([]string(nil), args...),
		Model:   model,
		Tool:    tool,
	}
}

func (l *LocalSTTMCP) Transcribe(ctx context.Context, audio []byte, format string, lang string) (string, error) {
	if len(l.Args) == 0 {
		return "", fmt.Errorf("local_mcp: missing command args")
	}

	tmpFile, err := os.CreateTemp("", "cc-connect-stt-*."+formatToExt(format))
	if err != nil {
		return "", fmt.Errorf("local_mcp: create temp audio file: %w", err)
	}
	tmpPath := tmpFile.Name()
	defer os.Remove(tmpPath)

	if _, err := tmpFile.Write(audio); err != nil {
		tmpFile.Close()
		return "", fmt.Errorf("local_mcp: write temp audio file: %w", err)
	}
	if err := tmpFile.Close(); err != nil {
		return "", fmt.Errorf("local_mcp: close temp audio file: %w", err)
	}

	callCtx, cancel := context.WithTimeout(ctx, 90*time.Second)
	defer cancel()

	cmd := exec.CommandContext(callCtx, l.Command, l.Args...)
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return "", fmt.Errorf("local_mcp: stdin pipe: %w", err)
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return "", fmt.Errorf("local_mcp: stdout pipe: %w", err)
	}
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Start(); err != nil {
		return "", fmt.Errorf("local_mcp: start server: %w", err)
	}
	defer func() {
		cancel()
		_ = stdin.Close()
		_ = cmd.Wait()
	}()

	reader := bufio.NewReader(stdout)
	enc := json.NewEncoder(stdin)

	if err := enc.Encode(map[string]any{
		"jsonrpc": "2.0",
		"id":      1,
		"method":  "initialize",
		"params": map[string]any{
			"protocolVersion": "2024-11-05",
			"capabilities":    map[string]any{},
			"clientInfo": map[string]any{
				"name":    "cc-connect",
				"version": "local-stt-mcp",
			},
		},
	}); err != nil {
		return "", fmt.Errorf("local_mcp: send initialize: %w", err)
	}
	if _, err := waitForJSONRPCResponse(reader, 1); err != nil {
		return "", fmt.Errorf("local_mcp: initialize failed: %w (stderr: %s)", err, strings.TrimSpace(stderr.String()))
	}

	if err := enc.Encode(map[string]any{
		"jsonrpc": "2.0",
		"method":  "notifications/initialized",
		"params":  map[string]any{},
	}); err != nil {
		return "", fmt.Errorf("local_mcp: send initialized notification: %w", err)
	}

	options := map[string]any{
		"model":         l.Model,
		"output_format": "txt",
	}
	if lang != "" {
		options["language"] = lang
	}

	if err := enc.Encode(map[string]any{
		"jsonrpc": "2.0",
		"id":      2,
		"method":  "tools/call",
		"params": map[string]any{
			"name": l.Tool,
			"arguments": map[string]any{
				"audio_path":   tmpPath,
				"auto_convert": true,
				"options":      options,
			},
		},
	}); err != nil {
		return "", fmt.Errorf("local_mcp: send tool call: %w", err)
	}

	resultRaw, err := waitForJSONRPCResponse(reader, 2)
	if err != nil {
		return "", fmt.Errorf("local_mcp: tool call failed: %w (stderr: %s)", err, strings.TrimSpace(stderr.String()))
	}

	var result struct {
		Content []struct {
			Type string `json:"type"`
			Text string `json:"text"`
		} `json:"content"`
		IsError bool `json:"isError,omitempty"`
	}
	if err := json.Unmarshal(resultRaw, &result); err != nil {
		return "", fmt.Errorf("local_mcp: decode tool result: %w", err)
	}
	if result.IsError {
		return "", fmt.Errorf("local_mcp: server returned tool error")
	}

	for _, item := range result.Content {
		if item.Type != "text" || strings.TrimSpace(item.Text) == "" {
			continue
		}
		text := strings.TrimSpace(item.Text)
		var payload struct {
			Transcription string `json:"transcription"`
		}
		if json.Unmarshal([]byte(text), &payload) == nil && strings.TrimSpace(payload.Transcription) != "" {
			return strings.TrimSpace(payload.Transcription), nil
		}
		return text, nil
	}

	return "", fmt.Errorf("local_mcp: empty tool result")
}

type jsonrpcError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func waitForJSONRPCResponse(r *bufio.Reader, targetID int) (json.RawMessage, error) {
	target := fmt.Sprintf("%d", targetID)
	for {
		line, err := r.ReadBytes('\n')
		if err != nil {
			if err == io.EOF {
				return nil, fmt.Errorf("connection closed while waiting for response")
			}
			return nil, err
		}

		line = bytes.TrimSpace(line)
		if len(line) == 0 {
			continue
		}

		var env struct {
			ID     json.RawMessage `json:"id"`
			Method string          `json:"method"`
			Result json.RawMessage `json:"result"`
			Error  *jsonrpcError   `json:"error"`
		}
		if err := json.Unmarshal(line, &env); err != nil {
			continue
		}
		if env.Method != "" {
			continue
		}
		if strings.TrimSpace(string(env.ID)) != target {
			continue
		}
		if env.Error != nil {
			return nil, fmt.Errorf("json-rpc %d: %s", env.Error.Code, env.Error.Message)
		}
		return env.Result, nil
	}
}

func JoinCommandArgs(entry string, extra []string) []string {
	args := make([]string, 0, len(extra)+1)
	if entry != "" {
		args = append(args, filepath.Clean(entry))
	}
	args = append(args, extra...)
	return args
}
