{ pkgs }: {
  deps = [
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.postgresql
    pkgs.openssl
    pkgs.libffi
    pkgs.cacert
  ];
}
