# Job Finder Example

Example application demonstrating ASMF for job search and tracking.

## Features

- Multi-source job aggregation (APIs, MCPs, web scraping)
- AI-powered relevance scoring
- Block lists and deduplication
- Status tracking (new, reviewed, applied, rejected)
- Web UI for management

## Usage

```python
from job_finder.aggregator import JobAggregator
from asmf.providers import AIProviderFactory

# Initialize
aggregator = JobAggregator()
ai_provider = AIProviderFactory.create_provider()

# Search and score jobs
jobs = aggregator.search("python developer", count=20)
for job in jobs:
    score = ai_provider.analyze_text(f"Rate this job: {job['title']}")
    print(f"{job['title']}: {score}")
```

See main ASMF documentation for framework details.
