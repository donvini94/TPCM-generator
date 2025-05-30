{
  description = "Python development environment with Poetry";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs =
    { self, nixpkgs }:
    {
      devShells = {
        x86_64-linux.default =
          let
            pkgs = import nixpkgs { system = "x86_64-linux"; };
            pythonWithPackages = pkgs.python312.withPackages (ps: with ps; [
              pip
              virtualenv
            ]);
          in
          pkgs.mkShell {
            buildInputs = [
              pkgs.jdk21
              pythonWithPackages
              pkgs.poetry
              # Build dependencies that might be needed
              pkgs.gcc
              pkgs.pkg-config
            ];
            shellHook = ''
              # Create and activate a virtual environment if it doesn't exist
              if [ ! -d ".venv" ]; then
                ${pythonWithPackages}/bin/python -m venv .venv
                echo "Created virtual environment"
              fi
              source .venv/bin/activate

              # Install required packages directly with pip if poetry fails
              pip install --upgrade pip
              pip install pyecore textx[cli]

              # Set PYTHONPATH to include the project
              export PYTHONPATH=$PYTHONPATH:$(pwd)
              echo "Python environment ready with direct pip installations"
            '';
          };
      };
    };
}
