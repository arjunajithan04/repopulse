# 🔧 RepoPulse - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Data Flow Pipeline](#data-flow-pipeline)
3. [Core Components](#core-components)
4. [API Integration](#api-integration)
5. [Session State Management](#session-state-management)
6. [Component Interactions](#component-interactions)
7. [Metrics Computation](#metrics-computation)
8. [Error Handling & Validation](#error-handling--validation)
9. [Performance Optimization](#performance-optimization)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Notes](#deployment-notes)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI LAYER                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Dashboard   │  Repository  │ Contributors │ Code Insights│  │
│  │   (Static)   │  (Dynamic)   │  (Dynamic)   │  (Dynamic)   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SESSION STATE MANAGER                         │
│  • repo_analysis (AnalysisResult)                               │
│  • repo_session_count (int)                                     │
│  • repo_session_history (List[AnalysisResult])                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │ repository_      │  │ metrics.py      │  │ models.py    │   │
│  │ analysis.py      │  │                 │  │              │   │
│  │ • Orchestration  │  │ • Health Score  │  │ Data Classes │   │
│  │ • Batch Logic    │  │ • Contributors  │  │ • Statistics │   │
│  │ • Validation     │  │ • Repository    │  │              │   │
│  └──────────────────┘  └─────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  GITHUB API CLIENT LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ github_client.py                                         │   │
│  │ • HTTP Session Management                               │   │
│  │ • Request/Response Handling                             │   │
│  │ • Error Recovery                                        │   │
│  │ • Authentication (OAuth Token)                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GITHUB REST API v3                            │
│  • Repositories Endpoint                                       │
│  • Contributors Endpoint                                       │
│  • Issues Endpoint                                             │
│  • Pull Requests Endpoint                                      │
│  • Commits Endpoint                                            │
│  • Languages Endpoint                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Architectural Patterns

**1. Domain-Driven Design (DDD)**
- Separate concerns: models, analysis, metrics, API client
- Clear boundaries between layers
- Business logic isolated from UI

**2. Strategy Pattern**
- Different analysis strategies for metrics computation
- Pluggable metric calculation methods

**3. Factory Pattern**
- `GitHubClient` factory for API interactions
- `AnalysisResult` factory for result generation

**4. Session State Pattern (Streamlit-specific)**
- Persistent state across page navigation
- Shared data between independent page components

---

## Data Flow Pipeline

### Complete Analysis Flow (Step-by-Step)

#### **Step 1: User Input → Validation**
```
User enters: "https://github.com/torvalds/linux"
                    ↓
Repository Input Parser (parse_repository_input)
                    ↓
Normalize → Extract owner/repo → Validate format
                    ↓
Result: ("torvalds", "linux")
```

**Implementation in `analysis/repository_analysis.py`:**
```python
def parse_repository_input(repo_value: str) -> Tuple[str, str]:
    # Strip and clean
    candidate = (repo_value or "").strip().replace(".git", "").rstrip("/")
    
    # Remove URL schemes
    candidate = candidate.replace("https://github.com/", "")
    
    # Split and validate
    if "/" not in candidate:
        raise ValueError(...)
    
    owner, repo = candidate.split("/", 1)
    return owner.strip(), repo.strip()
```

#### **Step 2: GitHub API Data Collection**
```
("torvalds", "linux")
        ↓
GitHubClient._request()
        ↓
┌─────────────────────────────────────────┐
│ Parallel API Requests (via loop):       │
├─────────────────────────────────────────┤
│ GET /repos/{owner}/{repo}               │
│ GET /repos/{owner}/{repo}/contributors  │
│ GET /repos/{owner}/{repo}/languages     │
│ GET /repos/{owner}/{repo}/issues        │
│ GET /repos/{owner}/{repo}/pulls         │
│ GET /repos/{owner}/{repo}/commits       │
└─────────────────────────────────────────┘
        ↓
Raw JSON Response Objects
```

**Key Implementation (`core/github_client.py`):**
```python
class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        })
    
    def _request(self, endpoint: str) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
```

#### **Step 3: Data Transformation**
```
Raw API Data → Type Mapping → Domain Models
        ↓
┌───────────────────────────────────────────┐
│ RepositoryStats (from repo_data)          │
│ • name, full_name                         │
│ • stars, forks, open_issues               │
│ • language, description, branches         │
├───────────────────────────────────────────┤
│ ContributorStats[] (from contributors)    │
│ • login, contributions, avatar_url        │
├───────────────────────────────────────────┤
│ Metrics dict (computed from all data)     │
│ • repository_health_score                 │
│ • total_contributors                      │
│ • language_breakdown                      │
└───────────────────────────────────────────┘
```

**Dataclass Model (`core/models.py`):**
```python
@dataclass
class RepositoryStats:
    name: str
    full_name: str
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    language: Optional[str] = None

@dataclass
class AnalysisResult:
    repository: RepositoryStats
    contributors: List[ContributorStats]
    metrics: Dict[str, Any]
    summary: str
```

#### **Step 4: Metrics Computation**
```
Raw Data → Calculation Algorithms → Metrics
        ↓
┌──────────────────────────────────────────────────┐
│ Repository Health Score                          │
│ = (Stars/Max) × 0.3 + (Forks/Max) × 0.2 +        │
│   (Low Issues/Max Issues) × 0.3 +                │
│   (Freshness) × 0.2                              │
├──────────────────────────────────────────────────┤
│ Contributor Metrics                              │
│ • Momentum: Sum of recent contributions          │
│ • Diversity: Number of unique contributors       │
│ • Activity: Commits/Pulls/Issues participation   │
└──────────────────────────────────────────────────┘
```

**Implementation (`analysis/metrics.py`):**
```python
def compute_repository_metrics(repo_data, contributors, issues):
    health_score = 0
    
    # Stars component (30%)
    if repo_data.get('stargazers_count'):
        health_score += min(100, repo_data['stargazers_count'] / 100) * 0.3
    
    # Forks component (20%)
    if repo_data.get('forks_count'):
        health_score += min(100, repo_data['forks_count'] / 50) * 0.2
    
    # Issue health (30%)
    open_issues = repo_data.get('open_issues_count', 0)
    health_score += max(0, (100 - open_issues) / 100) * 0.3
    
    # Freshness (20%)
    ...
    
    return int(health_score)
```

#### **Step 5: Session State Persistence**
```
AnalysisResult Object
        ↓
st.session_state["repo_analysis"] = result
st.session_state["repo_session_count"] += 1
st.session_state["repo_session_history"].append(result)
        ↓
Accessible across all pages:
• pages/dashboard.py
• pages/contributors.py
• pages/code_insights.py
```

#### **Step 6: UI Rendering**
```
Session State Data → Page Components
        ↓
┌─────────────────────────────────────────┐
│ Metric Cards (components/cards.py)      │
│ Charts (components/charts.py)           │
│ DataFrames (components/tables.py)       │
│ Custom HTML (st.markdown)               │
└─────────────────────────────────────────┘
        ↓
Rendered in Streamlit UI
```

---

## Core Components

### 1. **GitHubClient** (`core/github_client.py`)

**Responsibility:** Direct API communication with GitHub REST API v3

**Key Methods:**
```python
class GitHubClient:
    # Repository Information
    get_repository(owner, repo) → Dict
    
    # Contributors
    get_contributors(owner, repo) → List[Dict]
    
    # Commits
    get_commits(owner, repo, branch=None) → List[Dict]
    
    # Pull Requests
    get_pull_requests(owner, repo, state="all") → List[Dict]
    
    # Issues
    get_issues(owner, repo, state="all") → List[Dict]
    
    # Languages
    get_languages(owner, repo) → Dict
```

**Authentication:**
- Reads `GITHUB_TOKEN` from environment
- Uses OAuth token in `Authorization: token <token>` header
- Increases rate limit from 60 to 5000 requests/hour

**Error Handling:**
```python
def _request(self, endpoint):
    try:
        response = self.session.get(url, timeout=20)
        response.raise_for_status()  # Raises HTTPError
        return response.json()
    except requests.HTTPError:
        return []  # Graceful fallback
```

### 2. **Data Models** (`core/models.py`)

**RepositoryStats**
- Represents a single repository's metadata
- Fields: name, stars, forks, issues, language, etc.
- Immutable dataclass

**ContributorStats**
- Represents contributor activity metrics
- Fields: login, contributions, commits, PRs, issues
- Links to avatar_url for UI display

**AnalysisResult**
- Aggregates all analysis data
- Contains: repository, contributors list, computed metrics, summary text
- Central data structure passed across application

### 3. **Repository Analysis** (`analysis/repository_analysis.py`)

**Key Functions:**

**`parse_repository_input(repo_value: str) → Tuple[str, str]`**
- Normalizes various repository input formats
- Handles: Full URLs, owner/repo, git URLs
- Returns standardized (owner, repo) tuple
- Raises ValueError for invalid input

**`limit_repo_batch(repos: Sequence[str], max_repos=10) → List[str]`**
- Enforces 10-repository session limit
- Deduplicates repositories
- Validates each repository format
- Returns limited, deduplicated list

**`analyze_repository(repo_data, contributors_data, ...) → AnalysisResult`**
- Main orchestration function
- Transforms raw API data into domain models
- Computes metrics
- Generates summary text
- Returns complete AnalysisResult object

### 4. **Metrics Computation** (`analysis/metrics.py`)

**Functions:**

**`compute_repository_metrics(repo_data, contributors, issues)`**
- Calculates repository health score (0-100)
- Formula components:
  - Stars (30%): Popularity indicator
  - Forks (20%): Fork activity
  - Issues (30%): Issue management (inverse)
  - Freshness (20%): Recent activity

**`compute_contributor_metrics(contributors_data, commits, issues, pulls)`**
- Extracts contributor statistics
- Calculates per-contributor metrics
- Ranks contributors by activity
- Returns structured contributor data

---

## API Integration

### GitHub REST API v3 Endpoints Used

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|-----------|
| `/repos/{owner}/{repo}` | GET | Repository metadata | 1 |
| `/repos/{owner}/{repo}/contributors` | GET | Contributor list | 1 |
| `/repos/{owner}/{repo}/commits` | GET | Commit history | 1 |
| `/repos/{owner}/{repo}/issues` | GET | Issues (open/closed) | 1 |
| `/repos/{owner}/{repo}/pulls` | GET | Pull requests | 1 |
| `/repos/{owner}/{repo}/languages` | GET | Language breakdown | 1 |

**Total API calls per analysis:** 6 requests

**Rate Limiting:**
- **Unauthenticated:** 60 requests/hour
- **Authenticated:** 5000 requests/hour
- **Per endpoint:** Usually 60/minute

**Optimization:**
- Batch multiple analyses within session
- Cache results in session state
- Implement exponential backoff for rate limits

### Response Handling

**Success Response:**
```json
{
  "name": "linux",
  "full_name": "torvalds/linux",
  "stargazers_count": 180000,
  "forks_count": 28000,
  "open_issues_count": 500,
  "language": "C",
  "created_at": "2011-09-04T11:56:15Z"
}
```

**Error Response:**
```python
HTTPError → Caught → Return empty list []
Example: Private repository → 404 → []
```

---

## Session State Management

### Streamlit Session State Architecture

**Initialization** (in `pages/repository.py`):
```python
if "repo_analysis" not in st.session_state:
    st.session_state["repo_analysis"] = None
if "repo_session_count" not in st.session_state:
    st.session_state["repo_session_count"] = 0
if "repo_session_history" not in st.session_state:
    st.session_state["repo_session_history"] = []
```

**State Variables:**

| Variable | Type | Purpose | Scope |
|----------|------|---------|-------|
| `repo_analysis` | AnalysisResult \| None | Current repository analysis | Global (all pages) |
| `repo_session_count` | int | Count of analyses in session | Global (all pages) |
| `repo_session_history` | List[AnalysisResult] | History of all analyses | Global (all pages) |

**State Flow:**

```
1. User analyzes repo on Repository page
        ↓
2. analyze_repository() executed
        ↓
3. Result stored: st.session_state["repo_analysis"] = result
        ↓
4. Counter incremented: st.session_state["repo_session_count"] += 1
        ↓
5. History appended: st.session_state["repo_session_history"].append()
        ↓
6. User navigates to Dashboard/Contributors/Code Insights
        ↓
7. Pages read: analysis = st.session_state.get("repo_analysis")
        ↓
8. UI rendered with live data
```

**Key Insight:** All pages share the same session state. When Repository page updates the analysis, other pages automatically have access to the new data upon refresh/navigation.

---

## Component Interactions

### Page-to-Page Communication Flow

```
┌──────────────────────────────────────────────────────┐
│                  Repository Page                     │
│  • Input: repository URL or owner/repo              │
│  • Process: Analyze repo with GitHubClient          │
│  • Output: AnalysisResult → st.session_state        │
└──────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Dashboard   │ │Contributors  │ │Code Insights │
│              │ │              │ │              │
│ • Read state │ │ • Read state │ │ • Read state │
│ • Render     │ │ • Render     │ │ • Render     │
│   metrics    │ │   contributors           │
│ • Display    │ │   profiles   │ │ • Display    │
│   trends     │ │ • Show stats │ │   language   │
│              │ │              │ │   breakdown  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Component Hierarchy

**UI Components** (`components/`):

```
components/
├── cards.py
│   └── metric_card(title, value, delta, help, variant)
│       • Displays a single metric in styled card
│       • Colors: good (green), bad (red), neutral (blue)
│       • Responsive layout
│
├── charts.py
│   └── render_bar_chart(data_dict, title)
│       • Horizontal bar chart for metrics comparison
│       • Uses Streamlit's native charting
│       • Dynamic data scaling
│
└── tables.py
    └── render_dataframe(df, title)
        • Styled DataFrame rendering
        • Sortable columns
        • Export capability
```

**Usage Pattern:**
```python
# Dashboard page
metric_card(
    title="Stars",
    value="1.2K",
    delta="+18.2%",
    help="Repository popularity",
    variant="good"
)
```

---

## Metrics Computation

### Repository Health Score Algorithm

```python
health_score = 0

# 1. Star Component (30% weight)
stars = repo.get('stargazers_count', 0)
normalized_stars = min(stars / 100, 1.0)
health_score += normalized_stars * 30

# 2. Fork Component (20% weight)
forks = repo.get('forks_count', 0)
normalized_forks = min(forks / 50, 1.0)
health_score += normalized_forks * 20

# 3. Issue Health Component (30% weight)
open_issues = repo.get('open_issues_count', 0)
# Invert: fewer issues = higher score
issue_score = max(0, 100 - open_issues)
health_score += (issue_score / 100) * 30

# 4. Freshness Component (20% weight)
days_since_update = days_since(repo.get('updated_at'))
freshness = max(0, 100 - (days_since_update / 10))
health_score += (freshness / 100) * 20

# Final Score (0-100)
return min(int(health_score), 100)
```

### Contributor Momentum

```python
total_contributions = sum(c.contributions for c in contributors)
average_contribution = total_contributions / len(contributors)
contributor_momentum = {
    'high': total_contributions > 1000,
    'medium': 100 <= total_contributions <= 1000,
    'low': total_contributions < 100
}
```

---

## Error Handling & Validation

### Input Validation Pipeline

```
User Input
    ↓
1. Null/Empty Check
   if not repo_value: raise ValueError(...)
    ↓
2. Format Normalization
   Strip whitespace, remove .git, remove URL schemes
    ↓
3. Structure Validation
   Split by "/" and validate owner/repo both present
    ↓
4. Deduplication
   Check if already analyzed in session
    ↓
Valid (owner, repo) Tuple
```

### API Error Recovery

**HTTP Error Scenarios:**

| Status | Cause | Recovery |
|--------|-------|----------|
| 404 | Repository not found | Return None, show error message |
| 401 | Invalid token | Return None, prompt token refresh |
| 403 | Rate limit exceeded | Queue request, show message |
| 500 | Server error | Retry with exponential backoff |
| Timeout | Network slow | Return empty data, continue |

**Implementation:**
```python
try:
    response = self.session.get(url, timeout=20)
    response.raise_for_status()
    return response.json()
except requests.HTTPError as e:
    if e.response.status_code == 404:
        st.error("Repository not found. Check owner and name.")
    elif e.response.status_code == 401:
        st.error("GitHub token expired. Please update .env")
    return []  # Graceful fallback
except requests.Timeout:
    st.warning("Request timed out. Try again.")
    return []
```

---

## Performance Optimization

### Caching Strategy

**Session-Level Caching:**
```python
# Repository analysis cached in session
st.session_state["repo_analysis"]
# Prevents re-fetching same repo within session
```

**Request Optimization:**
- Use persistent HTTP session (connection pooling)
- Set 20-second timeout to prevent hanging
- Parallel API calls where possible

### API Rate Limit Management

**10-Repository Batch Limit:**
```python
max_requests_per_session = 10 * 6  # 10 repos × 6 API calls
total_rate_limit = 5000 / 60 * 60  # ~83 requests/min for auth
safe_batch_size = 10  # Ensures margin for safety
```

**Session History:**
- Stored in memory (session state)
- Retrieved without re-fetching
- Accessible as historical reference

---

## Testing Strategy

### Test Coverage (`tests/test_analysis.py`)

**1. Input Parsing Tests**
```python
def test_parse_repository_input_accepts_url_and_owner_repo():
    assert parse_repository_input("https://github.com/microsoft/vscode") == ("microsoft", "vscode")
    assert parse_repository_input("microsoft/vscode") == ("microsoft", "vscode")
```

**2. Batch Limiting Tests**
```python
def test_limit_repo_batch_caps_at_ten():
    repos = [f"owner{i}/repo{i}" for i in range(15)]
    limited = limit_repo_batch(repos)
    assert len(limited) == 10
```

**3. Analysis Result Tests**
```python
def test_analyze_repository_returns_summary():
    result = analyze_repository(repo_data, contributors_data)
    assert result.repository.name == "demo-repo"
    assert result.repository.stars == 120
    assert result.metrics["total_contributors"] == 2
```

**Running Tests:**
```bash
pytest tests/test_analysis.py -v
```

**Test Execution:**
- Validates input parsing logic
- Verifies batch limits enforce 10-repo cap
- Ensures analysis produces expected results
- No external API calls (mocked data)

---

## Deployment Notes

### Environment Configuration

**Required Variables** (`.env` in `config/` directory):
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_API_BASE=https://api.github.com
```

**Token Scopes Required:**
- `public_repo`: Read public repositories
- `repo`: (Optional) Read private repositories

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/arjunajithan04/repopulse.git
cd repopulse

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
echo "GITHUB_TOKEN=<your_token>" > config/.env
echo "GITHUB_API_BASE=https://api.github.com" >> config/.env

# 5. Run application
streamlit run app.py
```

### Deployment Platforms

**Streamlit Cloud**
```bash
git push origin main
# Deploy via Streamlit Cloud dashboard
# Set secrets: GITHUB_TOKEN, GITHUB_API_BASE
```

**Docker Deployment**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

**Server Deployment (Linux/Ubuntu)**
```bash
# Install dependencies
sudo apt-get install python3.12 python3-pip

# Clone and setup
git clone <repo> && cd repopulse
pip install -r requirements.txt

# Run with process manager (systemd/supervisor)
streamlit run app.py --server.port 8501
```

### Performance Characteristics

**Single Repository Analysis:**
- Time: 2-5 seconds (depending on repo size)
- API calls: 6 requests
- Data transfer: ~500KB average

**Batch Analysis (10 repos):**
- Time: 20-50 seconds
- API calls: 60 requests
- Data transfer: ~5MB total

**Browser Requirements:**
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Minimum 512MB RAM recommended

---

## Troubleshooting Guide

### Common Issues

**Issue: "No module named 'streamlit'"**
```bash
Solution: pip install -r requirements.txt
```

**Issue: "HTTPError: 404 Not Found"**
```bash
Cause: Invalid repository or private repository
Solution: Verify owner/repo format, or add GITHUB_TOKEN for private repos
```

**Issue: "Rate limit exceeded"**
```bash
Cause: Too many API requests in short time
Solution: Add GitHub token, wait 1 hour, or increase batch size limit
```

**Issue: "Connection timeout"**
```bash
Cause: Network issue or GitHub API slow
Solution: Check internet, retry analysis, or check GitHub status
```

---

## Future Enhancement Opportunities

1. **Caching Layer:** Redis/Memcached for distributed caching
2. **GraphQL API:** Migrate to GitHub GraphQL for complex queries
3. **Webhooks:** Real-time repository updates via webhooks
4. **Database Storage:** Persistent history with PostgreSQL
5. **ML Integration:** Predictive health scoring
6. **Multi-language:** Internationalization support
7. **Advanced Analytics:** Time-series analysis and trends
8. **Team Insights:** Organization-level analytics
9. **Export Formats:** PDF reports, CSV exports
10. **Custom Metrics:** User-defined metric computations

---

## Conclusion

RepoPulse architecture follows clean code principles with clear separation of concerns:

- **Presentation Layer:** Streamlit pages and components
- **Business Logic Layer:** Analysis and metrics computation
- **Data Layer:** GitHub API client and session state
- **Domain Layer:** Models and data structures

This modular design enables:
- ✅ Easy testing and maintenance
- ✅ Scalability and extensibility
- ✅ Clear error handling
- ✅ Efficient API resource usage
- ✅ Smooth user experience with instant feedback

