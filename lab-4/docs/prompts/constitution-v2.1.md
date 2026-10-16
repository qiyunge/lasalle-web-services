# Constitution Prompt v2.1

Input for `/speckit-constitution`. This prompt adds and tightens architecture and domain-modeling constraints and updates the constitution to v2.1.0.

/speckit-constitution

Update the Lab-4 Constitution from version 2.0.4 to version 2.1.0.

This is a minor bump. It adds domain-modeling, boundary-validation, type-isolation, dependency, and package-organization constraints, and it tightens the existing architecture principles. It does not remove a business invariant, an engineering requirement, or a quality gate.

Replace the Sync Impact Report at the top of the constitution so it describes this amendment.

Where a statement below restates an adopted architecture principle, amend that principle in place. Do not keep a duplicate rule.

## Preservation

Preserve all existing business invariants, engineering requirements, quality gates, gap-governance rules, and the domain vocabulary.

Preserve the feature-specification requirements.

The Domain Layer remains free of third-party packages, frameworks, persistence, and transport. The existing allowance for the Python standard library stays in force. "External libraries" in the principles below means third-party and infrastructure libraries.

## Core Architecture & Domain Modeling Principles

### 1. Core Architecture

The system MUST adopt a **Full Bridge Hexagonal Architecture**, with the Core consisting of two layers:

- **Application Layer:** Owns use cases, business orchestration, application workflows, and inbound/outbound ports. MAY use external libraries.
- **Domain Layer:** Owns domain models, business behavior, and domain invariants. MUST remain independent of external libraries and infrastructure frameworks.

Adapters MUST communicate with the Core through explicitly defined ports and boundary mappings. Dependencies MUST point inward.

### 2. Domain-Driven Design (DDD)

The Domain Layer MUST follow DDD tactical modeling principles, including:

- Entities
- Value Objects
- Aggregates and Aggregate Roots
- Domain Services
- Domain Events
- Domain Factories
- Domain Policies / Specifications

Domain behavior and business rules MUST reside in the appropriate domain models rather than being duplicated in Application handlers.

Aggregates MUST define and protect their consistency boundaries. DDD constructs SHOULD be introduced only when justified by actual domain requirements.

### 3. Domain Types and Value Objects

Domain-significant values MUST be represented by explicit domain types rather than unstructured primitives.

Value Objects MUST encapsulate their intrinsic invariants and prevent invalid instances from being created through supported interfaces.

Primitive types MAY be used internally within Value Objects, for domain-neutral implementation details, and at external boundaries.

Business rules MUST be assigned to their appropriate owners: Value Objects, Entities, Aggregates, or Domain Services.

### 4. Core Boundary Validation

All external inputs entering the Core MUST be validated and converted into appropriate domain types before being used in domain behavior.

Independent validation failures MUST be accumulated and returned together as a structured, non-empty collection of validation errors rather than failing fast.

Dependent validations MUST execute only when their prerequisites are valid.

Validation failures MUST use explicit typed results with stable error codes. Inbound adapters MUST translate validation results into transport-specific responses without duplicating domain rules.

### 5. Full Bridge Type Isolation

Independent architectural boundaries MUST use explicit type conversion to prevent external representations and infrastructure-specific types from leaking into the Core.

- Inbound Adapters: External DTOs → Core Commands / Domain Types
- Application → Domain: Direct use of domain types is permitted; redundant DTO conversion is NOT required.
- Core → Outbound Adapters: Explicit ports and boundary mappings
- Outbound Adapters → Core: Infrastructure data → Core-defined types

Internal Core interactions MUST NOT introduce unnecessary DTO layers.

### 6. Dependency Rules

- Domain MUST NOT depend on Application, Adapters, or infrastructure libraries.
- Application MAY depend on Domain and permitted external libraries, but MUST NOT depend on concrete Adapters.
- Adapters MAY depend on Core contracts and domain types.
- Composition Root MAY depend on both Core and Adapters for dependency injection and application assembly.

### 7. Package Organization and Semantic API Design

The project MUST maintain explicit architectural boundaries between `core/domain`, `core/application`, and `adapters`.

Package organization MUST balance development convenience, high cohesion, low coupling, domain semantics, and external API clarity.

Package and module names MUST accurately communicate their domain meaning, architectural responsibilities, and intended usage.

Public import paths MUST expose meaningful and stable domain or application concepts rather than unnecessarily revealing internal implementation details.

Internal implementation structures MAY be reorganized without affecting public contracts. Public API changes MUST be deliberate and their impact evaluated.

The AI agent MAY determine internal package structures during planning, but MUST preserve architectural boundaries, semantic correctness, and public API stability.

New packages and abstractions SHOULD be introduced only when they improve cohesion, clarity, maintainability, or meaningful encapsulation.
Directories SHOULD be introduced incrementally as actual domain complexity requires. Package organization MUST reflect architectural ownership and dependency boundaries, not impose unnecessary abstractions.

## Limits

These are project-wide architecture and domain-modeling constraints, not feature-specific implementation details.

Do not modify feature specifications, plans, task lists, or application code.

Do not create a Git commit.
