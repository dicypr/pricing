# 🎯 The Price Is Right — LLM Price Predictor

> Fine-tune Llama 3.2 with QLoRA to beat GPT-5.1, Claude, and Gemini at product price prediction — then ship it as a web app.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/pricer)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🏆 The Result

A fine-tuned **Llama 3.2 3B** model that costs pennies to run **outperforms every frontier model** on Amazon product price prediction — including GPT-5.1, Claude 4.5 Sonnet, and Gemini 3 Pro.

| Rank | Model | Avg Absolute Error | Type |
|------|-------|--------------------|------|
| 🥇 1 | **Fine-tuned Llama 3.2 (Full)** | **$39.85** | Fine-tuned OSS |
| 2 | GPT-5.1 | $44.74 | Frontier |
| 3 | Deep Neural Network | $46.49 | Custom NN |
| 4 | Claude 4.5 Sonnet | $47.10 | Frontier |
| 5 | Gemini 3 Pro | $50.54 | Frontier |
| 6 | Grok 4.1 Fast | $57.62 | Frontier |
| 7 | GPT 4.1 Nano | $62.51 | Frontier |
| 8 | Neural Network | $63.97 | Custom NN |
| 9 | Fine-tuned Llama 3.2 (Lite) | $65.40 | Fine-tuned OSS |
| 10 | GPT-4.1 Nano (Fine-tuned) | $75.91 | Fine-tuned |
| — | Human (Ed) | $87.62 | Baseline |
| — | Base Llama 3.2 4-bit | $110.72 | Untuned |

> **Key insight:** Domain-specific fine-tuning with ~400k examples transforms a mediocre base model ($110 error → $39 error) into a task specialist that outperforms models 10–100× its size.

---

## 📁 Project Structure

```
pricer-project/
│
├── pricer/                          # Core Python package
│   ├── __init__.py
│   ├── items.py                     # Item dataclass, prompt generation, HF Hub I/O
│   ├── evaluator.py                 # Multi-threaded evaluation with live charts
│   └── util.py                      # Tester class, scatter plots, error trends
│
├── notebooks/
│   ├── day1_qlora_intro.ipynb       # QLoRA theory: quantization, LoRA, SFT
│   ├── day2_data_and_base_model.ipynb  # Dataset prep, token analysis, prompt format
│   ├── day3_4_training.ipynb        # Fine-tuning on Colab A100 (SFTTrainer + QLoRA)
│   ├── day5_evaluation.ipynb        # Evaluate all models: frontier + fine-tuned
│   └── results.ipynb                # Final comparison bar chart
│
├── api/
│   └── predict.py                   # Vercel serverless endpoint (Groq / Llama 3.3)
│
├── public/
│   └── index.html                   # Frontend demo — live price prediction UI
│
├── vercel.json                      # Vercel deployment routing
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧠 How It Works

### 1 · Dataset

Amazon product listings scraped and cleaned into ~400,000 items, each with a title, category, description, and ground-truth price. Hosted on HuggingFace:

- [`ed-donner/items_prompts_full`](https://huggingface.co/datasets/ed-donner/items_prompts_full) — 400k items
- [`ed-donner/items_prompts_lite`](https://huggingface.co/datasets/ed-donner/items_prompts_lite) — smaller subset for fast iteration

### 2 · Prompt Format

Each item becomes a completion task:

```
What does this cost to the nearest dollar?

Sony WH-1000XM5 Wireless Noise Canceling Headphones with Auto Noise
Canceling Optimizer, Crystal Clear Hands-Free Calling, Alexa Voice Control...

Price is $
```

The model learns to complete with `349.00`. Token summaries are capped at **110 tokens** (truncating only ~5% of items) to keep training efficient.

### 3 · Fine-Tuning with QLoRA

| Setting | Value |
|---------|-------|
| Base model | `meta-llama/Llama-3.2-3B` |
| Quantization | 4-bit NF4 (`bitsandbytes`) |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Target modules | `q_proj`, `v_proj` |
| Trainer | HuggingFace `SFTTrainer` |
| GPU | Google Colab A100 |
| Training set | ~320k items (full) |

QLoRA freezes the base model and trains only a tiny adapter (~1% of parameters), making fine-tuning feasible on a single GPU in hours rather than days.

### 4 · Evaluation

200 held-out test items are scored with Mean Absolute Error (MAE). The `Tester` class runs predictions in parallel (5 workers), streams live colored output, and auto-generates:
- A **running error trend** with 95% confidence intervals
- A **scatter plot** of predicted vs actual price

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A [HuggingFace](https://huggingface.co) account + token
- A [Groq](https://console.groq.com) API key (free tier available)
- Google Colab access (for GPU training — free tier works for Lite mode)

### Local Setup

```bash
# 1. Clone
git clone https://github.com/your-username/pricer.git
cd pricer

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets
cp .env.example .env
# Edit .env — add your HF_TOKEN and GROQ_API_KEY
```

### Run the Notebooks

```bash
jupyter notebook notebooks/
```

| Notebook | What you'll do |
|----------|---------------|
| `day1_qlora_intro` | Understand QLoRA, quantization, and LoRA adapters |
| `day2_data_and_base_model` | Load dataset, analyze token distribution, build prompts |
| `day3_4_training` | Fine-tune on Colab (open link, run with A100) |
| `day5_evaluation` | Test all models side-by-side and compare errors |
| `results` | View the final leaderboard chart |

---

## ☁️ Deploy to Vercel

The demo app is a static HTML frontend + a Python serverless API that calls Groq's ultra-fast inference endpoint.

### Steps

```bash
# 1. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/pricer.git
git push -u origin master

# 2. Import on Vercel
#    Go to https://vercel.com/new → import your repo

# 3. Add environment variable in Vercel dashboard:
#    GROQ_API_KEY = gsk_...your key...

# 4. Deploy — done!
```

### API Endpoint

`POST /api/predict`

```json
// Request
{ "description": "Sony WH-1000XM5 Wireless Headphones, Black" }

// Response
{ "price": 349.0, "raw": "349.00", "model": "llama-3.3-70b-versatile" }
```

The live demo uses `llama-3.3-70b-versatile` via Groq for fast inference. Groq's free tier is more than sufficient for a demo.

---

## 📦 Core Classes

### `Item` (`pricer/items.py`)

Pydantic model for a product data point. Key methods:

```python
item = Item(title="Laptop", category="Electronics", price=999.99, summary="...")

item.make_prompts(tokenizer, max_tokens=110, do_round=True)
# → item.prompt      = "What does this cost?...\nPrice is $"
# → item.completion  = "1000.00"

Item.push_prompts_to_hub("username/dataset", train, val, test)
train, val, test = Item.from_hub("username/dataset")
```

### `Tester` / `evaluate` (`pricer/evaluator.py`)

```python
from pricer import evaluate

def my_predictor(datapoint):
    return call_my_model(datapoint.prompt)

evaluate(my_predictor, test_items, size=200, workers=5)
# Runs 200 predictions in parallel, prints live colored errors,
# then shows trend chart + scatter plot
```

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| 🤗 Full Dataset | [ed-donner/items_prompts_full](https://huggingface.co/datasets/ed-donner/items_prompts_full) |
| 🤗 Lite Dataset | [ed-donner/items_prompts_lite](https://huggingface.co/datasets/ed-donner/items_prompts_lite) |
| 📓 Training (Colab) | [Day 3 & 4 Notebook](https://colab.research.google.com/drive/1fBTm_jzrFGr88PDOFTQF7JIlQ1JW15BG) |
| 📓 Evaluation (Colab) | [Day 5 Notebook](https://colab.research.google.com/drive/16e8aY_BlHjzzcR-2dCyDMCPdOQ8XeN1e) |
| ⚡ Groq Console | [console.groq.com](https://console.groq.com) |

---

## 📄 License

MIT — free to use, fork, and build on.
