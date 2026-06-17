# イベント入力

## 1. token usage 更新

#### 入力元

```text
thread/tokenUsage/updated
```

#### 正規化後データ

| field | 必須 |
|---|---|
| `threadId` | yes |
| `inputTokens` | yes |
| `outputTokens` | yes |
| `updatedAt` | yes |

#### field 正規化

| 正規化後 | 入力候補 |
|---|---|
| `inputTokens` | `input_tokens`, `inputTokens`, `input` |
| `outputTokens` | `output_tokens`, `outputTokens`, `output` |

`cached_input_tokens` は使わない。

---

## 2. turn 完了

#### 入力元

Codex `notify` の `agent-turn-complete`。

#### payload

| field | 必須 |
|---|---|
| `type` = `agent-turn-complete` | yes |
| `thread-id` | yes |
| `turn-id` | yes |
| `cwd` | no |
| `last-assistant-message` | no |

---

## 3. PR 作成完了

#### 入力元

PR 作成完了 hook。

#### payload

| field | 必須 |
|---|---|
| `type` = `pull-request-created` | yes |
| `repoRoot` | yes |
| `prNumber` | yes |
| `prTitle` | yes |
| `targetBranch` | yes |
| `prBranch` | yes |
| `additions` | yes |
| `deletions` | yes |
| `prUrl` | no |
