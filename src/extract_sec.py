from phase_a_evidence import extract_sec


if __name__ == "__main__":
    manifest = extract_sec()
    print(f"SEC extraction complete: {len(manifest)} cached artifacts.")
