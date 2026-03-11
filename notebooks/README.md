# TruthLens AI - Data Exploration & Model Training

This directory contains Jupyter notebooks for developing, training, and evaluating the TruthLens AI models.

## Notebooks

### 1. `01_dataset_exploration.ipynb`
Exploratory Data Analysis (EDA) of LIAR and FakeNewsNet datasets
- Data loading and inspection
- Label distributions
- Text statistics
- Visualization

### 2. `02_roberta_finetuning.ipynb`
Fine-tuning RoBERTa for fake news classification
- Model architecture
- Training pipeline
- Evaluation metrics
- Error analysis

### 3. `03_sbert_evidence_retrieval.ipynb`
Training evidence retrieval system with Sentence-BERT
- Embedding generation
- Vector similarity
- Pinecone indexing
- Retrieval evaluation

### 4. `04_propagation_analysis.ipynb`
Building and analyzing propagation networks
- Graph construction
- Network metrics
- Visualization

### 5. `05_model_fusion_experiments.ipynb`
Experimenting with fusion scoring engine
- Score combination strategies
- Performance benchmarking
- Error analysis

## Quick Start

```bash
# Install Jupyter
pip install jupyter notebook

# Start Jupyter
jupyter notebook

# Or use JupyterLab
pip install jupyterlab
jupyter lab
```

## Data Sources

1. **LIAR Dataset**: ~12.8K labeled news claims
   - Download: https://www.cs.ucsb.edu/~william/data/liar_dataset.zip

2. **FakeNewsNet**: ~100K news samples
   - Download: https://github.com/KaiDMML/FakeNewsNet

3. **CoAID Dataset**: COVID-19 misinformation
   - Download: https://github.com/cuilimeng/CoAID

## Credentials

- Pinecone: Set `PINECONE_API_KEY` environment variable
- AWS S3: Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
