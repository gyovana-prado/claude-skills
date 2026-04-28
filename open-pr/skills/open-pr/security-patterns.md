# Security Patterns Reference

Use these patterns to audit staged files before committing or opening a PR.

---

## Sensitive Filenames (block by default)

Flag any file matching these patterns that is NOT in `.gitignore`:

```
.env
.env.*
*.pem
*.key
*.p12
*.pfx
*credentials*.json
*service-account*.json
*serviceaccount*.json
*secret*.json
*secrets*.json
*keyfile*.json
*key.json
auth.json
token.json
config.secret.*
*.secret
secrets/
private/
```

---

## Sensitive Content Patterns (scan file contents)

Scan text files for these regex patterns. Flag any match that looks like a real value (not a placeholder like `YOUR_KEY_HERE`, `<secret>`, `example`, `xxxx`, `****`).

### Generic secrets
```
(?i)(api_key|apikey|api-key)\s*[:=]\s*["']?[A-Za-z0-9_\-]{16,}
(?i)(secret|secret_key|secretkey)\s*[:=]\s*["']?[A-Za-z0-9_\-]{16,}
(?i)(password|passwd|pwd)\s*[:=]\s*["']?[^\s"']{8,}
(?i)(token|access_token|auth_token|bearer)\s*[:=]\s*["']?[A-Za-z0-9_\-\.]{16,}
(?i)(private_key|private-key)\s*[:=]\s*["']?[A-Za-z0-9_\-]{16,}
```

### Cloud providers
```
AKIA[0-9A-Z]{16}                          # AWS Access Key ID
(?i)aws_secret_access_key\s*[:=]\s*\S{40} # AWS Secret
AIza[0-9A-Za-z\-_]{35}                    # Google API Key
ya29\.[0-9A-Za-z\-_]+                     # Google OAuth token
ghp_[A-Za-z0-9]{36}                       # GitHub Personal Access Token
ghs_[A-Za-z0-9]{36}                       # GitHub App token
sk-[A-Za-z0-9]{48}                        # OpenAI API Key
xoxb-[0-9\-]+[a-zA-Z0-9]+                 # Slack Bot Token
xoxp-[0-9\-]+[a-zA-Z0-9]+                 # Slack User Token
```

### Connection strings
```
(?i)(mongodb|postgres|mysql|redis|amqp):\/\/[^:]+:[^@]+@
(?i)jdbc:[a-z]+:\/\/[^:]+:[^@]+@
(?i)Server=.+;.*(Password|Pwd)\s*=\s*[^;]+
```

### Brazilian PII
```
\b\d{3}\.\d{3}\.\d{3}-\d{2}\b            # CPF formatted
\b\d{11}\b                                # CPF unformatted (11 digits — flag in context)
\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b    # CNPJ formatted
```

### Private key blocks
```
-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
```

---

## False Positive Heuristics

Do NOT flag if the value:
- Is clearly a placeholder: contains `your_`, `<`, `>`, `example`, `placeholder`, `xxxx`, `****`, `TODO`, `CHANGEME`
- Comes from an environment variable reference: `os.environ`, `process.env`, `${VAR}`, `$VAR`
- Is in a comment explaining what a key looks like (documentation)
- Is in a test file using obviously fake data (e.g., `test_secret_abc123` in `*_test.*` or `*spec*`)

---

## Risk Levels

| Level | Action |
|---|---|
| **High** — real-looking secret or PII in a non-test file | Pause, show the finding, ask user explicitly whether to proceed |
| **Medium** — sensitive filename outside `.gitignore` | Warn and ask |
| **Low** — possible false positive, uncertain context | Mention briefly, continue unless user says stop |
