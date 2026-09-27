### Overview

You're building a small backend service called MeterPay, your role at bigfunnel is to build a service that sells access to a metered API. Customers prepay into a wallet; every time they call the metered endpoint, a fixed fee is deducted from their wallet balance. If the balance can't cover the fee, the call is rejected instead of served. <br/>

That's the whole scenario. This is assignment is kept generic — no messaging platform, no third-party payment integration, no multi-tenant infrastructure. We're not testing whether you can wire up a payment gateway; we're testing how you design and reason about a shared, mutable balance that many requests can hit at once, and how honestly you handle the moment it runs out.

### Requirements
Build a small service (any language/framework you're comfortable with) that supports:
1. **Create account** — a new customer starts with a balance of 0.
2. **Top up** — add a specified amount to an account's balance.
3. **Consume** — call the metered endpoint on behalf of an account. Each call costs a fixed fee (exactly ₹0.10 per call — use this value so every ledger is directly comparable). If the balance covers it, deduct the fee and let the call succeed. If it doesn't, reject the call with a clear error and leave the balance untouched.
4. **Check balance** — return an account's current balance.
5. **Transaction history** — return a list of every top-up and every consume for an account, in order, in a form that lets someone reconstruct how the current balance was reached.

We're evaluating the APIs, not a UI. Expose each of the five operations above as a backend API. A frontend is optional and not required. Document every endpoint (method, path, request, response, and error cases) in the README, or include a Postman collection in the repo. <br/>

The part we care about most: requirement 3 under concurrency. If 50 consume calls hit the same account at once and only 30 of them can be afforded, exactly 30 should succeed and 20 should be cleanly rejected — the balance should never go negative and should never lose or double-count a deduction. Demonstrate this (a test, a script, whatever you like) rather than just asserting it in the README.

### Explicitly out of scope

- Authentication / authorization (assume every request is already trusted)
- A real payment gateway (top-up is just an API call that credits the balance — no Stripe/Razorpay integration)
- Multiple tenants, teams, or roles (one flat set of accounts is fine)
- A UI (a CLI, a Postman collection, or just curl examples in the README is enough)
- Retries, notifications, rate limiting, or an admin dashboard

### Deliverables
- A fork of the take-home repository [REPO LINK] with the service's code committed to it — share the link to your fork when you submit
- A README with: how to run it, how to run the concurrency test, and a short "design notes" section — your data model, why you chose it, and how you'd change it if this had to run across many independent customers instead of one shared account table


**NOTE:** We're not grading language/framework choice, visual polish, or how many endpoints you added beyond the five above.
