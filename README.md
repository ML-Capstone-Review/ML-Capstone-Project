# AirlinePulse — passenger feedback capstone

AirlinePulse is the classification-first Streamlit app for course 23CSE301. It provides a one-page airline journey feedback form and a separate evaluator view for the passenger satisfaction model. The demo does not save or transmit customer responses.

## Repository audit and model source of truth

The classification source of truth is `notebooks/classification.ipynb`; `models/best_model.pkl` is intentionally ignored by the app. The notebook cleans duplicate rows, drops the identifier, fills missing arrival delays with the cleaned-data median, performs an 80/20 stratified split (`random_state=42`), caps numerical outliers using training-set IQR bounds, adds `Total Delay`, then scales numeric features and one-hot encodes categoricals. Its final comparison selects Random Forest by weighted F1. The selected settings are `n_estimators=200`, `min_samples_split=5`, `max_depth=None`, `random_state=42`, `n_jobs=1`.

The saved notebook cells report held-out accuracy 0.963466, weighted precision 0.963665, weighted recall 0.963466, weighted F1 0.963396, and ROC-AUC 0.994471 (25,976 test rows). The saved F1 comparison table is included at `app/notebook_model_comparison.csv`, rounded exactly as the notebook displayed it.

A direct execution of the notebook cleaning, split, feature engineering, and RF cells in the supplied pandas 3.0.3 / NumPy 2.5.4 / scikit-learn 1.9.1 environment reproduced the app fit exactly: accuracy 0.963813, weighted precision 0.964021, weighted recall 0.963813, weighted F1 0.963742, and ROC-AUC 0.994490. This differs slightly from the notebook's saved outputs. The notebook requirements do not pin scikit-learn, so the precise source of the difference is not established. The app labels the live evaluation and saved comparison separately. pandas 3.x is required because pandas 2.x rejects the notebook's literal `select_dtypes(include=["str"])` expression; the app retains the repository's pandas 3.0.3 pin. It does not run hyperparameter searches or the entire notebook on each rerun or form submission.

## Run locally on Windows / VS Code

From the repository root (`ML-Capstone-Project`):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate. Open the local URL printed by Streamlit. The first load fits the notebook-selected model once per process; Streamlit caches it for later interactions.

## App structure

- `app.py` — Streamlit entry point and cached model resource.
- `app/schema.py` — feature names and customer-friendly labels derived from notebook inputs.
- `app/model.py` — notebook-aligned data preparation, selected estimator, evaluation artifacts, inference frame construction.
- `app/validation.py` — dataset/schema-based input validation.
- `app/prediction.py` — prediction boundary.
- `app/ui.py` — feedback form and evaluator presentation.
- `data/airline_passenger_satisfaction.csv` — required classification dataset (about 13 MB).

## Correctness and UI verification checklist

- Confirm the app reports 103,904 training rows and 25,976 test rows, with the fresh-fit metrics documented above.
- Execute the original notebook cleaning, split, feature engineering, and Random Forest cells under the pinned pandas/scikit-learn versions; app test metrics and predictions should match that fresh execution.
- Check the confusion matrix against notebook cell E3 and the feature-importance values against E4.
- Submit untouched example values, then edit each field type and submit again. The customer view should show only a thank-you, never the class or probability.
- Try values outside dataset ranges and confirm they are rejected; reset should restore the example values.
- Confirm no network request, persistence, or airline delivery is claimed by the form.

## Deploy to Streamlit Community Cloud

The repository must be pushed to GitHub and the dataset, `app.py`, `app/`, and `requirements.txt` must be committed. Do not commit `.venv/` or the 126 MB local model pickle. The 12.9 MB airline CSV is tracked as a regular file and is below GitHub's 100 MB per-file limit; it does not need Git LFS. Other project datasets are not loaded by this app.

1. Push this repository to a GitHub account/repository accessible to Streamlit Community Cloud.
2. Sign in to Streamlit Community Cloud and create an app from that repository. The connected repository is currently private; Community Cloud can deploy from it, but the app inherits private visibility by default. In the app's **Sharing** settings, set **Who can view this app** to public/searchable to meet the public deployment goal.
3. Choose the `main` branch and set **Main file path** to `app.py` (repository root). In **Advanced settings**, select Python 3.12, matching local setup.
4. Deploy, wait for the first model fit, then open the assigned public URL in a private browser window.
5. Verify the feedback page loads, submit an example form, and confirm only the thank-you message appears. Open Project evaluation and compare its metrics to the notebook values above.
6. Record the public URL and deployment date in this README after live verification. A deployment URL is intentionally omitted until the live app has been tested.

## Git commands

Review the existing work before staging (the repository already had a pandas pin change before this app work):

```powershell
git status --short
git add app.py app README.md requirements.txt
git add data/airline_passenger_satisfaction.csv
git commit -m "Build AirlinePulse classification feedback app"
git push origin main
```

Adjust `main` to the repository's deployment branch if needed. Review `git diff --cached` before committing so unrelated changes are not included.

## Adding the other tracks later

Keep classification as the deployed app until the live verification checklist is complete. After that, add regression and clustering as independent pages/modules with their own notebook-derived preprocessing, validation, metrics, and artifacts. Do not mix their inputs or models into this feedback flow, and preserve the current classification schema and evaluation path.

## Existing project track notes

The repository also contains the CarDekho used-car price prediction regression track and customer-segmentation clustering track. Their notebooks and datasets remain in the repository; AirlinePulse currently loads only the airline classification dataset.

The original regression work tracks a 15,411-row CarDekho used-car dataset and its EDA, cleaning, splitting, feature engineering, categorical encoding, and scaling. The listed candidate regressors are Linear Regression, Ridge, Lasso, ElasticNet, Polynomial Regression, Decision Tree, Random Forest, Gradient Boosting, Support Vector Regression, and K-Nearest Neighbors.
