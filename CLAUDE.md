# Arcade Interview Problem

This repo contains several projects that demonstrate the functionality and the SDK of the Arcade.dev's toolkits and other APIs. 

This is top-level of the mono-repo containing a couple of projects, serving different purpose each.

 * `problem` — contains the [original PDF with the interview problem statement](problem/problem-statement.pdf)
 * `client_js_setstars` — is a standalone client tool, which serves as an example of using Arcade.dev's Toolkits (`Github` and `Math`) and within it a single tool each (`Github.SetRepoStars` and `Math.Sqrt` respectively).
 * `client_py_getrepo` - a simple python client that similarly authenticates against YOUR Github account, and then prints information about a specific repo `kigster/githuh` — which is a simple ruby gem repo that has tests, but no CI/CD setup with Github Actions.
 * `toolkit` - the custom toolkit that's been scaffolded using the `arcade new` command (to be created after we decide what the toolkit does)
 * `app` - the app that utilizes the toolkit to perform something interesting (to be created after we choose the purpose of this app/toolkit combo)

## Running Existing Examples

1. Create an API key here: https://api.arcade.dev/dashboard/api-keys
2. Store it in `.env` file in this project (we alredy have one)
3. If using `direnv` run `direnv allow .` to load the value into the environment.

Verify that `$ARCADE_API_KEY` is set, and if not source `.env` to get it set.

You should be able to execute a command `make run` from the top level `Makefile`, which will then go into each of the following example projects and run them:

 * `client_js_setstars`
 * `client_py_getrepo`

It will run each project by issuing `make run` inside each folder, which should install all the dependencies and execute the calls.

## Few Rules Before We Start

1. Write all markdown documents using professional style and without any emojis ever.
2. If something can be effectively explained by a diagram, please use https://plantuml.com/ to generate a textual diagram and insert it into the markdown (Github supports it). For example, here is a sequential UML diagram: https://plantuml.com/sequence-diagram. 
3. Use UML diagrams as much as makes sense, but remember if a diagram is too complicated it might not be that useful. But for showing movement of data, or authentication process via OATH, those are ideal candidates for the diagrams.

And this file contains instructions for Claude agent, so that it can assist in completing this assignment within a reasonable timeframe.

## What is this repo about?

This repo already contains working examples of code that uses Arcade.dev's SDK to authenticate client code only with Arcade, and use Arcade Toolkit's OATH links to grant whatever local script/code we are running, and that's using Arcade API to access another third party application. The third party application can be one of Github, Asana, Dropbox, Gmail, Google Calendar, and many more. 

Arcade.dev issued us a working API key (stored in the `.env` file, and git-ignored), and that's all we need to request authentication link for each of the OAth-supported services on their list — https://docs.arcade.dev/toolkits

## What is our first task?

The first part of this project is learning as much as possible about everything that Arcade.dev does and offers, their existing integrations, how they are built, can they be extended, and so on. We are going to consume a systematic list of web pages that will provide our AI Agent with information about all parts of the documentation.

We are going to learn about Arcade.dev offering from the following sources in two parts:

1. Please research in depth what Arcade.dev does and how they fit into the current AI/Agentic industry. As part of that exploration, please visit the following URLs at the very least:
    * https://docs.arcade.dev/ — the main documentation website
    * https://www.arcade.dev/#whatisarcade
    * https://docs.arcade.dev/toolkits — list of existing toolkits
    * Please visit every toolkit's details page and save the list of "tools" available — i.e. the actual methods offered by a particular service. For example, Github's toolkit offers only 16 "tools" (or API calls to Github) that can be authenticated via Arcade. However, notice that a very useful `Github.CreatePullRequest` tool does not exist for some reason. So using `Github` toolkit as it is today you can not create pull requests of any repo, or can you push any code.You can commend, review, list and read pull requests, but not create them.
    * https://www.arcade.dev/apps/build-an-ai-agent-for-gmail — example agent for Gmail
    * https://reference.arcade.dev/api-reference — Arcade's API reference documentation
    * https://github.com/orgs/ArcadeAI/repositories — Arcade's public repositories that can provide some answers and have some useful examples we might need later.

2. To step this up a notch, here is the XML file containing every single page of their site: https://docs.arcade.dev/sitemap-0.xml — Please consume this file, and then for each URL mentioned there, connect to it,  read its contents and keep doing so until all pages have been consumed and read. At this point, we should be able to provide a very rich and complete summary of what Arcade.dev is doing, how it fits into the landscape of AI companies, what the primary use-cases are for using them as a platform. 

> [!NOTE]
> We are not doing a market fit or market research analysis here. We are evaluating this from a point of view of an AI developer who wants to build complex workflows using multi-agentic applications that leverage many third party services.

* [ ] Task 1: Create ARCADE.md file that explains what the offering is in a much more accessible and easy to understand way, and uses diagrams to get the point across. It should also list existing toolkit integrations, and their API calls, emphasizing that some of the critically important functions may be missing from the toolkit's API. For example, [Github's toolkit](https://docs.arcade.dev/toolkits/development/github/github) offers 15 "tools" (or API calls), but among them there is no `CreatePullRequest`, which is a key operation one might want to perform on Github. Is it missing because they didn't get time to build it yet, or is it missing because of some other technical reason? So for each service it would be good to critically think what their main operations/engagements are and whether they are sufficiently well represented by Arcade's toolkit for that service.

To summarize task No 1: Let's capture what we learned in the file at the top project level, called ARCADE.md. This file should include all the information on their technology, their offering explained in simple terms only as if the reader is a non-programmer. Why do this? I found their language around "building toolkits" and "tools" a bit confusing: on the Integrations page toolkits map one-to-one with third party companies that they have implemented OATH with. We need to cut through the thick fog of technical documentation to extract something that's easy to understand and reason about, something that should be easy to read and understand. What existing problem are they solving today? Is the problem big enough that people complain about it? If so, do they know Arcade exists? What's the path to dominance? That and everything else above — please capture as a succinct summary professionally written into ARCADE.md document that we'll use moving forward as a reference of their abilities and limitations.

## Second Task

This task is the interview question and is described for us to complete is in a parsable PDF file[problem-statement.pdf](problem/problem-statement.pdf).

1. We will use their `arcade new` command to create a scaffold for a new toolkit. It appears these are Python only, so we'll use `uv` command (pre-installed) described here: https://docs.astral.sh/uv/guides/install-python/ to install python and to run our commands.

2. Can application be written in Ruby, and still somehow access Arcade SDK (JS or Python) to authenticate, and do other things too? Since I am more comfortable with Ruby it would be a win if we could use their JS or Python SDK from inside of a Ruby application. 

3. We will build an app as part of that toolkit that will use the toolkit to do something useful. The application (if it requires Arcade's SDK), we know can be written in TypeScript, so if it can not be done in Ruby (see previous question) we'll do it in TypeScript. Automated tests are not optional for all the code we create.

**Having answered these questions, I would like for you to contemplate and come up with top ten creative but practical ideas for the new toolkit(s) and an application relying on them, so that it had a "wow" factor, but wasn't too difficult to implement.**

Please create a markdown file IDEAS.md where you will list your ideas and explain what each does, what third party services it calls, what does our custom toolkit need to implement, etc. Use UML diagrams where helpful.

I wanted to provide you with the list of services that I personally have an active account on and so a tool that uses one or several of these tools can be pretty useful to do, and we can prioritize these services above others:

 * Gmail
 * Google Calendar
 * Github
 * Google Docs
 * Dropbox
 * Google Maps
 * Google News
 * Google Sheets
 * Google Search
 * Google Jobs
 * LinkedIn
 * Notion
 * Reddit
 * Slack
 * Spotify
 * Stripe
 * X
 * YouTube Search
 * Discord
 * Jira
 * PostgreSQL
 
## Application Proposal 1: Github Workflow Toolkit

IN addition to your ten ideas I am going outline just one my idea next. You must evaluate it on feasibility.

Now, let me describe you my idea. It might require the `Github.CreatePullRequest` tool that doesn't exist, but maybe we can find a clever workaround, or build an additional toolkit `GithubContrib` and add new functions there. We may need to add calls to create forks of public repos, make local modifications and push them pu as a pull request.

The application I would like to build's goal is the following:

 * given the Github Repo URL (or username/repo pair), and assuming it's accessible, forkable, and downloadable, identify that it's a software with either tests or linting, or something that can be run on CI to validate this repo. If the repo already has Github Actions or `.github/workflows` folder — report that fact and refuse to continue. 
 * If the repo is determined to be software with tests included or lint configuration included (eg, `.rubocop.yml`) we should be able to:
  1. git clone this repo locally (but see if we can determine repo size ahead of time — and if so, max download size is 1Gb)
  2. create a branch `arcade-dev/github-actions`
  3. Drop `.github/workflows/ci.yml` in the project appropriate for the type of project it is, but before that ensure that the tests can be run locally. They don't need to pass locally, just started.
  4. We push this change up either as PR to the original, or we fork the original repo and push the PR to our fork. If it's our fork, we should be able to see if the action passes or fails. Would be good to attempt to iterate a bit on making the CI pass, but limit this to about 15 minutes of your time.

I suspect that this application may be too complicated and too difficult to do considering the existing Github toolkit doesn't suppose many of the operations we must perform ourselves. 

## Application Proposal 2: Auto-Answer my LinkedIn Messages

This application relies on LinkedIn Toolkit that can do more than just create a text posting: https://docs.arcade.dev/toolkits/social-communication/linkedin

Here is how this would work:

The application can be run as a CLI, and I can pass it a flag telling it whether or not I am currently interested in hearing about new positions, or not. The tool can read by convention a default response when I am not looking for a position AND when I am looking for a position, or those files can be passed via CLI flags. If I am in the "looking for work mode", for each unread message in my inbox, if this is a recruiter, analyze how the message matches my linked in profile and if the job is within my parameters, respond positively — with the template provided, possibly adding something specific about this opportunity. 

If I am not looking for work, politely decline but say that it wuold be great to stay in touch.