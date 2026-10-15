# Constitution Prompt v1.2

Input for `/speckit-constitution`. This prompt adds architectural constraints and updates the constitution to v1.2.0.

/speckit-constitution

Update the Lab-4 Constitution to version 1.2.0.

## Application

The application is a college management web service built with Python 3.12, Flask, and SQLite.

## Architecture

The system follows hexagonal architecture.

- Domain rules remain independent of frameworks and infrastructure.
- Application use cases coordinate business operations through explicit ports.
- Inbound adapters translate external requests into application commands or queries.
- Outbound adapters implement persistence and other infrastructure concerns.

Keep HTTP routes thin. Business rules MUST NOT be implemented in Flask routes or SQLite adapters. Persistence access goes through repository ports, and transaction boundaries MUST preserve domain invariants.

Maintain clear boundaries between the student, course, programme, and inscription capabilities. A feature's design MUST respect existing boundaries rather than introducing unnecessary coupling.

Prefer existing project conventions and minimal external dependencies. Do not introduce new architectural patterns, frameworks, or infrastructure without a demonstrated need.

Design questions that these constraints do not settle MUST be clarified with the architect rather than decided autonomously.

## Preservation

Preserve all existing business principles.

Amend the governance limit that currently excludes architecture, implementation technologies, and engineering practice only as far as needed to record these constraints. Do not remove or redefine the existing business principles, domain vocabulary, or feature-specification requirements.

## Limits

Do not modify application code or create a Git commit.
