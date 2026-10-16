"""Small plotting helpers for notebook evaluation artifacts."""
import matplotlib.pyplot as plt
import numpy as np


def confusion_matrix_figure(matrix):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1], labels=["Neutral /\ndissatisfied", "Satisfied"])
    ax.set_yticks([0, 1], labels=["Neutral /\ndissatisfied", "Satisfied"])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("Actual label")
    for (row, col), value in np.ndenumerate(matrix):
        ax.text(col, row, f"{value:,}", ha="center", va="center", color="#10243c", fontweight="bold")
    fig.tight_layout()
    return fig
