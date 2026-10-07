# Demo: zero-to-hero run in ~60s. Render with: vhs docs/demo.tape
# (needs: vhs + ttyd + ffmpeg — or run docs/demo.sh which needs only bash+python)
Output docs/img/demo.gif
Set Shell bash
Set FontSize 18
Set Width 1100
Set Height 700
Set Theme "Catppuccin Frappe"
Set TypingSpeed 40ms

Type "cd self-improving-trading-agent-phd-2026 && bash scripts/run_all.sh"
Enter
Wait+Line /done/
Sleep 2s
Type "cat results/self_improving_summary.csv"
Enter
Sleep 3s
