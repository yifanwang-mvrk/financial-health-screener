from build_q1_analysis_outputs import main as build_analysis_outputs
from build_q1_v3_pipeline import main as build_sql_marts
from phase_a_evidence import build_phase_a_evidence


def main() -> None:
    build_phase_a_evidence()
    build_sql_marts()
    build_analysis_outputs()
    print("Phase A and Q1 B4/B5 release rebuilt successfully.")


if __name__ == "__main__":
    main()
