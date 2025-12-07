import argparse
from plate_validator import validate_plate
from vehicle_info import get_vehicle_info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validador de placas (AAA-0000 e AAA0A00)")
    parser.add_argument("placas", nargs="+", help="Placas para validar")
    args = parser.parse_args()

    for raw in args.placas:
        result = validate_plate(raw)
        status = "OK" if result.valid else "ERRO"
        plate_type = result.plate_type or "-"
        errors = "; ".join(result.errors) if result.errors else ""
        vehicle = get_vehicle_info(result.normalized) if result.valid else None
        vehicle_str = (
            f" | veiculo={vehicle.brand} {vehicle.model} {vehicle.year} cor={vehicle.color}"
            if vehicle else " | veiculo=n/d"
        )
        print(
            f"{raw} -> {status} | tipo={plate_type} | normalizada={result.normalized}{vehicle_str} | {errors}"
        )


if __name__ == "__main__":
    main()
