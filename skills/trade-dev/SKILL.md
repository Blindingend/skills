---
name: trade-dev
description: Use when implementing or reviewing trading-system code involving trade dates, offline replay, backtests, online market data, or date configuration.
---

# Trade Development Conventions

Apply the relevant trading-system conventions in this skill. Treat explicit user requirements and established repository contracts as higher priority.

## Trading date

Trading-system programs must have an explicit concept of the current trading date. Resolve it once for the relevant run or task, then use that value consistently instead of deriving dates independently in different components.

Use this resolution contract:

| Input | Current trading date |
| --- | --- |
| A trading date is specified | Use the specified trading date |
| No trading date is specified | Use the current date |

Apply the contract by mode:

- Offline replay and backtest callers should normally specify the trading date explicitly so the requested dataset and run are unambiguous. The program-level fallback remains the current date when no value is provided.
- Online services normally omit the trading date and use the current date because each day's online run belongs to that day. An explicitly supplied value still takes precedence.

Do not silently replace this contract with a different policy, such as selecting the latest available dataset, requiring an exchange calendar, rejecting an online override, or treating an omitted offline date as an error. Introduce exchange-specific calendars, holiday handling, night-session ownership, time-zone rules, or cross-midnight switching only when the repository contract or current requirement defines them.

## Extending these conventions

Add new trading-system conventions only after the user establishes them. Keep them in this skill while the set remains short; split them into focused references or sub-skills when loading the whole skill would introduce substantial unrelated context.
