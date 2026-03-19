# Database Engineering Protocol

## Schema Analysis

Before modifying any schema:
1. Use serena to find ORM models, repository patterns, migration files
2. Understand current access patterns — what queries run against these tables?
3. Check index usage — unused indexes waste write performance
4. Review foreign key constraints and cascade rules

## Schema Design

1. **Normalize first, denormalize with evidence** — 3NF baseline, denormalize only when query performance data justifies it
2. **Design for access patterns** — the schema serves the application, not abstract data modeling
3. **Constraints at DB level** — NOT NULL, CHECK, UNIQUE, FK constraints. Don't rely on application-level validation alone.
4. **Data types matter** — use the most specific type (TIMESTAMPTZ not VARCHAR for dates, UUID not BIGINT for distributed IDs)

## Migration Authoring

1. **Forward and rollback** — every migration must be reversible. Write the down migration before the up.
2. **Zero-downtime** — for production databases:
   - Add columns as nullable first, backfill, then add NOT NULL
   - Create new indexes CONCURRENTLY
   - Never rename columns directly — add new, migrate data, drop old
3. **Test the chain** — run all migrations from scratch AND from current state. Both must work.
4. **One concern per migration** — don't mix schema changes with data migrations

## Query Optimization

1. **EXPLAIN ANALYZE first** — understand the execution plan before optimizing
2. **Index design** — composite indexes match query WHERE/ORDER patterns. Column order matters.
3. **N+1 detection** — ORM queries that loop are N+1 candidates. Use eager loading or batch queries.
4. **Connection pooling** — configure pool size based on concurrent load, not max connections
