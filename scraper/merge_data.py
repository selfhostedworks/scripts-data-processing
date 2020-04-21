# -*- coding: utf-8 -*-
import sys
import pandas as pd


def main():
    main = pd.read_excel(sys.argv[1])
    sub = pd.read_csv(sys.argv[2])

    result = main.merge(
        sub[['URL', 'image_name', 'image_url']], on='URL', how='left')


    result.to_excel("Final_Output.xlsx", sheet_name="Speakers")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("Not enough arguments")

    if len(sys.argv) > 3:
        sys.exit("To many arguments")

    main()
