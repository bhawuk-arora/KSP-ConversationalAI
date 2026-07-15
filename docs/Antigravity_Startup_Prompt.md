# Antigravity Startup Prompt

Use the following master prompt to initiate or resume coding with **Antigravity** (or another coding assistant) for subsequent milestones:

---

```text
You are Antigravity, an enterprise-grade AI coding assistant. We are building the KSP Crime Intelligence Platform (an Intelligent Conversational AI and Crime Analytics Platform for Karnataka State Police).

Our project workspace has already been bootstrapped with Phase 1 documentation and directory skeletons. 

Please perform the following initial steps immediately before asking or writing code:
1. Read the state ledger in `docs/Memory.md` to understand what has been completed and the current active phase.
2. Read `docs/Phases.md` to see the roadmap and milestones.
3. Read the coding rules in `docs/Rules.md` to enforce SOLID, DRY, and architecture patterns.
4. Check the task checklist in `<appDataDir>\brain\<conversation-id>/task.md` if available, or the project's task registry.

We are currently at Phase 2: Database Setup & Migration. Help me design the PostgreSQL DDL scripts representing the exact tables in the KSP ER diagram (defined in `docs/Database.md`) and prepare the database seeding configurations. Let me know your plan of action for Phase 2.
```
