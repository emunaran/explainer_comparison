import pandas as pd
import numpy as np

from sklearn.metrics import accuracy_score, mean_squared_error

from explainer_comparison.ExplainerFactory import ExplainerFactory


def run_and_collect_explanations(factory: ExplainerFactory, X_data, explainers=None) -> pd.DataFrame:
    results = []
    available_explainers = ["shap", "lime"]  # Easily extendable for additional explainers
    
    chosen_explainers = explainers if explainers is not None else available_explainers

    for explainer_type in chosen_explainers:
        explainer = factory.create_explainer(explainer_type)
        if explainer is not None:
            try:
                global_explanation = explainer.explain_global(X_data)
                results.append(global_explanation)
                print(f'\n {explainer_type.upper()} explanation created')
            except Exception as e:
                print(f"Failed to create {explainer_type.upper()} explanation: {e}")
        else:
            print(f"No explainer available for type: {explainer_type}")

    # Concatenate all results along columns (axis=1), handling cases where some explanations might fail
    if results:
        return pd.concat(results, axis=1)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no explanations were added

def permutation_feature_importance(model, X_data, y_data, metric='accuracy', random_state=None):
    """
    Calculates permutation feature importance for a given model.
    
    Parameters:
    - model: The trained machine learning model.
    - X: The feature matrix.
    - y: The target vector.
    - metric: The metric to use for evaluating the model. Either 'accuracy' or 'mse'.
    - random_state: The random seed for reproducibility.
    
    Returns:
    - feature_importances: A dict containing the feature names and their importance scores.
    """
    if metric == 'accuracy':
        baseline_score = accuracy_score(y_data, model.predict(X_data))
        scorer = accuracy_score
    elif metric == 'mse':
        baseline_score = mean_squared_error(y_data, model.predict(X_data))
        scorer = mean_squared_error
    else:
        raise ValueError("Invalid metric. Please choose 'accuracy' or 'mse'.")
    
    feature_importances = {}
    for feature in X_data.columns:
        X_data_permuted = X_data.copy()
        X_data_permuted[feature] = np.random.permutation(X_data[feature])
        permuted_score = scorer(y_data, model.predict(X_data_permuted))
        feature_importances[feature] = baseline_score - permuted_score

    return feature_importances
