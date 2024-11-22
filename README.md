# 🧙 Project Guide
### Your magical AI-powered project documentation generator

![Project Guide](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge)
![Powered by Anthropic](https://img.shields.io/badge/Powered%20by-Anthropic-blue?style=for-the-badge)

Ever wished your project could explain itself? Now it can! 🪄 Project Whisperer uses AI to analyze your codebase and generate comprehensive documentation automagically. 

## ✨ Features

- 🔍 Deep code analysis 
- 📚 Generates detailed developer guides
- 🎯 Identifies project purpose and architecture
- 🗺️ Creates clear documentation structure
- 🤖 AI-powered insights
- 📝 Markdown-formatted output
- 🔄 Recursive directory analysis
- 🎨 Well-organized documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Anthropic API key
- Your favorite code project to document! 

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/project-whisperer.git
cd project-whisperer
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export GUIDE_TARGET_PROJECT_DIRECTORY="/path/to/your/project"
```

5. Run the magic spell:
```bash
python guide.py
```

## 📦 Output

The script creates three magical artifacts:

- 📘 `initial-summaries_{timestamp}.txt` - Raw project insights
- 🗄️ `findings/{timestamp}/findings.json` - Structured analysis data  
- 📚 `guidebook_{timestamp}.md` - Your beautiful developer guide!

## 🎯 Usage Tips

- 🧹 The script automatically excludes common non-source directories (.git, node_modules, etc.)
- 🔮 Works best with well-organized codebases
- 📏 Large projects may take longer to analyze
- 💡 The better organized your code, the better the documentation!

## ⚙️ Configuration

Want to exclude more directories? Modify the `EXCLUSION_LIST` in the script:

```python
EXCLUSION_LIST = [
    '.git', 
    '.venv', 
    'node_modules', 
    '__pycache__', 
    '.DS_Store',
    'pb_data',
    'pb_public',
    'migrations'
]
```

## 🎨 Example Output Structure

```
📁 Your Project
├── 📄 initial-summaries_20240122_123456.txt
├── 📁 findings
│   └── 📁 20240122_123456
│       └── 📄 findings.json
└── 📄 guidebook_20240122_123456.md
```

## 🛟 Troubleshooting

### Common Issues:

1. **API Key Error**
```bash
# Make sure your API key is set:
echo $ANTHROPIC_API_KEY  # Should show your key
```

2. **Project Directory Error**
```bash
# Verify your project directory is set and exists:
echo $GUIDE_TARGET_PROJECT_DIRECTORY
ls $GUIDE_TARGET_PROJECT_DIRECTORY
```

3. **Virtual Environment Issues**
```bash
# Make sure you're in the virtual environment:
# You should see (.venv) in your terminal
# If not, activate it:
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

## 🤝 Contributing

Got ideas to make Project Whisperer even more magical? Contributions are welcome! 

1. 🍴 Fork the repo
2. 🌱 Create your feature branch
3. 💫 Make your changes
4. 🚀 Submit a PR

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ✨ Acknowledgments

- 🤖 Powered by Anthropic's Claude API
- 🧙‍♂️ Inspired by all the developers who hate writing documentation
- 🌟 Special thanks to coffee and late-night coding sessions

---

Made with 💜 and a bit of AI magic

Remember: Documentation is like a love letter to your future self! 💌
