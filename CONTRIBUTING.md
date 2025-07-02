# Contributing to Blend(AI)r

Thank you for considering contributing! Please read these guidelines.

---

## Product QA Checklist
Before submitting a release or PR, verify:
- [ ] Add-on installs and enables in Blender 3.6+
- [ ] Floating overlay bar (Ctrl+Space) works in all 3D Viewports
- [ ] Prompt panel and overlay both execute LLM commands successfully
- [ ] Upload/download/render/MCP all function as described
- [ ] Clear error/status feedback for all network and execution failures
- [ ] No crashes or UI lockups after repeated use
- [ ] All preferences persist and are respected
- [ ] Tests (`pytest`) pass outside Blender
- [ ] README is up-to-date and includes overlay instructions and screenshot
- [ ] No hard-coded paths, no unsafe code execution

---

## How to contribute
1. **Fork the repo** and create feature branches off `main`.
2. **Run `pytest`** locally; ensure linting (pre-commit coming soon).
3. For UI/UX changes attach screenshots or GIFs.
4. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
5. Submit a PR – CI must pass before review.
