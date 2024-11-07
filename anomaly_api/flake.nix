{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixos-unstable";
  };
  outputs =
    { nixpkgs, nixpkgs-unstable, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pkgs-unstable = import nixpkgs-unstable { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages =
          (with pkgs; [
            python312
            vscode-langservers-extracted
            djlint
            poetry
            tailwindcss-language-server
            tailwindcss
            emmet-language-server
            prettierd
            eslint_d
            nodejs_22
            typescript
          ])
          ++ (with pkgs-unstable; [
            cargo
            rustc
            rustup

            typescript-language-server
            basedpyright
          ]);
        LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

        POETRY_VIRTUALENVS_IN_PROJECT = true;
        POETRY_INSTALLER_NO_BINARY = "ruff";
        shellHook = ''
          set -a && . .env && set +a
          source $(poetry env info --path)/bin/activate
          exec zsh
        '';
      };
    };
}
