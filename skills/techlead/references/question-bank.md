# Question Bank

Use this bank to run the TechLead interview. Ask at most five questions per round. Prefer structured multiple-choice questions when the host supports them. Otherwise ask numbered questions and wait for the answers.

Do not read the entire bank to the user. Select the next questions that reduce the most uncertainty. Cover every category before writing the PRD. When a category does not apply, record why in the PRD instead of skipping it silently.

## Round 1: Problem, users, and outcome

### Product idea

- What is the project called?
- Describe the idea in one sentence.
- What concrete problem does it solve?
- Why is this worth solving now?
- What happens if the team does nothing?

### Users and jobs

- Who is the primary user?
- Who are the secondary users and operators?
- What are the top three jobs the user needs to complete?
- What do users do today instead?
- What makes the current alternative painful or expensive?

### Success

- What measurable outcome proves the project worked?
- What is the target value and the measurement window?
- Which metric must not get worse?
- What is the smallest release that would be useful?

## Round 2: Scope and behavior

### Scope

- Which capabilities are must-have for the first release?
- Which capabilities are explicitly out of scope?
- What can be deferred without breaking the core promise?
- Which existing systems, teams, or contracts constrain the scope?

### Functional behavior

- Walk through the primary user journey from start to finish.
- What are the most important alternate and failure paths?
- What data does the user create, read, update, or delete?
- What must an administrator or operator be able to do?
- Which actions are destructive and need confirmation, audit, or recovery?

### Rules and edge cases

- Which business rules decide whether an action is allowed?
- What are the limits: size, count, rate, time, quota, or concurrency?
- What should happen on duplicate input, partial failure, timeout, or retry?
- Which states and transitions does the domain have?

## Round 3: Data, security, and integrations

### Data

- Which entities and relationships does the product need?
- What is the source of truth for each important piece of data?
- How long is data retained?
- What must be exportable or deletable?
- Is there personal, financial, health, or otherwise sensitive data?

### Authentication and authorization

- Who needs an account?
- How do users authenticate?
- Which roles and permissions exist?
- What must be audited?
- How are sessions revoked?

### Integrations

- Which external services, APIs, webhooks, or files are involved?
- What happens when an integration is unavailable?
- Are there rate limits, costs, or contractual constraints?
- Which events must be idempotent?

### Security and compliance

- Which threats matter most for this product?
- Are there regulatory or contractual requirements?
- Where will secrets live?
- What is the backup, restore, and incident-response expectation?
- What must be logged, and what must never be logged?

## Round 4: Technology, quality, and delivery

### Architecture and stack

- Is there an existing stack or platform the project must use?
- What are the expected traffic, data volume, and growth?
- Which latency, availability, and recovery targets apply?
- Is the system a web app, API, worker, CLI, mobile app, or a combination?
- Which build, package, and deployment constraints apply?

### Quality

- Which test levels are required: unit, integration, end-to-end, contract, performance, accessibility?
- What is the coverage gate? The default is at least 80 percent.
- Which browsers, devices, or clients must be supported?
- Which accessibility or internationalization requirements apply?
- Which quality checks must block a release?

### Delivery and operations

- Who operates the product after launch?
- What is the expected release cadence?
- Which CI/CD platform is available?
- What are the VPS provider, region, CPU, memory, disk, and network constraints?
- Is there a domain and TLS requirement?
- What are the backup, monitoring, alerting, and on-call expectations?
- What is the rollback strategy?
- Are there budget or deadline constraints?

### Risks

- What is the biggest technical risk?
- What is the biggest product or adoption risk?
- Which dependency is most likely to fail?
- What would make the team stop or reshape the project?

## Decision rules

- Prefer measurable answers over adjectives. Replace "fast" with a latency and percentile. Replace "secure" with a threat and control. Replace "many users" with a volume and growth assumption.
- When the user does not know, propose two or three concrete options with trade-offs and ask the user to choose.
- When the user delegates the decision, record it as an assumption and ask for approval at Gate 3.
- Do not ask about technology before the problem, users, and scope are clear.
- Do not ask more than five questions at once. Group related questions.
- Do not repeat a question that the repository or a previous answer already answers.
- Do not infer a requirement from silence. Mark it as an assumption or an open decision.
- Stop when the remaining questions would not change the scope, architecture, acceptance criteria, or definition of done.

## Minimum coverage before writing the PRD

Record an answer or an explicit non-applicability note for:

- problem and product promise;
- primary users and jobs;
- measurable success criteria;
- must-have and out-of-scope scope;
- primary flow and critical failure paths;
- data and retention;
- authentication and authorization, or why they do not apply;
- external integrations, or why they do not apply;
- security, privacy, and compliance;
- stack and architecture constraints;
- quality targets and the coverage gate;
- local/test Docker approach;
- production/VPS approach;
- deployment, rollback, backup, and monitoring;
- risks and open decisions.
