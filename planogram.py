import numpy as np
import pandas as pd
import itertools

fixture = pd.read_csv("fixture.csv")
fixture.head()
products = pd.read_csv("products.csv")
products = products.head()


def fun(fixture, products):
    fixture["shelf_width_mm"] = fixture["shelf_width_cm"] * 10
    products = products.sort_values("profit", ascending=False)
    products["target_shelf"] = "None"
    add_profit = 0

    for i in range(fixture.shape[0]):
        target_shelf_list = []
        products_on_shelf = []
        shelf_no = fixture["shelf_no"].iloc[i]
        shelf_width_mm = fixture["shelf_width_mm"].iloc[i]
        for j in range(products.shape[0]):
            product_width = products["product_width_mm"].iloc[j]
            product_profit = products["profit"].iloc[j]
            product_id = products["product_id"].iloc[j]
            target_shelf = products["target_shelf"].iloc[j]

            if shelf_width_mm >= product_width and target_shelf == "None":
                target_shelf_list.append(shelf_no)
                shelf_width_mm -= product_width
                add_profit += product_profit
                products_on_shelf.append(product_id)
            else:
                target_shelf_list.append(target_shelf)
        products["target_shelf"] = target_shelf_list

    return add_profit, products


def planogram(fixture, products):
    """
    Arguments:
    - fixture :: DataFrame[["shelf_no", "shelf_width_cm"]]
    - products :: DataFrame[["product_id", "product_width_mm", "profit"]]

    Returns: DataFrame[["shelf_no", "product_id"]]

    """
    # permutate fixture index to generate best arrangement to fit max. of profit

    fixture_permutate = [list(x) for x in list(set(itertools.permutations(fixture.index.tolist())))]
    profit_list = []

    for index in fixture_permutate:
        profit, df = fun(fixture.iloc[index], products)
        profit_list.append((profit, index, df))

    products = max(profit_list)[2]
    products["shelf_no"] = products["target_shelf"]
    products = products[products["shelf_no"] != "None"][["shelf_no", "product_id"]]

    return products.sort_values("shelf_no")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--products",
        type=argparse.FileType(mode="r"),
        default="products.csv",
        help="products input file",
    )
    parser.add_argument(
        "--fixture",
        type=argparse.FileType(mode="r"),
        default="fixture.csv",
        help="fixture input file",
    )
    parser.add_argument(
        "--out", "-o", default="solution.csv", help="solution output file"
    )

    parser.add_argument(
        '-f'
    )

    args = parser.parse_args()

    fixture = pd.read_csv(args.fixture)
    products = pd.read_csv(args.products)

    solution = planogram(fixture, products)

    solution.to_csv(args.out, index=False)

    print(
        "stats:",
        solution[["shelf_no", "product_id"]]
            .merge(fixture, on="shelf_no")
            .merge(products, on="product_id")
            .assign(n_products=1)
            .pivot_table(
            index=["shelf_no", "shelf_width_cm"],
            values=["n_products", "profit", "product_width_mm"],
            aggfunc=np.sum,
            margins=True,
        ),
        sep="\n",
    )






