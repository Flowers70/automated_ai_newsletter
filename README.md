# Automated AI Newsletter

A pipeline that thinks in structured pieces but writes like a person.

The Automated AI Newsletter is a fully end‑to‑end system I built for a coding challenge after noticing how many AI newsletters feel fragmented and templated. This project pulls in fresh AI news, community gossip, and a daily GitHub repo, filters the noise, and uses AI‑driven synthesis to produce a cohesive, human‑readable markdown newsletter every morning — it’s an automation that thinks in logic but speaks in story.

## Setup

**Clone the Repo**
In your Command Prompt or Terminal navigate to the directory you want to clone the repository code into.\
Enter the following:
1. `git clone https://github.com/Flowers70/automated_ai_newsletter.git`
2. `cd automated_ai_newsletter`
3. `pip install -r requirements.txt`

**Environment Variables**
| Key | Description |
| --- | ----------- |
| Tavily_DEV | [Tavily](tavily.com) is a search engine | 
| Google_AI_Key | [Google AI](https://ai.google.dev/gemini-api/docs) is an AI |
| MISTRAL_API_KEY | [Mistral AI](https://docs.mistral.ai/admin/identity-access/api-keys) is an AI |
| OPENROUTER | [OpenRouter](https://openrouter.ai/) is an AI |
| NVIDIA_DEV | [NVIDIA](https://build.nvidia.com/settings/api-keys) is an AI |
| EMAIL_PASS | An app password for programmatic access to your email |
| EMAIL_USER | Your email or username |
| EMAIL_RECIPIENTS | The list of emails the newsletter will be sent to |
| SUPABASE_URL | [Supabase](https://supabase.com/) is the url to your cloud storage |
| SUPABASE_PRIVATE_KEY | The key that enables write and read access to your Supabase storage |

Create an .env file in the root of the project and create and/or enter the corresponding secret for each of the above environement variables. Be sure to use the key above as the variable name. If using [GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), create respository secrets.\
**WARNING:** Ensure that you keep these secret and don't upload them to your GitHub repo (use .gitignore). 🤫

To initialize the environment variables be sure to install and uncomment the parts concerning `dotenv`.

**Running Locally**
In your Command Prompt or Terminal ensure you are in the main directory of the automated_ai_newsletter.

Enter `python newsletter_generator.py`

This will generate a newsletter, email it to the recipients stored in the EMAIL_RECIPIENTS variable, and archive the edition in the 'newsletter_archive' folder.

**Running Automatically (GitHub Actions)**
The GitHub workflow file is stored in the '.github/worflows' folder in the main directory of this project and is titled 'newsletter.yml'. Within this yaml file is the cron schedule:

```
schedule:
    - cron: "30 3 * * *" # Time scheduled to run
```

By default this is set to run at 3:30 am (UTC) daily. Once this yaml file is uploaded to GitHub as is it will create a corresponding GitHub Action automatically. You can trigger this automatically by navigating to the Actions tab in your repository.

To add the secrets to your GitHub repository follow these [instructions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

## Architecture
This project follows a linear pipeline architecture, designed to run end-to-end every morning without human intervention. Each stage collects, transforms, and enriches data:

![Architecture Diagram](architecture_diagram.png)

### 1. AI News | Intake

Retrieves daily AI related articles using a search provider.\
Each result includes:
- Title
- url
- Content (summary of page contents)
- Relevance
- Publication Date
This stage provides the raw materials for the newsletter's "Big Story" and "Frontier Watch" sections.

Output: A list of AI-related articles published in the past day.

### 2. AI News | Transform

Processes and filters the raw articles:
- Classifies each article as news, analysis, or noise
- Discards noise
- Discards articles with insufficient relevant articles
- Normalizes each article, cleaning the scraped data using NLP (Natural Language Processing)
- Condenses each article into a summary for the final newsletter synthesis
- Extracts key information (e.g. title) for downstream synthesis
This ensures only corroborated and consequential articles enter the final newsletter.

Output: A vetted list of meaningful AI articles.

### 3. Gossip | Intake

Retrieves gossip from X and Reddit related to the vetted articles using a search provider.\
Each result includes:
- Title
- url
- Content (summary of page contents)
This stage provides the raw materials for the newsletter's "The Street Says" section.

Output: A dictionary of lists containing the specific pages of gossip for each social media platform.

### 4. Gossip | Transform

Processes the raw gossip capturing:
- Gossip
- Sentiment
- Drama
This provides a short summary concerning the gossip's sentiment for the final newsletter.

Output: Short summaries containing the overall sentiment of gossip for each social media platform.

### 5. GitHub | Intake

Fetches trending AI-related repositories from GitHub's public endpoint.\
This includes:
- Name
- url
- Description
- Homepage
- Stars
- Programming language
This stage obtains the raw data needed structured in a dictionary for the "Repo of the Day" section.

Output: A dictionary containing metadata on a meaningful AI-related GitHub repository.

### 6. Newsletter | Synthesis

Combines all the processed inputs into a single editorial markdown formatted newsletter.
A structured prompt generates the newsletter's five sections:
- The Big Story
  - The overarching story that emerges from the inputs
- Frontier Watch
  - The vetted news articles
- The Street Says
  - The gossip concerning the news on X and Reddit
- Repo of the Day
  - An AI-related GitHub repository trending amongst developers
- Two Steps Ahead
  - An educated guess on what this news implies for the future
This layer ensures each section answers *why* it matters, provides forward-looking insight, and is written with non-technical readers in mind. 

Output: A markdown formatted newsletter.

### 7. Email | Output

Transforms the markdown into html and delivers it through email.\
This is automatically triggered by the automated workflow.

Output: A daily edition delivered by email.

## Design Decisions

### Pipeline Structure

In sketching out the high-level flow of the project, a clear structure formed. The gossip section depends on the news itself revealing the pipeline must begin with AI news ingestion. Three key sources of data were required: AI news, gossip, and a daily GitHub repo. These form the foundation of the newsletter ensuring the newsletter provides consequential and corroborated information. 

To create a clean separation of concerns each source of data was approached as a unique piece of the problem. Doing so led to clearer signals and better AI performance. After each data source was properly handled the outputs were fed into a final structured prompt, completing the informational picture. This enabled the final prompt to produce high-quality output while remaining within free limits.

### Data Quality & Filtering

AI news intake is inherently the noisiest part of the pipeline due to the sheer number and variability of sources. Because of this, it received the most intensive filtering and cleaning. Each story passed through three stages — classification, corroboration, and data wrangling — to ensure that only consequential, multi‑sourced information reached the editorial layer.

Gossip was intentionally constrained to two sources (X and Reddit). Rather than treating gossip as independent data, it was filtered through the AI news intake: only posts related to the day’s verified stories were considered. This prevented hype amplification and kept the sentiment layer grounded in actual events.

For the GitHub Repo of the Day, filtering focused on recency and relevance. Repositories were limited to those created within the past week and sorted by star count to reflect genuine developer engagement. To ensure alignment with the newsletter’s core topic, the final selection was further filtered to repositories tagged with the AI topic.

### AI-Driven Synthesis

I subscribe to many newsletters, and I've noticed a common weakness. Even though the information is accurate the writing feels formulaic and fragmented built to fill a pretty template. They lack cohesion and narrative that makes human-written newsletters so compelling. To avoid this template trap, the pipeline uses AI-Driven synthesis to blend each data source into a single unified markdown newsletter. This gives the system the freedom to combine each story with a larger signal that feels more meaningful.

### Automation & Scheduling

To ensure a consistent experience for recipients, the newsletter is fully automated using a GitHub Actions cron job scheduled for 3:30 AM UTC. Running early in the morning gives the pipeline ample time to handle retries, recover from transient API failures, and complete time‑intensive tasks without rushing. By the time readers wake up, the system has already ingested the day’s data, synthesized the newsletter, and delivered a fresh edition reliably.

### Storage & Persistence

To ensure the GitHub Repo of the Day remained unique across editions, the system needed a way to persist previously selected repositories. Because the repo filter only considers projects created within the past week, a simple in‑memory approach wasn’t sufficient; the pipeline required durable, cross‑day storage. I used this requirement as an opportunity to reach a stretch goal by introducing Supabase Storage as a lightweight, web‑based persistence layer. The system stores a JSON file containing the historical repo selections and saves each generated newsletter as an HTML file, creating a reliable archive that supports both uniqueness guarantees and long‑term retrieval.

### Resilience & Error Handling

The most error‑prone components of the system are the AI providers, which impose strict free‑tier rate limits and occasionally experience outages. To make the pipeline resilient, all four AI providers are wrapped in a single abstraction that automatically falls back to the next model when one fails, preventing the automation from breaking due to a single provider’s downtime or quota exhaustion. Every external dependency (AI, search, and storage) has its own wrapper to standardize error handling and isolate failures. Hallucinations posed a subtler risk, especially when expected sources were absent, so each ingestion stage returns an explicit “no sources available” marker, and the final synthesis prompt includes repeated instructions to acknowledge missing data rather than invent stories. Together, these safeguards ensure the system degrades gracefully and maintains reliability across unpredictable inputs.