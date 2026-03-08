# Proposal Review

Present improvement proposals to the user for accept/reject/modify decisions.

## Inputs

Read:
1. `.dominion/phases/{N}/review.toml` `[[proposals]]` — current phase proposals
2. `.dominion/improvements.toml` — historical proposals (filter out re-proposals of rejected items)

## Filtering

Before presenting:
1. Remove proposals whose title closely matches a previously rejected proposal in improvements.toml
2. Remove proposals for changes that are already implemented (status = "accepted" with applied_at set)

## Presentation

For each remaining proposal, present:

```
Proposal {id}: {title}
  Type: {type}
  Evidence: {evidence list}
  Reason: {reason}

  [Accept / Reject / Modify]
```

- **Accept**: mark as accepted in improvements.toml, queue for apply in Step 3
- **Reject**: mark as rejected in improvements.toml with reason (ask user for brief reason)
- **Modify**: ask user how to modify, update the proposal text, then accept

## Record Decisions

For each proposal, write to `.dominion/improvements.toml`:
- Copy all fields from review.toml proposal
- Add `phase` = current phase number
- Set `status` = "accepted" or "rejected"
- Leave `applied_at` and `applied_by` empty (filled in Step 3 for accepted proposals)

## Summary

After all proposals reviewed:
```
Proposals: {accepted} accepted, {rejected} rejected, {modified} modified
```

If no proposals exist:
"No improvement proposals from this phase's review. Proceeding to knowledge management."
