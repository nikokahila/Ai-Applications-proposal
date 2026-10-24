# Project decisions

Use this decision log to document significant technical and architectural choices made by your team during development.

## Decision 1 — Model selection


**Decision:**
Lama 3.2:latest was used in running the model.

**Alternatives considered:**
Gwen 3.8:B was slower and had timeouts.

**Why we chose this:**
Model came recomended in project work. Light model easy to run.

---

## Decision 2 — Additional AI capability

**Decision:**
Memory and Web search

**Why it is needed:**
Memory was used to so Ai remembers what recipes it has used previously. Web search was used to find recepies for Ai and give sources for user.

**Alternatives considered:**
Rag was considered but it was unnecessary because it made process more complicated.

---

## Decision 3 — Architecture

**Decision:**
App and ui had own folder, while tools and capabilities were in source folder each in own independet file.

**Why:**
Made it easier to fix and debug codes when tools and ui were split into own files and folder instead having few files with a lot of code.
