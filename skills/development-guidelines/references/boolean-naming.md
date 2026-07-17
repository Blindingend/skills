# Boolean naming

Make each Boolean name read like a question that can be answered directly with `true` or `false`. Name the proposition, not the storage type.

## Choose the semantic prefix

- Use `is` for a state or condition, followed by an adjective: `isActive`, `isDeleted`, `isEmpty`.
- Use `has` for possession, presence, or containment, followed by a noun: `hasAccess`, `hasChildren`, `hasValidationErrors`.
- Use `can` for capability or permission, followed by a verb: `canEdit`, `canDelete`, `canRetry`.
- Use `should` for intent, policy, or a decision produced by logic, followed by a verb: `shouldRetry`, `shouldCacheResponse`.

Choose by meaning rather than grammar alone. Use `canRetry` when retrying is allowed or possible. Use `shouldRetry` when the program has decided that retrying is the correct next action.

## Prefer positive propositions

Name the normal proposition so that `true` means the named condition holds.

- Prefer `isEnabled` and represent the disabled state as `isEnabled == false`.
- Avoid grammatical negation such as `isNotReady`, `hasNoOwner`, and `cannotEdit`.
- Avoid inverse names that make call sites read as double negatives, such as `if (!isDisabled)`.
- Keep a negative domain state such as `isDeleted`, `isEmpty`, or `hasValidationErrors` only when it is the concept the program actually models. Do not invent an awkward opposite that changes the meaning.

## Replace vague names

Do not use names that only reveal the representation:

| Avoid | Prefer | Reason |
| --- | --- | --- |
| `flag` | `isActive` | Names the state. |
| `accessFlag` | `hasAccess` | Names the relationship. |
| `editStatus` | `canEdit` | Names the permission. |
| `retryFlag` | `canRetry` or `shouldRetry` | Keeps capability and decision distinct. |

Apply the same rules to predicate functions. Prefer `isEmpty()`, `hasAccess()`, `canEdit()`, and `shouldRetry()` over `checkEmpty()` or `getRetryFlag()` when the return value is Boolean.

## Review the call site

Read representative uses aloud:

```text
if (isEnabled)
if (hasAccess)
if (canEdit)
if (shouldRetry)
```

Reject the name if the call site does not state one unambiguous proposition, or if `true` and `false` require extra explanation.
