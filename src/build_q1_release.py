from build_q1_analysis_outputs import main as build_analysis_outputs
from build_q1_v3_pipeline import main as build_sql_marts


def main() -> None:
    build_sql_marts()
    build_analysis_outputs()
    print("Q1 B4 analytical release rebuilt successfully.")


if __name__ == "__main__":
    main()
