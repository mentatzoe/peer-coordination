package core

import "testing"

func TestIsSilentPassResponse(t *testing.T) {
	tests := []struct {
		name    string
		content string
		want    bool
	}{
		// Canonical sentinel — exact and whitespace tolerance.
		{"canonical exact", SilentPassSentinel, true},
		{"canonical with leading/trailing whitespace", "  \n\t" + SilentPassSentinel + " \n", true},

		// Legacy sentinel — preserved for backward compat during transition.
		{"legacy exact", SilentPassResponse, true},
		{"legacy with whitespace", " " + SilentPassResponse + "\n", true},

		// Inline-code wrapping.
		{"canonical wrapped in inline code", "`" + SilentPassSentinel + "`", true},
		{"legacy wrapped in inline code", "`" + SilentPassResponse + "`", true},
		{"canonical inline code with whitespace", " `" + SilentPassSentinel + "` ", true},

		// Fenced-code wrapping.
		{"canonical in fenced code", "```\n" + SilentPassSentinel + "\n```", true},
		{"legacy in fenced code", "```\n" + SilentPassResponse + "\n```", true},
		{"canonical in fenced code with language tag", "```text\n" + SilentPassSentinel + "\n```", true},
		{"canonical in fenced code single line", "```" + SilentPassSentinel + "```", true},

		// Failure modes that MUST stay visible (operator can see the leak).
		{"trailing underscore typo", "__CC_CONNECT_SILENT_PASS___", false},
		{"missing underscore typo", "_CC_CONNECT_SILENT_PASS__", false},
		{"prefix label", "PASS: " + SilentPassSentinel, false},
		{"suffix commentary", SilentPassSentinel + " because I have nothing to add", false},
		{"mid-sentence substring", "I will emit " + SilentPassSentinel + " now.", false},
		{"legacy mid-sentence substring", "agent said " + SilentPassResponse + " but with extra text", false},

		// Other non-matches.
		{"empty", "", false},
		{"whitespace only", "   \n\t  ", false},
		{"unrelated content", "no, I have something to say", false},
		{"bare PASS word", "PASS", false},
		{"angle-bracket near-miss", "<silent_pass>", false},
		{"angle-bracket extra-space near-miss", "< SILENT_PASS >", false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := IsSilentPassResponse(tc.content)
			if got != tc.want {
				t.Errorf("IsSilentPassResponse(%q) = %v, want %v", tc.content, got, tc.want)
			}
		})
	}
}
