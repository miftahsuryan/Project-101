import csv
from pathlib import Path

from production_app.services.risk_baseline import (
    RiskBaselineService,
)


def main() -> None:
    csv_file = Path("data/ai4i2020.csv")
    service = RiskBaselineService()

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    with csv_file.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            prediction = service.predict(
                air_temperature=float(row["Air temperature [K]"]),
                process_temperature=float(
                    row["Process temperature [K]"]
                ),
                rotational_speed=float(
                    row["Rotational speed [rpm]"]
                ),
                torque=float(row["Torque [Nm]"]),
                tool_wear=float(row["Tool wear [min]"]),
            )

            actual_failure = row["Machine failure"] == "1"
            predicted_failure = prediction.risk_level == "high"

            if actual_failure and predicted_failure:
                true_positive += 1
            elif not actual_failure and not predicted_failure:
                true_negative += 1
            elif not actual_failure and predicted_failure:
                false_positive += 1
            else:
                false_negative += 1

    total = (
        true_positive
        + true_negative
        + false_positive
        + false_negative
    )

    accuracy = (
        (true_positive + true_negative) / total
        if total > 0
        else 0.0
    )

    print(f"rows: {total}")
    print(f"true_positive: {true_positive}")
    print(f"true_negative: {true_negative}")
    print(f"false_positive: {false_positive}")
    print(f"false_negative: {false_negative}")
    print(f"accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()