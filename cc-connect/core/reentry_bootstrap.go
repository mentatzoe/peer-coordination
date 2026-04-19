package core

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const repoBootstrapReadLimit = 12 * 1024

func buildRepoReentryBootstrap(agent Agent) string {
	mp, ok := agent.(MemoryFileProvider)
	if !ok {
		return ""
	}

	memFile := mp.ProjectMemoryFile()
	if memFile == "" {
		return ""
	}

	repoRoot := filepath.Dir(memFile)
	sessionReentryPath := filepath.Join(repoRoot, "docs", "ways-of-working", "session-reentry.md")
	activeSlicesPath := filepath.Join(repoRoot, "ACTIVE-SLICES.md")

	sessionReentry, err := readBootstrapFile(sessionReentryPath)
	if err != nil {
		return ""
	}
	activeSlices, err := readBootstrapFile(activeSlicesPath)
	if err != nil {
		return ""
	}

	var extraHints []string
	if readmePreview, err := readBootstrapPreview(filepath.Join(repoRoot, "README.md"), 1600); err == nil && readmePreview != "" {
		extraHints = append(extraHints, "README.md excerpt:\n"+readmePreview)
	}
	if prPreview, err := readBootstrapPreview(filepath.Join(repoRoot, "docs", "ways-of-working", "pull-requests.md"), 1600); err == nil && prPreview != "" {
		extraHints = append(extraHints, "pull-requests.md excerpt:\n"+prPreview)
	}

	var b strings.Builder
	b.WriteString("[cc-connect repo bootstrap]\n")
	b.WriteString("Fresh session in a repo with explicit re-entry workflow. Use the bundled repo context below before forming the first substantive reply.\n")
	b.WriteString("If the first user prompt is low-information (for example `howdy` or `status?`), do repo-aware orientation first instead of replying generically.\n\n")
	b.WriteString("session-reentry.md:\n")
	b.WriteString(sessionReentry)
	b.WriteString("\n\nACTIVE-SLICES.md:\n")
	b.WriteString(activeSlices)
	if len(extraHints) > 0 {
		b.WriteString("\n\nAdditional context:\n")
		for i, hint := range extraHints {
			if i > 0 {
				b.WriteString("\n\n")
			}
			b.WriteString(hint)
		}
	}

	return b.String()
}

func readBootstrapFile(path string) (string, error) {
	return readBootstrapPreview(path, repoBootstrapReadLimit)
}

func readBootstrapPreview(path string, limit int) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	if limit > 0 && len(data) > limit {
		data = data[:limit]
	}
	text := strings.TrimSpace(string(data))
	if text == "" {
		return "", fmt.Errorf("empty bootstrap file: %s", path)
	}
	return text, nil
}
