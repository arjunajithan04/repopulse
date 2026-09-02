# 🚀 RepoPulse
### _GitHub Repository Intelligence Dashboard_

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![GitHub API](https://img.shields.io/badge/GitHub_API-REST-black?style=for-the-badge&logo=github)](https://docs.github.com/en/rest)

---

## ✨ What is RepoPulse?

**RepoPulse** is an intelligent GitHub repository analysis dashboard that transforms raw repository data into actionable insights. Powered by the GitHub REST API and built with Streamlit, it provides a comprehensive view of repository health, contributor dynamics, and code quality metrics in real-time.

Whether you're evaluating repositories, tracking team velocity, or monitoring project health, RepoPulse delivers **dynamic, data-driven intelligence** at your fingertips.

---

## 🎯 Core Features

### 📊 **Executive Dashboard**
- **Real-time metrics** at a glance: Stars, Forks, Open Issues, Health Score
- **Adaptive highlights** that respond to repository characteristics
- **Trend analysis** with intelligent insights based on repository metrics
- **Visual summary charts** displaying repository activity

### 📁 **Repository Analysis**
- Analyze **any public GitHub repository** by URL or owner/repo format
- Support for **batch analysis** (up to 10 repositories per session)
- Automatic repository normalization and validation
- Session history tracking with analysis persistence

### 👥 **Contributor Intelligence**
- Deep dive into **contributor activity and contributions**
- Identify key team members and collaborators
- Analyze **contributor momentum** and participation trends
- Visual contributor cards with contribution metrics

### 🧠 **Code Insights**
- **Language breakdown** analysis
- Repository **health scoring** system
- **Code quality metrics** and signals
- Issue and pull request tracking
- Recent commit activity monitoring

### 🎨 **Modern Dark Theme**
- Sleek, minimalist dark interface
- Smooth gradient backgrounds and animations
- Purple and blue accent colors for visual hierarchy
- Fully responsive design with adaptive layouts

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.28+ |
| **Backend** | Python 3.12 |
| **API** | GitHub REST API v3 |
| **Data Processing** | Pandas |
| **HTTP Client** | Python requests |
| **Testing** | pytest |

---

## 📦 Project Architecture

```
repopulse/
├── app.py                    # Main entry point with theme & navigation
├── config/
│   └── settings.py           # Configuration & environment variables
├── core/
│   ├── github_client.py      # GitHub API wrapper
│   ├── models.py             # Data models (RepositoryStats, etc.)
│   └── repository.py         # Repository domain logic
├── analysis/
│   ├── repository_analysis.py # Analysis orchestration & batch logic
│   ├── metrics.py            # Metrics computation
│   └── code_analysis.py      # Code-level analysis
├── pages/
│   ├── dashboard.py          # Executive Overview
│   ├── repository.py         # Repository Analyzer
│   ├── contributors.py       # Contributor Intelligence
│   └── code_insights.py      # Code Quality Metrics
├── components/
│   ├── cards.py              # Metric card components
│   ├── charts.py             # Visualization components
│   └── tables.py             # Data table components
├── utils/
│   ├── helpers.py            # Utility functions
│   └── validators.py         # Input validation
├── tests/
│   └── test_analysis.py      # Unit tests
└── assets/
    └── repo-icon.png         # Application favicon
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- GitHub personal access token (for increased API rate limits)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/arjunajithan04/repopulse.git
cd repopulse

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file in the config/ directory with:
# GITHUB_TOKEN=your_github_token
# GITHUB_API_BASE=https://api.github.com
```

### Run the Application

```bash
streamlit run app.py
```

The application will start at `http://localhost:8501` 🎉

---

## 📖 How to Use

### 1️⃣ **Analyze a Repository**
- Navigate to the **Repository** page via the sidebar
- Enter a GitHub repository URL or owner/repo format
  - Examples: `https://github.com/torvalds/linux` or `torvalds/linux`
- View real-time analysis with repository metrics

### 2️⃣ **View Executive Overview**
- Head to the **Dashboard** for high-level insights
- See key metrics: Stars, Forks, Issues, Health Score
- Read intelligent trend analysis based on repository data

### 3️⃣ **Explore Contributors**
- Navigate to **Contributors** page
- Discover top contributors and their activity
- Understand team dynamics and contribution patterns

### 4️⃣ **Analyze Code Quality**
- Visit **Code Insights** for deep dives
- Review language breakdown and repository health
- Track issue and pull request activity

---

## 🔑 Key Capabilities

### 🔄 Real-Time Data Integration
- Live GitHub API queries for current repository state
- Cross-page session state management
- Automatic data caching within session

### 📊 Intelligent Batch Processing
- Analyze **up to 10 repositories per session**
- Session history with persistent analysis results
- Efficient API rate limit management

### ✅ Input Validation
- Robust URL and repository format parsing
- Automatic normalization of repository identifiers
- Error handling for invalid repositories

### 🎯 Smart Metrics
- Adaptive health scoring based on multiple factors
- Contributor velocity analysis
- Issue resolution trend tracking

---

## 🌟 Example Workflows

### Evaluate an Open-Source Project
1. Paste the repository URL in the Repository page
2. Check the Executive Dashboard for quick overview
3. Review contributors to assess team strength
4. Inspect code insights for quality signals

### Track Team Performance
1. Analyze your team's main repository
2. Monitor contributor momentum on Contributors page
3. Watch health metrics trend over time
4. Use insights for sprint planning

### Compare Multiple Repositories
1. Analyze up to 10 repos in a single session
2. Use session history to compare metrics
3. Identify high-performing vs. struggling projects
4. Make data-driven decisions

---

## 🧪 Testing

Run the test suite to validate repository analysis logic:

```bash
pytest tests/test_analysis.py -v
```

Tests validate:
- Repository input parsing and normalization
- Batch processing with 10-repository cap
- Analysis result generation and metrics computation

---

## 📝 Environment Configuration

Create a `.env` file in the `config/` directory:

```env
GITHUB_TOKEN=your_personal_access_token_here
GITHUB_API_BASE=https://api.github.com
```

**Get your GitHub token:**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select `public_repo` scope
4. Copy and paste into `.env`

---

## 📊 Supported Metrics

| Metric | Description |
|--------|-------------|
| **Stars** | Repository popularity and adoption |
| **Forks** | Community interest and extension attempts |
| **Open Issues** | Outstanding work and bug backlog |
| **Health Score** | Overall repository vitality (0-100) |
| **Contributors** | Team size and collaboration scope |
| **Languages** | Technology stack breakdown |
| **Commits** | Development activity and momentum |
| **Pull Requests** | Ongoing development work |

---

## 🎨 UI/UX Highlights

✨ **Modern Dark Theme** with gradient backgrounds  
🎯 **Intuitive Navigation** through collapsible sidebar  
📱 **Responsive Design** adapting to all screen sizes  
⚡ **Smooth Animations** for enhanced interactivity  
🎭 **Color-Coded Metrics** for quick visual scanning  

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙋 Support

For questions, issues, or feature requests, please open an issue on [GitHub Issues](https://github.com/arjunajithan04/repopulse/issues).

---

<div align="center">

**Made with ❤️ by Arjun Ajithan**

[⭐ Star us on GitHub](https://github.com/arjunajithan04/repopulse)

</div>
