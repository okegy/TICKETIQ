package com.ticketiq.rules;

import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Deterministic, rule-based priority and urgency classifier.
 *
 * Rules are evaluated top-to-bottom; the first matching rule wins.
 * This guarantees fully transparent, explainable prioritisation with
 * zero hallucination risk — consistent with the TicketIQ design brief.
 *
 * Priority levels : P1 (Critical) → P2 (High) → P3 (Medium) → P4 (Low)
 * Urgency levels  : CRITICAL | HIGH | MEDIUM | LOW
 */
@Component
public class PriorityRulesEngine {

    public record PriorityDecision(
            String priority,
            String urgency,
            String rationale,
            List<String> matchedRules
    ) {}

    // ── Keyword sets ──────────────────────────────────────────────────────────

    private static final List<String> P1_KEYWORDS = List.of(
            "production down", "all users", "service unavailable",
            "data loss", "breach", "security incident", "ransomware",
            "database corrupted", "complete outage", "critical failure",
            "system-wide", "entire organisation", "revenue impact"
    );

    private static final List<String> P2_KEYWORDS = List.of(
            "multiple users", "team unable", "degraded performance",
            "partial outage", "batch job failed", "nightly job",
            "partner api", "integration failure", "major feature",
            "high cpu", "memory leak", "timeout", "escalation required"
    );

    private static final List<String> P3_KEYWORDS = List.of(
            "single user", "one user", "account locked", "password reset",
            "login loop", "sso", "slow report", "missing dashboard",
            "duplicate record", "blank pdf", "export failed",
            "interface file rejected"
    );

    // P4 is the default (anything not matched above)

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Evaluate a (possibly redacted) ticket description and optional
     * category metadata to produce a priority decision.
     *
     * @param ticketText  Raw or redacted ticket text
     * @param category    Category string from AI classification (may be null)
     * @param subcategory Subcategory string from AI classification (may be null)
     * @return PriorityDecision record
     */
    public PriorityDecision evaluate(String ticketText, String category, String subcategory) {
        if (ticketText == null) ticketText = "";
        String lower = ticketText.toLowerCase();
        String cat   = category    != null ? category.toLowerCase()    : "";
        String sub   = subcategory != null ? subcategory.toLowerCase() : "";
        String combined = lower + " " + cat + " " + sub;

        // P1 — Critical
        for (String kw : P1_KEYWORDS) {
            if (combined.contains(kw)) {
                return new PriorityDecision(
                        "P1", "CRITICAL",
                        "Keyword '" + kw + "' indicates a production-wide critical incident.",
                        List.of("KEYWORD_MATCH:" + kw, "RULE:P1_CRITICAL")
                );
            }
        }

        // P2 — High
        for (String kw : P2_KEYWORDS) {
            if (combined.contains(kw)) {
                return new PriorityDecision(
                        "P2", "HIGH",
                        "Keyword '" + kw + "' indicates a high-impact multi-user or integration incident.",
                        List.of("KEYWORD_MATCH:" + kw, "RULE:P2_HIGH")
                );
            }
        }

        // P3 — Medium
        for (String kw : P3_KEYWORDS) {
            if (combined.contains(kw)) {
                return new PriorityDecision(
                        "P3", "MEDIUM",
                        "Keyword '" + kw + "' indicates a single-user or standard service-desk incident.",
                        List.of("KEYWORD_MATCH:" + kw, "RULE:P3_MEDIUM")
                );
            }
        }

        // P4 — Low (default)
        return new PriorityDecision(
                "P4", "LOW",
                "No high-priority keyword matched. Defaulting to standard low-priority queue.",
                List.of("RULE:P4_DEFAULT")
        );
    }

    /**
     * Convenience wrapper that returns a plain Map suitable for JSON serialisation.
     */
    public Map<String, Object> evaluateAsMap(String ticketText, String category, String subcategory) {
        PriorityDecision d = evaluate(ticketText, category, subcategory);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("priority", d.priority());
        m.put("urgency",  d.urgency());
        m.put("rationale", d.rationale());
        m.put("matchedRules", d.matchedRules());
        return m;
    }
}
