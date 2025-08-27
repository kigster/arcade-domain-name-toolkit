# What Is Arcade.dev?

Arcade.dev is a developer platform that enables AI agents to perform real-world tasks—like sending emails, accessing calendars, or interacting with GitHub—through **authenticated, reusable "tools"**. These tools are pre-built integrations that handle the complexity of secure access and execution, allowing your AI to *act*, not just *chat* :contentReference[oaicite:1]{index=1}.

---

## Why This Matters for AI Developers

- **Unified Interface**  
  Whether it's Gmail, Slack, GitHub, or custom services, Arcade gives you a single point of interaction. You avoid juggling multiple OAuth flows and API wrappers :contentReference[oaicite:2]{index=2}.

- **Security & Authentication Handled**  
  Arcade manages OAuth, API keys, token refreshes, and required scopes. Your agent only asks for what it needs—and Arcade guides the user to authorize it :contentReference[oaicite:3]{index=3}.

- **Clean, Maintainable Code**  
  Tool definition and invocation are separate from your AI logic. The LLM triggers actions via Arcade, not direct API calls built by hand :contentReference[oaicite:4]{index=4}.

- **Extensible**  
  Use existing toolkits or create and publish your own through Arcade’s SDK and CLI :contentReference[oaicite:5]{index=5}.

---

## High-Level Architecture

```plantuml
@startuml
actor User
participant Agent
participant ArcadeEngine
participant ThirdPartyService

User -> Agent: "Send meeting invite"
Agent -> ArcadeEngine: Calls GoogleCalendar.CreateEvent (with user_id)
ArcadeEngine -> ThirdPartyService: OAuth + API call
ThirdPartyService --> ArcadeEngine: Confirmation
ArcadeEngine --> Agent: "Event scheduled"
Agent --> User: "Meeting scheduled for Tuesday, 3 PM"
@enduml
````

* **User**: Initiates a request (e.g. "Send meeting invite")
* **Agent**: AI that determines which tool to call
* **Arcade Engine**: Manages tools, authentication, and execution
* **Third‑Party Service** (e.g., Gmail, GitHub): Performs the real-world action

---

## Available Toolkits & Their Reach

Arcade offers official, verified, and community toolkits across many domains:

* **Developer Tools**: GitHub, Firecrawl (web scraping)
* **Productivity & Docs**: Gmail, Google Drive, Sheets, Docs, Slides, Notion, Outlook, Jira, Linear, Asana, Dropbox
* **Communication**: Slack, Discord, LinkedIn, X (Twitter), Teams, Zoom
* **Media & Entertainment**: Spotify, Twitch, YouTube
* **Search & Data**: Google Search, Maps, News, Finance, Shopping, Flights, Jobs; Walmart
* **Business & CRM**: HubSpot, Salesforce, Zendesk
* **Databases**: Postgres, Clickhouse
* **Payments**: Stripe ([Arcade Docs][1], [Arcade Docs][2], [Arcade Docs][3])

---

## What Each Toolkit Offers—and Sometimes Doesn't

For every toolkit, Arcade provides a curated set of tools—specific operations you can programmatically invoke via Arcade.

**Example: GitHub Toolkit**
It includes tools like `ListPullRequests`, `GetRepositoryInfo`, and `SetRepoStars`. However, it **does not** include crucial operations like **CreatePullRequest**, which may be a significant limitation depending on your workflow ([WorkOS][4]).

**Why might a key function be missing?**

* It may be pending development, or
* It may have been omitted due to complexity, security concerns, or demand prioritization.

As you evaluate each toolkit, it's worth asking:
*Does it support the operations I need? If not, can I create custom tools to fill those gaps?*

---

## Building Your Own Custom Toolkit

Arcade makes it straightforward to define your own tools and deploy them:

1. Use the Arcade CLI to scaffold a toolkit template.
2. Define tools (e.g., arithmetic operations or domain-specific actions).
3. Test locally with Arcade’s development tools.
4. Publish and register it to use with agents. ([Arcade Docs][5], [Arcade Docs][6], [Arcade Docs][3])

Arcade supports a seamless local-to-cloud development flow—so you can mix in-house, private, and public tools in a single agent.

---

## Key Developer Benefits Summary

| Feature                       | What It Means                                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Simple agent architecture** | You separate AI logic from tool execution.                                                                                                                   |
| **Secure auth flows**         | OAuth and user permissions are managed for you.                                                                                                              |
| **Extensive integrations**    | Broad coverage across productivity, communication, data, search, etc.                                                                                        |
| **Customizability**           | Build, test, and deploy your own toolkits.                                                                                                                   |
| **Hybrid deployments**        | Run Arcade in the cloud, on-prem, or use a hybrid approach ([Arcade Docs][7], [GitHub][8], [Arcade Docs][9], [developers.arcgis.com][10], [Arcade Docs][6]). |

---

## Final Thoughts (Plain-Language Summary)

Arcade is like a smart connector between your AI and the apps or data you care about. Instead of telling your AI to craft API requests for Gmail, GitHub, or Slack—and deal with logins and tokens—Arcade provides ready-made, secure tools. Your agent just says, "Use the Google.SendEmail tool," and Arcade handles the rest. If Arcade doesn't include a tool you need (like "create a GitHub PR"), you can build it yourself, and Arcade makes deployment easy.

---

## What Might Be Missing or Warrant Further Review

* **Coverage vs. Completeness**: Some toolkits lack key features (e.g., GitHub.CreatePullRequest). You'll want to review each needed integration critically.
* **Documentation Depth**: You'll need to systematically review every toolkit’s detailed reference pages to list tool names and scopes. (Suggested next step: retrieve tools per toolkit via the API or tool list endpoints.)
* **User Experience Details**: Are scope prompts smooth? Can users connect multiple accounts? Some capabilities depend on configuration or provider support ([Arcade Docs][11], [Arcade Docs][6]).
* **MCP & Agent Framework Compatibility**: Arcade supports the Model Context Protocol and integrates with frameworks like LangGraph, OpenAI Agents, or LangChain via conversion tools ([Arcade Docs][12]).

---

That completes the initial draft of `ARCADE.md`. It’s designed for clarity, accessibility, and practicality, with room to expand once you gather the granular details of each toolkit's tool list and limitations.

Let me know if you'd like me to help extract tool lists from specific toolkit documentation or diagram key workflows in more depth!

[1]: https://docs.arcade.dev/home/auth/how-arcade-helps?utm_source=chatgpt.com "How Arcade helps with Agent Authorization"
[2]: https://docs.arcade.dev/toolkits?utm_source=chatgpt.com "Arcade Toolkit"
[3]: https://docs.arcade.dev/?utm_source=chatgpt.com "Arcade Docs - Arcade.dev's"
[4]: https://workos.com/blog/what-is-arcade-dev-an-llm-tool-calling-platform?utm_source=chatgpt.com "What is Arcade.dev? An LLM tool calling platform"
[5]: https://docs.arcade.dev/home/build-tools/create-a-toolkit?utm_source=chatgpt.com "Creating a Toolkit"
[6]: https://docs.arcade.dev/home/faq?utm_source=chatgpt.com "Frequently Asked Questions - Arcade Docs"
[7]: https://docs.arcade.dev/home/hosting-overview?utm_source=chatgpt.com "Hosting Overview"
[8]: https://github.com/ArcadeAI/arcade-ai/blob/main/README.md?utm_source=chatgpt.com "README.md - ArcadeAI/arcade-ai"
[9]: https://docs.arcade.dev/home/quickstart?utm_source=chatgpt.com "Start using Arcade"
[10]: https://developers.arcgis.com/arcade/?utm_source=chatgpt.com "Introduction | ArcGIS Arcade - Esri Developer"
[11]: https://docs.arcade.dev/home/oai-agents/use-arcade-tools?utm_source=chatgpt.com "Use Arcade with OpenAI Agents"
[12]: https://docs.arcade.dev/home/langchain/use-arcade-tools?utm_source=chatgpt.com "Use Arcade tools with LangGraph"

