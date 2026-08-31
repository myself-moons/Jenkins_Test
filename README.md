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


## 0. Create the virtual environment

```bash
cd /workspaces/Jenkins_Test
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas numpy scikit-learn fastapi uvicorn pydantic
```
## 1. Set up Jenkins with the repo

Use the following steps to connect Jenkins to this repository and run the pipeline using the included JenkinsFile.

1. Install Jenkins on the machine that will run the build.
2. Open Jenkins in the browser at `http://localhost:8080` (or the machine's IP and port if it is remote).
3. Create a user if needed for local testing when installing, for example `jadmin` with password `1234`.
4. In the Jenkins Dashboard, click `New Item` and create a `Pipeline` job named something like `Pipeline_Eg`.
5. In the job configuration:
   - Set `Definition` to `Pipeline script from SCM`
   - Set `SCM` to `Git`
   - Repository URL: `https://github.com/myself-moons/Jenkins_Test.git`
   - Branch Specifier: `main` (or `*/main` depending on your Jenkins Git configuration)
   - Script Path: `JenkinsFile`
6. Save the job and click `Build Now` to validate the connection.
7. To trigger automatic builds, enable `Poll SCM` and use a schedule such as `H/2 * * * *`.
8. Make sure the Jenkins agent has Git, Python, and DVC installed so the project can run correctly.
9. If the repository is private, add the required GitHub credentials to Jenkins before saving the pipeline configuration.

This repo is already set up to use `JenkinsFile` as the pipeline definition. The key requirement is that Jenkins must run the same project commands described later in this README, especially `dvc repro` for the ML pipeline.

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

## Important notes

- The pipeline must run in order: collection -> preprocessing -> training -> evaluation.
- The model file `model.pkl` must exist before starting the API service.
- Use the docs at `/docs` to check all FastAPI endpoints quickly.
- If you change a dependency upstream, rerun `dvc repro` to rebuild the downstream stages automatically.
- Jenkins should be treated as the automation layer that runs the same project commands you run locally.
