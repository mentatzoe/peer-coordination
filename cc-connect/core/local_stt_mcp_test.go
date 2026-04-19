package core

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestLocalSTTMCP_Transcribe_Success(t *testing.T) {
	dir := t.TempDir()
	script := filepath.Join(dir, "fake_mcp.py")
	content := `import sys
sys.stdin.readline()
sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"fake","version":"1.0"}}}\n')
sys.stdout.flush()
sys.stdin.readline()
sys.stdin.readline()
sys.stdout.write('{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{\\"transcription\\":\\"hello from local mcp\\"}"}]}}\n')
sys.stdout.flush()
`
	if err := os.WriteFile(script, []byte(content), 0o755); err != nil {
		t.Fatalf("write fake server: %v", err)
	}

	stt := NewLocalSTTMCP("python3", []string{script}, "base.en", "transcribe")
	text, err := stt.Transcribe(context.Background(), []byte("fake-audio"), "mp3", "en")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if text != "hello from local mcp" {
		t.Fatalf("expected transcription, got %q", text)
	}
}

func TestLocalSTTMCP_Transcribe_ServerError(t *testing.T) {
	dir := t.TempDir()
	script := filepath.Join(dir, "fake_mcp_error.py")
	content := `import sys
sys.stdin.readline()
sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"fake","version":"1.0"}}}\n')
sys.stdout.flush()
sys.stdin.readline()
sys.stdin.readline()
sys.stdout.write('{"jsonrpc":"2.0","id":2,"error":{"code":-32001,"message":"tool failed"}}\n')
sys.stdout.flush()
`
	if err := os.WriteFile(script, []byte(content), 0o755); err != nil {
		t.Fatalf("write fake server: %v", err)
	}

	stt := NewLocalSTTMCP("python3", []string{script}, "base.en", "transcribe")
	_, err := stt.Transcribe(context.Background(), []byte("fake-audio"), "mp3", "")
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "tool failed") {
		t.Fatalf("expected tool failure in error, got %v", err)
	}
}
