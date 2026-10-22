{
  description = "multisurveys-apis dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Python
            python
            poetry

            # Node (tailwind CSS build)
            nodejs_24

            # Database
            postgresql_16 # psql, pg_dump, pg_isready, etc.

            jinja-lsp
            ruff

            # Deploy tooling
            awscli2
            kubectl
            kubernetes-helm
            helm-docs

            # Process manager
            process-compose

            gettext # envsubst
            jq
            yq-go
            gh
          ];

          shellHook = ''
            export POETRY_VIRTUALENVS_IN_PROJECT=true
            export POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON=true
          '';

          # Needed for psycopg2-binary / numpy / scipy wheels
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
        };
      }
    );
}
