from collections import Counter
from pathlib import Path

import pandas as pd

structure = {
    'asia': [],
    'tub': ['asia'],
    'smoke': [],
    'lung': ['smoke'],
    'bronc': ['smoke'],
    'either': ['tub', 'lung'],
    'xray': ['either'],
    'dysp': ['bronc', 'either']
}



def marginal(df, col):
    return df[col].value_counts(normalize=True).to_dict()


def conditional(df, child, parents):
    if not parents:
        return marginal(df, child)
    cpt = {}
    parent_values = df[parents].drop_duplicates().to_dict('records')
    for pv in parent_values:
        mask = (df[parents] == pd.Series(pv)).all(axis=1)
        sub = df[mask]
        if len(sub) == 0:
            continue
        cpt_key = tuple((k, pv[k]) for k in parents)
        cpt[cpt_key] = sub[child].value_counts(normalize=True).to_dict()
    return cpt


def main(df):
    for node, parents in structure.items():
        print(f"\nRozkład dla {node} | {parents if parents else 'brak'}:")
        cpt = conditional(df, node, parents)

        if not parents:
            print("-" * 30)
            print(f"{'Value':<15} {'Probability':<15}")
            print("-" * 30)
            for value, prob in cpt.items():
                print(f"{str(value):<15} {prob:.4f}")
            print("-" * 30)
        else:
            for parent_comb, probs in cpt.items():
                print("\nGiven:")
                for parent, value in parent_comb:
                    print(f"{parent} = {value}")
                print("-" * 30)
                print(f"{'Value':<15} {'Probability':<15}")
                print("-" * 30)
                for value, prob in probs.items():
                    print(f"{str(value):<15} {prob:.4f}")
                print("-" * 30)


if __name__ == "__main__":
    data_fp = Path("raport") / "ASIA_DATA.csv"
    df = pd.read_csv(data_fp)
    main(df)
