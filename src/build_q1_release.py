from build_q1_analysis_outputs import main as build_analysis_outputs
from build_q1_v3_pipeline import main as build_sql_marts
from phase_a_evidence import build_b1_pilot_evidence


def main() -> None:
    build_b1_pilot_evidence()
    build_sql_marts()
    build_analysis_outputs()
    print("Six-company B1 Pilot analytical and display snapshot rebuilt successfully.")


if __name__ == "__main__":
    main()
