# Jenkins Test - Water Potability ML Pipeline

This project builds a machine learning pipeline for a water potability prediction model and exposes it through a FastAPI service.

## Project Workflow

The DVC pipeline is intentionally sequential and validated by the actual project graph:

```bash
dvc dag
```

This produces the following order:

```text
Data_Collection
  -> Data_Preprocessing
      -> Model_Training
          -> Evaluation
```

This is the correct workflow for the project because each stage depends on the outputs of the previous stage.

## 1. Create the virtual environment

```bash
cd /workspaces/Jenkins_Test
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas numpy scikit-learn fastapi uvicorn pydantic
```

## 2. Initialize DVC

```bash
dvc init
```

## 3. Create the DVC pipeline stages

These commands match the actual dependency flow defined in the repository and follow the real sequential order shown by `dvc dag`.

### Stage 1: Data Collection

```bash
dvc stage add -n Data_Collection \
  -d src/data_collection.py \
  -o data/raw/train.csv \
  -o data/raw/test.csv \
  python src/data_collection.py
```

### Stage 2: Data Preprocessing

```bash
dvc stage add -n Data_Preprocessing \
  -d src/data_preprocessing.py \
  -d data/raw/train.csv \
  -d data/raw/test.csv \
  -o data/processed/train_processed.csv \
  -o data/processed/test_processed.csv \
  python src/data_preprocessing.py
```

### Stage 3: Model Training

```bash
dvc stage add -n Model_Training \
  -d src/model_training.py \
  -d data/processed/train_processed.csv \
  -d data/processed/test_processed.csv \
  -o model.pkl \
  python src/model_training.py
```

### Stage 4: Evaluation

```bash
dvc stage add -n Evaluation \
  -d src/model_evaluation.py \
  -d model.pkl \
  -o metrics.json \
  python src/model_evaluation.py
```

## 4. Run the pipeline

```bash
dvc repro
```

This executes the stages in the correct order and only reruns changed stages.

## 5. Validate the workflow

The repository was verified with:

```bash
dvc dag
```

and

```bash
dvc repro
```

The command output confirmed the sequential chain and showed:

```text
Stage 'Data_Collection' didn't change, skipping
Stage 'Data_Preprocessing' didn't change, skipping
Stage 'Model_Training' didn't change, skipping
Stage 'Evaluation' didn't change, skipping
Data and pipelines are up to date.
```

This confirms the sequential DVC workflow is working properly.

## 6. Run the FastAPI app

```bash
cd /workspaces/Jenkins_Test
.venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/
- http://localhost:8000/docs
- http://localhost:8000/predict

## 7. Example prediction request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 7.0,
    "Hardness": 200.0,
    "Solids": 20000.0,
    "Chloramines": 7.0,
    "Sulfate": 300.0,
    "Conductivity": 450.0,
    "Organic_carbon": 15.0,
    "Trihalomethanes": 60.0,
    "Turbidity": 3.5
  }'
```

## 8. Important notes

- The pipeline must run in order: collection -> preprocessing -> training -> evaluation.
- The model file `model.pkl` must exist before starting the API service.
- Use the docs at `/docs` to check all FastAPI endpoints quickly.
- If you change a dependency upstream, rerun `dvc repro` to rebuild the downstream stages automatically.
