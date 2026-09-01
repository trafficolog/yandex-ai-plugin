# Safety policy

All consequential work follows:

`read → analyze → preview → explicit approval → write → verify`

## Read-first

Read counters/goals/report context before proposing configuration changes. For imports, inspect the file before upload. For Logs, evaluate feasibility before create when quota/size is uncertain.

## Approval-gated writes

- create/update counters and goals
- create Logs requests
- offline conversion/call/expense uploads

## Destructive actions

Counter/goal deletion and Logs `clean` require explicit confirmation. Never infer destructive approval from requests such as “optimize”, “clean up”, or “fix”.

## Expense guard

Do not manually import Yandex Direct expenses. Direct sends cost data automatically; duplicate import makes reporting incorrect.

## Secrets and data

Never echo OAuth tokens. Avoid printing raw Logs/API datasets into chat; save full exports as files and summarize compactly.
