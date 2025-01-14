{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShell {
            venvDir = ".venv";
            packages =
              with pkgs;
              [ python311 ]
              ++ (with pkgs.python311Packages; [
                pip
                venvShellHook
                requests
                pandas
                openpyxl
              ]);
            shellHook = ''
              if [ ! -d ".venv" ]; then
                python -m venv .venv
                source .venv/bin/activate
                pip install --upgrade pip setuptools
                pip install pyecore
                echo "Virtual environment and dependencies installed."
              elif [ -z "$VIRTUAL_ENV" ]; then
                source .venv/bin/activate
              fi
            '';
          };
        }
      );
    };
}
