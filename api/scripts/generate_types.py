#!/usr/bin/env python

import subprocess
from pathlib import Path


def main():
    # Ensure the output directory exists
    output_dir = Path("../frontend/src/types/generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate the GraphQL schema
    schema_path = output_dir / "schema.graphql"
    subprocess.run(
        [
            "strawberry",
            "export-schema",
            "src.main:schema",
            "--output",
            str(schema_path),
        ],
        cwd=".",
    )

    # Generate TypeScript types
    subprocess.run(["graphql-codegen", "--config", "codegen.yml"], cwd="../frontend")


if __name__ == "__main__":
    main()
