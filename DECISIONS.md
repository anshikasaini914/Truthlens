# Decision Points — TruthLens

## DP1 · Feed order

**Choice:** Risk-first, then recency within each group — High Risk + newest, High Risk + older, Normal + newest, Normal + older. A toggle lets anyone switch to pure "Newest first" instead.

**Why:** A triage tool's entire job is to surface danger before it spreads, not just to log activity in order. A dangerous claim submitted two hours ago is more urgent than a harmless one submitted two minutes ago — pure recency would bury it. But recency still matters for situational awareness, so it's the tie-breaker inside each risk tier, and the toggle exists because a reviewer working a shift may specifically want "what just came in" rather than "what's scariest."

## DP2 · Visibility

**Choice:** Unverified claims are publicly visible immediately, always clearly labeled with a grey "Unverified" badge (and a red "High Risk" pill where relevant).

**Why:** The whole point of a triage feed is to show a newsroom or citizen group what's trending *before* anyone has had time to check it — that's the "triage" part. Hiding claims until reviewed would turn this into a slower, delayed fact-check archive instead of an early-warning tool, and would also hide the very high-risk content that most needs eyes on it fast. The tradeoff is handled by making the unverified state impossible to miss — clear badge, no ambiguity about what "unverified" means.

## DP3 · Editing

**Choice:** Editing is allowed after submission, and flags/risk level are fully recalculated from the new text on every save. Review status and reviewer notes are untouched by an edit (they don't silently reset).

**Why:** Viral text is often copy-pasted messily or mistyped during rapid submission, and forcing someone to delete-and-resubmit just to fix a typo or add a missing source link creates friction that discourages good data hygiene (e.g., adding a source link after the fact should actually reward the claim by dropping a flag). Recalculating flags on edit keeps the risk signal honest — a flag can't survive past the text change that justified it. Leaving the review status alone (rather than resetting it to Unverified) avoids the trust problem of erasing a reviewer's prior judgment on a minor edit; if the edit is substantive enough to warrant re-review, that's a reviewer's call, not something the system should force silently.
