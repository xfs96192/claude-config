# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
conda () {
	\local cmd="${1-__missing__}"
	case "$cmd" in
		(activate | deactivate) __conda_activate "$@" ;;
		(install | update | upgrade | remove | uninstall) __conda_exe "$@" || \return
			__conda_reactivate ;;
		(*) __conda_exe "$@" ;;
	esac
}
# Shell Options
setopt nohashdirs
setopt login
# Aliases
alias -- kimi_claude='export ANTHROPIC_BASE_URL="https://api.moonshot.cn/anthropic/"; export ANTHROPIC_API_KEY="sk-I8WiOypz8mv8gflB0wTNUEOSxOjD3EkSOvZMmVTGZ7uHT6Mj"; echo "Claude环境变量已设置"'
alias -- run-help=man
alias -- which-command=whence
# Check for rg availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/Users/fanshengxia/.npm-global/lib/node_modules/\@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg'
fi
export PATH=/Users/fanshengxia/.antigravity/antigravity/bin\:/Users/fanshengxia/.npm-global/bin\:/usr/local/bin\:/usr/local/bin\:/opt/homebrew/bin\:/opt/homebrew/sbin\:/usr/local/bin\:/System/Cryptexes/App/usr/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin\:/opt/pmk/env/global/bin\:/Users/fanshengxia/.antigravity/antigravity/bin\:/Users/fanshengxia/.npm-global/bin\:/Users/fanshengxia/opt/anaconda3/bin\:/Users/fanshengxia/opt/anaconda3/condabin\:/Users/fanshengxia/.cargo/bin\:/Users/fanshengxia/.trae/extensions/ms-python.debugpy-2025.14.1-darwin-arm64/bundled/scripts/noConfigScripts
